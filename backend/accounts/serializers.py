from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password_confirm", "city", "state"]
        extra_kwargs = {
            'username': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'city': {'required': True, 'allow_blank': False},
            'state': {'required': True, 'allow_blank': False},
        }

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username deve ter pelo menos 3 caracteres.")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este username já está em uso.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return value

    def validate_state(self, value):
        if len(value) != 2:
            raise serializers.ValidationError("Estado deve ter 2 caracteres (ex: AL).")
        return value.upper()

    def validate_city(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Cidade deve ter pelo menos 2 caracteres.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Senha deve ter pelo menos 8 caracteres.")
        if value.isdigit():
            raise serializers.ValidationError("Senha não pode conter apenas números.")
        return value

    def validate(self, data):
        if data.get("password") != data.get("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "As senhas não coincidem."})
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
        fields = ["id", "username", "email", "city", "state"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
