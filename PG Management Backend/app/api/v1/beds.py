from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentMembership, CurrentTenantId, DbSession
from app.core.exceptions import ForbiddenError
from app.models.bed import BedStatus
from app.schemas.bed import BedCreate, BedListParams, BedResponse, BedUpdate
from app.schemas.common import PaginatedResponse
from app.schemas.tenant_context import resolve_permissions
from app.services.bed_service import BedService

router = APIRouter(tags=["beds"])


def get_bed_service(db: DbSession, tenant_id: CurrentTenantId) -> BedService:
    return BedService(db, tenant_id)


BedServiceDep = Annotated[BedService, Depends(get_bed_service)]


async def require_manage_beds(membership: CurrentMembership) -> None:
    if not resolve_permissions(membership.role).manage_beds:
        raise ForbiddenError("Insufficient permissions to manage beds")


ManageBedsDep = Annotated[None, Depends(require_manage_beds)]


def get_list_params(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=255),
    room_id: UUID | None = Query(default=None),
    status: BedStatus | None = Query(default=None),
) -> BedListParams:
    return BedListParams(
        page=page,
        page_size=page_size,
        search=search,
        room_id=room_id,
        status=status,
    )


BedListParamsDep = Annotated[BedListParams, Depends(get_list_params)]


@router.post("", response_model=BedResponse, status_code=status.HTTP_201_CREATED)
async def create_bed(
    data: BedCreate,
    _permission: ManageBedsDep,
    service: BedServiceDep,
) -> BedResponse:
    return await service.create_bed(data)


@router.get("", response_model=PaginatedResponse[BedResponse])
async def list_beds(
    params: BedListParamsDep,
    service: BedServiceDep,
) -> PaginatedResponse[BedResponse]:
    return await service.list_beds(params)


@router.get("/{bed_id}", response_model=BedResponse)
async def get_bed(
    bed_id: UUID,
    service: BedServiceDep,
) -> BedResponse:
    return await service.get_bed(bed_id)


@router.put("/{bed_id}", response_model=BedResponse)
async def update_bed(
    bed_id: UUID,
    data: BedUpdate,
    _permission: ManageBedsDep,
    service: BedServiceDep,
) -> BedResponse:
    return await service.update_bed(bed_id, data)


@router.delete("/{bed_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bed(
    bed_id: UUID,
    _permission: ManageBedsDep,
    service: BedServiceDep,
) -> None:
    await service.delete_bed(bed_id)
