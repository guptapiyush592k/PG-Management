import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.security import hash_password
from app.core.exceptions import ConflictError, ForbiddenError, UnauthorizedError
from app.core.settings import Settings
from app.models.tenant import Tenant
from app.models.tenant_user import TenantUser, TenantUserRole
from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest
from app.services.auth_service import AuthService


@pytest.fixture
def settings() -> Settings:
    return Settings(
        database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/test",
        jwt_secret_key="test-secret-key-with-at-least-32-chars",
        jwt_algorithm="HS256",
        access_token_expire_minutes=60,
        refresh_token_expire_days=7,
        demo_tenant_slug="demo",
    )


@pytest.fixture
def demo_tenant() -> Tenant:
    return Tenant(id=uuid.uuid4(), name="Demo PG", slug="demo", is_active=True)


@pytest.fixture
def user() -> User:
    return User(
        id=uuid.uuid4(),
        email="owner@example.com",
        full_name="Owner User",
        hashed_password=hash_password("Password123"),
        is_active=True,
    )


@pytest.fixture
def membership(user: User, demo_tenant: Tenant) -> TenantUser:
    return TenantUser(
        id=uuid.uuid4(),
        tenant_id=demo_tenant.id,
        user_id=user.id,
        role=TenantUserRole.OWNER,
        is_primary=True,
    )


@pytest.fixture
def auth_service(settings: Settings) -> AuthService:
    session = AsyncMock()
    session.commit = AsyncMock()

    service = AuthService(
        session,
        settings=settings,
        user_repo=AsyncMock(),
        tenant_repo=AsyncMock(),
        tenant_user_repo=AsyncMock(),
        refresh_token_repo=AsyncMock(),
    )
    return service


@pytest.mark.asyncio
async def test_signup_creates_user_and_assigns_demo_tenant(
    auth_service: AuthService,
    demo_tenant: Tenant,
) -> None:
    auth_service.user_repo.get_by_email.return_value = None
    auth_service.tenant_repo.get_or_create_demo.return_value = demo_tenant

    created_user = User(
        id=uuid.uuid4(),
        email="new@example.com",
        full_name="New User",
        hashed_password="hashed",
        is_active=True,
    )
    auth_service.user_repo.create.return_value = created_user
    auth_service.tenant_user_repo.create_membership.return_value = MagicMock()
    auth_service.refresh_token_repo.create_for_jwt.return_value = MagicMock()

    result = await auth_service.signup(
        SignupRequest(full_name="New User", email="new@example.com", password="Password123")
    )

    assert result.user.email == "new@example.com"
    assert result.tenant_id == str(demo_tenant.id)
    assert result.access_token
    assert result.refresh_token
    auth_service.tenant_repo.get_or_create_demo.assert_awaited_once()
    auth_service.session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_signup_rejects_duplicate_email(auth_service: AuthService, user: User) -> None:
    auth_service.user_repo.get_by_email.return_value = user

    with pytest.raises(ConflictError):
        await auth_service.signup(
            SignupRequest(full_name="Dup", email="owner@example.com", password="Password123")
        )


@pytest.mark.asyncio
async def test_login_returns_tokens(
    auth_service: AuthService,
    user: User,
    membership: TenantUser,
) -> None:
    auth_service.user_repo.get_by_email.return_value = user
    auth_service.tenant_user_repo.get_primary_for_user.return_value = membership
    auth_service.refresh_token_repo.create_for_jwt.return_value = MagicMock()

    result = await auth_service.login(
        LoginRequest(email="owner@example.com", password="Password123")
    )

    assert result.access_token
    assert result.refresh_token
    assert result.user.email == user.email


@pytest.mark.asyncio
async def test_login_rejects_invalid_password(auth_service: AuthService, user: User) -> None:
    auth_service.user_repo.get_by_email.return_value = user

    with pytest.raises(UnauthorizedError):
        await auth_service.login(LoginRequest(email="owner@example.com", password="wrong"))


@pytest.mark.asyncio
async def test_login_rejects_user_without_tenant(auth_service: AuthService, user: User) -> None:
    auth_service.user_repo.get_by_email.return_value = user
    auth_service.tenant_user_repo.get_primary_for_user.return_value = None

    with pytest.raises(ForbiddenError):
        await auth_service.login(
            LoginRequest(email="owner@example.com", password="Password123")
        )


@pytest.mark.asyncio
async def test_refresh_rotates_token(
    auth_service: AuthService,
    user: User,
    membership: TenantUser,
    settings: Settings,
) -> None:
    from app.core.security import create_refresh_token_jwt

    token_id = uuid.uuid4()
    refresh_jwt = create_refresh_token_jwt(user.id, token_id, settings=settings)
    stored = MagicMock()
    stored.id = token_id
    stored.user_id = user.id
    stored.revoked_at = None
    stored.expires_at = datetime.now(UTC) + timedelta(days=1)

    auth_service.refresh_token_repo.get_by_id.return_value = stored
    auth_service.refresh_token_repo.is_valid = MagicMock(return_value=True)
    auth_service.user_repo.get_by_id.return_value = user
    auth_service.tenant_user_repo.get_primary_for_user.return_value = membership
    auth_service.refresh_token_repo.create_for_jwt.return_value = MagicMock()

    result = await auth_service.refresh(refresh_jwt)

    assert result.access_token
    assert result.refresh_token
    auth_service.refresh_token_repo.revoke.assert_awaited_once_with(stored)


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(
    auth_service: AuthService,
    user: User,
    settings: Settings,
) -> None:
    from app.core.security import create_refresh_token_jwt

    token_id = uuid.uuid4()
    refresh_jwt = create_refresh_token_jwt(user.id, token_id, settings=settings)
    stored = MagicMock()

    auth_service.refresh_token_repo.get_by_id.return_value = stored

    await auth_service.logout(refresh_jwt)

    auth_service.refresh_token_repo.revoke.assert_awaited_once_with(stored)
    auth_service.session.commit.assert_awaited_once()
