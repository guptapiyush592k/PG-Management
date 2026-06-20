from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import AuthorizedContextDep, DbSession
from app.models.booking import BookingStatus
from app.schemas.booking import BookingCheckout, BookingCreate, BookingListParams, BookingResponse
from app.schemas.common import PaginatedResponse
from app.services.booking_service import BookingService

router = APIRouter(tags=["bookings"])


def get_booking_service(auth: AuthorizedContextDep, db: DbSession) -> BookingService:
    return BookingService(db, auth.tenant_id, auth.membership.role)


BookingServiceDep = Annotated[BookingService, Depends(get_booking_service)]


def get_list_params(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=255),
    resident_id: UUID | None = Query(default=None),
    bed_id: UUID | None = Query(default=None),
    status: BookingStatus | None = Query(default=None),
) -> BookingListParams:
    return BookingListParams(
        page=page,
        page_size=page_size,
        search=search,
        resident_id=resident_id,
        bed_id=bed_id,
        status=status,
    )


BookingListParamsDep = Annotated[BookingListParams, Depends(get_list_params)]


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    data: BookingCreate,
    service: BookingServiceDep,
) -> BookingResponse:
    return await service.create_booking(data)


@router.get("", response_model=PaginatedResponse[BookingResponse])
async def list_bookings(
    params: BookingListParamsDep,
    service: BookingServiceDep,
) -> PaginatedResponse[BookingResponse]:
    return await service.list_bookings(params)


@router.post("/{booking_id}/checkout", response_model=BookingResponse)
async def checkout_booking(
    booking_id: UUID,
    data: BookingCheckout,
    service: BookingServiceDep,
) -> BookingResponse:
    return await service.checkout_booking(booking_id, data)
