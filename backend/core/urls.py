"""
URL Configuration — Banco de Talentos Comunitário
Projeto Integrador IFAL — 2026.1
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenVerifyView
# Importação cirúrgica das views customizadas do app accounts para suporte a cookies httponly
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