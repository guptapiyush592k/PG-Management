from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentMembership, CurrentTenantId, DbSession
from app.core.exceptions import ForbiddenError
from app.schemas.common import PaginatedResponse
from app.schemas.resident import (
    ResidentCreate,
    ResidentListParams,
    ResidentResponse,
    ResidentUpdate,
)
from app.schemas.tenant_context import resolve_permissions
from app.services.resident_service import ResidentService

router = APIRouter(tags=["residents"])


def get_resident_service(db: DbSession, tenant_id: CurrentTenantId) -> ResidentService:
    return ResidentService(db, tenant_id)


ResidentServiceDep = Annotated[ResidentService, Depends(get_resident_service)]


async def require_manage_residents(membership: CurrentMembership) -> None:
    if not resolve_permissions(membership.role).manage_residents:
        raise ForbiddenError("Insufficient permissions to manage residents")


ManageResidentsDep = Annotated[None, Depends(require_manage_residents)]


def get_list_params(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=255),
    is_active: bool | None = Query(default=None),
) -> ResidentListParams:
    return ResidentListParams(
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active,
    )


ResidentListParamsDep = Annotated[ResidentListParams, Depends(get_list_params)]


@router.post("", response_model=ResidentResponse, status_code=status.HTTP_201_CREATED)
async def create_resident(
    data: ResidentCreate,
    _permission: ManageResidentsDep,
    service: ResidentServiceDep,
) -> ResidentResponse:
    return await service.create_resident(data)


@router.get("", response_model=PaginatedResponse[ResidentResponse])
async def list_residents(
    params: ResidentListParamsDep,
    service: ResidentServiceDep,
) -> PaginatedResponse[ResidentResponse]:
    return await service.list_residents(params)


@router.get("/{resident_id}", response_model=ResidentResponse)
async def get_resident(
    resident_id: UUID,
    service: ResidentServiceDep,
) -> ResidentResponse:
    return await service.get_resident(resident_id)


@router.put("/{resident_id}", response_model=ResidentResponse)
async def update_resident(
    resident_id: UUID,
    data: ResidentUpdate,
    _permission: ManageResidentsDep,
    service: ResidentServiceDep,
) -> ResidentResponse:
    return await service.update_resident(resident_id, data)


@router.delete("/{resident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resident(
    resident_id: UUID,
    _permission: ManageResidentsDep,
    service: ResidentServiceDep,
) -> None:
    await service.delete_resident(resident_id)
