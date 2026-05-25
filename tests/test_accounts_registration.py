import uuid

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient


User = get_user_model()


def build_payload(**overrides):
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "username": f"user_{suffix}",
        "email": f"user_{suffix}@example.com",
        "password": "Senha1234",
        "password_confirm": "Senha1234",
        "city": "Maceió",
        "state": "AL",
        "consentimento": True,
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
def test_ct_001_cadastro_valido_retornando_201_e_permite_login():
    client = APIClient()
    register_response = client.post("/api/accounts/register/", build_payload(), format="json")

    assert register_response.status_code == status.HTTP_201_CREATED
    assert register_response.data["city"] == "Maceió"
    assert register_response.data["state"] == "AL"
    assert {"id", "username", "email", "city", "state"}.issubset(register_response.data.keys())

    login_response = client.post(
        "/api/auth/login/",
        {
            "username": register_response.data["username"],
            "password": "Senha1234",
        },
        format="json",
    )

    assert login_response.status_code == status.HTTP_200_OK
    assert login_response.data["message"] == "Autenticação efetuada com sucesso."
    assert "access_token" in login_response.cookies
    assert "refresh_token" in login_response.cookies


@pytest.mark.django_db
def test_ct_002_rejeita_email_duplicado():
    client = APIClient()
    first_payload = build_payload(email="joao@email.com")
    second_payload = build_payload(username="user_outro", email="joao@email.com")

    assert client.post("/api/accounts/register/", first_payload, format="json").status_code == status.HTTP_201_CREATED

    duplicate_response = client.post("/api/accounts/register/", second_payload, format="json")

    assert duplicate_response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in duplicate_response.data
    assert User.objects.filter(email__iexact="joao@email.com").count() == 1


@pytest.mark.django_db
def test_ct_003_rejeita_senhas_nao_coincidentes():
    client = APIClient()
    response = client.post(
        "/api/accounts/register/",
        build_payload(password_confirm="Senha4321"),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.data
    assert User.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "missing_field",
    ["username", "email", "password", "password_confirm", "city", "state"],
)
def test_ct_004_requer_campos_obrigatorios_no_cadastro(missing_field):
    client = APIClient()
    payload = build_payload()
    payload.pop(missing_field)

    response = client.post("/api/accounts/register/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert missing_field in response.data


@pytest.mark.django_db
def test_ct_005_rejeita_email_malformado():
    client = APIClient()
    response = client.post(
        "/api/accounts/register/",
        build_payload(email="email_invalido"),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_ct_006_rejeita_username_duplicado():
    client = APIClient()
    existing_payload = build_payload(username="joao_silva", email="joao_silva_1@example.com")
    duplicate_payload = build_payload(username="joao_silva", email="joao_silva_2@example.com")

    assert client.post("/api/accounts/register/", existing_payload, format="json").status_code == status.HTTP_201_CREATED

    duplicate_response = client.post("/api/accounts/register/", duplicate_payload, format="json")

    assert duplicate_response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in duplicate_response.data
    assert User.objects.filter(username="joao_silva").count() == 1