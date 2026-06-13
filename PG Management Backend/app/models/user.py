from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.tenant_user import TenantUser


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Platform user who can belong to one or more PG businesses."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tenant_memberships: Mapped[list["TenantUser"]] = relationship(
        "TenantUser",
        back_populates="user",
        cascade="all, delete-orphan",
    )
