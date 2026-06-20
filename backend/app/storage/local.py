import hashlib
import hmac
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

from app.core.settings import Settings
from app.storage.base import PresignedUpload, StorageProvider

logger = logging.getLogger(__name__)


class LocalStorageProvider(StorageProvider):
    """Filesystem-backed storage for local development and testing."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._root = Path(settings.local_storage_path).resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    async def generate_upload_url(
        self,
        storage_key: str,
        content_type: str,
        *,
        expires_in: int,
    ) -> PresignedUpload:
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
        file_id = storage_key.split("/")[1]
        signature = self._sign(file_id, storage_key, expires_at)
        query = urlencode(
            {
                "expires": int(expires_at.timestamp()),
                "signature": signature,
            }
        )
        upload_url = (
            f"{self._settings.local_storage_public_base_url.rstrip('/')}"
            f"/api/v1/files/{file_id}/content?{query}"
        )
        return PresignedUpload(
            upload_url=upload_url,
            method="PUT",
            headers={"Content-Type": content_type},
            expires_at=expires_at,
        )

    async def generate_download_url(
        self,
        storage_key: str,
        *,
        expires_in: int,
    ) -> str:
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
        file_id = storage_key.split("/")[1]
        signature = self._sign(file_id, storage_key, expires_at, purpose="download")
        query = urlencode(
            {
                "expires": int(expires_at.timestamp()),
                "signature": signature,
            }
        )
        return (
            f"{self._settings.local_storage_public_base_url.rstrip('/')}"
            f"/api/v1/files/{file_id}/content?{query}"
        )

    async def delete_object(self, storage_key: str) -> None:
        path = self._root / storage_key
        if path.exists():
            path.unlink()
            logger.info("Deleted local storage object: %s", storage_key)

    async def save_object(self, storage_key: str, content: bytes) -> None:
        path = self._root / storage_key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    async def read_object(self, storage_key: str) -> bytes:
        path = self._root / storage_key
        return path.read_bytes()

    async def get_object_metadata(self, storage_key: str) -> tuple[bool, int | None]:
        path = self._root / storage_key
        if not path.exists():
            return False, None
        return True, path.stat().st_size

    def verify_signature(
        self,
        file_id: str,
        storage_key: str,
        expires_at: datetime,
        signature: str,
        *,
        purpose: str = "upload",
    ) -> bool:
        expected = self._sign(file_id, storage_key, expires_at, purpose=purpose)
        return hmac.compare_digest(expected, signature)

    def _sign(
        self,
        file_id: str,
        storage_key: str,
        expires_at: datetime,
        *,
        purpose: str = "upload",
    ) -> str:
        payload = f"{purpose}:{file_id}:{storage_key}:{int(expires_at.timestamp())}"
        digest = hmac.new(
            self._settings.effective_storage_signing_key.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()
        return digest
