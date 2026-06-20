from pydantic import BaseModel

from app.models.tenant_user import TenantUserRole


class PermissionsResponse(BaseModel):
    manage_flats: bool
    manage_rooms: bool
    manage_beds: bool
    manage_residents: bool
    manage_payments: bool
    manage_files: bool


class UserContextResponse(BaseModel):
    id: str
    name: str
    email: str


class TenantContextResponse(BaseModel):
    id: str
    name: str
    logo_url: str | None
    primary_color: str
    secondary_color: str
    is_demo: bool
    subscription_status: str


class MeContextResponse(BaseModel):
    user: UserContextResponse
    tenant: TenantContextResponse
    permissions: PermissionsResponse


def resolve_permissions(role: TenantUserRole) -> PermissionsResponse:
    if role in (TenantUserRole.SUPER_ADMIN, TenantUserRole.OWNER):
        return PermissionsResponse(
            manage_flats=True,
            manage_rooms=True,
            manage_beds=True,
            manage_residents=True,
            manage_payments=True,
            manage_files=True,
        )

    return PermissionsResponse(
        manage_flats=False,
        manage_rooms=False,
        manage_beds=True,
        manage_residents=True,
        manage_payments=True,
        manage_files=True,
    )
