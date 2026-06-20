from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.room import Room
from app.repositories.flat_repository import FlatRepository
from app.repositories.room_repository import RoomRepository
from app.schemas.common import PaginatedResponse
from app.schemas.room import RoomCreate, RoomListParams, RoomResponse, RoomUpdate


class RoomService:
    def __init__(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        *,
        room_repo: RoomRepository | None = None,
        flat_repo: FlatRepository | None = None,
    ) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.room_repo = room_repo or RoomRepository(session, tenant_id)
        self.flat_repo = flat_repo or FlatRepository(session, tenant_id)

    async def create_room(self, data: RoomCreate) -> RoomResponse:
        await self._ensure_flat_exists(data.flat_id)
        await self._ensure_unique_room_number(data.flat_id, data.room_number)

        room = await self.room_repo.create(
            flat_id=data.flat_id,
            room_number=data.room_number,
        )
        await self.session.commit()
        return self._to_response(room)

    async def list_rooms(self, params: RoomListParams) -> PaginatedResponse[RoomResponse]:
        if params.flat_id is not None:
            await self._ensure_flat_exists(params.flat_id)

        total = await self.room_repo.count(search=params.search, flat_id=params.flat_id)
        rooms = await self.room_repo.list_paginated(
            offset=params.offset,
            limit=params.page_size,
            search=params.search,
            flat_id=params.flat_id,
        )
        return PaginatedResponse[RoomResponse](
            items=[self._to_response(room) for room in rooms],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_room(self, room_id: UUID) -> RoomResponse:
        room = await self._get_room_or_404(room_id)
        return self._to_response(room)

    async def update_room(self, room_id: UUID, data: RoomUpdate) -> RoomResponse:
        room = await self._get_room_or_404(room_id)
        await self._ensure_flat_exists(data.flat_id)
        await self._ensure_unique_room_number(
            data.flat_id,
            data.room_number,
            exclude_id=room_id,
        )

        updated = await self.room_repo.update(
            room,
            flat_id=data.flat_id,
            room_number=data.room_number,
        )
        await self.session.commit()
        return self._to_response(updated)

    async def delete_room(self, room_id: UUID) -> None:
        room = await self._get_room_or_404(room_id)
        await self.room_repo.delete(room)
        await self.session.commit()

    async def _get_room_or_404(self, room_id: UUID) -> Room:
        room = await self.room_repo.get_by_id(room_id)
        if room is None:
            raise NotFoundError("Room not found")
        return room

    async def _ensure_flat_exists(self, flat_id: UUID) -> None:
        flat = await self.flat_repo.get_by_id(flat_id)
        if flat is None:
            raise NotFoundError("Flat not found")

    async def _ensure_unique_room_number(
        self,
        flat_id: UUID,
        room_number: str,
        *,
        exclude_id: UUID | None = None,
    ) -> None:
        existing = await self.room_repo.get_by_flat_and_room_number(
            flat_id,
            room_number,
            exclude_id=exclude_id,
        )
        if existing is not None:
            raise ConflictError("Room number already exists for this flat")

    def _to_response(self, room: Room) -> RoomResponse:
        return RoomResponse(
            id=str(room.id),
            tenant_id=str(room.tenant_id),
            flat_id=str(room.flat_id),
            room_number=room.room_number,
            created_at=room.created_at,
            updated_at=room.updated_at,
        )
