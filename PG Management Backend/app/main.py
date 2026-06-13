from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.db.session import dispose_engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    register_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from app.middleware.request_logging import RequestLoggingMiddleware, TenantContextMiddleware

    app.add_middleware(TenantContextMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
