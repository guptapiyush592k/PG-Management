from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import AuthorizedContextDep, DbSession
from app.models.rent_payment import PaymentStatus
from app.schemas.common import PaginatedResponse
from app.schemas.payment import (
    PaymentCreate,
    PaymentListParams,
    PaymentResponse,
    PaymentSummaryResponse,
    PaymentUpdate,
)
from app.services.payment_service import PaymentService

router = APIRouter(tags=["payments"])


def get_payment_service(auth: AuthorizedContextDep, db: DbSession) -> PaymentService:
    return PaymentService(db, auth.tenant_id, auth.membership.role)


PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]


def get_list_params(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=255),
    resident_id: UUID | None = Query(default=None),
    status: PaymentStatus | None = Query(default=None),
) -> PaymentListParams:
    return PaymentListParams(
        page=page,
        page_size=page_size,
        search=search,
        resident_id=resident_id,
        status=status,
    )


PaymentListParamsDep = Annotated[PaymentListParams, Depends(get_list_params)]


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    data: PaymentCreate,
    service: PaymentServiceDep,
) -> PaymentResponse:
    return await service.create_payment(data)


@router.get("/summary", response_model=PaymentSummaryResponse)
async def get_payment_summary(
    service: PaymentServiceDep,
) -> PaymentSummaryResponse:
    return await service.get_summary()


@router.get("", response_model=PaginatedResponse[PaymentResponse])
async def list_payments(
    params: PaymentListParamsDep,
    service: PaymentServiceDep,
) -> PaginatedResponse[PaymentResponse]:
    return await service.list_payments(params)


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: UUID,
    data: PaymentUpdate,
    service: PaymentServiceDep,
) -> PaymentResponse:
    return await service.update_payment(payment_id, data)
