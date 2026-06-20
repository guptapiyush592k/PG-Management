from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.flat import Flat
from app.models.tenant_user import TenantUserRole
from app.repositories.flat_repository import FlatRepository
from app.repositories.room_repository import RoomRepository
from app.schemas.common import PaginatedResponse
from app.schemas.flat import FlatCreate, FlatListParams, FlatResponse, FlatUpdate
from app.services.permissions import require_permission


class FlatService:
    def __init__(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        role: TenantUserRole,
        *,
        flat_repo: FlatRepository | None = None,
        room_repo: RoomRepository | None = None,
    ) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.role = role
        self.flat_repo = flat_repo or FlatRepository(session, tenant_id)
        self.room_repo = room_repo or RoomRepository(session, tenant_id)

    async def create_flat(self, data: FlatCreate) -> FlatResponse:
        require_permission(self.role, "manage_flats")
        flat = await self.flat_repo.create(
            name=data.name,
            address=data.address,
            is_active=data.is_active,
        )
        await self.session.commit()
        return self._to_response(flat)

    async def list_flats(self, params: FlatListParams) -> PaginatedResponse[FlatResponse]:
        total = await self.flat_repo.count(
            search=params.search,
            is_active=params.is_active,
        )
        flats = await self.flat_repo.list_paginated(
            offset=params.offset,
            limit=params.page_size,
            search=params.search,
            is_active=params.is_active,
        )
        return PaginatedResponse[FlatResponse](
            items=[self._to_response(flat) for flat in flats],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_flat(self, flat_id: UUID) -> FlatResponse:
        flat = await self._get_flat_or_404(flat_id)
        return self._to_response(flat)

    async def update_flat(self, flat_id: UUID, data: FlatUpdate) -> FlatResponse:
        require_permission(self.role, "manage_flats")
        flat = await self._get_flat_or_404(flat_id)

        if "name" in data.model_fields_set and data.name is not None:
            flat.name = data.name.strip()
        if "address" in data.model_fields_set and data.address is not None:
            flat.address = data.address.strip()
        if "is_active" in data.model_fields_set and data.is_active is not None:
            flat.is_active = data.is_active

        await self.session.flush()
        await self.session.refresh(flat)
        await self.session.commit()
        return self._to_response(flat)

    async def delete_flat(self, flat_id: UUID) -> None:
        require_permission(self.role, "manage_flats")
        flat = await self._get_flat_or_404(flat_id)
        room_count = await self.room_repo.count(flat_id=flat_id)
        if room_count > 0:
            raise ValidationError("Cannot delete a flat that still has rooms")
        await self.flat_repo.delete(flat)
        await self.session.commit()

    async def _get_flat_or_404(self, flat_id: UUID) -> Flat:
        flat = await self.flat_repo.get_by_id(flat_id)
        if flat is None:
            raise NotFoundError("Flat not found")
        return flat

    def _to_response(self, flat: Flat) -> FlatResponse:
        return FlatResponse(
            id=str(flat.id),
            tenant_id=str(flat.tenant_id),
            name=flat.name,
            address=flat.address,
            is_active=flat.is_active,
            created_at=flat.created_at,
            updated_at=flat.updated_at,
        )
