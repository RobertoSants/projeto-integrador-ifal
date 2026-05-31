"""
Settings — Banco de Talentos Comunitário
Projeto Integrador IFAL 2026.1
Foco: Segurança Avançada & Conformidade com LGPD
"""

from datetime import timedelta
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# Chave secreta carregada via variável de ambiente (Crucial nunca expor no Git)
SECRET_KEY = config("SECRET_KEY")

# Em produção, DEBUG deve ser obrigatoriamente False
DEBUG = config("DEBUG", default=False, cast=bool)

# [SEGURANÇA] Restrição de Hosts para mitigar HTTP Host Header Injection
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", 
    default="localhost,127.0.0.1", 
    cast=lambda v: [s.strip() for s in v.split(",")]
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Libs de Terceiros
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    # Apps do Projeto Escopo Local
    "accounts",
    "workers",
    "services",
    "reviews",
    "search",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware", # Gerencia políticas de CORS
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware", # Proteção activa contra CSRF
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware", # Bloqueia Clickjacking
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Banco de Dados — PostgreSQL para Desenvolvimento/Produção
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# Validação estrita de senhas dos usuários (Trabalhadores/Contratantes)
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Maceio"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model unificando a autenticação
AUTH_USER_MODEL = "accounts.User"

# Django REST Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # Substitui a classe padrão pela nossa classe customizada com suporte a Cookies e Bearer
        "accounts.authentication.CookieJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
}

# [SEGURANÇA & LGPD] Configuração Robusta de Tokens JWT via Cookie HttpOnly
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_FLUSH_AFTER_LOGOUT": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    
    "AUTH_COOKIE": "access_token",
    "AUTH_COOKIE_HTTP_ONLY": True,  # Proteção XSS ativa
    "AUTH_COOKIE_SECURE": False,     # OBRIGATÓRIO False para permitir tráfego local sem HTTPS
    "AUTH_COOKIE_SAMESITE": "Lax",   
}

# [SEGURANÇA] Controle estrito de Origens do CORS para as portas do Live Server
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5501",
    "http://127.0.0.1:5501",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True # Essencial para permitir o tráfego dos cookies HttpOnly

# [SEGURANÇA OBRIGATÓRIA PARA DEPLOY / PRODUÇÃO]
if not DEBUG:
    # Força redirecionamento total para HTTPS
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Cabeçalhos extras de proteção do navegador
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    
    # Proteção HTTP Strict Transport Security (HSTS)
    SECURE_HSTS_SECONDS = 31536000 # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True