import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TenantScopedMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.tenant import Tenant
    from app.models.user import User


class FileStatus(str, enum.Enum):
    PENDING = "pending"
    UPLOADED = "uploaded"


class StoredFile(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "stored_files"
    __table_args__ = (
        Index("ix_stored_files_tenant_created_at", "tenant_id", "created_at"),
        Index("ix_stored_files_tenant_status", "tenant_id", "status"),
    )

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[FileStatus] = mapped_column(
        Enum(FileStatus, name="file_status", native_enum=False),
        default=FileStatus.PENDING,
        nullable=False,
        index=True,
    )
    uploaded_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="stored_files")
    uploaded_by: Mapped["User | None"] = relationship("User", back_populates="uploaded_files")
