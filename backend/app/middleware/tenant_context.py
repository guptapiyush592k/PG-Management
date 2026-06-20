from contextvars import ContextVar
from uuid import UUID

_tenant_id_ctx: ContextVar[UUID | None] = ContextVar("tenant_id", default=None)


def set_current_tenant_id(tenant_id: UUID | str | None) -> None:
    if tenant_id is None:
        _tenant_id_ctx.set(None)
        return
    _tenant_id_ctx.set(tenant_id if isinstance(tenant_id, UUID) else UUID(str(tenant_id)))


def get_current_tenant_id() -> UUID | None:
    return _tenant_id_ctx.get()
