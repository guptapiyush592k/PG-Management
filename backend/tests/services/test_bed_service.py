import uuid
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import ConflictError, NotFoundError
from app.models.bed import Bed, BedStatus
from app.models.room import Room
from app.schemas.bed import BedCreate, BedListParams, BedUpdate
from app.services.bed_service import BedService


@pytest.fixture
def tenant_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def room_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def room(tenant_id: uuid.UUID, room_id: uuid.UUID) -> Room:
    now = datetime.now(UTC)
    return Room(
        id=room_id,
        tenant_id=tenant_id,
        flat_id=uuid.uuid4(),
        room_number="101",
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def bed(tenant_id: uuid.UUID, room_id: uuid.UUID) -> Bed:
    now = datetime.now(UTC)
    return Bed(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        room_id=room_id,
        bed_label="A",
        rent_amount=Decimal("5000.00"),
        status=BedStatus.VACANT,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def bed_service(tenant_id: uuid.UUID) -> BedService:
    session = AsyncMock()
    session.commit = AsyncMock()
    return BedService(
        session,
        tenant_id,
        bed_repo=AsyncMock(),
        room_repo=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_create_bed(
    bed_service: BedService,
    bed: Bed,
    room: Room,
    room_id: uuid.UUID,
) -> None:
    bed_service.room_repo.get_by_id.return_value = room
    bed_service.bed_repo.get_by_room_and_bed_label.return_value = None
    bed_service.bed_repo.create.return_value = bed

    result = await bed_service.create_bed(
        BedCreate(
            room_id=room_id,
            bed_label="A",
            rent_amount=Decimal("5000.00"),
            status=BedStatus.VACANT,
        )
    )

    assert result.bed_label == "A"
    bed_service.session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_bed_rejects_missing_room(
    bed_service: BedService,
    room_id: uuid.UUID,
) -> None:
    bed_service.room_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await bed_service.create_bed(
            BedCreate(
                room_id=room_id,
                bed_label="A",
                rent_amount=Decimal("5000.00"),
            )
        )


@pytest.mark.asyncio
async def test_create_bed_rejects_duplicate_label(
    bed_service: BedService,
    room: Room,
    bed: Bed,
    room_id: uuid.UUID,
) -> None:
    bed_service.room_repo.get_by_id.return_value = room
    bed_service.bed_repo.get_by_room_and_bed_label.return_value = bed

    with pytest.raises(ConflictError):
        await bed_service.create_bed(
            BedCreate(
                room_id=room_id,
                bed_label="A",
                rent_amount=Decimal("5000.00"),
            )
        )


@pytest.mark.asyncio
async def test_list_beds(
    bed_service: BedService,
    bed: Bed,
    room: Room,
    room_id: uuid.UUID,
) -> None:
    bed_service.room_repo.get_by_id.return_value = room
    bed_service.bed_repo.count.return_value = 1
    bed_service.bed_repo.list_paginated.return_value = [bed]

    result = await bed_service.list_beds(
        BedListParams(page=1, page_size=20, room_id=room_id, search="A", status=BedStatus.VACANT)
    )

    assert result.total == 1
    assert result.items[0].bed_label == "A"


@pytest.mark.asyncio
async def test_delete_bed(
    bed_service: BedService,
    bed: Bed,
) -> None:
    bed_service.bed_repo.get_by_id.return_value = bed

    await bed_service.delete_bed(bed.id)

    bed_service.bed_repo.delete.assert_awaited_once_with(bed)
    bed_service.session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_bed(
    bed_service: BedService,
    bed: Bed,
    room: Room,
    room_id: uuid.UUID,
) -> None:
    bed_service.bed_repo.get_by_id.return_value = bed
    bed_service.room_repo.get_by_id.return_value = room
    bed_service.bed_repo.get_by_room_and_bed_label.return_value = None
    bed_service.bed_repo.update.return_value = bed

    await bed_service.update_bed(
        bed.id,
        BedUpdate(
            room_id=room_id,
            bed_label="B",
            rent_amount=Decimal("6000.00"),
            status=BedStatus.MAINTENANCE,
        ),
    )

    bed_service.session.commit.assert_awaited_once()
