from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

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
