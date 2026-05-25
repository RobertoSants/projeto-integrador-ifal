import uuid

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from reviews.models import Review
from services.models import ServiceCategory
from workers.models import Worker


User = get_user_model()


def make_unique(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def create_user(password="Senha1234", city="Maceió"):
    suffix = uuid.uuid4().hex[:8]
    return User.objects.create_user(
        username=f"user_{suffix}",
        email=f"user_{suffix}@example.com",
        password=password,
        city=city,
        state="AL",
    )


def login_client(client, user, password="Senha1234"):
    response = client.post(
        "/api/auth/login/",
        {"username": user.username, "password": password},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    for key, cookie in response.cookies.items():
        client.cookies[key] = cookie.value
    return response


def create_service(name=None):
    return ServiceCategory.objects.create(
        name=name or make_unique("Servico"),
        description="Categoria de teste",
        icon="tool",
    )


def create_worker_with_reviews(*, full_name, city, state, services, rating_values, bio="", phone="82999990000", user=None):
    owner = user or create_user(city=city)
    worker = Worker.objects.create(
        user=owner,
        full_name=full_name,
        bio=bio,
        phone=phone,
        city=city,
        state=state,
    )
    worker.services.set(services)
    for rating in rating_values:
        Review.objects.create(worker=worker, author=None, rating=rating, comment="ok")
    return worker


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
    user = create_user()
    service = create_service()
    client = APIClient()
    login_client(client, user)

    response = client.post(
        "/api/workers/",
        worker_payload(full_name="Carlos Pintor", bio="Profissional dedicado", services=[service.id]),
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    worker = Worker.objects.get(user=user)
    assert worker.full_name == "Carlos Pintor"
    assert worker.services.filter(id=service.id).exists()


@pytest.mark.django_db
def test_ct_008_rejeita_cadastro_de_worker_sem_autenticacao():
    service = create_service()
    client = APIClient()

    response = client.post(
        "/api/workers/",
        worker_payload(full_name="Carlos Pintor", services=[service.id]),
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Worker.objects.count() == 0


@pytest.mark.django_db
def test_ct_009_rejeita_token_invalido_no_cadastro_de_worker():
    service = create_service()
    client = APIClient()
    client.cookies[settings.SIMPLE_JWT["AUTH_COOKIE"]] = "token-invalido"

    response = client.post(
        "/api/workers/",
        worker_payload(full_name="Carlos Pintor", services=[service.id]),
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Worker.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize("missing_field", ["full_name", "phone", "city", "state", "services"])
def test_ct_010_rejeita_campos_obrigatorios_faltando_no_worker(missing_field):
    user = create_user()
    service = create_service()
    client = APIClient()
    login_client(client, user)

    payload = worker_payload(full_name="Carlos Pintor", services=[service.id])
    payload.pop(missing_field)

    response = client.post("/api/workers/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert missing_field in response.data


@pytest.mark.django_db
def test_ct_011_rejeita_service_ids_invalidos():
    user = create_user()
    client = APIClient()
    login_client(client, user)

    response = client.post(
        "/api/workers/",
        worker_payload(full_name="Carlos Pintor", services=[999, 1000]),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "services" in response.data
    assert Worker.objects.count() == 0


@pytest.mark.django_db
def test_ct_012_busca_texto_livre_no_nome_ou_bio():
    service = create_service()
    create_worker_with_reviews(
        full_name="Carlos Oliveira",
        city="Maceió",
        state="AL",
        services=[service],
        rating_values=[5],
        bio="Especialista em pintura residencial",
    )
    create_worker_with_reviews(
        full_name="Marcos Silva",
        city="Arapiraca",
        state="AL",
        services=[service],
        rating_values=[4],
        bio="Pedreiro e pintor",
    )

    response = APIClient().get("/api/search/?q=pintura")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["full_name"] == "Carlos Oliveira"


@pytest.mark.django_db
def test_ct_013_busca_sem_resultado_retorna_lista_vazia():
    service = create_service()
    create_worker_with_reviews(
        full_name="Carlos Oliveira",
        city="Maceió",
        state="AL",
        services=[service],
        rating_values=[5],
        bio="Especialista em pintura residencial",
    )

    response = APIClient().get("/api/search/?q=xyz_nao_existe")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_ct_014_filtra_por_cidade():
    service = create_service()
    local_worker = create_worker_with_reviews(
        full_name="Carlos Oliveira",
        city="Maceió",
        state="AL",
        services=[service],
        rating_values=[5],
        bio="Pintor local",
    )
    create_worker_with_reviews(
        full_name="Marcos Silva",
        city="Arapiraca",
        state="AL",
        services=[service],
        rating_values=[4],
        bio="Pintor remoto",
    )

    response = APIClient().get("/api/search/?city=Maceió")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == local_worker.id
    assert response.data["results"][0]["city"] == "Maceió"


@pytest.mark.django_db
def test_ct_015_filtra_por_categoria_de_servico():
    service_one = create_service("Pintura")
    service_two = create_service("Eletricista")
    worker_one = create_worker_with_reviews(
        full_name="Carlos Oliveira",
        city="Maceió",
        state="AL",
        services=[service_one],
        rating_values=[5],
        bio="Pintor local",
    )
    create_worker_with_reviews(
        full_name="Marcos Silva",
        city="Arapiraca",
        state="AL",
        services=[service_two],
        rating_values=[4],
        bio="Eletricista remoto",
    )

    response = APIClient().get(f"/api/search/?service={service_one.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == worker_one.id


@pytest.mark.django_db
def test_ct_016_filtra_por_avaliacao_minima():
    service = create_service()
    high_rating_worker = create_worker_with_reviews(
        full_name="Carlos Oliveira",
        city="Maceió",
        state="AL",
        services=[service],
        rating_values=[4, 5],
        bio="Pintor bem avaliado",
    )
    create_worker_with_reviews(
        full_name="Marcos Silva",
        city="Arapiraca",
        state="AL",
        services=[service],
        rating_values=[3, 3],
        bio="Pintor com nota menor",
    )

    response = APIClient().get("/api/search/?rating=4.0")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == high_rating_worker.id
    assert response.data["results"][0]["avg_rating"] >= 4.0


@pytest.mark.django_db
def test_ct_017_prioriza_trabalhadores_da_mesma_cidade_para_usuario_autenticado():
    service = create_service()
    local_worker = create_worker_with_reviews(
        full_name="Carlos Oliveira",
        city="Maceió",
        state="AL",
        services=[service],
        rating_values=[4],
        bio="Pintor local",
    )
    remote_worker = create_worker_with_reviews(
        full_name="Marcos Silva",
        city="Arapiraca",
        state="AL",
        services=[service],
        rating_values=[5],
        bio="Pintor remoto",
    )
    user = create_user(city="Maceió")
    client = APIClient()
    login_client(client, user)

    response = client.get("/api/search/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"][0]["id"] == local_worker.id
    assert response.data["results"][0]["city"] == "Maceió"
    assert remote_worker.id in [item["id"] for item in response.data["results"]]


@pytest.mark.django_db
def test_ct_018_busca_anonima_ordena_apenas_por_rating():
    service = create_service()
    higher_rating_worker = create_worker_with_reviews(
        full_name="Carlos Oliveira",
        city="Maceió",
        state="AL",
        services=[service],
        rating_values=[5],
        bio="Pintor local",
    )
    lower_rating_worker = create_worker_with_reviews(
        full_name="Marcos Silva",
        city="Arapiraca",
        state="AL",
        services=[service],
        rating_values=[3],
        bio="Pintor remoto",
    )

    response = APIClient().get("/api/search/?q=pintor")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["contratante_city"] is None
    assert response.data["results"][0]["id"] == higher_rating_worker.id
    assert response.data["results"][1]["id"] == lower_rating_worker.id


@pytest.mark.django_db
def test_ct_019_aplica_multiplos_filtros_com_logica_and():
    service_one = create_service("Pintura")
    service_two = create_service("Eletricista")
    matching_worker = create_worker_with_reviews(
        full_name="Carlos Pintor",
        city="Maceió",
        state="AL",
        services=[service_one],
        rating_values=[4, 5],
        bio="Especialista em pintura residencial",
    )
    create_worker_with_reviews(
        full_name="Carlos Pintor",
        city="Arapiraca",
        state="AL",
        services=[service_two],
        rating_values=[5],
        bio="Especialista em elétrica",
    )

    response = APIClient().get(
        f"/api/search/?q=pintor&city=Maceió&service={service_one.id}&rating=4.0"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    result = response.data["results"][0]
    assert result["id"] == matching_worker.id
    assert result["city"] == "Maceió"
    assert result["avg_rating"] >= 4.0
    assert "Pintura" in result["services"]


@pytest.mark.django_db
def test_ct_020_rating_invalido_e_ignorado():
    service = create_service()
    create_worker_with_reviews(
        full_name="Carlos Oliveira",
        city="Maceió",
        state="AL",
        services=[service],
        rating_values=[5],
        bio="Pintor local",
    )
    create_worker_with_reviews(
        full_name="Marcos Silva",
        city="Arapiraca",
        state="AL",
        services=[service],
        rating_values=[3],
        bio="Pintor remoto",
    )

    response = APIClient().get("/api/search/?rating=abc")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 2
    assert len(response.data["results"]) == 2


@pytest.mark.django_db
def test_ct_021_busca_case_insensitive():
    service = create_service()
    target_worker = create_worker_with_reviews(
        full_name="Carlos Oliveira",
        city="Maceió",
        state="AL",
        services=[service],
        rating_values=[5],
        bio="Profissional conhecido como Carlos",
    )
    create_worker_with_reviews(
        full_name="Marcos Silva",
        city="Arapiraca",
        state="AL",
        services=[service],
        rating_values=[4],
        bio="Outro profissional",
    )

    lower_response = APIClient().get("/api/search/?q=carlos")
    upper_response = APIClient().get("/api/search/?q=CARLOS")

    assert lower_response.status_code == status.HTTP_200_OK
    assert upper_response.status_code == status.HTTP_200_OK
    assert lower_response.data["count"] == upper_response.data["count"] == 1
    assert lower_response.data["results"][0]["id"] == upper_response.data["results"][0]["id"] == target_worker.id


@pytest.mark.django_db
def test_ct_022_parametros_desconhecidos_sao_ignorados():
    service = create_service()
    target_worker = create_worker_with_reviews(
        full_name="Carlos Pintor",
        city="Maceió",
        state="AL",
        services=[service],
        rating_values=[5],
        bio="Especialista em pintura",
    )
    create_worker_with_reviews(
        full_name="Marcos Silva",
        city="Arapiraca",
        state="AL",
        services=[service],
        rating_values=[4],
        bio="Outro profissional",
    )

    base_response = APIClient().get("/api/search/?q=pintor")
    noisy_response = APIClient().get("/api/search/?q=pintor&unknown_param=value&xyz=123")

    assert base_response.status_code == status.HTTP_200_OK
    assert noisy_response.status_code == status.HTTP_200_OK
    assert base_response.data["count"] == noisy_response.data["count"] == 1
    assert base_response.data["results"][0]["id"] == noisy_response.data["results"][0]["id"] == target_worker.id