from rest_framework import serializers
from .models import Worker
from services.serializers import ServiceCategorySerializer


class WorkerListSerializer(serializers.ModelSerializer):
    services = serializers.StringRelatedField(many=True)
    is_local = serializers.SerializerMethodField()

    class Meta:
        model = Worker
        fields = ["id", "full_name", "city", "state", "phone", "avg_rating", "services", "is_local"]

    def get_is_local(self, obj):
        contratante_city = self.context.get("contratante_city")
        if contratante_city:
            return obj.city.lower() == contratante_city.lower()
        return False


class WorkerDetailSerializer(serializers.ModelSerializer):
    services = ServiceCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Worker
        fields = [
            "id", "user", "full_name", "bio", "phone",
            "city", "state", "photo", "services",
            "avg_rating", "created_at",
        ]


class WorkerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = ["full_name", "bio", "phone", "city", "state", "photo", "services"]

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
