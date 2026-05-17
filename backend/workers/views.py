from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Worker
from .serializers import WorkerListSerializer, WorkerDetailSerializer, WorkerCreateSerializer


class WorkerListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        workers = Worker.objects.all()
        serializer = WorkerListSerializer(workers, many=True, context={"request": request})
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
    def get(self, request, pk):
        try:
            worker = Worker.objects.get(pk=pk)
        except Worker.DoesNotExist:
            return Response({"error": "Trabalhador não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        from reviews.serializers import ReviewSerializer
        serializer = ReviewSerializer(worker.reviews.all(), many=True)
        return Response(serializer.data)
