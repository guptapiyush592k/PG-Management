from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.resident import Resident
from app.repositories.resident_repository import ResidentRepository
from app.schemas.common import PaginatedResponse
from app.schemas.resident import (
    ResidentCreate,
    ResidentListParams,
    ResidentResponse,
    ResidentUpdate,
)


class ResidentService:
    def __init__(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        *,
        resident_repo: ResidentRepository | None = None,
    ) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.resident_repo = resident_repo or ResidentRepository(session, tenant_id)

    async def create_resident(self, data: ResidentCreate) -> ResidentResponse:
        await self._ensure_unique_phone(data.phone)

        resident = await self.resident_repo.create(
            name=data.name,
            phone=data.phone,
            email=str(data.email) if data.email else None,
            aadhaar=data.aadhaar,
            joining_date=data.joining_date,
            deposit=data.deposit,
            notes=data.notes,
            is_active=data.is_active,
        )
        await self.session.commit()
        return self._to_response(resident)

    async def list_residents(
        self,
        params: ResidentListParams,
    ) -> PaginatedResponse[ResidentResponse]:
        total = await self.resident_repo.count(
            search=params.search,
            is_active=params.is_active,
        )
        residents = await self.resident_repo.list_paginated(
            offset=params.offset,
            limit=params.page_size,
            search=params.search,
            is_active=params.is_active,
        )
        return PaginatedResponse[ResidentResponse](
            items=[self._to_response(resident) for resident in residents],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_resident(self, resident_id: UUID) -> ResidentResponse:
        resident = await self._get_resident_or_404(resident_id)
        return self._to_response(resident)

    async def update_resident(
        self,
        resident_id: UUID,
        data: ResidentUpdate,
    ) -> ResidentResponse:
        resident = await self._get_resident_or_404(resident_id)
        await self._ensure_unique_phone(data.phone, exclude_id=resident_id)

        updated = await self.resident_repo.update(
            resident,
            name=data.name,
            phone=data.phone,
            email=str(data.email) if data.email else None,
            aadhaar=data.aadhaar,
            joining_date=data.joining_date,
            deposit=data.deposit,
            notes=data.notes,
            is_active=data.is_active,
        )
        await self.session.commit()
        return self._to_response(updated)

    async def delete_resident(self, resident_id: UUID) -> None:
        resident = await self._get_resident_or_404(resident_id)
        await self.resident_repo.delete(resident)
        await self.session.commit()

    async def _get_resident_or_404(self, resident_id: UUID) -> Resident:
        resident = await self.resident_repo.get_by_id(resident_id)
        if resident is None:
            raise NotFoundError("Resident not found")
        return resident

    async def _ensure_unique_phone(
        self,
        phone: str,
        *,
        exclude_id: UUID | None = None,
    ) -> None:
        existing = await self.resident_repo.get_by_phone(phone, exclude_id=exclude_id)
        if existing is not None:
            raise ConflictError("Phone number already registered for this tenant")

    def _to_response(self, resident: Resident) -> ResidentResponse:
        return ResidentResponse(
            id=str(resident.id),
            tenant_id=str(resident.tenant_id),
            name=resident.name,
            phone=resident.phone,
            email=resident.email,
            aadhaar=resident.aadhaar,
            joining_date=resident.joining_date,
            deposit=resident.deposit,
            notes=resident.notes,
            is_active=resident.is_active,
            created_at=resident.created_at,
            updated_at=resident.updated_at,
        )
