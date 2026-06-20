from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import Response as FastAPIResponse

from app.api.deps import AuthorizedContextDep, DbSession
from app.models.stored_file import FileStatus
from app.schemas.common import PaginatedResponse
from app.schemas.file import (
    FileListParams,
    FileResponse,
    FileUploadUrlRequest,
    FileUploadUrlResponse,
)
from app.services.file_service import FileService
from app.storage.deps import StorageProviderDep

router = APIRouter(tags=["files"])


def get_file_service(
    auth: AuthorizedContextDep,
    db: DbSession,
    storage: StorageProviderDep,
) -> FileService:
    return FileService(
        db,
        auth.tenant_id,
        auth.membership.role,
        storage,
        user_id=auth.user_id,
    )


FileServiceDep = Annotated[FileService, Depends(get_file_service)]


def get_list_params(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=255),
    status: FileStatus | None = Query(default=None),
) -> FileListParams:
    return FileListParams(
        page=page,
        page_size=page_size,
        search=search,
        status=status,
    )


FileListParamsDep = Annotated[FileListParams, Depends(get_list_params)]


@router.post(
    "/upload-url",
    response_model=FileUploadUrlResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_upload_url(
    data: FileUploadUrlRequest,
    service: FileServiceDep,
) -> FileUploadUrlResponse:
    return await service.create_upload_url(data)


@router.get("", response_model=PaginatedResponse[FileResponse])
async def list_files(
    params: FileListParamsDep,
    service: FileServiceDep,
) -> PaginatedResponse[FileResponse]:
    return await service.list_files(params)


@router.put("/{file_id}/content", response_model=FileResponse)
async def upload_file_content(
    file_id: UUID,
    request: Request,
    service: FileServiceDep,
    expires: int = Query(..., ge=1),
    signature: str = Query(..., min_length=1),
) -> FileResponse:
    """Complete a local-storage upload using the presigned URL from POST /files/upload-url."""
    content = await request.body()
    return await service.complete_local_upload(
        file_id,
        content,
        expires=expires,
        signature=signature,
    )


@router.get("/{file_id}/content")
async def download_file_content(
    file_id: UUID,
    service: FileServiceDep,
    expires: int = Query(..., ge=1),
    signature: str = Query(..., min_length=1),
) -> FastAPIResponse:
    """Download a file stored locally using a signed URL."""
    stored_file, content = await service.download_local_file(
        file_id,
        expires=expires,
        signature=signature,
    )
    return FastAPIResponse(
        content=content,
        media_type=stored_file.content_type,
        headers={"Content-Disposition": f'inline; filename="{stored_file.filename}"'},
    )
