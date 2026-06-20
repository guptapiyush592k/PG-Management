import uuid
from datetime import UTC, date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.api.v1.bookings import get_booking_service
from app.models.booking import BookingStatus
from app.models.tenant_user import TenantUser, TenantUserRole
from app.schemas.booking import BookingResponse
from app.schemas.common import PaginatedResponse


@pytest.fixture
def mock_booking_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def booking_response() -> BookingResponse:
    now = datetime.now(UTC)
    tenant_id = uuid.uuid4()
    return BookingResponse(
        id=str(uuid.uuid4()),
        tenant_id=str(tenant_id),
        resident_id=str(uuid.uuid4()),
        bed_id=str(uuid.uuid4()),
        start_date=date(2026, 6, 1),
        end_date=None,
        status=BookingStatus.ACTIVE,
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
async def test_create_booking_route(
    client: AsyncClient,
    mock_booking_service: AsyncMock,
    booking_response: BookingResponse,
) -> None:
    mock_booking_service.create_booking.return_value = booking_response
    tenant_id = uuid.UUID(booking_response.tenant_id)

    client._transport.app.dependency_overrides[get_booking_service] = lambda: mock_booking_service
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_id, TenantUserRole.MANAGER),
    ):
        response = await client.post(
            "/api/v1/bookings",
            json={
                "resident_id": booking_response.resident_id,
                "bed_id": booking_response.bed_id,
                "start_date": "2026-06-01",
            },
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": booking_response.tenant_id,
            },
        )

    assert response.status_code == 201
    assert response.json()["status"] == "active"


@pytest.mark.asyncio
async def test_list_bookings_route(
    client: AsyncClient,
    mock_booking_service: AsyncMock,
    booking_response: BookingResponse,
) -> None:
    mock_booking_service.list_bookings.return_value = PaginatedResponse(
        items=[booking_response],
        total=1,
        page=1,
        page_size=20,
    )
    tenant_id = uuid.UUID(booking_response.tenant_id)

    client._transport.app.dependency_overrides[get_booking_service] = lambda: mock_booking_service
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_id, TenantUserRole.MANAGER),
    ):
        response = await client.get(
            f"/api/v1/bookings?resident_id={booking_response.resident_id}&status=active",
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": booking_response.tenant_id,
            },
        )

    assert response.status_code == 200
    assert response.json()["total"] == 1


@pytest.mark.asyncio
async def test_checkout_booking_route(
    client: AsyncClient,
    mock_booking_service: AsyncMock,
    booking_response: BookingResponse,
) -> None:
    booking_response.status = BookingStatus.COMPLETED
    booking_response.end_date = date(2026, 6, 30)
    mock_booking_service.checkout_booking.return_value = booking_response
    tenant_id = uuid.UUID(booking_response.tenant_id)

    client._transport.app.dependency_overrides[get_booking_service] = lambda: mock_booking_service
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_id, TenantUserRole.MANAGER),
    ):
        response = await client.post(
            f"/api/v1/bookings/{booking_response.id}/checkout",
            json={"end_date": "2026-06-30"},
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": booking_response.tenant_id,
            },
        )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["end_date"] == "2026-06-30"
