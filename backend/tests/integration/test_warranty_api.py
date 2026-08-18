"""Integration tests for the warranty endpoints and triage agent wiring."""
from datetime import datetime, timedelta
from uuid import uuid4

from httpx import AsyncClient

from backend.app.models import ServiceTicket


def _payload(ticket_id: str, *, expired: bool = False) -> dict[str, object]:
    """Build a warranty claim payload for an in-warranty or expired product."""
    failure_date = datetime.utcnow() - timedelta(days=5)
    warranty_end = (
        failure_date - timedelta(days=30) if expired else failure_date + timedelta(days=200)
    )
    return {
        "ticket_id": ticket_id,
        "product_serial": "SN-12345",
        "product_model": "RTU-5000",
        "purchase_date": (failure_date - timedelta(days=400)).isoformat(),
        "failure_date": failure_date.isoformat(),
        "warranty_end_date": warranty_end.isoformat(),
        "failure_description": "Compressor malfunction during normal operation",
    }


async def test_create_claim_within_warranty_is_approved(
    client: AsyncClient, ticket: ServiceTicket
) -> None:
    """Test that a claim inside the warranty window is approved with coverage."""
    response = await client.post("/api/warranty/", json=_payload(str(ticket.id)))

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "approved"
    assert body["coverage_percentage"] > 0
    assert body["agent_recommendation"]["confidence"] > 0


async def test_create_claim_after_warranty_expiry_is_rejected(
    client: AsyncClient, ticket: ServiceTicket
) -> None:
    """Test that a claim after warranty expiry is not approved."""
    response = await client.post(
        "/api/warranty/", json=_payload(str(ticket.id), expired=True)
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


async def test_get_and_list_claims(client: AsyncClient, ticket: ServiceTicket) -> None:
    """Test reading a claim and filtering the claim list by status."""
    created = await client.post("/api/warranty/", json=_payload(str(ticket.id)))
    claim_id = created.json()["claim_id"]

    detail = await client.get(f"/api/warranty/{claim_id}")
    listing = await client.get("/api/warranty/")
    filtered = await client.get("/api/warranty/", params={"status": "pending"})

    assert detail.json()["product_model"] == "RTU-5000"
    assert listing.json()["total"] == 1
    assert filtered.json()["total"] == 0


async def test_get_claim_missing_returns_404(client: AsyncClient) -> None:
    """Test that an unknown claim id returns a 404."""
    response = await client.get(f"/api/warranty/{uuid4()}")

    assert response.status_code == 404


async def test_update_claim(client: AsyncClient, ticket: ServiceTicket) -> None:
    """Test a human override of an agent-triaged claim."""
    created = await client.post("/api/warranty/", json=_payload(str(ticket.id)))
    claim_id = created.json()["claim_id"]

    response = await client.patch(
        f"/api/warranty/{claim_id}",
        json={
            "status": "rejected",
            "approved_amount": 0.0,
            "rejection_reason": "Customer-induced damage",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


async def test_update_claim_missing_returns_404(client: AsyncClient) -> None:
    """Test that updating an unknown claim returns a 404."""
    response = await client.patch(f"/api/warranty/{uuid4()}", json={"status": "approved"})

    assert response.status_code == 404
