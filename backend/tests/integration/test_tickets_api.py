"""Integration tests for the ticket endpoints and dispatch agent wiring."""
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import AgentDecision, ServiceTicket, Technician

TICKET_PAYLOAD = {
    "title": "Rooftop unit down",
    "description": "Unit trips breaker on start",
    "service_type": "breakdown",
    "priority": "high",
    "customer_name": "Globex",
    "customer_phone": "+1-415-555-0111",
    "customer_email": "facilities@globex.example",
    "location_address": "1 Market St",
    "location_city": "San Francisco",
    "location_state": "CA",
    "location_zip_code": "94105",
    "location_latitude": 37.7936,
    "location_longitude": -122.3965,
    "required_skills": ["hvac"],
    "estimated_duration_hours": 2.5,
}


async def test_health_and_root(client: AsyncClient) -> None:
    """Test the service metadata endpoints."""
    health = await client.get("/health")
    root = await client.get("/")

    assert health.status_code == 200
    assert health.json() == {"status": "healthy"}
    assert root.status_code == 200
    assert root.json()["name"] == "Field Service Agent Platform"


async def test_create_ticket_records_dispatch_decision(
    client: AsyncClient, db_session: AsyncSession, technician: Technician
) -> None:
    """Test that creating a ticket persists the ticket and a dispatch decision."""
    response = await client.post("/api/tickets/", json=TICKET_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    recommendation = body["agent_recommendation"]
    assert recommendation["recommended_technician"] == str(technician.id)
    assert 0.0 < recommendation["confidence"] <= 1.0
    assert recommendation["reasoning"]

    decisions = (await db_session.execute(select(AgentDecision))).scalars().all()
    assert [d.agent_name for d in decisions] == ["DispatchOptimizerAgent"]
    assert decisions[0].entity_id == UUID(body["ticket_id"])


async def test_create_ticket_without_available_technician(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test that dispatch degrades gracefully when nobody can be assigned."""
    response = await client.post("/api/tickets/", json=TICKET_PAYLOAD)

    assert response.status_code == 200
    recommendation = response.json()["agent_recommendation"]
    assert recommendation["recommended_technician"] is None


async def test_get_and_list_tickets(client: AsyncClient, ticket: ServiceTicket) -> None:
    """Test reading a single ticket and filtering the ticket list."""
    detail = await client.get(f"/api/tickets/{ticket.id}")
    listing = await client.get("/api/tickets/")
    filtered = await client.get("/api/tickets/", params={"status": "closed"})

    assert detail.status_code == 200
    assert detail.json()["location"]["city"] == "San Francisco"
    assert listing.json()["total"] == 1
    assert filtered.json()["total"] == 0


async def test_get_ticket_missing_returns_404(client: AsyncClient) -> None:
    """Test that an unknown ticket id returns a 404."""
    response = await client.get(f"/api/tickets/{uuid4()}")

    assert response.status_code == 404


async def test_update_ticket(
    client: AsyncClient, ticket: ServiceTicket, technician: Technician
) -> None:
    """Test updating status, assignment, schedule, and parts on a ticket."""
    start = datetime.utcnow() + timedelta(hours=2)
    payload = {
        "status": "assigned",
        "assigned_technician_id": str(technician.id),
        "scheduled_start": start.isoformat(),
        "scheduled_end": (start + timedelta(hours=2)).isoformat(),
        "parts_needed": ["TEST-001"],
    }

    response = await client.patch(f"/api/tickets/{ticket.id}", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "assigned"


async def test_update_ticket_missing_returns_404(client: AsyncClient) -> None:
    """Test that updating an unknown ticket returns a 404."""
    response = await client.patch(f"/api/tickets/{uuid4()}", json={"status": "cancelled"})

    assert response.status_code == 404
