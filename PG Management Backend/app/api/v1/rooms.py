from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentMembership, CurrentTenantId, DbSession
from app.core.exceptions import ForbiddenError
from app.schemas.common import PaginatedResponse
from app.schemas.room import RoomCreate, RoomListParams, RoomResponse, RoomUpdate
from app.schemas.tenant_context import resolve_permissions
from app.services.room_service import RoomService

router = APIRouter(tags=["rooms"])


def get_room_service(db: DbSession, tenant_id: CurrentTenantId) -> RoomService:
    return RoomService(db, tenant_id)


RoomServiceDep = Annotated[RoomService, Depends(get_room_service)]


async def require_manage_rooms(membership: CurrentMembership) -> None:
    if not resolve_permissions(membership.role).manage_rooms:
        raise ForbiddenError("Insufficient permissions to manage rooms")


ManageRoomsDep = Annotated[None, Depends(require_manage_rooms)]


def get_list_params(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=255),
    flat_id: UUID | None = Query(default=None),
) -> RoomListParams:
    return RoomListParams(page=page, page_size=page_size, search=search, flat_id=flat_id)


RoomListParamsDep = Annotated[RoomListParams, Depends(get_list_params)]


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    data: RoomCreate,
    _permission: ManageRoomsDep,
    service: RoomServiceDep,
) -> RoomResponse:
    return await service.create_room(data)


@router.get("", response_model=PaginatedResponse[RoomResponse])
async def list_rooms(
    params: RoomListParamsDep,
    service: RoomServiceDep,
) -> PaginatedResponse[RoomResponse]:
    return await service.list_rooms(params)


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: UUID,
    service: RoomServiceDep,
) -> RoomResponse:
    return await service.get_room(room_id)


@router.put("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: UUID,
    data: RoomUpdate,
    _permission: ManageRoomsDep,
    service: RoomServiceDep,
) -> RoomResponse:
    return await service.update_room(room_id, data)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: UUID,
    _permission: ManageRoomsDep,
    service: RoomServiceDep,
) -> None:
    await service.delete_room(room_id)
