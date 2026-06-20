from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.stored_file import FileStatus
from app.schemas.common import PaginationParams


class FileUploadUrlRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., min_length=1, max_length=255)


class FileUploadUrlResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    file_id: str
    upload_url: str
    method: str
    headers: dict[str, str]
    storage_key: str
    expires_at: datetime | None


class FileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    filename: str
    content_type: str
    storage_key: str
    size_bytes: int | None
    status: FileStatus
    uploaded_by_user_id: str | None
    download_url: str | None = None
    created_at: datetime
    updated_at: datetime


class FileListParams(PaginationParams):
    search: str | None = Field(default=None, max_length=255)
    status: FileStatus | None = None
