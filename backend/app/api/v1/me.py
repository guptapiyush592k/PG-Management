from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import DbSession, JwtCurrentUser, JwtTenantId
from app.schemas.tenant_context import MeContextResponse
from app.services.tenant_context_service import TenantContextService

router = APIRouter(tags=["me"])


def get_tenant_context_service(db: DbSession) -> TenantContextService:
    return TenantContextService(db)


TenantContextServiceDep = Annotated[TenantContextService, Depends(get_tenant_context_service)]


@router.get("/context", response_model=MeContextResponse)
async def get_me_context(
    current_user: JwtCurrentUser,
    tenant_id: JwtTenantId,
    service: TenantContextServiceDep,
) -> MeContextResponse:
    return await service.get_context(current_user, tenant_id)
