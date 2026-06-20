from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import decode_access_token
from app.models.tenant import Tenant
from app.models.tenant_user import TenantUser
from app.models.user import User
from app.repositories.refresh_token_repository import TenantUserRepository
from app.repositories.tenant_repository import TenantRepository
from app.repositories.user_repository import UserRepository


@dataclass(frozen=True)
class AuthorizedContext:
    user: User
    tenant: Tenant
    membership: TenantUser
    user_id: UUID
    tenant_id: UUID


class TenantAuthorizationService:
    def __init__(
        self,
        session: AsyncSession,
        *,
        user_repo: UserRepository | None = None,
        tenant_repo: TenantRepository | None = None,
        tenant_user_repo: TenantUserRepository | None = None,
    ) -> None:
        self.session = session
        self.user_repo = user_repo or UserRepository(session)
        self.tenant_repo = tenant_repo or TenantRepository(session)
        self.tenant_user_repo = tenant_user_repo or TenantUserRepository(session)

    async def authorize(
        self,
        *,
        access_token: str,
        tenant_id_header: str,
    ) -> AuthorizedContext:
        payload = decode_access_token(access_token)
        user_id_raw = payload.get("sub")
        if not user_id_raw:
            raise UnauthorizedError("Invalid token payload")

        try:
            user_id = UUID(str(user_id_raw))
            tenant_id = UUID(str(tenant_id_header))
        except ValueError as exc:
            raise ForbiddenError("Invalid user or tenant identifier") from exc

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        if not user.is_active:
            raise ForbiddenError("User account is inactive")

        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        if not tenant.is_active:
            raise ForbiddenError("Tenant account is inactive")

        membership = await self.tenant_user_repo.get_membership_for_user_and_tenant(
            user_id,
            tenant_id,
        )
        if membership is None:
            raise ForbiddenError("User does not have access to this tenant")

        return AuthorizedContext(
            user=user,
            tenant=tenant,
            membership=membership,
            user_id=user_id,
            tenant_id=tenant_id,
        )
