from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.tenant import Tenant
from app.models.tenant_user import TenantUser
from app.models.user import User
from app.repositories.refresh_token_repository import TenantUserRepository
from app.repositories.tenant_repository import TenantRepository
from app.schemas.tenant_context import (
    MeContextResponse,
    TenantContextResponse,
    UserContextResponse,
    resolve_permissions,
)


class TenantContextService:
    def __init__(
        self,
        session: AsyncSession,
        *,
        tenant_repo: TenantRepository | None = None,
        tenant_user_repo: TenantUserRepository | None = None,
    ) -> None:
        self.session = session
        self.tenant_repo = tenant_repo or TenantRepository(session)
        self.tenant_user_repo = tenant_user_repo or TenantUserRepository(session)

    async def get_context(
        self,
        user: User,
        tenant_id: UUID,
    ) -> MeContextResponse:
        membership = await self.tenant_user_repo.get_membership_for_user_and_tenant(
            user.id,
            tenant_id,
        )
        if membership is None:
            raise ForbiddenError("User does not belong to this tenant")

        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        if not tenant.is_active:
            raise ForbiddenError("Tenant account is inactive")

        return self._build_response(user, tenant, membership)

    def _build_response(
        self,
        user: User,
        tenant: Tenant,
        membership: TenantUser,
    ) -> MeContextResponse:
        return MeContextResponse(
            user=UserContextResponse(
                id=str(user.id),
                name=user.full_name,
                email=user.email,
            ),
            tenant=TenantContextResponse(
                id=str(tenant.id),
                name=tenant.name,
                logo_url=tenant.logo_url,
                primary_color=tenant.primary_color,
                secondary_color=tenant.secondary_color,
                is_demo=tenant.is_demo,
                subscription_status=tenant.subscription_status.value,
            ),
            permissions=resolve_permissions(membership.role),
        )
