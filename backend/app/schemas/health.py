from typing import Literal

from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: Literal["ok", "degraded"]
    app_name: str
    environment: str
    database: Literal["ok", "error"]
