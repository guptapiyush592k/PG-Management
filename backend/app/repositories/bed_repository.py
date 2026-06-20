from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bed import Bed, BedStatus
from app.repositories.base import BaseRepository


class BedRepository(BaseRepository[Bed]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Bed, tenant_id=tenant_id)

    def _apply_filters(
        self,
        stmt,
        *,
        search: str | None = None,
        room_id: UUID | None = None,
        status: BedStatus | None = None,
    ):
        stmt = self._apply_tenant_filter(stmt)
        if search:
            stmt = stmt.where(Bed.bed_label.ilike(f"%{search.strip()}%"))
        if room_id is not None:
            stmt = stmt.where(Bed.room_id == room_id)
        if status is not None:
            stmt = stmt.where(Bed.status == status)
        return stmt

    async def count(
        self,
        *,
        search: str | None = None,
        room_id: UUID | None = None,
        status: BedStatus | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Bed)
        stmt = self._apply_filters(stmt, search=search, room_id=room_id, status=status)
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        room_id: UUID | None = None,
        status: BedStatus | None = None,
    ) -> list[Bed]:
        stmt = self._apply_filters(select(Bed), search=search, room_id=room_id, status=status)
        stmt = stmt.order_by(Bed.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_room_and_bed_label(
        self,
        room_id: UUID,
        bed_label: str,
        *,
        exclude_id: UUID | None = None,
    ) -> Bed | None:
        stmt = select(Bed).where(
            Bed.room_id == room_id,
            Bed.bed_label == bed_label.strip(),
        )
        stmt = self._apply_tenant_filter(stmt)
        if exclude_id is not None:
            stmt = stmt.where(Bed.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        room_id: UUID,
        bed_label: str,
        rent_amount: Decimal,
        status: BedStatus,
    ) -> Bed:
        bed = Bed(
            tenant_id=self.tenant_id,
            room_id=room_id,
            bed_label=bed_label.strip(),
            rent_amount=rent_amount,
            status=status,
        )
        return await self.add(bed)

    async def update(
        self,
        bed: Bed,
        *,
        room_id: UUID,
        bed_label: str,
        rent_amount: Decimal,
        status: BedStatus,
    ) -> Bed:
        bed.room_id = room_id
        bed.bed_label = bed_label.strip()
        bed.rent_amount = rent_amount
        bed.status = status
        await self.session.flush()
        await self.session.refresh(bed)
        return bed

    async def update_status(self, bed: Bed, status: BedStatus) -> Bed:
        bed.status = status
        await self.session.flush()
        await self.session.refresh(bed)
        return bed
