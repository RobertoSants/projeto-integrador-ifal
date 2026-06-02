from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer
from accounts.authentication import CookieJWTAuthentication


def _set_auth_cookies(response, access_token, refresh_token=None):
    """
    Refatoração (Clean Code): Centraliza a injeção de cookies para eliminar 
    a duplicação de código (code smell: Duplicated Code) entre login e refresh.
    """
    response.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        value=access_token,
        expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
    )
    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            expires=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            httponly=True,
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data.get("access")
            refresh_token = response.data.get("refresh")
            
            del response.data["access"]
            if "refresh" in response.data:
                del response.data["refresh"]
                
            response.data["message"] = "Autenticação efetuada com sucesso."
            _set_auth_cookies(response, access_token, refresh_token)
        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        
        if not refresh_token:
            return Response(
                {"detail": "Nenhuma sessão ativa localizada."}, 
                status=status.HTTP_204_NO_CONTENT
            )
            
        request.data["refresh"] = refresh_token
        
        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                access_token = response.data.get("access")
                del response.data["access"]
                _set_auth_cookies(response, access_token)
            return response
        except (InvalidToken, TokenError):
            res = Response({"detail": "Sessão expirada."}, status=status.HTTP_401_UNAUTHORIZED)
            res.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE"])
            res.delete_cookie("refresh_token")
            return res


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({"message": "Sessão encerrada com sucesso."}, status=status.HTTP_200_OK)
        response.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE"])
        response.delete_cookie("refresh_token")
        return response


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        consentimento = request.data.get("consentimento", False)
        if not consentimento:
            return Response(
                {"error": "É obrigatório aceitar os termos de consentimento para processamento de dados sob as diretrizes da LGPD."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        return Response(UserSerializer(request.user, context={'request': request}).data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user_to_delete = request.user
        response = Response({"message": "Conta removida com sucesso."}, status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE"])
        response.delete_cookie("refresh_token")
        user_to_delete.delete()
        return response


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response(
                    {"error": "Senha atual incorreta."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"message": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)