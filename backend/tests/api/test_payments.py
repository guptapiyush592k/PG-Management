import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.api.v1.payments import get_payment_service
from app.models.rent_payment import PaymentStatus
from app.models.tenant_user import TenantUser, TenantUserRole
from app.schemas.common import PaginatedResponse
from app.schemas.payment import PaymentResponse, PaymentSummaryResponse


@pytest.fixture
def mock_payment_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def payment_response() -> PaymentResponse:
    now = datetime.now(UTC)
    tenant_id = uuid.uuid4()
    return PaymentResponse(
        id=str(uuid.uuid4()),
        tenant_id=str(tenant_id),
        resident_id=str(uuid.uuid4()),
        booking_id=None,
        amount=Decimal("9500.00"),
        due_date=date(2026, 6, 1),
        paid_date=None,
        status=PaymentStatus.PENDING,
        payment_mode=None,
        notes=None,
        created_at=now,
        updated_at=now,
    )


def _authorized_context(tenant_id: uuid.UUID, role: TenantUserRole):
    from app.services.tenant_authorization_service import AuthorizedContext

    membership = TenantUser(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        user_id=uuid.uuid4(),
        role=role,
        is_primary=True,
    )
    return AuthorizedContext(
        user=MagicMock(),
        tenant=MagicMock(),
        membership=membership,
        user_id=membership.user_id,
        tenant_id=tenant_id,
    )


@pytest.mark.asyncio
async def test_create_payment_route(
    client: AsyncClient,
    mock_payment_service: AsyncMock,
    payment_response: PaymentResponse,
) -> None:
    mock_payment_service.create_payment.return_value = payment_response
    tenant_id = uuid.UUID(payment_response.tenant_id)

    client._transport.app.dependency_overrides[get_payment_service] = lambda: mock_payment_service
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_id, TenantUserRole.MANAGER),
    ):
        response = await client.post(
            "/api/v1/payments",
            json={
                "resident_id": payment_response.resident_id,
                "amount": "9500.00",
                "due_date": "2026-06-01",
                "status": "pending",
            },
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": payment_response.tenant_id,
            },
        )

    assert response.status_code == 201
    assert response.json()["amount"] == "9500.00"


@pytest.mark.asyncio
async def test_list_payments_route(
    client: AsyncClient,
    mock_payment_service: AsyncMock,
    payment_response: PaymentResponse,
) -> None:
    mock_payment_service.list_payments.return_value = PaginatedResponse(
        items=[payment_response],
        total=1,
        page=1,
        page_size=20,
    )
    tenant_id = uuid.UUID(payment_response.tenant_id)

    client._transport.app.dependency_overrides[get_payment_service] = lambda: mock_payment_service
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_id, TenantUserRole.MANAGER),
    ):
        response = await client.get(
            f"/api/v1/payments?resident_id={payment_response.resident_id}&status=pending",
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": payment_response.tenant_id,
            },
        )

    assert response.status_code == 200
    assert response.json()["total"] == 1


@pytest.mark.asyncio
async def test_update_payment_route(
    client: AsyncClient,
    mock_payment_service: AsyncMock,
    payment_response: PaymentResponse,
) -> None:
    payment_response.status = PaymentStatus.PAID
    payment_response.paid_date = date(2026, 5, 30)
    payment_response.payment_mode = "UPI"
    mock_payment_service.update_payment.return_value = payment_response
    tenant_id = uuid.UUID(payment_response.tenant_id)

    client._transport.app.dependency_overrides[get_payment_service] = lambda: mock_payment_service
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_id, TenantUserRole.MANAGER),
    ):
        response = await client.patch(
            f"/api/v1/payments/{payment_response.id}",
            json={
                "resident_id": payment_response.resident_id,
                "amount": "9500.00",
                "due_date": "2026-06-01",
                "paid_date": "2026-05-30",
                "status": "paid",
                "payment_mode": "UPI",
            },
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": payment_response.tenant_id,
            },
        )

    assert response.status_code == 200
    assert response.json()["status"] == "paid"


@pytest.mark.asyncio
async def test_payment_summary_route(
    client: AsyncClient,
    mock_payment_service: AsyncMock,
    payment_response: PaymentResponse,
) -> None:
    mock_payment_service.get_summary.return_value = PaymentSummaryResponse(
        total_collected=Decimal("19000.00"),
        pending_amount=Decimal("9500.00"),
        overdue_amount=Decimal("3000.00"),
        counts={
            PaymentStatus.PAID: 2,
            PaymentStatus.PENDING: 1,
            PaymentStatus.PARTIAL: 0,
            PaymentStatus.OVERDUE: 1,
        },
    )
    tenant_id = uuid.UUID(payment_response.tenant_id)

    client._transport.app.dependency_overrides[get_payment_service] = lambda: mock_payment_service
    with patch(
        "app.middleware.tenant_authorization.TenantAuthorizationService.authorize",
        new_callable=AsyncMock,
        return_value=_authorized_context(tenant_id, TenantUserRole.MANAGER),
    ):
        response = await client.get(
            "/api/v1/payments/summary",
            headers={
                "Authorization": "Bearer test-token",
                "X-Tenant-ID": payment_response.tenant_id,
            },
        )

    assert response.status_code == 200
    assert response.json()["total_collected"] == "19000.00"
    assert response.json()["pending_amount"] == "9500.00"
