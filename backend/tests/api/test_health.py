import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_ok(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["app_name"] == "PG Management API"
    assert payload["environment"] == "development"
    assert payload["database"] == "ok"
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_health_check_degraded_when_db_fails(client: AsyncClient, mock_db_session) -> None:
    mock_db_session.execute.side_effect = Exception("connection refused")

    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "degraded"
    assert payload["database"] == "error"
