from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resident import Resident
from app.repositories.base import BaseRepository


class ResidentRepository(BaseRepository[Resident]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Resident, tenant_id=tenant_id)

    def _apply_filters(
        self,
        stmt,
        *,
        search: str | None = None,
        is_active: bool | None = None,
    ):
        stmt = self._apply_tenant_filter(stmt)
        if search:
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Resident.name.ilike(pattern),
                    Resident.phone.ilike(pattern),
                    Resident.email.ilike(pattern),
                )
            )
        if is_active is not None:
            stmt = stmt.where(Resident.is_active == is_active)
        return stmt

    async def count(
        self,
        *,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Resident)
        stmt = self._apply_filters(stmt, search=search, is_active=is_active)
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> list[Resident]:
        stmt = self._apply_filters(select(Resident), search=search, is_active=is_active)
        stmt = stmt.order_by(Resident.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_phone(
        self,
        phone: str,
        *,
        exclude_id: UUID | None = None,
    ) -> Resident | None:
        stmt = select(Resident).where(Resident.phone == phone.strip())
        stmt = self._apply_tenant_filter(stmt)
        if exclude_id is not None:
            stmt = stmt.where(Resident.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        name: str,
        phone: str,
        email: str | None,
        aadhaar: str | None,
        joining_date: date,
        deposit: Decimal,
        notes: str | None,
        is_active: bool,
    ) -> Resident:
        resident = Resident(
            tenant_id=self.tenant_id,
            name=name.strip(),
            phone=phone.strip(),
            email=email,
            aadhaar=aadhaar,
            joining_date=joining_date,
            deposit=deposit,
            notes=notes.strip() if notes else None,
            is_active=is_active,
        )
        return await self.add(resident)

    async def update(
        self,
        resident: Resident,
        *,
        name: str,
        phone: str,
        email: str | None,
        aadhaar: str | None,
        joining_date: date,
        deposit: Decimal,
        notes: str | None,
        is_active: bool,
    ) -> Resident:
        resident.name = name.strip()
        resident.phone = phone.strip()
        resident.email = email
        resident.aadhaar = aadhaar
        resident.joining_date = joining_date
        resident.deposit = deposit
        resident.notes = notes.strip() if notes else None
        resident.is_active = is_active
        await self.session.flush()
        await self.session.refresh(resident)
        return resident
