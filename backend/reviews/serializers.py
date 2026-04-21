from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "worker", "author", "rating", "comment", "created_at"]
        read_only_fields = ["author", "created_at"]

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("A nota deve ser entre 1 e 5.")
        return value
