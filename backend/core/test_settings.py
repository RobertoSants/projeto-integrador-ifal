from .settings import *  # noqa: F401,F403

TEST_DB_ENGINE = config("TEST_DB_ENGINE", default="django.db.backends.postgresql")

if TEST_DB_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": TEST_DB_ENGINE,
            "NAME": BASE_DIR / "test_db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": TEST_DB_ENGINE,
            "NAME": config("DB_NAME", default="banco_talentos"),
            "USER": config("DB_USER", default="pguser"),
            "PASSWORD": config("DB_PASSWORD", default="pgpass"),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("TEST_DB_PORT", default=config("DB_PORT", default="5433")),
        }
    }

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
