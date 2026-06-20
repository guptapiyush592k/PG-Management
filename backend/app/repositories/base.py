from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base, TenantScopedMixin

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, session: AsyncSession, model: type[ModelT], tenant_id: UUID | None = None):
        self.session = session
        self.model = model
        self.tenant_id = tenant_id

    def _apply_tenant_filter(self, stmt: Select[tuple[ModelT]]) -> Select[tuple[ModelT]]:
        if self.tenant_id is not None and issubclass(self.model, TenantScopedMixin):
            stmt = stmt.where(self.model.tenant_id == self.tenant_id)
        return stmt

    async def get_by_id(self, record_id: UUID) -> ModelT | None:
        stmt = select(self.model).where(self.model.id == record_id)
        stmt = self._apply_tenant_filter(stmt)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[ModelT]:
        stmt = select(self.model)
        stmt = self._apply_tenant_filter(stmt)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self.session.delete(instance)
        await self.session.flush()
