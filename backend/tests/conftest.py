import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/pg_management_test",
)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-with-at-least-32-chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

_init_db_patcher = patch("app.db.session.init_database", new_callable=AsyncMock)
_init_db_patcher.start()

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.session import get_db
from app.main import create_app


@pytest.fixture
def mock_db_session() -> AsyncMock:
    session = AsyncMock()
    session.execute = AsyncMock(return_value=None)
    session.close = AsyncMock()
    return session


@pytest.fixture
async def client(mock_db_session: AsyncMock) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    async def override_get_db() -> AsyncGenerator[AsyncMock, None]:
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
