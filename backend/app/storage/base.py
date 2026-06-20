from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class PresignedUpload:
    upload_url: str
    method: str = "PUT"
    headers: dict[str, str] = field(default_factory=dict)
    expires_at: datetime | None = None


class StorageProvider(ABC):
    """Cloud-agnostic object storage abstraction."""

    @abstractmethod
    async def generate_upload_url(
        self,
        storage_key: str,
        content_type: str,
        *,
        expires_in: int,
    ) -> PresignedUpload:
        """Return a presigned URL (or equivalent) for direct client upload."""

    @abstractmethod
    async def generate_download_url(
        self,
        storage_key: str,
        *,
        expires_in: int,
    ) -> str:
        """Return a time-limited URL to download the object."""

    @abstractmethod
    async def delete_object(self, storage_key: str) -> None:
        """Remove the object from storage."""

    async def get_object_metadata(self, storage_key: str) -> tuple[bool, int | None]:
        """Return whether the object exists and its size in bytes, if known."""
        raise NotImplementedError(f"{type(self).__name__} does not support metadata lookups")
