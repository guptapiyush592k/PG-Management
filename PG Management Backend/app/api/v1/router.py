from fastapi import APIRouter

from app.api.v1 import examples, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(examples.router, prefix="/examples")
