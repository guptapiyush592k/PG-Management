import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import request_id_ctx
from app.middleware.tenant_context import set_current_tenant_id

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = str(uuid.uuid4())
        request_id_ctx.set(request_id)
        start = time.perf_counter()

        logger.info("Request started %s %s", request.method, request.url.path)
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        response.headers["X-Request-ID"] = request_id
        logger.info(
            "Request completed %s %s status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


class TenantContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        tenant_header = request.headers.get("X-Tenant-ID")
        if tenant_header:
            try:
                set_current_tenant_id(tenant_header)
            except ValueError:
                logger.warning("Invalid X-Tenant-ID header: %s", tenant_header)
        else:
            set_current_tenant_id(None)

        try:
            return await call_next(request)
        finally:
            set_current_tenant_id(None)
