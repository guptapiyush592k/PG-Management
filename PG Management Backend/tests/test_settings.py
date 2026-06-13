import pytest
from pydantic import ValidationError

from app.core.settings import Settings, get_settings, validate_settings


@pytest.fixture(autouse=True)
def _reset_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_settings_loads_with_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/pg_management",
    )
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-with-at-least-32-chars")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

    settings = Settings()

    assert settings.database_url.startswith("postgresql+asyncpg://")
    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 60
    assert settings.sync_database_url.startswith("postgresql+psycopg://")


def test_settings_rejects_missing_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_ALGORITHM", raising=False)
    monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)

    with pytest.raises(ValidationError):
        Settings()


def test_validate_settings_exits_on_invalid_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_ALGORITHM", raising=False)
    monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)

    with pytest.raises(SystemExit):
        validate_settings()
