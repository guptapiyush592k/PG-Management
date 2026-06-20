import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.flats import get_flat_service
from app.core.exceptions import NotFoundError
from app.main import create_app
from app.models.tenant_user import TenantUser, TenantUserRole
from app.services.tenant_authorization_service import AuthorizedContext


def _authorized_context(tenant_id: uuid.UUID, role: TenantUserRole = TenantUserRole.OWNER):
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
async def test_flat_access_is_scoped_to_request_tenant() -> None:
    tenant_b = uuid.uuid4()
    flat_id = uuid.uuid4()

    mock_flat_service = AsyncMock()
    mock_flat_service.get_flat.side_effect = NotFoundError("Flat not found")

    app = create_app()
    app.dependency_overrides[get_flat_service] = lambda: mock_flat_service

    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_b),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/v1/flats/{flat_id}",
                headers={
                    "Authorization": "Bearer test-token",
                    "X-Tenant-ID": str(tenant_b),
                },
            )

    assert response.status_code == 404
    mock_flat_service.get_flat.assert_awaited_once_with(flat_id)
