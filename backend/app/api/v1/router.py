from fastapi import APIRouter

from app.api.v1 import beds, bookings, examples, flats, health, payments, residents, rooms

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(examples.router, prefix="/examples")
api_router.include_router(flats.router, prefix="/flats")
api_router.include_router(rooms.router, prefix="/rooms")
api_router.include_router(beds.router, prefix="/beds")
api_router.include_router(residents.router, prefix="/residents")
api_router.include_router(payments.router, prefix="/payments")
api_router.include_router(bookings.router, prefix="/bookings")
