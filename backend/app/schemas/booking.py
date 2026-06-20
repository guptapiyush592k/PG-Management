from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.booking import BookingStatus


class BookingCreate(BaseModel):
    resident_id: UUID
    bed_id: UUID
    start_date: date


class BookingCheckout(BaseModel):
    end_date: date | None = None


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    resident_id: str
    bed_id: str
    start_date: date
    end_date: date | None
    status: BookingStatus
    created_at: datetime
    updated_at: datetime


class BookingListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    search: str | None = Field(default=None, max_length=255)
    resident_id: UUID | None = None
    bed_id: UUID | None = None
    status: BookingStatus | None = None

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
