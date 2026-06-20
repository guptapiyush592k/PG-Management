from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import AuthorizedContextDep, DbSession
from app.schemas.common import PaginatedResponse
from app.schemas.flat import FlatCreate, FlatListParams, FlatResponse, FlatUpdate
from app.services.flat_service import FlatService

router = APIRouter(tags=["flats"])


def get_flat_service(auth: AuthorizedContextDep, db: DbSession) -> FlatService:
    return FlatService(db, auth.tenant_id, auth.membership.role)


FlatServiceDep = Annotated[FlatService, Depends(get_flat_service)]


def get_list_params(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=255),
    is_active: bool | None = Query(default=None),
) -> FlatListParams:
    return FlatListParams(page=page, page_size=page_size, search=search, is_active=is_active)


FlatListParamsDep = Annotated[FlatListParams, Depends(get_list_params)]


@router.post("", response_model=FlatResponse, status_code=status.HTTP_201_CREATED)
async def create_flat(
    data: FlatCreate,
    service: FlatServiceDep,
) -> FlatResponse:
    return await service.create_flat(data)


@router.get("", response_model=PaginatedResponse[FlatResponse])
async def list_flats(
    params: FlatListParamsDep,
    service: FlatServiceDep,
) -> PaginatedResponse[FlatResponse]:
    return await service.list_flats(params)


@router.get("/{flat_id}", response_model=FlatResponse)
async def get_flat(
    flat_id: UUID,
    service: FlatServiceDep,
) -> FlatResponse:
    return await service.get_flat(flat_id)


@router.patch("/{flat_id}", response_model=FlatResponse)
async def update_flat(
    flat_id: UUID,
    data: FlatUpdate,
    service: FlatServiceDep,
) -> FlatResponse:
    return await service.update_flat(flat_id, data)


@router.delete("/{flat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flat(
    flat_id: UUID,
    service: FlatServiceDep,
) -> None:
    await service.delete_flat(flat_id)
