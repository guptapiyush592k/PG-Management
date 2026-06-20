import asyncio
import logging
from datetime import UTC, datetime, timedelta

from botocore.exceptions import ClientError

from app.core.settings import Settings
from app.storage.base import PresignedUpload, StorageProvider

logger = logging.getLogger(__name__)


class S3StorageProvider(StorageProvider):
    """S3-compatible object storage (AWS S3, MinIO, etc.)."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client

        import boto3

        client_kwargs: dict = {
            "service_name": "s3",
            "region_name": self._settings.s3_region,
            "aws_access_key_id": self._settings.s3_access_key_id,
            "aws_secret_access_key": self._settings.s3_secret_access_key,
        }
        if self._settings.s3_endpoint_url:
            client_kwargs["endpoint_url"] = self._settings.s3_endpoint_url

        self._client = boto3.client(**client_kwargs)
        return self._client

    async def generate_upload_url(
        self,
        storage_key: str,
        content_type: str,
        *,
        expires_in: int,
    ) -> PresignedUpload:
        client = self._get_client()
        upload_url = await asyncio.to_thread(
            client.generate_presigned_url,
            "put_object",
            Params={
                "Bucket": self._settings.s3_bucket_name,
                "Key": storage_key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
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
        client = self._get_client()
        return await asyncio.to_thread(
            client.generate_presigned_url,
            "get_object",
            Params={
                "Bucket": self._settings.s3_bucket_name,
                "Key": storage_key,
            },
            ExpiresIn=expires_in,
        )

    async def delete_object(self, storage_key: str) -> None:
        client = self._get_client()
        await asyncio.to_thread(
            client.delete_object,
            Bucket=self._settings.s3_bucket_name,
            Key=storage_key,
        )
        logger.info("Deleted S3 object: %s", storage_key)

    async def get_object_metadata(self, storage_key: str) -> tuple[bool, int | None]:
        client = self._get_client()

        def _head() -> tuple[bool, int | None]:
            try:
                response = client.head_object(
                    Bucket=self._settings.s3_bucket_name,
                    Key=storage_key,
                )
            except ClientError as exc:
                error_code = exc.response.get("Error", {}).get("Code", "")
                if error_code in {"404", "NoSuchKey", "NotFound"}:
                    return False, None
                raise
            return True, int(response.get("ContentLength", 0))

        return await asyncio.to_thread(_head)
