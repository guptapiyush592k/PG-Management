import asyncio
import re
import uuid
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.core.settings import Settings, get_settings
from app.models.stored_file import FileStatus, StoredFile
from app.models.tenant_user import TenantUserRole
from app.repositories.file_repository import FileRepository
from app.schemas.common import PaginatedResponse
from app.schemas.file import (
    FileListParams,
    FileResponse,
    FileUploadUrlRequest,
    FileUploadUrlResponse,
)
from app.services.permissions import require_permission
from app.storage.base import StorageProvider
from app.storage.local import LocalStorageProvider

ALLOWED_CONTENT_TYPES = frozenset(
    {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/webp",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
)


class FileService:
    def __init__(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        role: TenantUserRole | None,
        storage: StorageProvider,
        *,
        user_id: UUID | None = None,
        file_repo: FileRepository | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.role = role
        self.user_id = user_id
        self.storage = storage
        self.settings = settings or get_settings()
        self.file_repo = file_repo or FileRepository(session, tenant_id)

    async def create_upload_url(self, data: FileUploadUrlRequest) -> FileUploadUrlResponse:
        require_permission(self.role, "manage_files")
        content_type = data.content_type.strip().lower()
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise ValidationError("Unsupported content type")

        file_id = uuid.uuid4()
        storage_key = self._build_storage_key(file_id, data.filename)
        stored_file = StoredFile(
            id=file_id,
            tenant_id=self.tenant_id,
            filename=data.filename.strip(),
            content_type=content_type,
            storage_key=storage_key,
            uploaded_by_user_id=self.user_id,
            status=FileStatus.PENDING,
        )
        stored_file = await self.file_repo.add(stored_file)

        presigned = await self.storage.generate_upload_url(
            storage_key,
            content_type,
            expires_in=self._upload_expires_in(),
        )
        await self.session.commit()

        return FileUploadUrlResponse(
            file_id=str(stored_file.id),
            upload_url=presigned.upload_url,
            method=presigned.method,
            headers=presigned.headers,
            storage_key=storage_key,
            expires_at=presigned.expires_at,
        )

    async def confirm_upload(self, file_id: UUID) -> FileResponse:
        require_permission(self.role, "manage_files")
        stored_file = await self._get_file_or_404(file_id)
        if stored_file.status == FileStatus.UPLOADED:
            return await self._to_response(stored_file, include_download_url=True)

        exists, size_bytes = await self.storage.get_object_metadata(stored_file.storage_key)
        if not exists:
            raise ValidationError("Uploaded file content was not found in storage")

        updated = await self.file_repo.mark_uploaded(
            stored_file,
            size_bytes=size_bytes or 0,
        )
        await self.session.commit()
        return await self._to_response(updated, include_download_url=True)

    async def list_files(self, params: FileListParams) -> PaginatedResponse[FileResponse]:
        total = await self.file_repo.count(search=params.search, status=params.status)
        files = await self.file_repo.list_paginated(
            offset=params.offset,
            limit=params.page_size,
            search=params.search,
            status=params.status,
        )
        items = await asyncio.gather(
            *(self._to_response(stored_file, include_download_url=True) for stored_file in files)
        )
        return PaginatedResponse[FileResponse](
            items=list(items),
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def get_file(self, file_id: UUID) -> FileResponse:
        stored_file = await self._get_file_or_404(file_id)
        return await self._to_response(stored_file, include_download_url=True)

    async def complete_local_upload(
        self,
        file_id: UUID,
        content: bytes,
        *,
        expires: int | None = None,
        signature: str | None = None,
    ) -> FileResponse:
        if len(content) > self.settings.max_upload_bytes:
            raise ValidationError(
                f"File exceeds maximum allowed size of {self.settings.max_upload_bytes} bytes"
            )

        if not isinstance(self.storage, LocalStorageProvider):
            raise ValidationError("Direct upload is only supported for local storage")

        stored_file = await self._get_file_or_404(file_id)
        if expires is not None and signature is not None:
            expires_at = datetime.fromtimestamp(expires, tz=UTC)
            if expires_at < datetime.now(UTC):
                raise ForbiddenError("Upload URL has expired")
            if not self.storage.verify_signature(
                str(file_id),
                stored_file.storage_key,
                expires_at,
                signature,
            ):
                raise ForbiddenError("Invalid upload signature")
        else:
            require_permission(self.role, "manage_files")

        await self.storage.save_object(stored_file.storage_key, content)
        updated = await self.file_repo.mark_uploaded(stored_file, size_bytes=len(content))
        await self.session.commit()
        return await self._to_response(updated, include_download_url=False)

    async def download_local_file(
        self,
        file_id: UUID,
        *,
        expires: int | None = None,
        signature: str | None = None,
    ) -> tuple[StoredFile, bytes]:
        if not isinstance(self.storage, LocalStorageProvider):
            raise ValidationError("Direct download is only supported for local storage")

        stored_file = await self._get_file_or_404(file_id)
        if stored_file.status != FileStatus.UPLOADED:
            raise NotFoundError("File not found")

        if expires is not None and signature is not None:
            expires_at = datetime.fromtimestamp(expires, tz=UTC)
            if expires_at < datetime.now(UTC):
                raise ForbiddenError("Download URL has expired")
            if not self.storage.verify_signature(
                str(file_id),
                stored_file.storage_key,
                expires_at,
                signature,
                purpose="download",
            ):
                raise ForbiddenError("Invalid download signature")
        else:
            require_permission(self.role, "manage_files")

        content = await self.storage.read_object(stored_file.storage_key)
        return stored_file, content

    async def _get_file_or_404(self, file_id: UUID) -> StoredFile:
        stored_file = await self.file_repo.get_by_id(file_id)
        if stored_file is None:
            raise NotFoundError("File not found")
        return stored_file

    async def _to_response(
        self,
        stored_file: StoredFile,
        *,
        include_download_url: bool,
    ) -> FileResponse:
        download_url = None
        if include_download_url and stored_file.status == FileStatus.UPLOADED:
            download_url = await self.storage.generate_download_url(
                stored_file.storage_key,
                expires_in=self._download_expires_in(),
            )

        return FileResponse(
            id=str(stored_file.id),
            tenant_id=str(stored_file.tenant_id),
            filename=stored_file.filename,
            content_type=stored_file.content_type,
            storage_key=stored_file.storage_key,
            size_bytes=stored_file.size_bytes,
            status=stored_file.status,
            uploaded_by_user_id=(
                str(stored_file.uploaded_by_user_id)
                if stored_file.uploaded_by_user_id
                else None
            ),
            download_url=download_url,
            created_at=stored_file.created_at,
            updated_at=stored_file.updated_at,
        )

    def _build_storage_key(self, file_id: uuid.UUID, filename: str) -> str:
        safe_name = re.sub(r"[^\w.\-]", "_", filename.strip()) or "file"
        return f"{self.tenant_id}/{file_id}/{safe_name}"

    def _upload_expires_in(self) -> int:
        return self.settings.storage_presigned_url_expires_seconds

    def _download_expires_in(self) -> int:
        return self._upload_expires_in()
