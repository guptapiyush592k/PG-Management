from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import DbSession, JwtCurrentUser
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    SignupRequest,
    SwitchTenantRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(tags=["auth"])


def get_auth_service(db: DbSession) -> AuthService:
    return AuthService(db)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: SignupRequest, auth_service: AuthServiceDep) -> TokenResponse:
    return await auth_service.signup(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, auth_service: AuthServiceDep) -> TokenResponse:
    return await auth_service.login(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(data: RefreshRequest, auth_service: AuthServiceDep) -> TokenResponse:
    return await auth_service.refresh(data.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(data: LogoutRequest, auth_service: AuthServiceDep) -> MessageResponse:
    await auth_service.logout(data.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.post("/switch-tenant", response_model=TokenResponse)
async def switch_tenant(
    data: SwitchTenantRequest,
    current_user: JwtCurrentUser,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    from uuid import UUID

    return await auth_service.switch_tenant(current_user, UUID(data.tenant_id))
