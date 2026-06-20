import logging

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.exceptions import AppException, ForbiddenError, UnauthorizedError
from app.core.paths import requires_tenant_authorization
from app.db.session import get_session_factory
from app.middleware.tenant_context import set_current_tenant_id
from app.services.tenant_authorization_service import TenantAuthorizationService

logger = logging.getLogger(__name__)

TENANT_ID_HEADER = "X-Tenant-ID"


def _error_response(exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code},
    )


class TenantAuthorizationMiddleware(BaseHTTPMiddleware):
    """
    Enforces multi-tenant authorization on protected routes:
    1. Validate JWT access token
    2. Extract user_id from token
    3. Require tenant_id from X-Tenant-ID header
    4. Verify membership via tenant_users
    5. Store user and tenant on request.state
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if not requires_tenant_authorization(request.url.path):
            return await call_next(request)

        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.lower().startswith("bearer "):
            return _error_response(UnauthorizedError("Missing authentication credentials"))

        tenant_id_header = request.headers.get(TENANT_ID_HEADER)
        if not tenant_id_header:
            return _error_response(
                ForbiddenError("X-Tenant-ID header is required")
            )

        access_token = authorization.split(" ", 1)[1].strip()
        if not access_token:
            return _error_response(UnauthorizedError("Missing authentication credentials"))

        session_factory = get_session_factory()
        try:
            async with session_factory() as session:
                service = TenantAuthorizationService(session)
                context = await service.authorize(
                    access_token=access_token,
                    tenant_id_header=tenant_id_header,
                )
                request.state.db_session = session
                request.state.user = context.user
                request.state.tenant = context.tenant
                request.state.tenant_membership = context.membership
                request.state.user_id = context.user_id
                request.state.tenant_id = context.tenant_id

                set_current_tenant_id(context.tenant_id)
                try:
                    return await call_next(request)
                finally:
                    set_current_tenant_id(None)
        except AppException as exc:
            logger.warning(
                "Tenant authorization failed path=%s status=%s detail=%s",
                request.url.path,
                exc.status_code,
                exc.detail,
            )
            return _error_response(exc)
