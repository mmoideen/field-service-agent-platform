"""Warranty claim API endpoints."""
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.agents.warranty_triage import WarrantyTriageAgent
from backend.app.core.database import get_db
from backend.app.models.warranty import WarrantyClaim
from packages.schemas.api import CreateWarrantyClaimRequest, UpdateWarrantyClaimRequest

router = APIRouter()


@router.post("/", response_model=dict)
async def create_warranty_claim(
    request: CreateWarrantyClaimRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Create a new warranty claim and run triage agent."""
    claim = WarrantyClaim(
        ticket_id=request.ticket_id,
        product_serial=request.product_serial,
        product_model=request.product_model,
        purchase_date=request.purchase_date,
        failure_date=request.failure_date,
        warranty_end_date=request.warranty_end_date,
        failure_description=request.failure_description,
        status="pending",
        estimated_cost=0.0,  # Will be updated by agent
    )

    db.add(claim)
    await db.commit()
    await db.refresh(claim)

    # Run warranty triage agent
    triage_agent = WarrantyTriageAgent()
    decision = await triage_agent.execute(
        entity_id=claim.id,
        entity_type="warranty_claim",
        context={
            "claim": {
                "failure_date": request.failure_date,
                "warranty_end_date": request.warranty_end_date,
                "failure_description": request.failure_description,
                "estimated_cost": 500.0,  # Placeholder
            }
        },
        db=db,
    )

    # Update claim with agent recommendation
    recommendation = decision.recommendation
    claim.status = recommendation["status"]
    claim.coverage_percentage = recommendation["coverage_percentage"]
    claim.estimated_cost = recommendation["estimated_cost"]
    claim.approved_amount = recommendation.get("approved_amount")
    claim.agent_confidence_score = decision.confidence_score

    await db.commit()
    await db.refresh(claim)

    return {
        "claim_id": str(claim.id),
        "status": claim.status,
        "coverage_percentage": claim.coverage_percentage,
        "agent_recommendation": {
            "decision_id": str(decision.id),
            "confidence": decision.confidence_score,
            "reasoning": decision.reasoning,
            "risk_factors": recommendation.get("risk_factors", []),
        },
    }


@router.get("/{claim_id}")
async def get_warranty_claim(
    claim_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get a specific warranty claim by ID."""
    claim = await db.get(WarrantyClaim, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Warranty claim not found")

    return {
        "id": str(claim.id),
        "ticket_id": str(claim.ticket_id),
        "product_serial": claim.product_serial,
        "product_model": claim.product_model,
        "purchase_date": claim.purchase_date.isoformat(),
        "failure_date": claim.failure_date.isoformat(),
        "warranty_end_date": claim.warranty_end_date.isoformat(),
        "failure_description": claim.failure_description,
        "status": claim.status,
        "coverage_percentage": claim.coverage_percentage,
        "estimated_cost": claim.estimated_cost,
        "approved_amount": claim.approved_amount,
        "agent_confidence_score": claim.agent_confidence_score,
        "created_at": claim.created_at.isoformat(),
    }


@router.get("/")
async def list_warranty_claims(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List all warranty claims with optional status filter."""
    query = select(WarrantyClaim)
    if status:
        query = query.where(WarrantyClaim.status == status)

    result = await db.execute(query)
    claims = result.scalars().all()

    return {
        "claims": [
            {
                "id": str(c.id),
                "ticket_id": str(c.ticket_id),
                "product_model": c.product_model,
                "status": c.status,
                "coverage_percentage": c.coverage_percentage,
                "estimated_cost": c.estimated_cost,
                "created_at": c.created_at.isoformat(),
            }
            for c in claims
        ],
        "total": len(claims),
    }


@router.patch("/{claim_id}")
async def update_warranty_claim(
    claim_id: UUID,
    request: UpdateWarrantyClaimRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Update a warranty claim (typically for human override)."""
    claim = await db.get(WarrantyClaim, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Warranty claim not found")

    if request.status:
        claim.status = request.status.value
    if request.approved_amount is not None:
        claim.approved_amount = request.approved_amount
    if request.rejection_reason:
        claim.rejection_reason = request.rejection_reason

    await db.commit()
    await db.refresh(claim)

    return {
        "claim_id": str(claim.id),
        "status": claim.status,
        "message": "Warranty claim updated successfully",
    }
