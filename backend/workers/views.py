from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from .models import Worker
from .serializers import WorkerListSerializer, WorkerDetailSerializer, WorkerCreateSerializer
from accounts.authentication import CookieJWTAuthentication  # Importação da sua autenticação segura

class WorkerListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
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


class OptimizeBioMockView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        raw_bio = request.data.get("bio", "")
        if not raw_bio:
            return Response({"error": "O campo 'bio' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
        
        optimized = f"Profissional qualificado com experiência prática em Alagoas. Especialista em serviços sob demanda, focado em eficiência, pontualidade e excelência na execução: '{raw_bio}'"
        return Response({"optimized_bio": optimized}, status=status.HTTP_200_OK)


class MyProfileView(APIView):
    """
    ENDPOINT PROFISSIONAL: Localiza diretamente o perfil do trabalhador logado 
    com base no cookie seguro da sessão. Evita dependências de filtros complexos no front.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        try:
            worker = Worker.objects.get(user=request.user)
            serializer = WorkerDetailSerializer(worker, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Worker.DoesNotExist:
            return Response({"detail": "Perfil profissional não encontrado."}, status=status.HTTP_404_NOT_FOUND)