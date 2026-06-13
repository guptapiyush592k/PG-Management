import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.api.v1.rooms import get_room_service
from app.models.tenant_user import TenantUser, TenantUserRole
from app.schemas.common import PaginatedResponse
from app.schemas.room import RoomResponse


@pytest.fixture
def mock_room_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def room_response() -> RoomResponse:
    now = datetime.now(UTC)
    tenant_id = uuid.uuid4()
    return RoomResponse(
        id=str(uuid.uuid4()),
        tenant_id=str(tenant_id),
        flat_id=str(uuid.uuid4()),
        room_number="101",
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
async def test_create_room_route(
    client: AsyncClient,
    mock_room_service: AsyncMock,
    room_response: RoomResponse,
) -> None:
    mock_room_service.create_room.return_value = room_response
    tenant_id = uuid.UUID(room_response.tenant_id)

    client._transport.app.dependency_overrides[get_room_service] = lambda: mock_room_service
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_id, TenantUserRole.OWNER),
    ):
        response = await client.post(
            "/api/v1/rooms",
            json={"flat_id": room_response.flat_id, "room_number": "101"},
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": room_response.tenant_id,
            },
        )

    assert response.status_code == 201
    assert response.json()["room_number"] == "101"


@pytest.mark.asyncio
async def test_list_rooms_route(
    client: AsyncClient,
    mock_room_service: AsyncMock,
    room_response: RoomResponse,
) -> None:
    mock_room_service.list_rooms.return_value = PaginatedResponse(
        items=[room_response],
        total=1,
        page=1,
        page_size=20,
    )
    tenant_id = uuid.UUID(room_response.tenant_id)

    client._transport.app.dependency_overrides[get_room_service] = lambda: mock_room_service
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_id, TenantUserRole.STAFF),
    ):
        response = await client.get(
            f"/api/v1/rooms?flat_id={room_response.flat_id}",
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": room_response.tenant_id,
            },
        )

    assert response.status_code == 200
    assert response.json()["total"] == 1


@pytest.mark.asyncio
async def test_create_room_forbidden_for_staff(
    client: AsyncClient,
    room_response: RoomResponse,
) -> None:
    tenant_id = uuid.UUID(room_response.tenant_id)

    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_id, TenantUserRole.STAFF),
    ):
        response = await client.post(
            "/api/v1/rooms",
            json={"flat_id": room_response.flat_id, "room_number": "101"},
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": room_response.tenant_id,
            },
        )

    assert response.status_code == 403
