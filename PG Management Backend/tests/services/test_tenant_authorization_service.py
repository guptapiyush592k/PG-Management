import uuid
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import ForbiddenError
from app.models.tenant import Tenant
from app.models.tenant_user import TenantUser, TenantUserRole
from app.models.user import User
from app.services.tenant_authorization_service import TenantAuthorizationService


@pytest.fixture
def user() -> User:
    return User(
        id=uuid.uuid4(),
        email="owner@example.com",
        full_name="Owner",
        hashed_password="hashed",
        is_active=True,
    )


@pytest.fixture
def tenant() -> Tenant:
    return Tenant(id=uuid.uuid4(), name="Demo PG", slug="demo", is_active=True)


@pytest.fixture
def service() -> TenantAuthorizationService:
    session = AsyncMock()
    return TenantAuthorizationService(
        session,
        user_repo=AsyncMock(),
        tenant_repo=AsyncMock(),
        tenant_user_repo=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_authorize_succeeds_for_valid_membership(
    service: TenantAuthorizationService,
    user: User,
    tenant: Tenant,
) -> None:
    membership = TenantUser(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        user_id=user.id,
        role=TenantUserRole.OWNER,
        is_primary=True,
    )
    service.user_repo.get_by_id.return_value = user
    service.tenant_repo.get_by_id.return_value = tenant
    service.tenant_user_repo.get_membership_for_user_and_tenant.return_value = membership

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "app.services.tenant_authorization_service.decode_access_token",
            lambda token: {"sub": str(user.id), "tenant_id": str(tenant.id), "type": "access"},
        )
        context = await service.authorize(
            access_token="token",
            tenant_id_header=str(tenant.id),
        )

    assert context.user_id == user.id
    assert context.tenant_id == tenant.id


@pytest.mark.asyncio
async def test_authorize_rejects_missing_membership(
    service: TenantAuthorizationService,
    user: User,
    tenant: Tenant,
) -> None:
    service.user_repo.get_by_id.return_value = user
    service.tenant_repo.get_by_id.return_value = tenant
    service.tenant_user_repo.get_membership_for_user_and_tenant.return_value = None

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "app.services.tenant_authorization_service.decode_access_token",
            lambda token: {"sub": str(user.id), "tenant_id": str(tenant.id), "type": "access"},
        )
        with pytest.raises(ForbiddenError):
            await service.authorize(
                access_token="token",
                tenant_id_header=str(tenant.id),
            )
