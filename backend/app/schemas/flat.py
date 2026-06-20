from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FlatBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    address: str = Field(min_length=1, max_length=2000)
    is_active: bool = True


class FlatCreate(FlatBase):
    pass


class FlatUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = Field(default=None, min_length=1, max_length=2000)
    is_active: bool | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "FlatUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class FlatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    name: str
    address: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class FlatListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    search: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
