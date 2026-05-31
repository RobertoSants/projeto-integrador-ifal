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

# ENGENHARIA DE PROMPT OTIMIZADA: Força a expansão rica de competências práticas com linguagem acessível
_SYSTEM_PROMPT = """
Você é um redator especialista em Recursos Humanos focado no mercado de trabalho comunitário de Alagoas. Sua única função é transformar rascunhos simples de trabalhadores com baixo letramento digital em apresentações profissionais robustas, completas e detalhadas para currículos.

REGRAS OBRIGATÓRIAS DE ESCRITA:
1. Apresentação Pessoal: Você DEVE, obrigatoriamente, iniciar o primeiro parágrafo estruturando os metadados recebidos no formato exato: "Meu nome é [Nome], tenho [X] anos e atuo de forma profissional com...". 
2. Expansão Rica de Competências: Nunca devolva uma resposta curta ou resumida. Mesmo que o rascunho seja curto (Ex: "conserto computador"), desmembre a atividade em processos práticos completos da rotina (Ex: desmontagem, detecção de curtos, substituição de hardware, formatação, instalação de drivers e manutenção preventiva). 
3. Tom Equilibrado: Mantenha a linguagem profissional, clara, humilde e realista para o mercado local. Não utilize jargões corporativos complexos da Faria Lima (Evite termos como "expertise", "know-how", "gestão de prazos", "otimização"). Substitua por termos simples como "compromisso", "cuidado", "organização", "testes de funcionamento".
4. Formatação por Blocos Obligatória: Divida o texto estritamente em duas partes separadas por uma quebra de linha dupla (\\n\\n). O primeiro bloco é o resumo estendido do perfil e o segundo bloco detalha as frentes de serviços práticas.

EXEMPLO DE FORMATO DE SAÍDA EXIGIDO:
Meu nome é Roberto dos Santos, tenho 25 anos e atuo de forma profissional com serviços completos de assistência técnica, manutenção e reparo de computadores e notebooks na região. Trabalho com o diagnóstico de falhas, substituição de peças com defeito, formatação de sistemas operacionais e limpeza interna de componentes para garantir o bom desempenho dos equipamentos.

Principais frentes de atendimento:
- Formatação e instalação de sistemas operacionais, antivírus e programas utilitários.
- Diagnóstico avançado de problemas de hardware, placas e troca de componentes internos.
- Testes rigorosos de funcionamento para assegurar a estabilidade completa da máquina.
- Atendimento direto focado no compromisso, na transparência e no cuidado com o aparelho do cliente.

DIRETRIZES DE SEGURANÇA (ANTI-ZOEIRA):
1. Se o rascunho contiver qualquer tipo de palavrão, termos ofensivos, piadas ou tentativas de testar o sistema com perguntas gerais fora de contexto de trabalho (como receitas ou códigos), interrompa e retorne exatamente a frase de erro padrão abaixo.

FRASE DE ERRO PADRÃO:
"O assistente inteligente foi projetado exclusivamente para transformar textos brutos em experiências e perfis profissionais formais. Por favor, insira um rascunho válido sobre os seus serviços autônomos para que possamos aprimorá-lo."

FORMATO DE SAÍDA:
Retorne estritamente o texto estruturado conforme o modelo com as quebras de linha duplas, sem comentários extras da IA e sem saudações.
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
        serializer = WorkerListSerializer(workers, many=True, context={"request": request, "contratante_city": city})
        return Response(serializer.data)

    def post(self, request):
        serializer = WorkerCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OptimizeBioView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        raw_bio = ""
        name = ""
        age = ""
        
        if isinstance(request.data, dict):
            raw_bio = str(request.data.get("bio", "") or "").strip()
            name = str(request.data.get("name", "") or "").strip()
            age = str(request.data.get("age", "") or "").strip()
        else:
            raw_bio = str(request.data or "").strip()

        if not raw_bio:
            return Response({"error": "O campo 'bio' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        instruction_payload = raw_bio
        if name and age:
            instruction_payload = f"INSTRUÇÕES EXTRAS DE IDENTIFICAÇÃO:\nNome do trabalhador: {name}\nIdade do trabalhador: {age} anos\n\nRASCUNHO BRUTO A SER OTIMIZADO:\n{raw_bio}"

        optimized_bio = self._call_gemini(instruction_payload)
        return Response({"optimized_bio": optimized_bio}, status=status.HTTP_200_OK)

    def _call_gemini(self, instruction_payload: str) -> str:
        if not _GEMINI_AVAILABLE:
            return _FALLBACK_MESSAGE
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=instruction_payload,
                config=genai_types.GenerateContentConfig(
                    system_instruction=_SYSTEM_PROMPT,
                    temperature=0.3,
                    max_output_tokens=1024,
                ),
            )
            return response.text.strip()
        except Exception as exc:
            logger.error("Erro interno ao chamar Gemini: %s", exc, exc_info=True)
        return _FALLBACK_MESSAGE


class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        try:
            worker = Worker.objects.get(user=request.user)
            return Response(WorkerDetailSerializer(worker, context={"request": request}).data, status=status.HTTP_200_OK)
        except Worker.DoesNotExist:
            return Response({"detail": "Perfil profissional não encontrado."}, status=status.HTTP_404_NOT_FOUND)


class WorkerDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try: return Worker.objects.get(pk=pk)
        except Worker.DoesNotExist: return None

    def get(self, request, pk):
        worker = self.get_object(pk)
        if not worker: return Response({"error": "Trabalhador não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        return Response(WorkerDetailSerializer(worker, context={"request": request}).data)

    def put(self, request, pk):
        worker = self.get_object(pk)
        if not worker: return Response({"error": "Trabalhador não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        if worker.user != request.user: return Response({"error": "Sem permissão."}, status=status.HTTP_403_FORBIDDEN)
        serializer = WorkerCreateSerializer(worker, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        worker = self.get_object(pk)
        if not worker: return Response({"error": "Trabalhador não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        if worker.user != request.user: return Response({"error": "Sem permissão."}, status=status.HTTP_403_FORBIDDEN)
        worker.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkerServicesView(APIView):
    def get(self, request, pk):
        try: worker = Worker.objects.get(pk=pk)
        except Worker.DoesNotExist: return Response({"error": "Trabalhador não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        from services.serializers import ServiceCategorySerializer
        return Response(ServiceCategorySerializer(worker.services.all(), many=True).data)


class WorkerReviewsView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, pk):
        try: worker = Worker.objects.get(pk=pk)
        except Worker.DoesNotExist: return Response({"error": "Trabalhador não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        from reviews.serializers import ReviewSerializer
        return Response(ReviewSerializer(worker.reviews.all(), many=True).data)

    def post(self, request, pk):
        try: worker = Worker.objects.get(pk=pk)
        except Worker.DoesNotExist: return Response({"error": "Trabalhador não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        from reviews.serializers import ReviewSerializer
        data = request.data.copy()
        data["worker"] = worker.id
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            user = request.user if (request.user and request.user.is_authenticated) else None
            serializer.save(worker=worker, author=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)