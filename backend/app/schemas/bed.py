from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.bed import BedStatus


class BedBase(BaseModel):
    room_id: UUID
    bed_label: str = Field(min_length=1, max_length=50)
    rent_amount: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    status: BedStatus = BedStatus.VACANT


class BedCreate(BedBase):
    pass


class BedUpdate(BaseModel):
    room_id: UUID | None = None
    bed_label: str | None = Field(default=None, min_length=1, max_length=50)
    rent_amount: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    status: BedStatus | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "BedUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class BedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    room_id: str
    bed_label: str
    rent_amount: Decimal
    status: BedStatus
    created_at: datetime
    updated_at: datetime


class BedListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    search: str | None = Field(default=None, max_length=255)
    room_id: UUID | None = None
    status: BedStatus | None = None

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
