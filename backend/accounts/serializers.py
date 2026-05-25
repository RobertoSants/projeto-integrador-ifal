import re
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    # REQUISITO DE SEGURANÇA: E-mail obrigatório e único em nível de serializador
    email = serializers.EmailField(required=True)
    city = serializers.CharField(required=True, allow_blank=False)
    state = serializers.CharField(required=True, allow_blank=False, max_length=2)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password_confirm", "city", "state", "first_name"]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Este endereço de e-mail já está sendo utilizado.")
        return value

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        
        # POLÍTICA DE SENHAS PROFISSIONAIS: Mínimo de 8 caracteres, pelo menos uma letra e um número
        password = data["password"]
        if len(password) < 8:
            raise serializers.ValidationError({"password": "A senha deve conter no mínimo 8 caracteres."})
        if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            raise serializers.ValidationError({"password": "A senha deve ser forte: conter pelo menos uma letra e um número."})
            
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "city", "state", "first_name"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("A nova senha deve conter no mínimo 8 caracteres.")
        if not re.search(r"[A-Za-z]", value) or not re.search(r"[0-9]", value):
            raise serializers.ValidationError("A nova senha deve conter pelo menos uma letra e um número.")
        return value