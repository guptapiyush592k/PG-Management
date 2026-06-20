from datetime import date
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rent_payment import PaymentStatus, RentPayment
from app.models.resident import Resident
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[RentPayment]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, RentPayment, tenant_id=tenant_id)

    def _apply_filters(
        self,
        stmt,
        *,
        search: str | None = None,
        resident_id: UUID | None = None,
        status: PaymentStatus | None = None,
    ):
        stmt = self._apply_tenant_filter(stmt)
        if search or resident_id is not None:
            stmt = stmt.join(Resident, RentPayment.resident_id == Resident.id)
        if search:
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Resident.name.ilike(pattern),
                    Resident.phone.ilike(pattern),
                )
            )
        if resident_id is not None:
            stmt = stmt.where(RentPayment.resident_id == resident_id)
        if status is not None:
            stmt = stmt.where(RentPayment.status == status)
        return stmt

    async def count(
        self,
        *,
        search: str | None = None,
        resident_id: UUID | None = None,
        status: PaymentStatus | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(RentPayment)
        stmt = self._apply_filters(stmt, search=search, resident_id=resident_id, status=status)
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        resident_id: UUID | None = None,
        status: PaymentStatus | None = None,
    ) -> list[RentPayment]:
        stmt = self._apply_filters(
            select(RentPayment),
            search=search,
            resident_id=resident_id,
            status=status,
        )
        stmt = (
            stmt.order_by(RentPayment.due_date.desc(), RentPayment.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        *,
        resident_id: UUID,
        booking_id: UUID | None,
        amount: Decimal,
        due_date: date,
        paid_date: date | None,
        status: PaymentStatus,
        payment_mode: str | None,
        notes: str | None,
    ) -> RentPayment:
        payment = RentPayment(
            tenant_id=self.tenant_id,
            resident_id=resident_id,
            booking_id=booking_id,
            amount=amount,
            due_date=due_date,
            paid_date=paid_date,
            status=status,
            payment_mode=payment_mode.strip() if payment_mode else None,
            notes=notes.strip() if notes else None,
        )
        return await self.add(payment)

    async def update(
        self,
        payment: RentPayment,
        *,
        resident_id: UUID,
        booking_id: UUID | None,
        amount: Decimal,
        due_date: date,
        paid_date: date | None,
        status: PaymentStatus,
        payment_mode: str | None,
        notes: str | None,
    ) -> RentPayment:
        payment.resident_id = resident_id
        payment.booking_id = booking_id
        payment.amount = amount
        payment.due_date = due_date
        payment.paid_date = paid_date
        payment.status = status
        payment.payment_mode = payment_mode.strip() if payment_mode else None
        payment.notes = notes.strip() if notes else None
        await self.session.flush()
        await self.session.refresh(payment)
        return payment

    async def get_summary(self) -> tuple[dict[PaymentStatus, Decimal], dict[PaymentStatus, int]]:
        stmt = (
            select(
                RentPayment.status,
                func.coalesce(func.sum(RentPayment.amount), 0),
                func.count(),
            )
            .select_from(RentPayment)
            .group_by(RentPayment.status)
        )
        stmt = self._apply_tenant_filter(stmt)
        result = await self.session.execute(stmt)

        amounts: dict[PaymentStatus, Decimal] = {status: Decimal("0.00") for status in PaymentStatus}
        counts: dict[PaymentStatus, int] = {status: 0 for status in PaymentStatus}
        for status, amount, count in result.all():
            amounts[status] = Decimal(str(amount))
            counts[status] = int(count)
        return amounts, counts

    async def mark_overdue_before(self, as_of: date) -> None:
        stmt = (
            update(RentPayment)
            .where(
                RentPayment.tenant_id == self.tenant_id,
                RentPayment.status == PaymentStatus.PENDING,
                RentPayment.due_date < as_of,
            )
            .values(status=PaymentStatus.OVERDUE)
        )
        await self.session.execute(stmt)
        await self.session.flush()
