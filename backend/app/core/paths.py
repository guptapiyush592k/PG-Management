"""Route classification for tenant authorization."""

import re
from uuid import UUID

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

# Routes that require JWT but not X-Tenant-ID.
JWT_ONLY_PATHS = (
    "/me/context",
    "/auth/switch-tenant",
)

_SIGNED_FILE_CONTENT_PATTERN = re.compile(
    r"^/api/v1/files/(?P<file_id>[0-9a-fA-F-]{36})/content$"
)


def is_public_path(path: str) -> bool:
    return any(
        path == prefix or path.startswith(f"{prefix}/")
        for prefix in PUBLIC_PATH_PREFIXES
    )


def is_jwt_tenant_path(path: str) -> bool:
    return path in JWT_TENANT_PATHS


def is_signed_file_content_path(path: str) -> bool:
    return _SIGNED_FILE_CONTENT_PATTERN.match(path) is not None


def parse_signed_file_content_path(path: str) -> UUID | None:
    match = _SIGNED_FILE_CONTENT_PATTERN.match(path)
    if match is None:
        return None
    return UUID(match.group("file_id"))


def requires_tenant_authorization(path: str) -> bool:
    if is_public_path(path) or is_jwt_tenant_path(path):
        return False
    if is_signed_file_content_path(path):
        return False
    return True
