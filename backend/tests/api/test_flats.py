import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.api.v1.flats import get_flat_service
from app.models.tenant_user import TenantUser, TenantUserRole
from app.schemas.common import PaginatedResponse
from app.schemas.flat import FlatResponse


@pytest.fixture
def mock_flat_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def flat_response() -> FlatResponse:
    now = datetime.now(UTC)
    tenant_id = uuid.uuid4()
    return FlatResponse(
        id=str(uuid.uuid4()),
        tenant_id=str(tenant_id),
        name="Sunrise PG",
        address="123 Main Street",
        is_active=True,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_create_flat_route(
    client: AsyncClient,
    mock_flat_service: AsyncMock,
    flat_response: FlatResponse,
) -> None:
    mock_flat_service.create_flat.return_value = flat_response
    membership = TenantUser(
        id=uuid.uuid4(),
        tenant_id=uuid.UUID(flat_response.tenant_id),
        user_id=uuid.uuid4(),
        role=TenantUserRole.OWNER,
        is_primary=True,
    )

    app = client._transport.app
    app.dependency_overrides[get_flat_service] = lambda: mock_flat_service
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
    ) as authorize_mock:
        from app.services.tenant_authorization_service import AuthorizedContext

        authorize_mock.return_value = AuthorizedContext(
            user=MagicMock(),
            tenant=MagicMock(),
            membership=membership,
            user_id=membership.user_id,
            tenant_id=membership.tenant_id,
        )
        response = await client.post(
            "/api/v1/flats",
            json={"name": "Sunrise PG", "address": "123 Main Street"},
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": flat_response.tenant_id,
            },
        )

    assert response.status_code == 201
    assert response.json()["name"] == "Sunrise PG"


@pytest.mark.asyncio
async def test_list_flats_route(
    client: AsyncClient,
    mock_flat_service: AsyncMock,
    flat_response: FlatResponse,
) -> None:
    mock_flat_service.list_flats.return_value = PaginatedResponse(
        items=[flat_response],
        total=1,
        page=1,
        page_size=20,
    )
    membership = TenantUser(
        id=uuid.uuid4(),
        tenant_id=uuid.UUID(flat_response.tenant_id),
        user_id=uuid.uuid4(),
        role=TenantUserRole.MANAGER,
        is_primary=True,
    )

    app = client._transport.app
    app.dependency_overrides[get_flat_service] = lambda: mock_flat_service
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
    ) as authorize_mock:
        from app.services.tenant_authorization_service import AuthorizedContext

        authorize_mock.return_value = AuthorizedContext(
            user=MagicMock(),
            tenant=MagicMock(),
            membership=membership,
            user_id=membership.user_id,
            tenant_id=membership.tenant_id,
        )
        response = await client.get(
            "/api/v1/flats?search=sun&page=1&page_size=20",
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": flat_response.tenant_id,
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["name"] == "Sunrise PG"


@pytest.mark.asyncio
async def test_create_flat_forbidden_for_manager(
    client: AsyncClient,
    flat_response: FlatResponse,
) -> None:
    membership = TenantUser(
        id=uuid.uuid4(),
        tenant_id=uuid.UUID(flat_response.tenant_id),
        user_id=uuid.uuid4(),
        role=TenantUserRole.MANAGER,
        is_primary=True,
    )

    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
    ) as authorize_mock:
        from app.services.tenant_authorization_service import AuthorizedContext

        authorize_mock.return_value = AuthorizedContext(
            user=MagicMock(),
            tenant=MagicMock(),
            membership=membership,
            user_id=membership.user_id,
            tenant_id=membership.tenant_id,
        )
        response = await client.post(
            "/api/v1/flats",
            json={"name": "Sunrise PG", "address": "123 Main Street"},
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": flat_response.tenant_id,
            },
        )

    assert response.status_code == 403
