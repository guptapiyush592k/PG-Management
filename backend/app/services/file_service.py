import re
import uuid
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
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


class FileService:
    def __init__(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        role: TenantUserRole,
        storage: StorageProvider,
        *,
        user_id: UUID | None = None,
        file_repo: FileRepository | None = None,
    ) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self.role = role
        self.user_id = user_id
        self.storage = storage
        self.file_repo = file_repo or FileRepository(session, tenant_id)

    async def create_upload_url(self, data: FileUploadUrlRequest) -> FileUploadUrlResponse:
        require_permission(self.role, "manage_files")

        file_id = uuid.uuid4()
        storage_key = self._build_storage_key(file_id, data.filename)
        stored_file = StoredFile(
            id=file_id,
            tenant_id=self.tenant_id,
            filename=data.filename.strip(),
            content_type=data.content_type.strip(),
            storage_key=storage_key,
            uploaded_by_user_id=self.user_id,
            status=FileStatus.PENDING,
        )
        stored_file = await self.file_repo.add(stored_file)

        presigned = await self.storage.generate_upload_url(
            storage_key,
            data.content_type.strip(),
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

    async def list_files(self, params: FileListParams) -> PaginatedResponse[FileResponse]:
        total = await self.file_repo.count(search=params.search, status=params.status)
        files = await self.file_repo.list_paginated(
            offset=params.offset,
            limit=params.page_size,
            search=params.search,
            status=params.status,
        )
        items = [await self._to_response(stored_file) for stored_file in files]
        return PaginatedResponse[FileResponse](
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
        )

    async def complete_local_upload(
        self,
        file_id: UUID,
        content: bytes,
        *,
        expires: int,
        signature: str,
    ) -> FileResponse:
        if not isinstance(self.storage, LocalStorageProvider):
            raise ValidationError("Direct upload is only supported for local storage")

        stored_file = await self._get_file_or_404(file_id)
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

        await self.storage.save_object(stored_file.storage_key, content)
        updated = await self.file_repo.mark_uploaded(stored_file, size_bytes=len(content))
        await self.session.commit()
        return await self._to_response(updated)

    async def download_local_file(
        self,
        file_id: UUID,
        *,
        expires: int,
        signature: str,
    ) -> tuple[StoredFile, bytes]:
        if not isinstance(self.storage, LocalStorageProvider):
            raise ValidationError("Direct download is only supported for local storage")

        stored_file = await self._get_file_or_404(file_id)
        if stored_file.status != FileStatus.UPLOADED:
            raise NotFoundError("File not found")

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

        content = await self.storage.read_object(stored_file.storage_key)
        return stored_file, content

    async def _get_file_or_404(self, file_id: UUID) -> StoredFile:
        stored_file = await self.file_repo.get_by_id(file_id)
        if stored_file is None:
            raise NotFoundError("File not found")
        return stored_file

    async def _to_response(self, stored_file: StoredFile) -> FileResponse:
        download_url = None
        if stored_file.status == FileStatus.UPLOADED:
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
        from app.core.settings import get_settings

        return get_settings().storage_presigned_url_expires_seconds

    def _download_expires_in(self) -> int:
        return self._upload_expires_in()
