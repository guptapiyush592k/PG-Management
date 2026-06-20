from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.bed import Bed
from app.models.tenant_user import TenantUserRole
from app.repositories.bed_repository import BedRepository
from app.repositories.room_repository import RoomRepository
from app.schemas.bed import BedCreate, BedListParams, BedResponse, BedUpdate
from app.schemas.common import PaginatedResponse
from app.services.permissions import require_permission


class BedService:
    def __init__(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        role: TenantUserRole,
        *,
        bed_repo: BedRepository | None = None,
        room_repo: RoomRepository | None = None,
    ) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.role = role
        self.bed_repo = bed_repo or BedRepository(session, tenant_id)
        self.room_repo = room_repo or RoomRepository(session, tenant_id)

    async def create_bed(self, data: BedCreate) -> BedResponse:
        require_permission(self.role, "manage_beds")
        await self._ensure_room_exists(data.room_id)
        await self._ensure_unique_bed_label(data.room_id, data.bed_label)

        bed = await self.bed_repo.create(
            room_id=data.room_id,
            bed_label=data.bed_label,
            rent_amount=data.rent_amount,
            status=data.status,
        )
        await self.session.commit()
        return self._to_response(bed)

    async def list_beds(self, params: BedListParams) -> PaginatedResponse[BedResponse]:
        if params.room_id is not None:
            await self._ensure_room_exists(params.room_id)

        total = await self.bed_repo.count(
            search=params.search,
            room_id=params.room_id,
            status=params.status,
        )
        beds = await self.bed_repo.list_paginated(
            offset=params.offset,
            limit=params.page_size,
            search=params.search,
            room_id=params.room_id,
            status=params.status,
        )
        return PaginatedResponse[BedResponse](
            items=[self._to_response(bed) for bed in beds],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_bed(self, bed_id: UUID) -> BedResponse:
        bed = await self._get_bed_or_404(bed_id)
        return self._to_response(bed)

    async def update_bed(self, bed_id: UUID, data: BedUpdate) -> BedResponse:
        require_permission(self.role, "manage_beds")
        bed = await self._get_bed_or_404(bed_id)
        await self._ensure_room_exists(data.room_id)
        await self._ensure_unique_bed_label(
            data.room_id,
            data.bed_label,
            exclude_id=bed_id,
        )

        updated = await self.bed_repo.update(
            bed,
            room_id=data.room_id,
            bed_label=data.bed_label,
            rent_amount=data.rent_amount,
            status=data.status,
        )
        await self.session.commit()
        return self._to_response(updated)

    async def delete_bed(self, bed_id: UUID) -> None:
        require_permission(self.role, "manage_beds")
        bed = await self._get_bed_or_404(bed_id)
        await self.bed_repo.delete(bed)
        await self.session.commit()

    async def _get_bed_or_404(self, bed_id: UUID) -> Bed:
        bed = await self.bed_repo.get_by_id(bed_id)
        if bed is None:
            raise NotFoundError("Bed not found")
        return bed

    async def _ensure_room_exists(self, room_id: UUID) -> None:
        room = await self.room_repo.get_by_id(room_id)
        if room is None:
            raise NotFoundError("Room not found")

    async def _ensure_unique_bed_label(
        self,
        room_id: UUID,
        bed_label: str,
        *,
        exclude_id: UUID | None = None,
    ) -> None:
        existing = await self.bed_repo.get_by_room_and_bed_label(
            room_id,
            bed_label,
            exclude_id=exclude_id,
        )
        if existing is not None:
            raise ConflictError("Bed label already exists for this room")

    def _to_response(self, bed: Bed) -> BedResponse:
        return BedResponse(
            id=str(bed.id),
            tenant_id=str(bed.tenant_id),
            room_id=str(bed.room_id),
            bed_label=bed.bed_label,
            rent_amount=bed.rent_amount,
            status=bed.status,
            created_at=bed.created_at,
            updated_at=bed.updated_at,
        )
