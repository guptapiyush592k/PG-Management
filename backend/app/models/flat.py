from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.room import Room
    from app.models.tenant import Tenant


class Flat(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    """PG property / building."""

    __tablename__ = "flats"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="flats")
    rooms: Mapped[list["Room"]] = relationship(
        "Room",
        back_populates="flat",
        cascade="all, delete-orphan",
    )
