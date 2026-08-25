"""Integration tests for the agent decision endpoints."""
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import AgentDecision


async def _create_decision(db_session: AsyncSession) -> AgentDecision:
    """Persist a pending agent decision."""
    decision = AgentDecision(
        agent_name="dispatch_optimizer",
        decision_type="technician_assignment",
        entity_id=uuid4(),
        entity_type="service_ticket",
        reasoning="Closest available technician with matching skills",
        confidence_score=0.91,
        recommendation={"technician_id": str(uuid4())},
        status="pending",
    )
    db_session.add(decision)
    await db_session.commit()
    await db_session.refresh(decision)
    return decision


async def test_list_decisions_with_status_filter(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test listing decisions and filtering by status."""
    await _create_decision(db_session)

    listing = await client.get("/api/decisions/")
    filtered = await client.get("/api/decisions/", params={"status": "approved"})

    assert listing.json()["total"] == 1
    assert filtered.json()["total"] == 0


async def test_get_decision(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test reading a single decision."""
    decision = await _create_decision(db_session)

    response = await client.get(f"/api/decisions/{decision.id}")

    assert response.status_code == 200
    assert response.json()["confidence_score"] == 0.91


async def test_get_decision_missing_returns_404(client: AsyncClient) -> None:
    """Test that an unknown decision id returns a 404."""
    response = await client.get(f"/api/decisions/{uuid4()}")

    assert response.status_code == 404


async def test_override_decision_once(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test that a decision can be overridden once and not twice."""
    decision = await _create_decision(db_session)
    payload = {"override_reason": "Customer requested a specialist", "overridden_by": "ops@example"}

    first = await client.post(f"/api/decisions/{decision.id}/override", json=payload)
    second = await client.post(f"/api/decisions/{decision.id}/override", json=payload)

    assert first.status_code == 200
    assert first.json()["status"] == "overridden"
    assert second.status_code == 400


async def test_override_decision_missing_returns_404(client: AsyncClient) -> None:
    """Test that overriding an unknown decision returns a 404."""
    response = await client.post(
        f"/api/decisions/{uuid4()}/override",
        json={"override_reason": "n/a", "overridden_by": "ops@example"},
    )

    assert response.status_code == 404


async def test_approve_decision(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test approving a pending decision."""
    decision = await _create_decision(db_session)

    response = await client.post(
        f"/api/decisions/{decision.id}/approve", params={"approved_by": "ops@example"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved"


async def test_approve_decision_missing_returns_404(client: AsyncClient) -> None:
    """Test that approving an unknown decision returns a 404."""
    response = await client.post(
        f"/api/decisions/{uuid4()}/approve", params={"approved_by": "ops@example"}
    )

    assert response.status_code == 404
