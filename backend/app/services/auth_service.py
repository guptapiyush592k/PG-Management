from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token_jwt,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.core.settings import Settings, get_settings
from app.models.tenant_user import TenantUserRole
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository, TenantUserRepository
from app.repositories.tenant_repository import TenantRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserResponse


@dataclass
class AuthTokens:
    access_token: str
    refresh_token: str
    expires_in: int
    user: User
    tenant_id: UUID


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        *,
        settings: Settings | None = None,
        user_repo: UserRepository | None = None,
        tenant_repo: TenantRepository | None = None,
        tenant_user_repo: TenantUserRepository | None = None,
        refresh_token_repo: RefreshTokenRepository | None = None,
    ) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.user_repo = user_repo or UserRepository(session)
        self.tenant_repo = tenant_repo or TenantRepository(session)
        self.tenant_user_repo = tenant_user_repo or TenantUserRepository(session)
        self.refresh_token_repo = refresh_token_repo or RefreshTokenRepository(session)

    async def signup(self, data: SignupRequest) -> TokenResponse:
        existing = await self.user_repo.get_by_email(data.email)
        if existing is not None:
            raise ConflictError("Email is already registered")

        demo_tenant = await self.tenant_repo.get_or_create_demo(
            slug=self.settings.demo_tenant_slug,
            name="Demo PG",
        )

        user = await self.user_repo.create(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
        )
        await self.tenant_user_repo.create_membership(
            tenant_id=demo_tenant.id,
            user_id=user.id,
            role=TenantUserRole.MANAGER,
            is_primary=True,
        )

        tokens = await self._issue_tokens(user, demo_tenant.id)
        await self.session.commit()
        return self._to_token_response(tokens)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise ForbiddenError("User account is inactive")

        tenant_id = await self._resolve_login_tenant_id(user.id, data.tenant_id)
        tokens = await self._issue_tokens(user, tenant_id)
        await self.session.commit()
        return self._to_token_response(tokens)

    async def switch_tenant(self, user: User, tenant_id: UUID) -> TokenResponse:
        if not user.is_active:
            raise ForbiddenError("User account is inactive")
        await self._ensure_tenant_membership(user.id, tenant_id)
        tokens = await self._issue_tokens(user, tenant_id)
        await self.session.commit()
        return self._to_token_response(tokens)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_refresh_token(refresh_token, settings=self.settings)
        user_id = payload.get("sub")
        jti = payload.get("jti")
        if not user_id or not jti:
            raise UnauthorizedError("Invalid refresh token payload")

        stored = await self.refresh_token_repo.get_by_id(UUID(jti))
        if stored is None:
            raise UnauthorizedError("Refresh token is invalid or expired")
        if stored.revoked_at is not None:
            await self.refresh_token_repo.revoke_all_for_user(stored.user_id)
            await self.session.commit()
            raise UnauthorizedError("Refresh token has been revoked")
        if not self.refresh_token_repo.is_valid(stored):
            raise UnauthorizedError("Refresh token is invalid or expired")
        if str(stored.user_id) != str(user_id):
            raise UnauthorizedError("Refresh token does not belong to this user")

        user = await self.user_repo.get_by_id(UUID(user_id))
        if user is None or not user.is_active:
            raise UnauthorizedError("User account is unavailable")

        await self.refresh_token_repo.revoke(stored)

        membership = await self.tenant_user_repo.get_primary_for_user(user.id)
        if membership is None:
            raise ForbiddenError("User is not assigned to any tenant")

        tokens = await self._issue_tokens(user, membership.tenant_id)
        await self.session.commit()
        return self._to_token_response(tokens)

    async def logout(self, refresh_token: str) -> None:
        payload = decode_refresh_token(refresh_token, settings=self.settings)
        jti = payload.get("jti")
        if not jti:
            raise UnauthorizedError("Invalid refresh token payload")

        stored = await self.refresh_token_repo.get_by_id(UUID(jti))
        if stored is None:
            raise UnauthorizedError("Refresh token not found")

        await self.refresh_token_repo.revoke(stored)
        await self.session.commit()

    async def _resolve_login_tenant_id(
        self,
        user_id: UUID,
        tenant_id_raw: str | None,
    ) -> UUID:
        if tenant_id_raw:
            tenant_id = UUID(str(tenant_id_raw))
            await self._ensure_tenant_membership(user_id, tenant_id)
            return tenant_id

        membership = await self.tenant_user_repo.get_primary_for_user(user_id)
        if membership is None:
            raise ForbiddenError("User is not assigned to any tenant")
        return membership.tenant_id

    async def _ensure_tenant_membership(self, user_id: UUID, tenant_id: UUID) -> None:
        membership = await self.tenant_user_repo.get_membership_for_user_and_tenant(
            user_id,
            tenant_id,
        )
        if membership is None:
            raise ForbiddenError("User does not have access to this tenant")

    async def _issue_tokens(self, user: User, tenant_id: UUID) -> AuthTokens:
        expires_delta = timedelta(minutes=self.settings.access_token_expire_minutes)
        access_token = create_access_token(
            user.id,
            tenant_id,
            settings=self.settings,
            expires_delta=expires_delta,
        )

        refresh_expires = datetime.now(UTC) + timedelta(days=self.settings.refresh_token_expire_days)
        token_id = uuid4()
        refresh_jwt = create_refresh_token_jwt(
            user.id,
            token_id,
            settings=self.settings,
            expires_delta=timedelta(days=self.settings.refresh_token_expire_days),
        )
        await self.refresh_token_repo.create_for_jwt(
            token_id=token_id,
            user_id=user.id,
            refresh_jwt=refresh_jwt,
            expires_at=refresh_expires,
        )

        return AuthTokens(
            access_token=access_token,
            refresh_token=refresh_jwt,
            expires_in=int(expires_delta.total_seconds()),
            user=user,
            tenant_id=tenant_id,
        )

    def _to_token_response(self, tokens: AuthTokens) -> TokenResponse:
        return TokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type="bearer",
            expires_in=tokens.expires_in,
            user=UserResponse(
                id=str(tokens.user.id),
                email=tokens.user.email,
                full_name=tokens.user.full_name,
            ),
            tenant_id=str(tokens.tenant_id),
        )
