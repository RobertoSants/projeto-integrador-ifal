import logging

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from .models import Worker
from .serializers import WorkerListSerializer, WorkerDetailSerializer, WorkerCreateSerializer
from accounts.authentication import CookieJWTAuthentication

try:
    from google import genai
    from google.genai import types as genai_types
    from google.genai.errors import APIError, ClientError, ServerError
    _GEMINI_AVAILABLE = True
except ImportError:
    _GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """
Você é um redator especialista em reescrita de perfis profissionais para
plataformas de serviços no Brasil, com foco em trabalhadores do interior de
Alagoas que possuem baixo letramento digital.

REGRAS INVIOLÁVEIS:
1. Reescreva somente o que o trabalhador já descreveu. Nunca invente, suponha
   ou acrescente competências, certificações, experiências ou habilidades que
   não estejam explicitamente presentes no texto original.
2. Corrija erros ortográficos, gramaticais e de pontuação.
3. Organize o texto em linguagem formal, clara e objetiva.
4. Mantenha o tom humilde e acessível; não use jargões corporativos.
5. Limite a resposta ao texto reescrito, sem explicações adicionais,
   sem saudações, sem comentários sobre o processo.
6. Se o texto original estiver vazio ou ilegível, retorne exatamente:
   "Não foi possível melhorar o texto neste momento devido a uma "
   "instabilidade no serviço externo. Por favor, tente novamente em "
   "alguns instantes."

FORMATO DE SAÍDA:
Retorne apenas o perfil reescrito, em parágrafo(s) corrido(s), sem títulos
nem marcadores.
""".strip()

_FALLBACK_MESSAGE = (
    "Não foi possível melhorar o texto neste momento devido a uma "
    "instabilidade no serviço externo. Por favor, tente novamente em "
    "alguns instantes."
)


class WorkerListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        city = request.query_params.get("city", None)
        service_id = request.query_params.get("service", None)
        workers = Worker.objects.all()

        if city:
            workers = workers.filter(city__iexact=city)
        if service_id:
            workers = workers.filter(services__id=service_id)

        serializer = WorkerListSerializer(
            workers, many=True,
            context={"request": request, "contratante_city": city},
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = WorkerCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OptimizeBioView(APIView):
    """
    POST /api/workers/optimize-bio/
    Body : {"bio": "<rascunho bruto>"}
    200  : {"optimized_bio": "<texto aprimorado>"}
    400  : {"error": "O campo 'bio' é obrigatório e não pode estar vazio."}

    Aberto sem autenticação (AllowAny) para facilitar testes integrados.
    O método `_process_bio` é o ponto de injeção das bibliotecas de NLP —
    substitua sua implementação sem alterar a assinatura da view.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # --- extração e validação do payload ---
        raw_bio = ""
        if isinstance(request.data, dict):
            raw_bio = str(request.data.get("bio", "") or "").strip()

        if not raw_bio:
            return Response(
                {"error": "O campo 'bio' é obrigatório e não pode estar vazio."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --- ponto de injeção NLP: troque _process_bio pela sua implementação ---
        optimized_bio = self._process_bio(raw_bio)
        return Response({"optimized_bio": optimized_bio}, status=status.HTTP_200_OK)

    def _process_bio(self, raw_bio: str) -> str:
        """
        Ponto de entrada para as bibliotecas generativas de linguagem.
        Recebe o texto cru validado e devolve o texto processado.
        Delega para _call_gemini enquanto a integração NLP não for injetada.
        """
        return self._call_gemini(raw_bio)

    def _call_gemini(self, raw_bio: str) -> str:
        if not _GEMINI_AVAILABLE:
            logger.error("Biblioteca google-genai não instalada. Execute: pip install google-genai")
            return _FALLBACK_MESSAGE

        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=raw_bio,
                config=genai_types.GenerateContentConfig(
                    system_instruction=_SYSTEM_PROMPT,
                    temperature=0.3,
                    max_output_tokens=1024,
                ),
            )
            return response.text.strip()

        except ClientError as exc:
            # 429 = rate limit  |  408 = timeout do lado do cliente
            if exc.code == 429:
                logger.warning("Gemini API rate limit atingido (model=%s).", settings.GEMINI_MODEL)
            else:
                logger.error("Gemini API erro do cliente %s: %s", exc.code, exc, exc_info=True)

        except ServerError as exc:
            # 504 = gateway timeout  |  5xx = erro interno do servidor
            logger.warning("Gemini API erro do servidor %s (model=%s).", exc.code, settings.GEMINI_MODEL)

        except APIError as exc:
            # Qualquer outro erro da API (base de ClientError e ServerError)
            logger.error("Gemini API erro inesperado %s: %s", exc.code, exc, exc_info=True)

        except Exception as exc:  # noqa: BLE001
            logger.error("Erro interno ao chamar Gemini: %s", exc, exc_info=True)

        return _FALLBACK_MESSAGE


class MyProfileView(APIView):
    """
    GET /api/workers/me/
    Localiza o perfil do trabalhador logado via cookie seguro da sessão.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        try:
            worker = Worker.objects.get(user=request.user)
            serializer = WorkerDetailSerializer(worker, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Worker.DoesNotExist:
            return Response(
                {"detail": "Perfil profissional não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )


class WorkerDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Worker.objects.get(pk=pk)
        except Worker.DoesNotExist:
            return None

    def get(self, request, pk):
        worker = self.get_object(pk)
        if not worker:
            return Response({"error": "Trabalhador não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        return Response(WorkerDetailSerializer(worker, context={"request": request}).data)

    def put(self, request, pk):
        worker = self.get_object(pk)
        if not worker:
            return Response({"error": "Trabalhador não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        if worker.user != request.user:
            return Response({"error": "Sem permissão."}, status=status.HTTP_403_FORBIDDEN)
        serializer = WorkerCreateSerializer(worker, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        worker = self.get_object(pk)
        if not worker:
            return Response({"error": "Trabalhador não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        if worker.user != request.user:
            return Response({"error": "Sem permissão."}, status=status.HTTP_403_FORBIDDEN)
        worker.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkerServicesView(APIView):
    def get(self, request, pk):
        try:
            worker = Worker.objects.get(pk=pk)
        except Worker.DoesNotExist:
            return Response({"error": "Trabalhador não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        from services.serializers import ServiceCategorySerializer
        serializer = ServiceCategorySerializer(worker.services.all(), many=True)
        return Response(serializer.data)


class WorkerReviewsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, pk):
        try:
            worker = Worker.objects.get(pk=pk)
        except Worker.DoesNotExist:
            return Response({"error": "Trabalhador não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        from reviews.serializers import ReviewSerializer
        serializer = ReviewSerializer(worker.reviews.all(), many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        try:
            worker = Worker.objects.get(pk=pk)
        except Worker.DoesNotExist:
            return Response({"error": "Trabalhador não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        from reviews.serializers import ReviewSerializer
        data = request.data.copy()
        data["worker"] = worker.id
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            user = request.user if (request.user and request.user.is_authenticated) else None
            serializer.save(worker=worker, author=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)