from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.settings import Settings, get_settings
from app.repositories.file_repository import FileRepository
from app.storage.base import StorageProvider
from app.storage.local import LocalStorageProvider


class SignedFileAccessService:
    """Validate presigned local file URLs without JWT authentication."""

    def __init__(
        self,
        session: AsyncSession,
        storage: StorageProvider,
        *,
        settings: Settings | None = None,
        file_repo: FileRepository | None = None,
    ) -> None:
        self.session = session
        self.storage = storage
        self.settings = settings or get_settings()
        self.file_repo = file_repo or FileRepository(session, tenant_id=None)

    async def authorize(
        self,
        *,
        file_id: UUID,
        expires: int,
        signature: str,
        method: str,
    ) -> UUID:
        if not isinstance(self.storage, LocalStorageProvider):
            raise ForbiddenError("Signed file access is only supported for local storage")

        stored_file = await self.file_repo.get_by_id_global(file_id)
        if stored_file is None:
            raise NotFoundError("File not found")

        expires_at = datetime.fromtimestamp(expires, tz=UTC)
        if expires_at < datetime.now(UTC):
            raise ForbiddenError("Signed URL has expired")

        purpose = "download" if method.upper() == "GET" else "upload"
        if not self.storage.verify_signature(
            str(file_id),
            stored_file.storage_key,
            expires_at,
            signature,
            purpose=purpose,
        ):
            raise ForbiddenError("Invalid signed URL")

        return stored_file.tenant_id
