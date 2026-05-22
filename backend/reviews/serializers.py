from rest_framework import serializers
from .models import Review
from workers.models import Worker  # Importação cruzada para ler o nome do trabalhador

class ReviewSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    author_fullname = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ["id", "worker", "author", "author_username", "author_fullname", "rating", "comment", "created_at"]
        read_only_fields = ["author", "author_username", "author_fullname", "created_at"]

    def get_author_fullname(self, obj):
        if obj.author:
            # CORREÇÃO CIRÚRGICA: Busca se o usuário que comentou possui um perfil de Trabalhador cadastrado
            worker_profile = Worker.objects.filter(user=obj.author).first()
            if worker_profile and worker_profile.full_name:
                return worker_profile.full_name
            
            # Fallback secundário: Se não for trabalhador, tenta o nome do User ou o próprio username (Ex: "darknight")
            nome_user = obj.author.get_full_name()
            return nome_user.strip() if nome_user.strip() else obj.author.username
        return None

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("A nota deve ser entre 1 e 5.")
        return value