from typing import Annotated

from fastapi import Depends

from app.core.settings import Settings, get_settings
from app.storage.base import StorageProvider
from app.storage.factory import create_storage_provider


def get_storage_provider(
    settings: Annotated[Settings, Depends(get_settings)],
) -> StorageProvider:
    return create_storage_provider(settings)


StorageProviderDep = Annotated[StorageProvider, Depends(get_storage_provider)]
