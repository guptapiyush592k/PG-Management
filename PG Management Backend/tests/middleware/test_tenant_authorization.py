import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.main import create_app
from app.models.tenant import Tenant
from app.models.tenant_user import TenantUser, TenantUserRole
from app.models.user import User
from app.services.tenant_authorization_service import AuthorizedContext


@pytest.fixture
def authorized_user() -> User:
    return User(
        id=uuid.uuid4(),
        email="owner@example.com",
        full_name="Owner User",
        hashed_password="hashed",
        is_active=True,
    )


@pytest.fixture
def authorized_tenant() -> Tenant:
    return Tenant(
        id=uuid.uuid4(),
        name="Demo PG",
        slug="demo",
        is_active=True,
    )


@pytest.fixture
def authorized_context(authorized_user: User, authorized_tenant: Tenant) -> AuthorizedContext:
    membership = TenantUser(
        id=uuid.uuid4(),
        tenant_id=authorized_tenant.id,
        user_id=authorized_user.id,
        role=TenantUserRole.OWNER,
        is_primary=True,
    )
    return AuthorizedContext(
        user=authorized_user,
        tenant=authorized_tenant,
        membership=membership,
        user_id=authorized_user.id,
        tenant_id=authorized_tenant.id,
    )


@pytest.mark.asyncio
async def test_middleware_rejects_missing_authorization_header() -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/examples/tenant-scope",
            headers={"X-Tenant-ID": str(uuid.uuid4())},
        )

    assert response.status_code == 401
    assert response.json()["error_code"] == "unauthorized"


@pytest.mark.asyncio
async def test_middleware_rejects_missing_tenant_header() -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/examples/tenant-scope",
            headers={"Authorization": "Bearer test-token"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "X-Tenant-ID header is required"


@pytest.mark.asyncio
async def test_middleware_rejects_forbidden_tenant_access(
    authorized_context: AuthorizedContext,
) -> None:
    app = create_app()
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        side_effect=ForbiddenError("User does not have access to this tenant"),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/examples/tenant-scope",
                headers={
                    "Authorization": "Bearer test-token",
                    "X-Tenant-ID": str(uuid.uuid4()),
                },
            )

    assert response.status_code == 403
    assert response.json()["error_code"] == "forbidden"


@pytest.mark.asyncio
async def test_middleware_allows_authorized_request(
    authorized_context: AuthorizedContext,
) -> None:
    app = create_app()
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=authorized_context,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/examples/tenant-scope",
                headers={
                    "Authorization": "Bearer test-token",
                    "X-Tenant-ID": str(authorized_context.tenant_id),
                },
            )

    assert response.status_code == 200
    payload = response.json()
    assert payload["user_email"] == "owner@example.com"
    assert payload["tenant_name"] == "Demo PG"


@pytest.mark.asyncio
async def test_public_route_skips_tenant_authorization() -> None:
    authorize_mock = AsyncMock(side_effect=UnauthorizedError("should not be called"))
    app = create_app()
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        authorize_mock,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/health")

    assert response.status_code == 200
    authorize_mock.assert_not_awaited()
