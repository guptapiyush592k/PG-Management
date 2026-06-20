import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import ConflictError, NotFoundError
from app.models.resident import Resident
from app.schemas.resident import ResidentCreate, ResidentListParams, ResidentUpdate
from app.services.resident_service import ResidentService


@pytest.fixture
def tenant_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def resident(tenant_id: uuid.UUID) -> Resident:
    now = datetime.now(UTC)
    return Resident(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        name="Rahul Sharma",
        phone="9876543210",
        email="rahul@example.com",
        aadhaar="123456789012",
        joining_date=date(2025, 1, 15),
        deposit=Decimal("10000.00"),
        notes="Prefers ground floor",
        is_active=True,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def resident_service(tenant_id: uuid.UUID) -> ResidentService:
    session = AsyncMock()
    session.commit = AsyncMock()
    return ResidentService(session, tenant_id, resident_repo=AsyncMock())


@pytest.mark.asyncio
async def test_create_resident(
    resident_service: ResidentService,
    resident: Resident,
) -> None:
    resident_service.resident_repo.get_by_phone.return_value = None
    resident_service.resident_repo.create.return_value = resident

    result = await resident_service.create_resident(
        ResidentCreate(
            name="Rahul Sharma",
            phone="9876543210",
            email="rahul@example.com",
            aadhaar="123456789012",
            joining_date=date(2025, 1, 15),
            deposit=Decimal("10000.00"),
            notes="Prefers ground floor",
        )
    )

    assert result.name == "Rahul Sharma"
    resident_service.session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_resident_rejects_duplicate_phone(
    resident_service: ResidentService,
    resident: Resident,
) -> None:
    resident_service.resident_repo.get_by_phone.return_value = resident

    with pytest.raises(ConflictError):
        await resident_service.create_resident(
            ResidentCreate(
                name="Another Person",
                phone="9876543210",
                joining_date=date(2025, 1, 15),
            )
        )


@pytest.mark.asyncio
async def test_list_residents(
    resident_service: ResidentService,
    resident: Resident,
) -> None:
    resident_service.resident_repo.count.return_value = 1
    resident_service.resident_repo.list_paginated.return_value = [resident]

    result = await resident_service.list_residents(
        ResidentListParams(page=1, page_size=20, search="Rahul", is_active=True)
    )

    assert result.total == 1
    assert result.items[0].phone == "9876543210"


@pytest.mark.asyncio
async def test_get_resident_not_found(
    resident_service: ResidentService,
) -> None:
    resident_service.resident_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await resident_service.get_resident(uuid.uuid4())


@pytest.mark.asyncio
async def test_delete_resident(
    resident_service: ResidentService,
    resident: Resident,
) -> None:
    resident_service.resident_repo.get_by_id.return_value = resident

    await resident_service.delete_resident(resident.id)

    resident_service.resident_repo.delete.assert_awaited_once_with(resident)
    resident_service.session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_resident(
    resident_service: ResidentService,
    resident: Resident,
) -> None:
    resident_service.resident_repo.get_by_id.return_value = resident
    resident_service.resident_repo.get_by_phone.return_value = None
    resident_service.resident_repo.update.return_value = resident

    await resident_service.update_resident(
        resident.id,
        ResidentUpdate(
            name="Rahul S.",
            phone="9876543210",
            email="rahul.new@example.com",
            aadhaar="123456789012",
            joining_date=date(2025, 1, 15),
            deposit=Decimal("15000.00"),
            notes=None,
            is_active=False,
        ),
    )

    resident_service.session.commit.assert_awaited_once()
