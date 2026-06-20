import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.api.v1.residents import get_resident_service
from app.models.tenant_user import TenantUser, TenantUserRole
from app.schemas.common import PaginatedResponse
from app.schemas.resident import ResidentResponse


@pytest.fixture
def mock_resident_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def resident_response() -> ResidentResponse:
    now = datetime.now(UTC)
    tenant_id = uuid.uuid4()
    return ResidentResponse(
        id=str(uuid.uuid4()),
        tenant_id=str(tenant_id),
        name="Rahul Sharma",
        phone="9876543210",
        email="rahul@example.com",
        aadhaar="123456789012",
        joining_date=date(2025, 1, 15),
        deposit=Decimal("10000.00"),
        notes="Prefers ground floor",
        is_active=True,
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
async def test_create_resident_route(
    client: AsyncClient,
    mock_resident_service: AsyncMock,
    resident_response: ResidentResponse,
) -> None:
    mock_resident_service.create_resident.return_value = resident_response
    tenant_id = uuid.UUID(resident_response.tenant_id)

    client._transport.app.dependency_overrides[get_resident_service] = (
        lambda: mock_resident_service
    )
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_id, TenantUserRole.MANAGER),
    ):
        response = await client.post(
            "/api/v1/residents",
            json={
                "name": "Rahul Sharma",
                "phone": "9876543210",
                "email": "rahul@example.com",
                "aadhaar": "123456789012",
                "joining_date": "2025-01-15",
                "deposit": "10000.00",
                "notes": "Prefers ground floor",
                "is_active": True,
            },
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": resident_response.tenant_id,
            },
        )

    assert response.status_code == 201
    assert response.json()["name"] == "Rahul Sharma"


@pytest.mark.asyncio
async def test_list_residents_route(
    client: AsyncClient,
    mock_resident_service: AsyncMock,
    resident_response: ResidentResponse,
) -> None:
    mock_resident_service.list_residents.return_value = PaginatedResponse(
        items=[resident_response],
        total=1,
        page=1,
        page_size=20,
    )
    tenant_id = uuid.UUID(resident_response.tenant_id)

    client._transport.app.dependency_overrides[get_resident_service] = (
        lambda: mock_resident_service
    )
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_id, TenantUserRole.MANAGER),
    ):
        response = await client.get(
            "/api/v1/residents?search=Rahul&is_active=true",
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": resident_response.tenant_id,
            },
        )

    assert response.status_code == 200
    assert response.json()["total"] == 1
