from contextvars import ContextVar
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import Settings, get_settings
from app.core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.middleware.tenant_context import get_current_tenant_id, set_current_tenant_id
from app.models.tenant import Tenant
from app.models.tenant_user import TenantUser
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


async def get_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Missing authentication credentials")
    return decode_access_token(credentials.credentials)


async def get_current_user(
    db: DbSession,
    token_payload: Annotated[dict, Depends(get_token_payload)],
) -> User:
    user_id = token_payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token payload")

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundError("User not found")
    if not user.is_active:
        raise ForbiddenError("User account is inactive")
    return user


async def get_current_tenant(
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
    token_payload: Annotated[dict, Depends(get_token_payload)],
    x_tenant_id: Annotated[str | None, Header(alias="X-Tenant-ID")] = None,
) -> Tenant:
    tenant_id_value = (
        x_tenant_id
        or get_current_tenant_id()
        or token_payload.get("tenant_id")
    )
    if not tenant_id_value:
        raise ForbiddenError("Tenant context is required")

    tenant_uuid = UUID(str(tenant_id_value))
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_uuid))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise NotFoundError("Tenant not found")
    if not tenant.is_active:
        raise ForbiddenError("Tenant account is inactive")

    membership = await db.execute(
        select(TenantUser).where(
            TenantUser.tenant_id == tenant_uuid,
            TenantUser.user_id == current_user.id,
        )
    )
    if membership.scalar_one_or_none() is None:
        raise ForbiddenError("User does not belong to this tenant")

    set_current_tenant_id(tenant.id)
    return tenant


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentTenant = Annotated[Tenant, Depends(get_current_tenant)]


async def get_jwt_tenant_id(
    token_payload: Annotated[dict, Depends(get_token_payload)],
) -> UUID:
    """Resolve tenant id from JWT only — never from client-supplied headers."""
    tenant_id = token_payload.get("tenant_id")
    if not tenant_id:
        raise ForbiddenError("Tenant context missing from access token")
    return UUID(str(tenant_id))


JwtTenantId = Annotated[UUID, Depends(get_jwt_tenant_id)]
