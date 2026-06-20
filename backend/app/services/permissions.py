from app.core.exceptions import ForbiddenError
from app.models.tenant_user import TenantUserRole
from app.schemas.tenant_context import resolve_permissions


PERMISSION_LABELS = {
    "manage_flats": "manage flats",
    "manage_rooms": "manage rooms",
    "manage_beds": "manage beds",
    "manage_residents": "manage residents",
    "manage_payments": "manage payments",
    "manage_files": "manage files",
}


def require_permission(role: TenantUserRole | None, permission: str) -> None:
    if role is None:
        raise ForbiddenError("Authentication is required")
    permissions = resolve_permissions(role)
    if not getattr(permissions, permission, False):
        label = PERMISSION_LABELS.get(permission, permission.replace("_", " "))
        raise ForbiddenError(f"Insufficient permissions to {label}")
