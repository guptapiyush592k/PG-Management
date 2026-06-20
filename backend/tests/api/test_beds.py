import uuid
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.api.v1.beds import get_bed_service
from app.models.bed import BedStatus
from app.models.tenant_user import TenantUser, TenantUserRole
from app.schemas.bed import BedResponse
from app.schemas.common import PaginatedResponse


@pytest.fixture
def mock_bed_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def bed_response() -> BedResponse:
    now = datetime.now(UTC)
    tenant_id = uuid.uuid4()
    return BedResponse(
        id=str(uuid.uuid4()),
        tenant_id=str(tenant_id),
        room_id=str(uuid.uuid4()),
        bed_label="A",
        rent_amount=Decimal("5000.00"),
        status=BedStatus.VACANT,
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
async def test_create_bed_route(
    client: AsyncClient,
    mock_bed_service: AsyncMock,
    bed_response: BedResponse,
) -> None:
    mock_bed_service.create_bed.return_value = bed_response
    tenant_id = uuid.UUID(bed_response.tenant_id)

    client._transport.app.dependency_overrides[get_bed_service] = lambda: mock_bed_service
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_id, TenantUserRole.STAFF),
    ):
        response = await client.post(
            "/api/v1/beds",
            json={
                "room_id": bed_response.room_id,
                "bed_label": "A",
                "rent_amount": "5000.00",
                "status": "vacant",
            },
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": bed_response.tenant_id,
            },
        )

    assert response.status_code == 201
    assert response.json()["bed_label"] == "A"


@pytest.mark.asyncio
async def test_list_beds_route(
    client: AsyncClient,
    mock_bed_service: AsyncMock,
    bed_response: BedResponse,
) -> None:
    mock_bed_service.list_beds.return_value = PaginatedResponse(
        items=[bed_response],
        total=1,
        page=1,
        page_size=20,
    )
    tenant_id = uuid.UUID(bed_response.tenant_id)

    client._transport.app.dependency_overrides[get_bed_service] = lambda: mock_bed_service
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_id, TenantUserRole.STAFF),
    ):
        response = await client.get(
            f"/api/v1/beds?room_id={bed_response.room_id}&status=vacant",
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": bed_response.tenant_id,
            },
        )

    assert response.status_code == 200
    assert response.json()["total"] == 1
