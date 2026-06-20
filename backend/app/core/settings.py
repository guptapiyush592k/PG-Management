import logging
import sys
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field, ValidationError, field_validator, model_validator
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

    storage_provider: Literal["local", "s3"] = "local"
    local_storage_path: str = "./uploads"
    local_storage_public_base_url: str = "http://localhost:8000"
    storage_presigned_url_expires_seconds: int = Field(default=3600, ge=60, le=86400)

    s3_bucket_name: str | None = None
    s3_region: str | None = None
    s3_endpoint_url: str | None = None
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None

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

    @model_validator(mode="after")
    def validate_storage_settings(self) -> "Settings":
        if self.storage_provider != "s3":
            return self

        missing: list[str] = []
        if not self.s3_bucket_name:
            missing.append("S3_BUCKET_NAME")
        if not self.s3_region:
            missing.append("S3_REGION")
        if not self.s3_access_key_id:
            missing.append("S3_ACCESS_KEY_ID")
        if not self.s3_secret_access_key:
            missing.append("S3_SECRET_ACCESS_KEY")

        if missing:
            raise ValueError(
                f"When STORAGE_PROVIDER=s3, the following are required: {', '.join(missing)}"
            )
        return self


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
