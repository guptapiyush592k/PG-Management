from app.core.exceptions import ValidationError
from app.core.settings import Settings
from app.storage.base import StorageProvider
from app.storage.local import LocalStorageProvider
from app.storage.s3 import S3StorageProvider


def create_storage_provider(settings: Settings) -> StorageProvider:
    provider = settings.storage_provider
    if provider == "local":
        return LocalStorageProvider(settings)
    if provider == "s3":
        return S3StorageProvider(settings)
    raise ValidationError(f"Unsupported storage provider: {provider}")
