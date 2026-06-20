import logging

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.exceptions import AppException
from app.core.paths import is_signed_file_content_path, parse_signed_file_content_path
from app.core.rate_limit import SlidingWindowRateLimiter
from app.core.settings import get_settings
from app.db.session import get_session_factory
from app.middleware.tenant_context import set_current_tenant_id
from app.services.signed_file_access_service import SignedFileAccessService
from app.storage.factory import create_storage_provider

logger = logging.getLogger(__name__)


def _error_response(exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code},
    )


class SignedFileAccessMiddleware(BaseHTTPMiddleware):
    """
    Authorize local presigned file upload/download URLs using HMAC signatures.
    Sets request.state.signed_file_access when valid so tenant JWT auth is skipped.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if not is_signed_file_content_path(request.url.path):
            return await call_next(request)

        expires = request.query_params.get("expires")
        signature = request.query_params.get("signature")
        if not expires or not signature:
            return await call_next(request)

        file_id = parse_signed_file_content_path(request.url.path)
        if file_id is None:
            return await call_next(request)

        settings = get_settings()
        session_factory = get_session_factory()
        try:
            async with session_factory() as session:
                storage = create_storage_provider(settings)
                service = SignedFileAccessService(session, storage, settings=settings)
                tenant_id = await service.authorize(
                    file_id=file_id,
                    expires=int(expires),
                    signature=signature,
                    method=request.method,
                )
        except AppException as exc:
            logger.warning(
                "Signed file access failed path=%s status=%s detail=%s",
                request.url.path,
                exc.status_code,
                exc.detail,
            )
            return _error_response(exc)
        except ValueError:
            return _error_response(
                AppException("Invalid signed URL parameters", status_code=400)
            )

        request.state.signed_file_access = True
        request.state.tenant_id = tenant_id
        request.state.file_id = file_id

        set_current_tenant_id(tenant_id)
        try:
            return await call_next(request)
        finally:
            set_current_tenant_id(None)


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    """Rate-limit unauthenticated auth endpoints by client IP."""

    def __init__(self, app) -> None:
        super().__init__(app)
        settings = get_settings()
        self._limiter = SlidingWindowRateLimiter(
            max_requests=settings.auth_rate_limit_max_requests,
            window_seconds=settings.auth_rate_limit_window_seconds,
        )

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path.startswith("/auth"):
            client_host = request.client.host if request.client else "unknown"
            key = f"{client_host}:{request.url.path}"
            if not self._limiter.is_allowed(key):
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests. Please try again later.",
                        "error_code": "rate_limit_exceeded",
                    },
                )
        return await call_next(request)
