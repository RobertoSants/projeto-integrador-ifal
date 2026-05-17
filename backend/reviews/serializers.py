from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "worker", "author", "author_username", "rating", "comment", "created_at"]
        read_only_fields = ["author", "author_username", "created_at"]

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("A nota deve ser entre 1 e 5.")
        return value
