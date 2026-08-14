"""Parts inventory API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.agents.parts_procurement import PartsProcurementAgent
from backend.app.core.database import get_db
from backend.app.models.part import Part

router = APIRouter()


@router.get("/")
async def list_parts(
    low_stock_only: bool = False,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List all parts with optional low stock filter."""
    query = select(Part)
    if low_stock_only:
        query = query.where(Part.status == "low_stock")

    result = await db.execute(query)
    parts = result.scalars().all()

    return {
        "parts": [
            {
                "id": str(p.id),
                "part_number": p.part_number,
                "name": p.name,
                "category": p.category,
                "quantity_in_stock": p.quantity_in_stock,
                "reorder_point": p.reorder_point,
                "status": p.status,
                "unit_price": p.unit_price,
            }
            for p in parts
        ],
        "total": len(parts),
    }


@router.get("/{part_id}")
async def get_part(
    part_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get a specific part by ID."""
    part = await db.get(Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    return {
        "id": str(part.id),
        "part_number": part.part_number,
        "name": part.name,
        "description": part.description,
        "category": part.category,
        "unit_price": part.unit_price,
        "quantity_in_stock": part.quantity_in_stock,
        "reorder_point": part.reorder_point,
        "reorder_quantity": part.reorder_quantity,
        "status": part.status,
        "vendor_name": part.vendor_name,
        "lead_time_days": part.lead_time_days,
    }


@router.post("/{part_id}/check-procurement")
async def check_procurement(
    part_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Run procurement agent to check if part needs reordering."""
    part = await db.get(Part, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    procurement_agent = PartsProcurementAgent()
    decision = await procurement_agent.execute(
        entity_id=part.id,
        entity_type="part",
        context={
            "part": {
                "quantity_in_stock": part.quantity_in_stock,
                "reorder_point": part.reorder_point,
                "reorder_quantity": part.reorder_quantity,
                "unit_price": part.unit_price,
                "vendor_name": part.vendor_name,
                "lead_time_days": part.lead_time_days,
                "category": part.category,
            }
        },
        db=db,
    )

    return {
        "part_id": str(part.id),
        "part_number": part.part_number,
        "current_stock": part.quantity_in_stock,
        "agent_recommendation": {
            "decision_id": str(decision.id),
            "should_order": decision.recommendation["should_order"],
            "recommended_quantity": decision.recommendation["recommended_quantity"],
            "estimated_cost": decision.recommendation["estimated_cost"],
            "urgency_level": decision.recommendation["urgency_level"],
            "confidence": decision.confidence_score,
            "reasoning": decision.reasoning,
        },
    }
