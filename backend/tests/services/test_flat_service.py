import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.flat import Flat
from app.models.tenant_user import TenantUserRole
from app.schemas.flat import FlatCreate, FlatListParams, FlatUpdate
from app.services.flat_service import FlatService


@pytest.fixture
def tenant_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def flat(tenant_id: uuid.UUID) -> Flat:
    now = datetime.now(UTC)
    return Flat(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        name="Sunrise PG",
        address="123 Main Street",
        is_active=True,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def flat_service(tenant_id: uuid.UUID) -> FlatService:
    session = AsyncMock()
    session.commit = AsyncMock()
    return FlatService(session, tenant_id, TenantUserRole.OWNER, flat_repo=AsyncMock())


@pytest.mark.asyncio
async def test_create_flat(
    flat_service: FlatService,
    flat: Flat,
    tenant_id: uuid.UUID,
) -> None:
    flat_service.flat_repo.create.return_value = flat

    result = await flat_service.create_flat(
        FlatCreate(name="Sunrise PG", address="123 Main Street")
    )

    assert result.name == "Sunrise PG"
    assert result.tenant_id == str(tenant_id)
    flat_service.session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_flats_returns_paginated_response(
    flat_service: FlatService,
    flat: Flat,
) -> None:
    flat_service.flat_repo.count.return_value = 1
    flat_service.flat_repo.list_paginated.return_value = [flat]

    result = await flat_service.list_flats(FlatListParams(page=1, page_size=20, search="sun"))

    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].name == "Sunrise PG"
    flat_service.flat_repo.list_paginated.assert_awaited_once_with(
        offset=0,
        limit=20,
        search="sun",
        is_active=None,
    )


@pytest.mark.asyncio
async def test_get_flat_not_found(flat_service: FlatService) -> None:
    flat_service.flat_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await flat_service.get_flat(uuid.uuid4())


@pytest.mark.asyncio
async def test_update_flat(
    flat_service: FlatService,
    flat: Flat,
) -> None:
    flat_service.flat_repo.get_by_id.return_value = flat
    flat_service.flat_repo.update.return_value = flat

    result = await flat_service.update_flat(
        flat.id,
        FlatUpdate(name="Updated PG", address="New address", is_active=False),
    )

    assert result.name == "Sunrise PG"
    flat_service.session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_flat_forbidden_for_manager(flat_service: FlatService) -> None:
    manager_service = FlatService(
        flat_service.session,
        flat_service.tenant_id,
        TenantUserRole.MANAGER,
        flat_repo=flat_service.flat_repo,
    )

    with pytest.raises(ForbiddenError):
        await manager_service.create_flat(
            FlatCreate(name="Sunrise PG", address="123 Main Street")
        )


@pytest.mark.asyncio
async def test_delete_flat(
    flat_service: FlatService,
    flat: Flat,
) -> None:
    flat_service.flat_repo.get_by_id.return_value = flat

    await flat_service.delete_flat(flat.id)

    flat_service.flat_repo.delete.assert_awaited_once_with(flat)
    flat_service.session.commit.assert_awaited_once()
