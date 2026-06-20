from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.repositories.base import BaseRepository


class BookingRepository(BaseRepository[Booking]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Booking, tenant_id=tenant_id)
