from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.rent_payment import PaymentStatus


class PaymentBase(BaseModel):
    resident_id: UUID
    booking_id: UUID | None = None
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    due_date: date
    paid_date: date | None = None
    status: PaymentStatus = PaymentStatus.PENDING
    payment_mode: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=5000)


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    resident_id: UUID | None = None
    booking_id: UUID | None = None
    amount: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    due_date: date | None = None
    paid_date: date | None = None
    status: PaymentStatus | None = None
    payment_mode: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=5000)

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "PaymentUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    resident_id: str
    booking_id: str | None
    amount: Decimal
    due_date: date
    paid_date: date | None
    status: PaymentStatus
    payment_mode: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class PaymentListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    search: str | None = Field(default=None, max_length=255)
    resident_id: UUID | None = None
    status: PaymentStatus | None = None

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaymentSummaryResponse(BaseModel):
    total_collected: Decimal
    pending_amount: Decimal
    overdue_amount: Decimal
    counts: dict[PaymentStatus, int]
