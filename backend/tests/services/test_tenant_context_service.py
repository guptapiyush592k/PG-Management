import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.tenant import SubscriptionStatus, Tenant
from app.models.tenant_user import TenantUser, TenantUserRole
from app.models.user import User
from app.schemas.tenant_context import resolve_permissions
from app.services.tenant_context_service import TenantContextService


@pytest.fixture
def user() -> User:
    return User(
        id=uuid.uuid4(),
        email="owner@example.com",
        full_name="Owner User",
        hashed_password="hashed",
        is_active=True,
    )


@pytest.fixture
def tenant() -> Tenant:
    return Tenant(
        id=uuid.uuid4(),
        name="Demo PG",
        slug="demo",
        is_active=True,
        logo_url="https://cdn.example.com/logo.png",
        primary_color="#2563EB",
        secondary_color="#1E40AF",
        is_demo=True,
        subscription_status=SubscriptionStatus.TRIAL,
    )


@pytest.fixture
def membership(user: User, tenant: Tenant) -> TenantUser:
    return TenantUser(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        user_id=user.id,
        role=TenantUserRole.OWNER,
        is_primary=True,
    )


@pytest.fixture
def context_service() -> TenantContextService:
    session = AsyncMock()
    return TenantContextService(
        session,
        tenant_repo=AsyncMock(),
        tenant_user_repo=AsyncMock(),
    )


def test_owner_permissions_are_full() -> None:
    permissions = resolve_permissions(TenantUserRole.OWNER)
    assert permissions.manage_flats is True
    assert permissions.manage_payments is True
    assert permissions.manage_files is True


def test_super_admin_permissions_are_full() -> None:
    permissions = resolve_permissions(TenantUserRole.SUPER_ADMIN)
    assert permissions.manage_flats is True
    assert permissions.manage_payments is True
    assert permissions.manage_files is True


def test_manager_permissions_are_limited() -> None:
    permissions = resolve_permissions(TenantUserRole.MANAGER)
    assert permissions.manage_flats is False
    assert permissions.manage_rooms is False
    assert permissions.manage_beds is True
    assert permissions.manage_residents is True
    assert permissions.manage_payments is True
    assert permissions.manage_files is True


@pytest.mark.asyncio
async def test_get_context_returns_user_tenant_and_permissions(
    context_service: TenantContextService,
    user: User,
    tenant: Tenant,
    membership: TenantUser,
) -> None:
    context_service.tenant_user_repo.get_membership_for_user_and_tenant.return_value = membership
    context_service.tenant_repo.get_by_id.return_value = tenant

    result = await context_service.get_context(user, tenant.id)

    assert result.user.name == "Owner User"
    assert result.user.email == user.email
    assert result.tenant.name == "Demo PG"
    assert result.tenant.is_demo is True
    assert result.tenant.subscription_status == "trial"
    assert result.permissions.manage_flats is True


@pytest.mark.asyncio
async def test_get_context_rejects_non_member(
    context_service: TenantContextService,
    user: User,
    tenant: Tenant,
) -> None:
    context_service.tenant_user_repo.get_membership_for_user_and_tenant.return_value = None

    with pytest.raises(ForbiddenError):
        await context_service.get_context(user, tenant.id)


@pytest.mark.asyncio
async def test_get_context_rejects_missing_tenant(
    context_service: TenantContextService,
    user: User,
    tenant: Tenant,
    membership: TenantUser,
) -> None:
    context_service.tenant_user_repo.get_membership_for_user_and_tenant.return_value = membership
    context_service.tenant_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await context_service.get_context(user, tenant.id)


@pytest.mark.asyncio
async def test_get_context_rejects_inactive_tenant(
    context_service: TenantContextService,
    user: User,
    tenant: Tenant,
    membership: TenantUser,
) -> None:
    tenant.is_active = False
    context_service.tenant_user_repo.get_membership_for_user_and_tenant.return_value = membership
    context_service.tenant_repo.get_by_id.return_value = tenant

    with pytest.raises(ForbiddenError):
        await context_service.get_context(user, tenant.id)
