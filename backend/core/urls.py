"""
URL Configuration — Banco de Talentos Comunitário
Projeto Integrador IFAL — 2026.1
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Autenticação JWT
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # Módulos da aplicação
    path("api/accounts/", include("accounts.urls")),
    path("api/workers/", include("workers.urls")),
    path("api/services/", include("services.urls")),
    path("api/reviews/", include("reviews.urls")),
    path("api/search/", include("search.urls")),
]
