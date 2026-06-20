from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.api.v1.auth import get_auth_service
from app.schemas.auth import TokenResponse, UserResponse


@pytest.fixture
def mock_auth_service() -> AsyncMock:
    return AsyncMock()


@pytest.mark.asyncio
async def test_signup_route_returns_tokens(
    client: AsyncClient,
    mock_auth_service: AsyncMock,
) -> None:
    mock_auth_service.signup.return_value = TokenResponse(
        access_token="access",
        refresh_token="refresh",
        expires_in=3600,
        user=UserResponse(id="user-id", email="new@example.com", full_name="New User"),
        tenant_id="tenant-id",
    )
    client._transport.app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    response = await client.post(
        "/auth/signup",
        json={
            "full_name": "New User",
            "email": "new@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["access_token"] == "access"
    assert payload["user"]["email"] == "new@example.com"
    mock_auth_service.signup.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_route_returns_tokens(
    client: AsyncClient,
    mock_auth_service: AsyncMock,
) -> None:
    mock_auth_service.login.return_value = TokenResponse(
        access_token="access",
        refresh_token="refresh",
        expires_in=3600,
        user=UserResponse(id="user-id", email="owner@example.com", full_name="Owner"),
        tenant_id="tenant-id",
    )
    client._transport.app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    response = await client.post(
        "/auth/login",
        json={"email": "owner@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_route_returns_new_tokens(
    client: AsyncClient,
    mock_auth_service: AsyncMock,
) -> None:
    mock_auth_service.refresh.return_value = TokenResponse(
        access_token="new-access",
        refresh_token="new-refresh",
        expires_in=3600,
        user=UserResponse(id="user-id", email="owner@example.com", full_name="Owner"),
        tenant_id="tenant-id",
    )
    client._transport.app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    response = await client.post("/auth/refresh", json={"refresh_token": "old-refresh"})

    assert response.status_code == 200
    assert response.json()["access_token"] == "new-access"


@pytest.mark.asyncio
async def test_logout_route_returns_message(
    client: AsyncClient,
    mock_auth_service: AsyncMock,
) -> None:
    mock_auth_service.logout.return_value = None
    client._transport.app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    response = await client.post("/auth/logout", json={"refresh_token": "refresh"})

    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"
