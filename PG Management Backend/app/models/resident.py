from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.rent_payment import RentPayment
    from app.models.tenant import Tenant


class Resident(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    """PG resident (occupant)."""

    __tablename__ = "residents"
    __table_args__ = (
        UniqueConstraint("tenant_id", "phone", name="uq_residents_tenant_phone"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    aadhaar: Mapped[str | None] = mapped_column(String(12), nullable=True, index=True)
    joining_date: Mapped[date] = mapped_column(Date, nullable=False)
    deposit: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="residents")
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="resident",
        cascade="all, delete-orphan",
    )
    rent_payments: Mapped[list["RentPayment"]] = relationship(
        "RentPayment",
        back_populates="resident",
        cascade="all, delete-orphan",
    )
