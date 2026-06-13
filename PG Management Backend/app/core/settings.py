import logging
import sys
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = Field(..., description="Async PostgreSQL connection URL")
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = Field(...)
    access_token_expire_minutes: int = Field(..., ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)

    demo_tenant_slug: str = Field(default="demo")

    app_name: str = "PG Management API"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    database_url_sync: str | None = Field(
        default=None,
        description="Optional sync URL for Alembic; derived from DATABASE_URL when omitted",
    )

    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    log_level: str = "INFO"

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must use the asyncpg driver "
                "(postgresql+asyncpg://user:pass@host:port/dbname)"
            )
        return value

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, value: str) -> str:
        if value.strip() != value:
            raise ValueError("JWT_SECRET_KEY must not contain leading or trailing whitespace")
        return value

    @field_validator("jwt_algorithm")
    @classmethod
    def validate_jwt_algorithm(cls, value: str) -> str:
        allowed = {"HS256", "HS384", "HS512"}
        if value not in allowed:
            raise ValueError(f"JWT_ALGORITHM must be one of: {', '.join(sorted(allowed))}")
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> str:
        if isinstance(value, list):
            return ",".join(value)
        return value

    @property
    def sync_database_url(self) -> str:
        if self.database_url_sync:
            return self.database_url_sync
        return self.database_url.replace(
            "postgresql+asyncpg://",
            "postgresql+psycopg://",
            1,
        )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


def validate_settings() -> Settings:
    """Load settings and fail fast when required environment variables are missing or invalid."""
    get_settings.cache_clear()
    try:
        Settings()
    except ValidationError as exc:
        message = _format_validation_errors(exc)
        logger.error("Environment validation failed:\n%s", message)
        print(message, file=sys.stderr)
        raise SystemExit(1) from exc
    return get_settings()


def _format_validation_errors(exc: ValidationError) -> str:
    env_field_map = {
        "database_url": "DATABASE_URL",
        "jwt_secret_key": "JWT_SECRET_KEY",
        "jwt_algorithm": "JWT_ALGORITHM",
        "access_token_expire_minutes": "ACCESS_TOKEN_EXPIRE_MINUTES",
    }
    lines = ["Missing or invalid required environment variables:"]
    for error in exc.errors():
        field = str(error["loc"][0]) if error["loc"] else "unknown"
        env_name = env_field_map.get(field, field.upper())
        lines.append(f"  - {env_name}: {error['msg']}")
    lines.append("")
    lines.append("Copy .env.example to .env and set all required variables.")
    return "\n".join(lines)
