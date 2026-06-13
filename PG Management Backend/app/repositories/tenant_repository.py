from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Tenant)

    async def get_by_slug(self, slug: str) -> Tenant | None:
        result = await self.session.execute(select(Tenant).where(Tenant.slug == slug))
        return result.scalar_one_or_none()

    async def get_or_create_demo(self, *, slug: str, name: str = "Demo PG") -> Tenant:
        tenant = await self.get_by_slug(slug)
        if tenant is not None:
            return tenant

        tenant = Tenant(name=name, slug=slug, is_active=True)
        return await self.add(tenant)
