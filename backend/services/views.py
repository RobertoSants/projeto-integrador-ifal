from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ServiceCategory
from .serializers import ServiceCategorySerializer


class ServiceCategoryListView(APIView):
    def get(self, request):
        categories = ServiceCategory.objects.all()
        serializer = ServiceCategorySerializer(categories, many=True)
        return Response(serializer.data)


class ServiceCategoryDetailView(APIView):
    def get(self, request, pk):
        try:
            category = ServiceCategory.objects.get(pk=pk)
        except ServiceCategory.DoesNotExist:
            return Response({"error": "Categoria não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ServiceCategorySerializer(category).data)


class ServiceWorkersView(APIView):
    def get(self, request, pk):
        try:
            category = ServiceCategory.objects.get(pk=pk)
        except ServiceCategory.DoesNotExist:
            return Response({"error": "Categoria não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        from workers.serializers import WorkerListSerializer
        workers = category.workers.all()
        serializer = WorkerListSerializer(workers, many=True)
        return Response(serializer.data)
