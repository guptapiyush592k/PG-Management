from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "PG Management API"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/pg_management",
        description="Async SQLAlchemy database URL",
    )
    database_url_sync: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/pg_management",
        description="Sync database URL for Alembic migrations",
    )

    jwt_secret_key: str = Field(
        default="change-me-in-production-use-a-long-random-secret",
        min_length=32,
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    log_level: str = "INFO"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> str:
        if isinstance(value, list):
            return ",".join(value)
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
