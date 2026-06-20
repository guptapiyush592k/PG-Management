from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stored_file import FileStatus, StoredFile
from app.repositories.base import BaseRepository


class FileRepository(BaseRepository[StoredFile]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, StoredFile, tenant_id=tenant_id)

    def _apply_filters(
        self,
        stmt,
        *,
        search: str | None = None,
        status: FileStatus | None = None,
    ):
        stmt = self._apply_tenant_filter(stmt)
        if search:
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    StoredFile.filename.ilike(pattern),
                    StoredFile.content_type.ilike(pattern),
                )
            )
        if status is not None:
            stmt = stmt.where(StoredFile.status == status)
        return stmt

    async def count(
        self,
        *,
        search: str | None = None,
        status: FileStatus | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(StoredFile)
        stmt = self._apply_filters(stmt, search=search, status=status)
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
        status: FileStatus | None = None,
    ) -> list[StoredFile]:
        stmt = self._apply_filters(
            select(StoredFile),
            search=search,
            status=status,
        )
        stmt = (
            stmt.order_by(StoredFile.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        *,
        filename: str,
        content_type: str,
        storage_key: str,
        uploaded_by_user_id: UUID | None,
        status: FileStatus = FileStatus.PENDING,
    ) -> StoredFile:
        stored_file = StoredFile(
            tenant_id=self.tenant_id,
            filename=filename,
            content_type=content_type,
            storage_key=storage_key,
            uploaded_by_user_id=uploaded_by_user_id,
            status=status,
        )
        return await self.add(stored_file)

    async def mark_uploaded(self, stored_file: StoredFile, *, size_bytes: int) -> StoredFile:
        stored_file.status = FileStatus.UPLOADED
        stored_file.size_bytes = size_bytes
        await self.session.flush()
        await self.session.refresh(stored_file)
        return stored_file
