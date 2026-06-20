from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class ResidentBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=1, max_length=20)
    email: EmailStr | None = None
    aadhaar: str | None = Field(default=None, pattern=r"^\d{12}$")
    joining_date: date
    deposit: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)
    notes: str | None = Field(default=None, max_length=5000)
    is_active: bool = True


class ResidentCreate(ResidentBase):
    pass


class ResidentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    email: EmailStr | None = None
    aadhaar: str | None = Field(default=None, pattern=r"^\d{12}$")
    joining_date: date | None = None
    deposit: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    notes: str | None = Field(default=None, max_length=5000)
    is_active: bool | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "ResidentUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class ResidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    name: str
    phone: str
    email: str | None
    aadhaar: str | None
    joining_date: date
    deposit: Decimal
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ResidentListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    search: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
