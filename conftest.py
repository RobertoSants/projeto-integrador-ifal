from pathlib import Path
import sys

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command


PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


User = get_user_model()
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures"
WORKERS_FIXTURE = FIXTURE_DIR / "qa_workers_search.json"
SERVICES_FIXTURE = BACKEND_DIR / "services" / "fixtures" / "categorias_iniciais.json"


@pytest.fixture(scope="session", autouse=True)
def load_seed_fixtures(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", str(SERVICES_FIXTURE), verbosity=0)
        call_command("loaddata", str(WORKERS_FIXTURE), verbosity=0)

        for username in ["qa_worker_creator", "qa_search_local", "qa_search_remote"]:
            user = User.objects.get(username=username)
            user.set_password("Senha1234")
            user.save(update_fields=["password"])
