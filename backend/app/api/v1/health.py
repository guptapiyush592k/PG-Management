import logging

from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DbSession, SettingsDep
from app.schemas.health import HealthCheckResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: DbSession, settings: SettingsDep) -> HealthCheckResponse:
    database_status: str = "error"
    try:
        await db.execute(text("SELECT 1"))
        database_status = "ok"
    except Exception:
        logger.exception("Database health check failed")

    overall_status = "ok" if database_status == "ok" else "degraded"
    return HealthCheckResponse(
        status=overall_status,
        app_name=settings.app_name,
        environment=settings.app_env,
        database=database_status,
    )
