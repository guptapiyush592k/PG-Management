from datetime import date
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking, BookingStatus
from app.models.resident import Resident
from app.repositories.base import BaseRepository


class BookingRepository(BaseRepository[Booking]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Booking, tenant_id=tenant_id)

    def _apply_filters(
        self,
        stmt,
        *,
        search: str | None = None,
        resident_id: UUID | None = None,
        bed_id: UUID | None = None,
        status: BookingStatus | None = None,
    ):
        stmt = self._apply_tenant_filter(stmt)
        if search:
            stmt = stmt.join(Resident, Booking.resident_id == Resident.id)
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Resident.name.ilike(pattern),
                    Resident.phone.ilike(pattern),
                )
            )
        if resident_id is not None:
            stmt = stmt.where(Booking.resident_id == resident_id)
        if bed_id is not None:
            stmt = stmt.where(Booking.bed_id == bed_id)
        if status is not None:
            stmt = stmt.where(Booking.status == status)
        return stmt

    async def count(
        self,
        *,
        search: str | None = None,
        resident_id: UUID | None = None,
        bed_id: UUID | None = None,
        status: BookingStatus | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Booking)
        stmt = self._apply_filters(
            stmt,
            search=search,
            resident_id=resident_id,
            bed_id=bed_id,
            status=status,
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        resident_id: UUID | None = None,
        bed_id: UUID | None = None,
        status: BookingStatus | None = None,
    ) -> list[Booking]:
        stmt = self._apply_filters(
            select(Booking),
            search=search,
            resident_id=resident_id,
            bed_id=bed_id,
            status=status,
        )
        stmt = (
            stmt.order_by(Booking.start_date.desc(), Booking.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_by_bed_id(
        self,
        bed_id: UUID,
        *,
        exclude_id: UUID | None = None,
    ) -> Booking | None:
        stmt = select(Booking).where(
            Booking.bed_id == bed_id,
            Booking.status == BookingStatus.ACTIVE,
        )
        stmt = self._apply_tenant_filter(stmt)
        if exclude_id is not None:
            stmt = stmt.where(Booking.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        resident_id: UUID,
        bed_id: UUID,
        start_date: date,
    ) -> Booking:
        booking = Booking(
            tenant_id=self.tenant_id,
            resident_id=resident_id,
            bed_id=bed_id,
            start_date=start_date,
            end_date=None,
            status=BookingStatus.ACTIVE,
        )
        return await self.add(booking)

    async def checkout(
        self,
        booking: Booking,
        *,
        end_date: date,
    ) -> Booking:
        booking.end_date = end_date
        booking.status = BookingStatus.COMPLETED
        await self.session.flush()
        await self.session.refresh(booking)
        return booking
