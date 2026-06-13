"""Route classification for tenant authorization."""

PUBLIC_PATH_PREFIXES = (
    "/auth",
    "/api/v1/health",
    "/docs",
    "/redoc",
    "/openapi.json",
)

# Routes that require JWT but resolve tenant from the token (not X-Tenant-ID header).
JWT_TENANT_PATHS = (
    "/me/context",
)


def is_public_path(path: str) -> bool:
    return any(
        path == prefix or path.startswith(f"{prefix}/")
        for prefix in PUBLIC_PATH_PREFIXES
    )


def is_jwt_tenant_path(path: str) -> bool:
    return path in JWT_TENANT_PATHS


def requires_tenant_authorization(path: str) -> bool:
    return not is_public_path(path) and not is_jwt_tenant_path(path)
