from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room import Room
from app.repositories.base import BaseRepository


class RoomRepository(BaseRepository[Room]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Room, tenant_id=tenant_id)

    def _apply_filters(
        self,
        stmt,
        *,
        search: str | None = None,
        flat_id: UUID | None = None,
    ):
        stmt = self._apply_tenant_filter(stmt)
        if search:
            stmt = stmt.where(Room.room_number.ilike(f"%{search.strip()}%"))
        if flat_id is not None:
            stmt = stmt.where(Room.flat_id == flat_id)
        return stmt

    async def count(
        self,
        *,
        search: str | None = None,
        flat_id: UUID | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Room)
        stmt = self._apply_filters(stmt, search=search, flat_id=flat_id)
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        flat_id: UUID | None = None,
    ) -> list[Room]:
        stmt = self._apply_filters(select(Room), search=search, flat_id=flat_id)
        stmt = stmt.order_by(Room.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_flat_and_room_number(
        self,
        flat_id: UUID,
        room_number: str,
        *,
        exclude_id: UUID | None = None,
    ) -> Room | None:
        stmt = select(Room).where(
            Room.flat_id == flat_id,
            Room.room_number == room_number.strip(),
        )
        stmt = self._apply_tenant_filter(stmt)
        if exclude_id is not None:
            stmt = stmt.where(Room.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, *, flat_id: UUID, room_number: str) -> Room:
        room = Room(
            tenant_id=self.tenant_id,
            flat_id=flat_id,
            room_number=room_number.strip(),
        )
        return await self.add(room)

    async def update(
        self,
        room: Room,
        *,
        flat_id: UUID,
        room_number: str,
    ) -> Room:
        room.flat_id = flat_id
        room.room_number = room_number.strip()
        await self.session.flush()
        await self.session.refresh(room)
        return room
