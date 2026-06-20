from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import AuthorizedContextDep, DbSession
from app.schemas.common import PaginatedResponse
from app.schemas.resident import (
    ResidentCreate,
    ResidentListParams,
    ResidentResponse,
    ResidentUpdate,
)
from app.services.resident_service import ResidentService

router = APIRouter(tags=["residents"])


def get_resident_service(auth: AuthorizedContextDep, db: DbSession) -> ResidentService:
    return ResidentService(db, auth.tenant_id, auth.membership.role)


ResidentServiceDep = Annotated[ResidentService, Depends(get_resident_service)]


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


@router.patch("/{resident_id}", response_model=ResidentResponse)
async def update_resident(
    resident_id: UUID,
    data: ResidentUpdate,
    service: ResidentServiceDep,
) -> ResidentResponse:
    return await service.update_resident(resident_id, data)


@router.delete("/{resident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resident(
    resident_id: UUID,
    service: ResidentServiceDep,
) -> None:
    await service.delete_resident(resident_id)
