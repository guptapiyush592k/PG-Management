from fastapi import APIRouter

from app.api.v1 import examples, flats, health, rooms

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(examples.router, prefix="/examples")
api_router.include_router(flats.router, prefix="/flats")
api_router.include_router(rooms.router, prefix="/rooms")
