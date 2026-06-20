import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import NotFoundError, ValidationError
from app.models.rent_payment import PaymentStatus, RentPayment
from app.models.tenant_user import TenantUserRole
from app.schemas.payment import PaymentCreate, PaymentListParams, PaymentUpdate
from app.services.payment_service import PaymentService


@pytest.fixture
def tenant_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def payment(tenant_id: uuid.UUID) -> RentPayment:
    now = datetime.now(UTC)
    return RentPayment(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        resident_id=uuid.uuid4(),
        booking_id=None,
        amount=Decimal("9500.00"),
        due_date=date(2026, 6, 1),
        paid_date=None,
        status=PaymentStatus.PENDING,
        payment_mode=None,
        notes=None,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def payment_service(tenant_id: uuid.UUID) -> PaymentService:
    session = AsyncMock()
    session.commit = AsyncMock()
    return PaymentService(
        session,
        tenant_id,
        TenantUserRole.OWNER,
        payment_repo=AsyncMock(),
        resident_repo=AsyncMock(),
        booking_repo=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_create_payment(
    payment_service: PaymentService,
    payment: RentPayment,
) -> None:
    payment_service.resident_repo.get_by_id.return_value = object()
    payment_service.payment_repo.create.return_value = payment

    result = await payment_service.create_payment(
        PaymentCreate(
            resident_id=payment.resident_id,
            amount=Decimal("9500.00"),
            due_date=date(2026, 6, 1),
        )
    )

    assert result.amount == Decimal("9500.00")
    assert result.status == PaymentStatus.PENDING
    payment_service.session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_payment_rejects_missing_resident(
    payment_service: PaymentService,
    payment: RentPayment,
) -> None:
    payment_service.resident_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await payment_service.create_payment(
            PaymentCreate(
                resident_id=payment.resident_id,
                amount=Decimal("9500.00"),
                due_date=date(2026, 6, 1),
            )
        )


@pytest.mark.asyncio
async def test_create_payment_rejects_booking_resident_mismatch(
    payment_service: PaymentService,
    payment: RentPayment,
) -> None:
    booking_id = uuid.uuid4()
    payment_service.resident_repo.get_by_id.return_value = object()
    payment_service.booking_repo.get_by_id.return_value = type(
        "Booking",
        (),
        {"resident_id": uuid.uuid4()},
    )()

    with pytest.raises(ValidationError):
        await payment_service.create_payment(
            PaymentCreate(
                resident_id=payment.resident_id,
                booking_id=booking_id,
                amount=Decimal("9500.00"),
                due_date=date(2026, 6, 1),
            )
        )


@pytest.mark.asyncio
async def test_create_payment_sets_paid_date_for_paid_status(
    payment_service: PaymentService,
    payment: RentPayment,
) -> None:
    payment.status = PaymentStatus.PAID
    payment.paid_date = date.today()
    payment_service.resident_repo.get_by_id.return_value = object()
    payment_service.payment_repo.create.return_value = payment

    result = await payment_service.create_payment(
        PaymentCreate(
            resident_id=payment.resident_id,
            amount=Decimal("9500.00"),
            due_date=date(2026, 6, 1),
            status=PaymentStatus.PAID,
        )
    )

    assert result.paid_date == date.today()


@pytest.mark.asyncio
async def test_list_payments(
    payment_service: PaymentService,
    payment: RentPayment,
) -> None:
    payment_service.payment_repo.count.return_value = 1
    payment_service.payment_repo.list_paginated.return_value = [payment]

    result = await payment_service.list_payments(
        PaymentListParams(page=1, page_size=20, status=PaymentStatus.PENDING)
    )

    assert result.total == 1
    assert result.items[0].amount == Decimal("9500.00")


@pytest.mark.asyncio
async def test_update_payment(
    payment_service: PaymentService,
    payment: RentPayment,
) -> None:
    payment_service.payment_repo.get_by_id.return_value = payment
    payment_service.resident_repo.get_by_id.return_value = object()
    payment.status = PaymentStatus.PAID
    payment.paid_date = date(2026, 5, 30)
    payment_service.payment_repo.update.return_value = payment

    result = await payment_service.update_payment(
        payment.id,
        PaymentUpdate(
            resident_id=payment.resident_id,
            amount=Decimal("9500.00"),
            due_date=date(2026, 6, 1),
            paid_date=date(2026, 5, 30),
            status=PaymentStatus.PAID,
            payment_mode="UPI",
        ),
    )

    assert result.status == PaymentStatus.PAID
    payment_service.session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_payment_not_found(
    payment_service: PaymentService,
) -> None:
    payment_service.payment_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await payment_service.update_payment(
            uuid.uuid4(),
            PaymentUpdate(
                resident_id=uuid.uuid4(),
                amount=Decimal("9500.00"),
                due_date=date(2026, 6, 1),
                status=PaymentStatus.PENDING,
            ),
        )


@pytest.mark.asyncio
async def test_get_summary(
    payment_service: PaymentService,
) -> None:
    payment_service.payment_repo.get_summary.return_value = (
        {
            PaymentStatus.PAID: Decimal("19000.00"),
            PaymentStatus.PENDING: Decimal("9500.00"),
            PaymentStatus.PARTIAL: Decimal("5000.00"),
            PaymentStatus.OVERDUE: Decimal("3000.00"),
        },
        {
            PaymentStatus.PAID: 2,
            PaymentStatus.PENDING: 1,
            PaymentStatus.PARTIAL: 1,
            PaymentStatus.OVERDUE: 1,
        },
    )

    result = await payment_service.get_summary()

    assert result.total_collected == Decimal("19000.00")
    assert result.pending_amount == Decimal("14500.00")
    assert result.overdue_amount == Decimal("3000.00")
    assert result.counts[PaymentStatus.PAID] == 2
