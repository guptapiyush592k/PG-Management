from fastapi import APIRouter

from app.api.deps import CurrentTenant, CurrentTenantId, CurrentUser, CurrentUserId

router = APIRouter(tags=["examples"])


@router.get("/tenant-scope")
async def protected_tenant_scope_example(
    user: CurrentUser,
    tenant: CurrentTenant,
    user_id: CurrentUserId,
    tenant_id: CurrentTenantId,
) -> dict:
    """Example protected route requiring Authorization + X-Tenant-ID."""
    return {
        "message": "Authorized for tenant-scoped access",
        "user_id": str(user_id),
        "user_email": user.email,
        "tenant_id": str(tenant_id),
        "tenant_name": tenant.name,
    }
