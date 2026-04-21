from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Review
from .serializers import ReviewSerializer


class ReviewCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return None

    def get(self, request, pk):
        review = self.get_object(pk)
        if not review:
            return Response({"error": "Avaliação não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ReviewSerializer(review).data)

    def put(self, request, pk):
        review = self.get_object(pk)
        if not review:
            return Response({"error": "Avaliação não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        if review.author != request.user:
            return Response({"error": "Sem permissão."}, status=status.HTTP_403_FORBIDDEN)
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        review = self.get_object(pk)
        if not review:
            return Response({"error": "Avaliação não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        if review.author != request.user:
            return Response({"error": "Sem permissão."}, status=status.HTTP_403_FORBIDDEN)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
