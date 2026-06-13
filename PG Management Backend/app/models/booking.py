import enum
import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.bed import Bed
    from app.models.rent_payment import RentPayment
    from app.models.resident import Resident
    from app.models.tenant import Tenant


class BookingStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Booking(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    """Bed assignment for a resident."""

    __tablename__ = "bookings"
    __table_args__ = (
        Index("ix_bookings_tenant_status", "tenant_id", "status"),
        Index("ix_bookings_bed_status", "bed_id", "status"),
    )

    resident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("residents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    bed_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("beds.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, name="booking_status", native_enum=False),
        default=BookingStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="bookings")
    resident: Mapped["Resident"] = relationship("Resident", back_populates="bookings")
    bed: Mapped["Bed"] = relationship("Bed", back_populates="bookings")
    rent_payments: Mapped[list["RentPayment"]] = relationship(
        "RentPayment",
        back_populates="booking",
    )
