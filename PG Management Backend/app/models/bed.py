import enum
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.room import Room
    from app.models.tenant import Tenant


class BedStatus(str, enum.Enum):
    VACANT = "vacant"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"


class Bed(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "beds"
    __table_args__ = (
        UniqueConstraint("room_id", "bed_label", name="uq_beds_room_bed_label"),
    )

    room_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    bed_label: Mapped[str] = mapped_column(String(50), nullable=False)
    rent_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[BedStatus] = mapped_column(
        Enum(BedStatus, name="bed_status", native_enum=False),
        default=BedStatus.VACANT,
        nullable=False,
        index=True,
    )

    tenant: Mapped["Tenant"] = relationship("Tenant")
    room: Mapped["Room"] = relationship("Room", back_populates="beds")
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="bed",
        cascade="all, delete-orphan",
    )
