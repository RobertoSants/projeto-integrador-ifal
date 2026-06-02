import re
from rest_framework import serializers
from .models import Worker
from services.serializers import ServiceCategorySerializer
from services.models import ServiceCategory
from datetime import date

class WorkerListSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(read_only=True)
    services = serializers.StringRelatedField(many=True)
    is_local = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Worker
        fields = ["id", "full_name", "city", "state", "phone", "avg_rating", "services", "is_local", "photo_url"]

    def get_is_local(self, obj):
        contratante_city = self.context.get("contratante_city")
        if contratante_city:
            return obj.city.lower() == contratante_city.lower()
        return False

    def get_photo_url(self, obj):
        # Retorna a string Base64 direta guardada no campo photo
        return obj.photo if obj.photo else None


class WorkerDetailSerializer(serializers.ModelSerializer):
    services = ServiceCategorySerializer(many=True, read_only=True)
    photo_url = serializers.SerializerMethodField()
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Worker
        fields = ["id", "user", "full_name", "birth_date", "age", "bio", "phone", "city", "state", "photo_url", "services", "avg_rating", "created_at"]

    def get_photo_url(self, obj):
        return obj.photo if obj.photo else None


class WorkerCreateSerializer(serializers.ModelSerializer):
    services = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ServiceCategory.objects.all(),
        required=True,
        allow_empty=False,
    )
    photo = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Worker
        fields = ["full_name", "birth_date", "bio", "phone", "city", "state", "photo", "services"]

    def validate_birth_date(self, value):
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.year, value.day))
        if age < 18:
            raise serializers.ValidationError("É obrigatório ter mais de 18 anos para anunciar serviços.")
        return value

    def validate_phone(self, value):
        clean_phone = re.sub(r"\D", "", value)
        if not (10 <= len(clean_phone) <= 11):
            raise serializers.ValidationError("O telefone deve conter um formato regional válido com DDD.")
        return clean_phone

    def create(self, validated_data):
        services = validated_data.pop("services", [])
        worker = Worker.objects.create(**validated_data)
        worker.services.set(services)
        return worker

    def update(self, instance, validated_data):
        services = validated_data.pop("services", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if services is not None:
            instance.services.set(services)
        return instance