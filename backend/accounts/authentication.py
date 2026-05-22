from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings

class CookieJWTAuthentication(JWTAuthentication):
    """
    Extensão customizada do JWTAuthentication que intercepta a requisição e 
    extrai o token de dentro do Cookie seguro caso o cabeçalho Authorization não exista.
    """
    def authenticate(self, request):
        header = self.get_header(request)
        
        # Se não houver cabeçalho Authorization, busca o token no Cookie HttpOnly
        if header is None:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])
            if raw_token is not None:
                validated_token = self.get_validated_token(raw_token)
                return self.get_user(validated_token), validated_token

        return super().authenticate(request)