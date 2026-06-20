from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_refresh_token
from app.models.refresh_token import RefreshToken
from app.models.tenant_user import TenantUser
from app.repositories.base import BaseRepository


class TenantUserRepository(BaseRepository[TenantUser]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TenantUser)

    async def create_membership(
        self,
        *,
        tenant_id: UUID,
        user_id: UUID,
        role,
        is_primary: bool = False,
    ) -> TenantUser:
        membership = TenantUser(
            tenant_id=tenant_id,
            user_id=user_id,
            role=role,
            is_primary=is_primary,
        )
        return await self.add(membership)

    async def get_primary_for_user(self, user_id: UUID) -> TenantUser | None:
        result = await self.session.execute(
            select(TenantUser)
            .where(TenantUser.user_id == user_id)
            .order_by(TenantUser.is_primary.desc(), TenantUser.created_at.asc())
        )
        return result.scalars().first()

    async def get_membership_for_user_and_tenant(
        self,
        user_id: UUID,
        tenant_id: UUID,
    ) -> TenantUser | None:
        result = await self.session.execute(
            select(TenantUser).where(
                TenantUser.user_id == user_id,
                TenantUser.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RefreshToken)

    async def create_for_jwt(
        self,
        *,
        token_id: UUID,
        user_id: UUID,
        refresh_jwt: str,
        expires_at: datetime,
    ) -> RefreshToken:
        record = RefreshToken(
            id=token_id,
            user_id=user_id,
            token_hash=hash_refresh_token(refresh_jwt),
            expires_at=expires_at,
        )
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def get_by_id(self, token_id: UUID) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.id == token_id)
        )
        return result.scalar_one_or_none()

    async def revoke(self, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(UTC)
        await self.session.flush()

    def is_valid(self, token: RefreshToken) -> bool:
        now = datetime.now(UTC)
        expires_at = token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return token.revoked_at is None and expires_at > now
