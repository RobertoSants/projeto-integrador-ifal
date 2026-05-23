"""
URL Configuration — Banco de Talentos Comunitário
Projeto Integrador IFAL — 2026.1
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenVerifyView
from accounts.views import CustomTokenObtainPairView, CustomTokenRefreshView, LogoutView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Autenticação JWT (Atualizado para controle de cookies seguros)
    path("api/auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/auth/logout/", LogoutView.as_view(), name="token_logout"),

    # Módulos da aplicação
    path("api/accounts/", include("accounts.urls")),
    path("api/workers/", include("workers.urls")),
    path("api/services/", include("services.urls")),
    path("api/reviews/", include("reviews.urls")),
    path("api/search/", include("search.urls")),
]

# CORREÇÃO DE INFRAESTRUTURA: Habilita o Django para servir as fotos de perfil salvas em ambiente local (Evita erro 404)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)