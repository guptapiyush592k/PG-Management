from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.rent_payment import PaymentStatus, RentPayment
from app.models.tenant_user import TenantUserRole
from app.repositories.booking_repository import BookingRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.resident_repository import ResidentRepository
from app.schemas.common import PaginatedResponse
from app.schemas.payment import (
    PaymentCreate,
    PaymentListParams,
    PaymentResponse,
    PaymentSummaryResponse,
    PaymentUpdate,
)
from app.services.permissions import require_permission


class PaymentService:
    def __init__(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        role: TenantUserRole,
        *,
        payment_repo: PaymentRepository | None = None,
        resident_repo: ResidentRepository | None = None,
        booking_repo: BookingRepository | None = None,
    ) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.role = role
        self.payment_repo = payment_repo or PaymentRepository(session, tenant_id)
        self.resident_repo = resident_repo or ResidentRepository(session, tenant_id)
        self.booking_repo = booking_repo or BookingRepository(session, tenant_id)

    async def create_payment(self, data: PaymentCreate) -> PaymentResponse:
        require_permission(self.role, "manage_payments")
        await self._ensure_resident_exists(data.resident_id)
        await self._ensure_booking_valid(data.booking_id, data.resident_id)
        paid_date = self._resolve_paid_date(data.status, data.paid_date)

        payment = await self.payment_repo.create(
            resident_id=data.resident_id,
            booking_id=data.booking_id,
            amount=data.amount,
            due_date=data.due_date,
            paid_date=paid_date,
            status=data.status,
            payment_mode=data.payment_mode,
            notes=data.notes,
        )
        await self.session.commit()
        return self._to_response(payment)

    async def get_payment(self, payment_id: UUID) -> PaymentResponse:
        await self._sync_overdue_status()
        payment = await self._get_payment_or_404(payment_id)
        return self._to_response(payment)

    async def list_payments(
        self,
        params: PaymentListParams,
    ) -> PaginatedResponse[PaymentResponse]:
        await self._sync_overdue_status()
        if params.resident_id is not None:
            await self._ensure_resident_exists(params.resident_id)

        total = await self.payment_repo.count(
            search=params.search,
            resident_id=params.resident_id,
            status=params.status,
        )
        payments = await self.payment_repo.list_paginated(
            offset=params.offset,
            limit=params.page_size,
            search=params.search,
            resident_id=params.resident_id,
            status=params.status,
        )
        return PaginatedResponse[PaymentResponse](
            items=[self._to_response(payment) for payment in payments],
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def update_payment(self, payment_id: UUID, data: PaymentUpdate) -> PaymentResponse:
        require_permission(self.role, "manage_payments")
        payment = await self._get_payment_or_404(payment_id)

        target_resident_id = (
            data.resident_id if "resident_id" in data.model_fields_set else payment.resident_id
        )
        target_booking_id = (
            data.booking_id if "booking_id" in data.model_fields_set else payment.booking_id
        )
        target_status = data.status if "status" in data.model_fields_set else payment.status
        target_paid_date = (
            data.paid_date if "paid_date" in data.model_fields_set else payment.paid_date
        )

        await self._ensure_resident_exists(target_resident_id)
        await self._ensure_booking_valid(target_booking_id, target_resident_id)
        paid_date = self._resolve_paid_date(target_status, target_paid_date)

        if "resident_id" in data.model_fields_set and data.resident_id is not None:
            payment.resident_id = data.resident_id
        if "booking_id" in data.model_fields_set:
            payment.booking_id = data.booking_id
        if "amount" in data.model_fields_set and data.amount is not None:
            payment.amount = data.amount
        if "due_date" in data.model_fields_set and data.due_date is not None:
            payment.due_date = data.due_date
        payment.paid_date = paid_date
        if "status" in data.model_fields_set and data.status is not None:
            payment.status = data.status
        if "payment_mode" in data.model_fields_set:
            payment.payment_mode = data.payment_mode.strip() if data.payment_mode else None
        if "notes" in data.model_fields_set:
            payment.notes = data.notes.strip() if data.notes else None

        await self.session.flush()
        await self.session.refresh(payment)
        await self.session.commit()
        return self._to_response(payment)

    async def get_summary(self) -> PaymentSummaryResponse:
        await self._sync_overdue_status()
        amounts, counts = await self.payment_repo.get_summary()
        return PaymentSummaryResponse(
            total_collected=amounts[PaymentStatus.PAID],
            pending_amount=amounts[PaymentStatus.PENDING] + amounts[PaymentStatus.PARTIAL],
            overdue_amount=amounts[PaymentStatus.OVERDUE],
            counts=counts,
        )

    async def _sync_overdue_status(self) -> None:
        await self.payment_repo.mark_overdue_before(date.today())
        await self.session.commit()

    async def _get_payment_or_404(self, payment_id: UUID) -> RentPayment:
        payment = await self.payment_repo.get_by_id(payment_id)
        if payment is None:
            raise NotFoundError("Payment not found")
        return payment

    async def _ensure_resident_exists(self, resident_id: UUID) -> None:
        resident = await self.resident_repo.get_by_id(resident_id)
        if resident is None:
            raise NotFoundError("Resident not found")

    async def _ensure_booking_valid(
        self,
        booking_id: UUID | None,
        resident_id: UUID,
    ) -> None:
        if booking_id is None:
            return

        booking = await self.booking_repo.get_by_id(booking_id)
        if booking is None:
            raise NotFoundError("Booking not found")
        if booking.resident_id != resident_id:
            raise ValidationError("Booking does not belong to this resident")

    def _resolve_paid_date(self, status: PaymentStatus, paid_date: date | None) -> date | None:
        if status == PaymentStatus.PAID:
            return paid_date or date.today()
        if status in {PaymentStatus.PENDING, PaymentStatus.OVERDUE}:
            return None
        return paid_date

    def _to_response(self, payment: RentPayment) -> PaymentResponse:
        return PaymentResponse(
            id=str(payment.id),
            tenant_id=str(payment.tenant_id),
            resident_id=str(payment.resident_id),
            booking_id=str(payment.booking_id) if payment.booking_id else None,
            amount=payment.amount,
            due_date=payment.due_date,
            paid_date=payment.paid_date,
            status=payment.status,
            payment_mode=payment.payment_mode,
            notes=payment.notes,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )
