import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.bed import Bed
    from app.models.flat import Flat
    from app.models.tenant import Tenant


class Room(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "rooms"
    __table_args__ = (
        UniqueConstraint("flat_id", "room_number", name="uq_rooms_flat_room_number"),
    )

    flat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("flats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    room_number: Mapped[str] = mapped_column(String(50), nullable=False)

    tenant: Mapped["Tenant"] = relationship("Tenant")
    flat: Mapped["Flat"] = relationship("Flat", back_populates="rooms")
    beds: Mapped[list["Bed"]] = relationship(
        "Bed",
        back_populates="room",
        cascade="all, delete-orphan",
    )
