from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.flat import Flat
from app.repositories.base import BaseRepository


class FlatRepository(BaseRepository[Flat]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Flat, tenant_id=tenant_id)

    def _base_select(self):
        return select(Flat)

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
                    Flat.name.ilike(pattern),
                    Flat.address.ilike(pattern),
                )
            )
        if is_active is not None:
            stmt = stmt.where(Flat.is_active == is_active)
        return stmt

    async def count(
        self,
        *,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Flat)
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
    ) -> list[Flat]:
        stmt = self._apply_filters(self._base_select(), search=search, is_active=is_active)
        stmt = stmt.order_by(Flat.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        *,
        name: str,
        address: str,
        is_active: bool = True,
    ) -> Flat:
        flat = Flat(
            tenant_id=self.tenant_id,
            name=name.strip(),
            address=address.strip(),
            is_active=is_active,
        )
        return await self.add(flat)

    async def update(
        self,
        flat: Flat,
        *,
        name: str,
        address: str,
        is_active: bool,
    ) -> Flat:
        flat.name = name.strip()
        flat.address = address.strip()
        flat.is_active = is_active
        await self.session.flush()
        await self.session.refresh(flat)
        return flat
