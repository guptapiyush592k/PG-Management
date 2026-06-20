from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from app.core.settings import Settings
from app.storage.factory import create_storage_provider
from app.storage.local import LocalStorageProvider
from app.storage.s3 import S3StorageProvider


@pytest.fixture
def base_settings(tmp_path) -> Settings:
    return Settings(
        database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/pg_management",
        jwt_secret_key="test-secret-key-with-at-least-32-chars",
        jwt_algorithm="HS256",
        access_token_expire_minutes=60,
        storage_provider="local",
        local_storage_path=str(tmp_path / "uploads"),
        local_storage_public_base_url="http://localhost:8000",
    )


def test_factory_returns_local_provider(base_settings: Settings) -> None:
    provider = create_storage_provider(base_settings)
    assert isinstance(provider, LocalStorageProvider)


def test_factory_returns_s3_provider(base_settings: Settings) -> None:
    base_settings.storage_provider = "s3"
    base_settings.s3_bucket_name = "files"
    base_settings.s3_region = "us-east-1"
    base_settings.s3_access_key_id = "key"
    base_settings.s3_secret_access_key = "secret"

    provider = create_storage_provider(base_settings)
    assert isinstance(provider, S3StorageProvider)


@pytest.mark.asyncio
async def test_local_provider_generates_signed_upload_url(base_settings: Settings) -> None:
    provider = LocalStorageProvider(base_settings)
    presigned = await provider.generate_upload_url(
        "tenant-id/file-id/report.pdf",
        "application/pdf",
        expires_in=3600,
    )

    assert presigned.method == "PUT"
    assert presigned.headers["Content-Type"] == "application/pdf"
    assert "/api/v1/files/file-id/content" in presigned.upload_url
    assert presigned.expires_at is not None


@pytest.mark.asyncio
async def test_s3_provider_generates_presigned_url(base_settings: Settings) -> None:
    base_settings.storage_provider = "s3"
    base_settings.s3_bucket_name = "files"
    base_settings.s3_region = "us-east-1"
    base_settings.s3_access_key_id = "key"
    base_settings.s3_secret_access_key = "secret"

    provider = S3StorageProvider(base_settings)
    mock_client = MagicMock()
    mock_client.generate_presigned_url.return_value = "https://s3.example.com/upload"
    provider._client = mock_client

    presigned = await provider.generate_upload_url(
        "tenant-id/file-id/report.pdf",
        "application/pdf",
        expires_in=3600,
    )

    assert presigned.upload_url == "https://s3.example.com/upload"
    mock_client.generate_presigned_url.assert_called_once()
