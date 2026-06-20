import uuid
from datetime import UTC, date, datetime
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.bed import Bed, BedStatus
from app.models.booking import Booking, BookingStatus
from app.models.tenant_user import TenantUserRole
from app.schemas.booking import BookingCheckout, BookingCreate, BookingListParams
from app.services.booking_service import BookingService


@pytest.fixture
def tenant_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def resident_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def bed_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def booking(tenant_id: uuid.UUID, resident_id: uuid.UUID, bed_id: uuid.UUID) -> Booking:
    now = datetime.now(UTC)
    return Booking(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        resident_id=resident_id,
        bed_id=bed_id,
        start_date=date(2026, 6, 1),
        end_date=None,
        status=BookingStatus.ACTIVE,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def bed(tenant_id: uuid.UUID, bed_id: uuid.UUID) -> Bed:
    now = datetime.now(UTC)
    return Bed(
        id=bed_id,
        tenant_id=tenant_id,
        room_id=uuid.uuid4(),
        bed_label="A",
        rent_amount=5000,
        status=BedStatus.VACANT,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def booking_service(tenant_id: uuid.UUID) -> BookingService:
    session = AsyncMock()
    session.commit = AsyncMock()
    return BookingService(
        session,
        tenant_id,
        TenantUserRole.OWNER,
        booking_repo=AsyncMock(),
        resident_repo=AsyncMock(),
        bed_repo=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_create_booking(
    booking_service: BookingService,
    booking: Booking,
    bed: Bed,
    resident_id: uuid.UUID,
) -> None:
    resident = type("Resident", (), {"is_active": True})()
    booking_service.resident_repo.get_by_id.return_value = resident
    booking_service.bed_repo.get_by_id.return_value = bed
    booking_service.booking_repo.get_active_by_bed_id.return_value = None
    booking_service.booking_repo.create.return_value = booking
    booking_service.bed_repo.update_status.return_value = bed

    result = await booking_service.create_booking(
        BookingCreate(
            resident_id=resident_id,
            bed_id=booking.bed_id,
            start_date=date(2026, 6, 1),
        )
    )

    assert result.status == BookingStatus.ACTIVE
    booking_service.bed_repo.update_status.assert_awaited_once_with(bed, BedStatus.OCCUPIED)
    booking_service.session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_booking_rejects_inactive_resident(
    booking_service: BookingService,
    booking: Booking,
    bed: Bed,
    resident_id: uuid.UUID,
) -> None:
    resident = type("Resident", (), {"is_active": False})()
    booking_service.resident_repo.get_by_id.return_value = resident
    booking_service.bed_repo.get_by_id.return_value = bed

    with pytest.raises(ValidationError):
        await booking_service.create_booking(
            BookingCreate(
                resident_id=resident_id,
                bed_id=booking.bed_id,
                start_date=date(2026, 6, 1),
            )
        )


@pytest.mark.asyncio
async def test_create_booking_rejects_occupied_bed(
    booking_service: BookingService,
    booking: Booking,
    bed: Bed,
    resident_id: uuid.UUID,
) -> None:
    resident = type("Resident", (), {"is_active": True})()
    bed.status = BedStatus.OCCUPIED
    booking_service.resident_repo.get_by_id.return_value = resident
    booking_service.bed_repo.get_by_id.return_value = bed

    with pytest.raises(ConflictError):
        await booking_service.create_booking(
            BookingCreate(
                resident_id=resident_id,
                bed_id=booking.bed_id,
                start_date=date(2026, 6, 1),
            )
        )


@pytest.mark.asyncio
async def test_create_booking_rejects_active_booking_on_bed(
    booking_service: BookingService,
    booking: Booking,
    bed: Bed,
    resident_id: uuid.UUID,
) -> None:
    resident = type("Resident", (), {"is_active": True})()
    booking_service.resident_repo.get_by_id.return_value = resident
    booking_service.bed_repo.get_by_id.return_value = bed
    booking_service.booking_repo.get_active_by_bed_id.return_value = booking

    with pytest.raises(ConflictError):
        await booking_service.create_booking(
            BookingCreate(
                resident_id=resident_id,
                bed_id=booking.bed_id,
                start_date=date(2026, 6, 1),
            )
        )


@pytest.mark.asyncio
async def test_list_bookings(
    booking_service: BookingService,
    booking: Booking,
) -> None:
    booking_service.booking_repo.count.return_value = 1
    booking_service.booking_repo.list_paginated.return_value = [booking]

    result = await booking_service.list_bookings(
        BookingListParams(page=1, page_size=20, status=BookingStatus.ACTIVE)
    )

    assert result.total == 1
    assert result.items[0].status == BookingStatus.ACTIVE


@pytest.mark.asyncio
async def test_checkout_booking(
    booking_service: BookingService,
    booking: Booking,
    bed: Bed,
) -> None:
    booking_service.booking_repo.get_by_id.return_value = booking
    booking_service.bed_repo.get_by_id.return_value = bed
    completed = Booking(
        id=booking.id,
        tenant_id=booking.tenant_id,
        resident_id=booking.resident_id,
        bed_id=booking.bed_id,
        start_date=booking.start_date,
        end_date=date(2026, 6, 30),
        status=BookingStatus.COMPLETED,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )
    booking_service.booking_repo.checkout.return_value = completed

    result = await booking_service.checkout_booking(
        booking.id,
        BookingCheckout(end_date=date(2026, 6, 30)),
    )

    assert result.status == BookingStatus.COMPLETED
    assert result.end_date == date(2026, 6, 30)
    booking_service.bed_repo.update_status.assert_awaited_once_with(bed, BedStatus.VACANT)
    booking_service.session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_checkout_booking_defaults_end_date(
    booking_service: BookingService,
    booking: Booking,
    bed: Bed,
) -> None:
    booking_service.booking_repo.get_by_id.return_value = booking
    booking_service.bed_repo.get_by_id.return_value = bed
    completed = Booking(
        id=booking.id,
        tenant_id=booking.tenant_id,
        resident_id=booking.resident_id,
        bed_id=booking.bed_id,
        start_date=booking.start_date,
        end_date=date.today(),
        status=BookingStatus.COMPLETED,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )
    booking_service.booking_repo.checkout.return_value = completed

    await booking_service.checkout_booking(booking.id, BookingCheckout())

    booking_service.booking_repo.checkout.assert_awaited_once()
    assert booking_service.booking_repo.checkout.await_args.kwargs["end_date"] == date.today()


@pytest.mark.asyncio
async def test_checkout_booking_rejects_non_active(
    booking_service: BookingService,
    booking: Booking,
) -> None:
    booking.status = BookingStatus.COMPLETED
    booking_service.booking_repo.get_by_id.return_value = booking

    with pytest.raises(ValidationError):
        await booking_service.checkout_booking(
            booking.id,
            BookingCheckout(end_date=date(2026, 6, 30)),
        )


@pytest.mark.asyncio
async def test_checkout_booking_not_found(
    booking_service: BookingService,
) -> None:
    booking_service.booking_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await booking_service.checkout_booking(
            uuid.uuid4(),
            BookingCheckout(end_date=date(2026, 6, 30)),
        )
