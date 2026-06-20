from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.bed import Bed, BedStatus
from app.models.booking import Booking, BookingStatus
from app.models.resident import Resident
from app.models.tenant_user import TenantUserRole
from app.repositories.bed_repository import BedRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.resident_repository import ResidentRepository
from app.schemas.booking import BookingCheckout, BookingCreate, BookingListParams, BookingResponse
from app.schemas.common import PaginatedResponse
from app.services.permissions import require_permission


class BookingService:
    def __init__(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        role: TenantUserRole,
        *,
        booking_repo: BookingRepository | None = None,
        resident_repo: ResidentRepository | None = None,
        bed_repo: BedRepository | None = None,
    ) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.role = role
        self.booking_repo = booking_repo or BookingRepository(session, tenant_id)
        self.resident_repo = resident_repo or ResidentRepository(session, tenant_id)
        self.bed_repo = bed_repo or BedRepository(session, tenant_id)

    async def create_booking(self, data: BookingCreate) -> BookingResponse:
        require_permission(self.role, "manage_beds")
        resident = await self._get_resident_or_404(data.resident_id)
        if not resident.is_active:
            raise ValidationError("Resident is not active")
        bed = await self._get_bed_or_404(data.bed_id)
        await self._ensure_bed_available(bed)

        booking = await self.booking_repo.create(
            resident_id=data.resident_id,
            bed_id=data.bed_id,
            start_date=data.start_date,
        )
        await self.bed_repo.update_status(bed, BedStatus.OCCUPIED)
        await self.session.commit()
        return self._to_response(booking)

    async def list_bookings(
        self,
        params: BookingListParams,
    ) -> PaginatedResponse[BookingResponse]:
        if params.resident_id is not None:
            await self._get_resident_or_404(params.resident_id)
        if params.bed_id is not None:
            await self._get_bed_or_404(params.bed_id)

        total = await self.booking_repo.count(
            search=params.search,
            resident_id=params.resident_id,
            bed_id=params.bed_id,
            status=params.status,
        )
        bookings = await self.booking_repo.list_paginated(
            offset=params.offset,
            limit=params.page_size,
            search=params.search,
            resident_id=params.resident_id,
            bed_id=params.bed_id,
            status=params.status,
        )
        return PaginatedResponse[BookingResponse](
            items=[self._to_response(booking) for booking in bookings],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def checkout_booking(
        self,
        booking_id: UUID,
        data: BookingCheckout,
    ) -> BookingResponse:
        require_permission(self.role, "manage_beds")
        booking = await self._get_booking_or_404(booking_id)
        if booking.status != BookingStatus.ACTIVE:
            raise ValidationError("Only active bookings can be checked out")

        end_date = data.end_date or date.today()
        if end_date < booking.start_date:
            raise ValidationError("Checkout date cannot be before start date")

        bed = await self._get_bed_or_404(booking.bed_id)
        updated = await self.booking_repo.checkout(booking, end_date=end_date)
        await self.bed_repo.update_status(bed, BedStatus.VACANT)
        await self.session.commit()
        return self._to_response(updated)

    async def _get_booking_or_404(self, booking_id: UUID) -> Booking:
        booking = await self.booking_repo.get_by_id(booking_id)
        if booking is None:
            raise NotFoundError("Booking not found")
        return booking

    async def _get_resident_or_404(self, resident_id: UUID) -> Resident:
        resident = await self.resident_repo.get_by_id(resident_id)
        if resident is None:
            raise NotFoundError("Resident not found")
        return resident

    async def _get_bed_or_404(self, bed_id: UUID) -> Bed:
        bed = await self.bed_repo.get_by_id(bed_id)
        if bed is None:
            raise NotFoundError("Bed not found")
        return bed

    async def _ensure_bed_available(self, bed: Bed) -> None:
        if bed.status != BedStatus.VACANT:
            raise ConflictError("Bed is not vacant")
        active_booking = await self.booking_repo.get_active_by_bed_id(bed.id)
        if active_booking is not None:
            raise ConflictError("Bed already has an active booking")

    def _to_response(self, booking: Booking) -> BookingResponse:
        return BookingResponse(
            id=str(booking.id),
            tenant_id=str(booking.tenant_id),
            resident_id=str(booking.resident_id),
            bed_id=str(booking.bed_id),
            start_date=booking.start_date,
            end_date=booking.end_date,
            status=booking.status,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
        )
