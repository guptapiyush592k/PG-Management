import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, event, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, declared_attr, mapped_column

from app.middleware.tenant_context import get_current_tenant_id


class Base(DeclarativeBase):
    pass


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class TenantScopedMixin:
    @declared_attr
    def tenant_id(cls) -> Mapped[uuid.UUID]:  # noqa: N805
        return mapped_column(
            UUID(as_uuid=True),
            ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )


@event.listens_for(Session, "before_flush")
def auto_set_tenant_id(session, flush_context, instances) -> None:
    tenant_id = get_current_tenant_id()
    if tenant_id is None:
        return

    for obj in session.new:
        if isinstance(obj, TenantScopedMixin) and getattr(obj, "tenant_id", None) is None:
            obj.tenant_id = tenant_id
