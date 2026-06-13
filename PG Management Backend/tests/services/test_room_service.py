import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import ConflictError, NotFoundError
from app.models.flat import Flat
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomListParams, RoomUpdate
from app.services.room_service import RoomService


@pytest.fixture
def tenant_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def flat_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def flat(tenant_id: uuid.UUID, flat_id: uuid.UUID) -> Flat:
    now = datetime.now(UTC)
    return Flat(
        id=flat_id,
        tenant_id=tenant_id,
        name="Sunrise PG",
        address="123 Main Street",
        is_active=True,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def room(tenant_id: uuid.UUID, flat_id: uuid.UUID) -> Room:
    now = datetime.now(UTC)
    return Room(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        flat_id=flat_id,
        room_number="101",
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def room_service(tenant_id: uuid.UUID) -> RoomService:
    session = AsyncMock()
    session.commit = AsyncMock()
    return RoomService(
        session,
        tenant_id,
        room_repo=AsyncMock(),
        flat_repo=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_create_room(
    room_service: RoomService,
    room: Room,
    flat: Flat,
    flat_id: uuid.UUID,
) -> None:
    room_service.flat_repo.get_by_id.return_value = flat
    room_service.room_repo.get_by_flat_and_room_number.return_value = None
    room_service.room_repo.create.return_value = room

    result = await room_service.create_room(
        RoomCreate(flat_id=flat_id, room_number="101")
    )

    assert result.room_number == "101"
    room_service.session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_room_rejects_missing_flat(
    room_service: RoomService,
    flat_id: uuid.UUID,
) -> None:
    room_service.flat_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await room_service.create_room(RoomCreate(flat_id=flat_id, room_number="101"))


@pytest.mark.asyncio
async def test_create_room_rejects_duplicate_number(
    room_service: RoomService,
    flat: Flat,
    room: Room,
    flat_id: uuid.UUID,
) -> None:
    room_service.flat_repo.get_by_id.return_value = flat
    room_service.room_repo.get_by_flat_and_room_number.return_value = room

    with pytest.raises(ConflictError):
        await room_service.create_room(RoomCreate(flat_id=flat_id, room_number="101"))


@pytest.mark.asyncio
async def test_list_rooms(
    room_service: RoomService,
    room: Room,
    flat_id: uuid.UUID,
    flat: Flat,
) -> None:
    room_service.flat_repo.get_by_id.return_value = flat
    room_service.room_repo.count.return_value = 1
    room_service.room_repo.list_paginated.return_value = [room]

    result = await room_service.list_rooms(
        RoomListParams(page=1, page_size=20, flat_id=flat_id, search="10")
    )

    assert result.total == 1
    assert result.items[0].room_number == "101"


@pytest.mark.asyncio
async def test_delete_room(
    room_service: RoomService,
    room: Room,
) -> None:
    room_service.room_repo.get_by_id.return_value = room

    await room_service.delete_room(room.id)

    room_service.room_repo.delete.assert_awaited_once_with(room)
    room_service.session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_room(
    room_service: RoomService,
    room: Room,
    flat: Flat,
    flat_id: uuid.UUID,
) -> None:
    room_service.room_repo.get_by_id.return_value = room
    room_service.flat_repo.get_by_id.return_value = flat
    room_service.room_repo.get_by_flat_and_room_number.return_value = None
    room_service.room_repo.update.return_value = room

    await room_service.update_room(
        room.id,
        RoomUpdate(flat_id=flat_id, room_number="102"),
    )

    room_service.session.commit.assert_awaited_once()
