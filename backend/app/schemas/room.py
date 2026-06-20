from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RoomBase(BaseModel):
    flat_id: UUID
    room_number: str = Field(min_length=1, max_length=50)


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    flat_id: UUID | None = None
    room_number: str | None = Field(default=None, min_length=1, max_length=50)

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "RoomUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class RoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    flat_id: str
    room_number: str
    created_at: datetime
    updated_at: datetime


class RoomListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    search: str | None = Field(default=None, max_length=255)
    flat_id: UUID | None = None

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
