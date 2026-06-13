import uuid
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.api.v1.me import get_tenant_context_service
from app.core.deps import get_current_user, get_jwt_tenant_id
from app.models.user import User
from app.schemas.tenant_context import (
    MeContextResponse,
    PermissionsResponse,
    TenantContextResponse,
    UserContextResponse,
)


@pytest.fixture
def mock_context_service() -> AsyncMock:
    return AsyncMock()


@pytest.mark.asyncio
async def test_me_context_route_returns_context(
    client: AsyncClient,
    mock_context_service: AsyncMock,
) -> None:
    user = User(
        id=uuid.uuid4(),
        email="owner@example.com",
        full_name="Owner User",
        hashed_password="hashed",
        is_active=True,
    )
    tenant_id = uuid.uuid4()
    mock_context_service.get_context.return_value = MeContextResponse(
        user=UserContextResponse(id=str(user.id), name="Owner User", email=user.email),
        tenant=TenantContextResponse(
            id=str(tenant_id),
            name="Demo PG",
            logo_url=None,
            primary_color="#2563EB",
            secondary_color="#1E40AF",
            is_demo=True,
            subscription_status="trial",
        ),
        permissions=PermissionsResponse(
            manage_flats=True,
            manage_rooms=True,
            manage_beds=True,
            manage_residents=True,
            manage_payments=True,
        ),
    )

    app = client._transport.app
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_jwt_tenant_id] = lambda: tenant_id
    app.dependency_overrides[get_tenant_context_service] = lambda: mock_context_service

    response = await client.get(
        "/me/context",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["user"]["email"] == "owner@example.com"
    assert payload["tenant"]["is_demo"] is True
    assert payload["permissions"]["manage_flats"] is True
    mock_context_service.get_context.assert_awaited_once_with(user, tenant_id)


@pytest.mark.asyncio
async def test_me_context_ignores_client_tenant_header(
    client: AsyncClient,
    mock_context_service: AsyncMock,
) -> None:
    user = User(
        id=uuid.uuid4(),
        email="owner@example.com",
        full_name="Owner User",
        hashed_password="hashed",
        is_active=True,
    )
    jwt_tenant_id = uuid.uuid4()
    mock_context_service.get_context.return_value = MeContextResponse(
        user=UserContextResponse(id=str(user.id), name="Owner User", email=user.email),
        tenant=TenantContextResponse(
            id=str(jwt_tenant_id),
            name="Demo PG",
            logo_url=None,
            primary_color="#2563EB",
            secondary_color="#1E40AF",
            is_demo=True,
            subscription_status="trial",
        ),
        permissions=PermissionsResponse(
            manage_flats=True,
            manage_rooms=True,
            manage_beds=True,
            manage_residents=True,
            manage_payments=True,
        ),
    )

    app = client._transport.app
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_jwt_tenant_id] = lambda: jwt_tenant_id
    app.dependency_overrides[get_tenant_context_service] = lambda: mock_context_service

    await client.get(
        "/me/context",
        headers={
            "Authorization": "Bearer test-token",
            "X-Tenant-ID": str(uuid.uuid4()),
        },
    )

    mock_context_service.get_context.assert_awaited_once_with(user, jwt_tenant_id)
