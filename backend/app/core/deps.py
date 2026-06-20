from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import decode_access_token
from app.core.settings import Settings, get_settings
from app.db.session import get_db
from app.middleware.tenant_authorization import TENANT_ID_HEADER
from app.middleware.tenant_context import set_current_tenant_id
from app.models.tenant import Tenant
from app.models.tenant_user import TenantUser
from app.models.user import User
from app.services.tenant_authorization_service import (
    AuthorizedContext,
    TenantAuthorizationService,
)

security_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def _get_state_attr(request: Request, name: str):
    return getattr(request.state, name, None)


async def get_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Missing authentication credentials")
    return decode_access_token(credentials.credentials)


async def get_authorized_context(
    request: Request,
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    x_tenant_id: Annotated[str | None, Header(alias=TENANT_ID_HEADER)] = None,
) -> AuthorizedContext:
    """
    Dependency for protected routes. Reuses middleware-populated request.state when
    available; otherwise performs authorization using JWT + X-Tenant-ID header.
    """
    user = _get_state_attr(request, "user")
    tenant = _get_state_attr(request, "tenant")
    membership = _get_state_attr(request, "tenant_membership")
    user_id = _get_state_attr(request, "user_id")
    tenant_id = _get_state_attr(request, "tenant_id")

    if user is not None and tenant is not None and membership is not None:
        return AuthorizedContext(
            user=user,
            tenant=tenant,
            membership=membership,
            user_id=user_id,
            tenant_id=tenant_id,
        )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Missing authentication credentials")
    if not x_tenant_id:
        raise ForbiddenError("X-Tenant-ID header is required")

    service = TenantAuthorizationService(db)
    context = await service.authorize(
        access_token=credentials.credentials,
        tenant_id_header=x_tenant_id,
    )
    set_current_tenant_id(context.tenant_id)
    return context


async def get_current_user(
    auth_context: Annotated[AuthorizedContext, Depends(get_authorized_context)],
) -> User:
    return auth_context.user


async def get_current_tenant(
    auth_context: Annotated[AuthorizedContext, Depends(get_authorized_context)],
) -> Tenant:
    return auth_context.tenant


async def get_current_membership(
    auth_context: Annotated[AuthorizedContext, Depends(get_authorized_context)],
) -> TenantUser:
    return auth_context.membership


async def get_current_user_id(
    auth_context: Annotated[AuthorizedContext, Depends(get_authorized_context)],
) -> UUID:
    return auth_context.user_id


async def get_current_tenant_id(
    auth_context: Annotated[AuthorizedContext, Depends(get_authorized_context)],
) -> UUID:
    return auth_context.tenant_id


# JWT-only tenant resolution for /me/context (does not trust X-Tenant-ID).
async def get_jwt_tenant_id(
    token_payload: Annotated[dict, Depends(get_token_payload)],
) -> UUID:
    tenant_id = token_payload.get("tenant_id")
    if not tenant_id:
        raise ForbiddenError("Tenant context missing from access token")
    return UUID(str(tenant_id))


async def get_jwt_current_user(
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


AuthorizedContextDep = Annotated[AuthorizedContext, Depends(get_authorized_context)]
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentTenant = Annotated[Tenant, Depends(get_current_tenant)]
CurrentMembership = Annotated[TenantUser, Depends(get_current_membership)]
CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]
CurrentTenantId = Annotated[UUID, Depends(get_current_tenant_id)]
JwtTenantId = Annotated[UUID, Depends(get_jwt_tenant_id)]
JwtCurrentUser = Annotated[User, Depends(get_jwt_current_user)]
