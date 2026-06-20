import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.settings import Settings
from app.models.stored_file import FileStatus, StoredFile
from app.models.tenant_user import TenantUserRole
from app.repositories.file_repository import FileRepository
from app.schemas.file import FileUploadUrlRequest
from app.services.file_service import FileService
from app.storage.local import LocalStorageProvider


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(
        database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/pg_management",
        jwt_secret_key="test-secret-key-with-at-least-32-chars",
        jwt_algorithm="HS256",
        access_token_expire_minutes=60,
        storage_provider="local",
        local_storage_path=str(tmp_path / "uploads"),
        local_storage_public_base_url="http://localhost:8000",
        storage_presigned_url_expires_seconds=3600,
    )


@pytest.fixture
def storage(settings: Settings) -> LocalStorageProvider:
    return LocalStorageProvider(settings)


@pytest.fixture
def tenant_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def file_service(
    storage: LocalStorageProvider,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> FileService:
    session = AsyncMock()
    file_repo = AsyncMock(spec=FileRepository)
    return FileService(
        session,
        tenant_id,
        TenantUserRole.OWNER,
        storage,
        user_id=user_id,
        file_repo=file_repo,
    )


@pytest.mark.asyncio
async def test_create_upload_url_creates_pending_record(
    file_service: FileService,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    stored_file = StoredFile(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        filename="lease.pdf",
        content_type="application/pdf",
        storage_key=f"{tenant_id}/{uuid.uuid4()}/lease.pdf",
        uploaded_by_user_id=user_id,
        status=FileStatus.PENDING,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    file_service.file_repo.add = AsyncMock(return_value=stored_file)

    response = await file_service.create_upload_url(
        FileUploadUrlRequest(filename="lease.pdf", content_type="application/pdf")
    )

    assert response.file_id == str(stored_file.id)
    assert response.method == "PUT"
    assert "/api/v1/files/" in response.upload_url
    file_service.session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_manager_can_create_upload_url(
    storage: LocalStorageProvider,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    session = AsyncMock()
    file_repo = AsyncMock(spec=FileRepository)
    service = FileService(
        session,
        tenant_id,
        TenantUserRole.MANAGER,
        storage,
        user_id=user_id,
        file_repo=file_repo,
    )
    stored_file = StoredFile(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        filename="lease.pdf",
        content_type="application/pdf",
        storage_key=f"{tenant_id}/{uuid.uuid4()}/lease.pdf",
        uploaded_by_user_id=user_id,
        status=FileStatus.PENDING,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    file_repo.add = AsyncMock(return_value=stored_file)

    response = await service.create_upload_url(
        FileUploadUrlRequest(filename="lease.pdf", content_type="application/pdf")
    )

    assert response.file_id == str(stored_file.id)
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_local_upload_marks_file_uploaded(
    file_service: FileService,
    storage: LocalStorageProvider,
    tenant_id: uuid.UUID,
) -> None:
    file_id = uuid.uuid4()
    storage_key = f"{tenant_id}/{file_id}/lease.pdf"
    stored_file = StoredFile(
        id=file_id,
        tenant_id=tenant_id,
        filename="lease.pdf",
        content_type="application/pdf",
        storage_key=storage_key,
        status=FileStatus.PENDING,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    file_service.file_repo.get_by_id = AsyncMock(return_value=stored_file)
    file_service.file_repo.mark_uploaded = AsyncMock(
        return_value=StoredFile(
            id=file_id,
            tenant_id=tenant_id,
            filename="lease.pdf",
            content_type="application/pdf",
            storage_key=storage_key,
            size_bytes=5,
            status=FileStatus.UPLOADED,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )

    expires_at = datetime.now(UTC) + timedelta(hours=1)
    signature = storage._sign(str(file_id), storage_key, expires_at)

    response = await file_service.complete_local_upload(
        file_id,
        b"hello",
        expires=int(expires_at.timestamp()),
        signature=signature,
    )

    assert response.status == FileStatus.UPLOADED
    assert response.size_bytes == 5
    saved_path = storage.root / storage_key
    assert saved_path.read_bytes() == b"hello"
