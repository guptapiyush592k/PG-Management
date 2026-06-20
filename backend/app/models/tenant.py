import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.flat import Flat
    from app.models.rent_payment import RentPayment
    from app.models.resident import Resident
    from app.models.tenant_user import TenantUser


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    TRIAL = "trial"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Tenant(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """PG business / organization account."""

    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    primary_color: Mapped[str] = mapped_column(String(7), default="#2563EB", nullable=False)
    secondary_color: Mapped[str] = mapped_column(String(7), default="#1E40AF", nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    subscription_status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, name="subscription_status", native_enum=False),
        default=SubscriptionStatus.TRIAL,
        nullable=False,
    )

    members: Mapped[list["TenantUser"]] = relationship(
        "TenantUser",
        back_populates="tenant",
        cascade="all, delete-orphan",
    )
    flats: Mapped[list["Flat"]] = relationship(
        "Flat",
        back_populates="tenant",
        cascade="all, delete-orphan",
    )
    residents: Mapped[list["Resident"]] = relationship(
        "Resident",
        back_populates="tenant",
        cascade="all, delete-orphan",
    )
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="tenant",
        cascade="all, delete-orphan",
    )
    rent_payments: Mapped[list["RentPayment"]] = relationship(
        "RentPayment",
        back_populates="tenant",
        cascade="all, delete-orphan",
    )
