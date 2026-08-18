"""Agent decision API endpoints."""
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.agent_decision import AgentDecision
from packages.schemas.api import OverrideDecisionRequest

router = APIRouter()


@router.get("/")
async def list_decisions(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List all agent decisions with optional status filter."""
    query = select(AgentDecision).order_by(AgentDecision.created_at.desc())
    if status:
        query = query.where(AgentDecision.status == status)

    result = await db.execute(query)
    decisions = result.scalars().all()

    return {
        "decisions": [
            {
                "id": str(d.id),
                "agent_name": d.agent_name,
                "decision_type": d.decision_type,
                "entity_id": str(d.entity_id),
                "entity_type": d.entity_type,
                "confidence_score": d.confidence_score,
                "status": d.status,
                "created_at": d.created_at.isoformat(),
            }
            for d in decisions
        ],
        "total": len(decisions),
    }


@router.get("/{decision_id}")
async def get_decision(
    decision_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get a specific agent decision by ID."""
    decision = await db.get(AgentDecision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    return {
        "id": str(decision.id),
        "agent_name": decision.agent_name,
        "decision_type": decision.decision_type,
        "entity_id": str(decision.entity_id),
        "entity_type": decision.entity_type,
        "reasoning": decision.reasoning,
        "confidence_score": decision.confidence_score,
        "recommendation": decision.recommendation,
        "status": decision.status,
        "human_override_reason": decision.human_override_reason,
        "overridden_by": decision.overridden_by,
        "created_at": decision.created_at.isoformat(),
        "updated_at": decision.updated_at.isoformat(),
    }


@router.post("/{decision_id}/override")
async def override_decision(
    decision_id: UUID,
    request: OverrideDecisionRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Override an agent decision with human judgment."""
    decision = await db.get(AgentDecision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    if decision.status == "overridden":
        raise HTTPException(
            status_code=400,
            detail="Decision has already been overridden",
        )

    decision.status = "overridden"
    decision.human_override_reason = request.override_reason
    decision.overridden_by = request.overridden_by

    await db.commit()
    await db.refresh(decision)

    return {
        "decision_id": str(decision.id),
        "status": decision.status,
        "overridden_by": decision.overridden_by,
        "message": "Decision overridden successfully",
    }


@router.post("/{decision_id}/approve")
async def approve_decision(
    decision_id: UUID,
    approved_by: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Approve an agent decision."""
    decision = await db.get(AgentDecision, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    decision.status = "approved"
    decision.overridden_by = approved_by

    await db.commit()
    await db.refresh(decision)

    return {
        "decision_id": str(decision.id),
        "status": decision.status,
        "message": "Decision approved successfully",
    }
