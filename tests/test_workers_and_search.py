import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from workers.models import Worker


User = get_user_model()

LOCAL_WORKER_NAME = "Carlos Oliveira"
REMOTE_WORKER_NAME = "Marcos Silva"
CONSTRUCTION_SERVICE_ID = 2
TEST_PASSWORD = "Senha1234"


def login_client(client, user, password=TEST_PASSWORD):
    response = client.post(
        "/api/auth/login/",
        {"username": user.username, "password": password},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    for key, cookie in response.cookies.items():
        client.cookies[key] = cookie.value
    return response


def seeded_user(username):
    return User.objects.get(username=username)


def worker_payload(*, full_name, bio="", phone="82999990000", city="Maceió", state="AL", services=None):
    return {
        "full_name": full_name,
        "bio": bio,
        "phone": phone,
        "city": city,
        "state": state,
        "services": services or [],
    }


@pytest.mark.django_db
def test_ct_007_cadastro_de_worker_valido_retorna_201_e_vincula_ao_usuario():
    user = seeded_user("qa_worker_creator")
    client = APIClient()
    login_client(client, user)

    response = client.post(
        "/api/workers/",
        worker_payload(
            full_name="Carlos Pintor",
            bio="Profissional dedicado",
            services=[CONSTRUCTION_SERVICE_ID],
        ),
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    worker = Worker.objects.get(user=user)
    assert worker.full_name == "Carlos Pintor"
    assert worker.services.filter(id=CONSTRUCTION_SERVICE_ID).exists()


@pytest.mark.django_db
def test_ct_008_rejeita_cadastro_de_worker_sem_autenticacao():
    client = APIClient()

    response = client.post(
        "/api/workers/",
        worker_payload(full_name="Carlos Pintor", services=[CONSTRUCTION_SERVICE_ID]),
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Worker.objects.count() == 2


@pytest.mark.django_db
def test_ct_009_rejeita_token_invalido_no_cadastro_de_worker():
    client = APIClient()
    client.cookies[settings.SIMPLE_JWT["AUTH_COOKIE"]] = "token-invalido"

    response = client.post(
        "/api/workers/",
        worker_payload(full_name="Carlos Pintor", services=[CONSTRUCTION_SERVICE_ID]),
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Worker.objects.count() == 2


@pytest.mark.django_db
@pytest.mark.parametrize("missing_field", ["full_name", "phone", "city", "state", "services"])
def test_ct_010_rejeita_campos_obrigatorios_faltando_no_worker(missing_field):
    user = seeded_user("qa_worker_creator")
    client = APIClient()
    login_client(client, user)

    payload = worker_payload(full_name="Carlos Pintor", services=[CONSTRUCTION_SERVICE_ID])
    payload.pop(missing_field)

    response = client.post("/api/workers/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert missing_field in response.data


@pytest.mark.django_db
def test_ct_011_rejeita_service_ids_invalidos():
    user = seeded_user("qa_worker_creator")
    client = APIClient()
    login_client(client, user)

    response = client.post(
        "/api/workers/",
        worker_payload(full_name="Carlos Pintor", services=[999, 1000]),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "services" in response.data
    assert Worker.objects.count() == 2


@pytest.mark.django_db
def test_ct_012_busca_texto_livre_no_nome_ou_bio():
    response = APIClient().get("/api/search/?q=pintura")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["full_name"] == LOCAL_WORKER_NAME


@pytest.mark.django_db
def test_ct_013_busca_sem_resultado_retorna_lista_vazia():
    response = APIClient().get("/api/search/?q=xyz_nao_existe")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_ct_014_filtra_por_cidade():
    response = APIClient().get("/api/search/?city=Maceió")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert all(item["city"] == "Maceió" for item in response.data["results"])


@pytest.mark.django_db
def test_ct_015_filtra_por_categoria_de_servico():
    response = APIClient().get(f"/api/search/?service={CONSTRUCTION_SERVICE_ID}")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 2
    assert all("Construção" in item["services"] for item in response.data["results"])


@pytest.mark.django_db
def test_ct_016_filtra_por_avaliacao_minima():
    response = APIClient().get("/api/search/?rating=4.0")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 2
    assert all(item["avg_rating"] >= 4.0 for item in response.data["results"])


@pytest.mark.django_db
def test_ct_017_prioriza_trabalhadores_da_mesma_cidade_para_usuario_autenticado():
    user = seeded_user("qa_search_local")
    client = APIClient()
    login_client(client, user)

    response = client.get("/api/search/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"][0]["full_name"] == LOCAL_WORKER_NAME
    assert response.data["results"][0]["city"] == "Maceió"


@pytest.mark.django_db
def test_ct_018_busca_anonima_ordena_apenas_por_rating():
    response = APIClient().get("/api/search/?q=profissional")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["contratante_city"] is None
    assert response.data["results"][0]["full_name"] == REMOTE_WORKER_NAME
    assert response.data["results"][1]["full_name"] == LOCAL_WORKER_NAME


@pytest.mark.django_db
def test_ct_019_aplica_multiplos_filtros_com_logica_and():
    response = APIClient().get(
        f"/api/search/?q=profissional&city=Maceió&service={CONSTRUCTION_SERVICE_ID}&rating=4.0"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    result = response.data["results"][0]
    assert result["full_name"] == LOCAL_WORKER_NAME
    assert result["city"] == "Maceió"
    assert result["avg_rating"] >= 4.0
    assert "Construção" in result["services"]


@pytest.mark.django_db
def test_ct_020_rating_invalido_e_ignorado():
    response = APIClient().get("/api/search/?rating=abc")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 2
    assert len(response.data["results"]) == 2


@pytest.mark.django_db
def test_ct_021_busca_case_insensitive():
    lower_response = APIClient().get("/api/search/?q=carlos")
    upper_response = APIClient().get("/api/search/?q=CARLOS")

    assert lower_response.status_code == status.HTTP_200_OK
    assert upper_response.status_code == status.HTTP_200_OK
    assert lower_response.data["count"] == upper_response.data["count"] == 1
    assert lower_response.data["results"][0]["full_name"] == upper_response.data["results"][0]["full_name"] == LOCAL_WORKER_NAME


@pytest.mark.django_db
def test_ct_022_parametros_desconhecidos_sao_ignorados():
    base_response = APIClient().get("/api/search/?q=pintura")
    noisy_response = APIClient().get("/api/search/?q=pintura&unknown_param=value&xyz=123")

    assert base_response.status_code == status.HTTP_200_OK
    assert noisy_response.status_code == status.HTTP_200_OK
    assert base_response.data["count"] == noisy_response.data["count"] == 1
    assert base_response.data["results"][0]["full_name"] == noisy_response.data["results"][0]["full_name"] == LOCAL_WORKER_NAME