import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.api.v1.files import get_file_service
from app.models.stored_file import FileStatus
from app.models.tenant_user import TenantUser, TenantUserRole
from app.schemas.common import PaginatedResponse
from app.schemas.file import FileResponse, FileUploadUrlResponse


@pytest.fixture
def mock_file_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def file_upload_response() -> FileUploadUrlResponse:
    return FileUploadUrlResponse(
        file_id=str(uuid.uuid4()),
        upload_url="http://localhost:8000/api/v1/files/example/content?signature=abc",
        method="PUT",
        headers={"Content-Type": "application/pdf"},
        storage_key="tenant/file/report.pdf",
        expires_at=datetime.now(UTC),
    )


@pytest.fixture
def file_response() -> FileResponse:
    now = datetime.now(UTC)
    tenant_id = uuid.uuid4()
    return FileResponse(
        id=str(uuid.uuid4()),
        tenant_id=str(tenant_id),
        filename="report.pdf",
        content_type="application/pdf",
        storage_key=f"{tenant_id}/file/report.pdf",
        size_bytes=1024,
        status=FileStatus.UPLOADED,
        uploaded_by_user_id=str(uuid.uuid4()),
        download_url="http://localhost:8000/api/v1/files/example/content?signature=def",
        created_at=now,
        updated_at=now,
    )


def _authorized_context(tenant_id: uuid.UUID, role: TenantUserRole):
    from app.services.tenant_authorization_service import AuthorizedContext

    membership = TenantUser(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        user_id=uuid.uuid4(),
        role=role,
        is_primary=True,
    )
    return AuthorizedContext(
        user=MagicMock(),
        tenant=MagicMock(),
        membership=membership,
        user_id=membership.user_id,
        tenant_id=tenant_id,
    )


@pytest.mark.asyncio
async def test_create_upload_url_route(
    client: AsyncClient,
    mock_file_service: AsyncMock,
    file_upload_response: FileUploadUrlResponse,
) -> None:
    mock_file_service.create_upload_url.return_value = file_upload_response
    tenant_id = uuid.uuid4()

    client._transport.app.dependency_overrides[get_file_service] = lambda: mock_file_service
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_id, TenantUserRole.OWNER),
    ):
        response = await client.post(
            "/api/v1/files/upload-url",
            json={"filename": "report.pdf", "content_type": "application/pdf"},
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": str(tenant_id),
            },
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["file_id"] == file_upload_response.file_id
    assert payload["upload_url"] == file_upload_response.upload_url
    mock_file_service.create_upload_url.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_files_route(
    client: AsyncClient,
    mock_file_service: AsyncMock,
    file_response: FileResponse,
) -> None:
    mock_file_service.list_files.return_value = PaginatedResponse[FileResponse](
        items=[file_response],
        total=1,
        page=1,
        page_size=20,
    )
    tenant_id = uuid.UUID(file_response.tenant_id)

    client._transport.app.dependency_overrides[get_file_service] = lambda: mock_file_service
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_id, TenantUserRole.MANAGER),
    ):
        response = await client.get(
            "/api/v1/files",
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": str(tenant_id),
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["filename"] == "report.pdf"
    mock_file_service.list_files.assert_awaited_once()
