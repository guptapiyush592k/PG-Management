from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.settings import get_settings, validate_settings
from app.db.session import dispose_engine, init_database

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = validate_settings()
    setup_logging(settings.log_level)
    await init_database(settings)
    logger.info("Application startup complete env=%s", settings.app_env)
    yield
    await dispose_engine()
    logger.info("Application shutdown complete")


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
