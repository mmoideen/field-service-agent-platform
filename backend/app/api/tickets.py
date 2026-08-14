"""Service ticket API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.agents.dispatch_optimizer import DispatchOptimizerAgent
from backend.app.core.database import get_db
from backend.app.models.ticket import ServiceTicket
from packages.domain.models import Location
from packages.schemas.api import CreateTicketRequest, UpdateTicketRequest

router = APIRouter()


@router.post("/", response_model=dict)
async def create_ticket(
    request: CreateTicketRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Create a new service ticket."""
    ticket = ServiceTicket(
        title=request.title,
        description=request.description,
        service_type=request.service_type.value,
        priority=request.priority.value,
        status="open",
        customer_name=request.customer_name,
        customer_phone=request.customer_phone,
        customer_email=request.customer_email,
        location_address=request.location_address,
        location_city=request.location_city,
        location_state=request.location_state,
        location_zip_code=request.location_zip_code,
        location_latitude=request.location_latitude,
        location_longitude=request.location_longitude,
        required_skills=request.required_skills,
        estimated_duration_hours=request.estimated_duration_hours,
    )

    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    # Trigger dispatch optimization agent
    dispatch_agent = DispatchOptimizerAgent()
    decision = await dispatch_agent.execute(
        entity_id=ticket.id,
        entity_type="service_ticket",
        context={"ticket": ticket, "db": db},
        db=db,
    )

    return {
        "ticket_id": str(ticket.id),
        "status": ticket.status,
        "agent_recommendation": {
            "decision_id": str(decision.id),
            "recommended_technician": decision.recommendation.get("technician_id"),
            "confidence": decision.confidence_score,
            "reasoning": decision.reasoning,
        },
    }


@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get a specific ticket by ID."""
    ticket = await db.get(ServiceTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return {
        "id": str(ticket.id),
        "title": ticket.title,
        "description": ticket.description,
        "service_type": ticket.service_type,
        "priority": ticket.priority,
        "status": ticket.status,
        "customer_name": ticket.customer_name,
        "customer_phone": ticket.customer_phone,
        "customer_email": ticket.customer_email,
        "location": {
            "address": ticket.location_address,
            "city": ticket.location_city,
            "state": ticket.location_state,
            "zip_code": ticket.location_zip_code,
            "latitude": ticket.location_latitude,
            "longitude": ticket.location_longitude,
        },
        "assigned_technician_id": str(ticket.assigned_technician_id) if ticket.assigned_technician_id else None,
        "scheduled_start": ticket.scheduled_start.isoformat() if ticket.scheduled_start else None,
        "scheduled_end": ticket.scheduled_end.isoformat() if ticket.scheduled_end else None,
        "created_at": ticket.created_at.isoformat(),
        "updated_at": ticket.updated_at.isoformat(),
    }


@router.get("/")
async def list_tickets(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List all service tickets with optional status filter."""
    query = select(ServiceTicket)
    if status:
        query = query.where(ServiceTicket.status == status)

    result = await db.execute(query)
    tickets = result.scalars().all()

    return {
        "tickets": [
            {
                "id": str(t.id),
                "title": t.title,
                "service_type": t.service_type,
                "priority": t.priority,
                "status": t.status,
                "customer_name": t.customer_name,
                "created_at": t.created_at.isoformat(),
            }
            for t in tickets
        ],
        "total": len(tickets),
    }


@router.patch("/{ticket_id}")
async def update_ticket(
    ticket_id: UUID,
    request: UpdateTicketRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Update a service ticket."""
    ticket = await db.get(ServiceTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if request.status:
        ticket.status = request.status.value
    if request.assigned_technician_id:
        ticket.assigned_technician_id = request.assigned_technician_id
    if request.scheduled_start:
        ticket.scheduled_start = request.scheduled_start
    if request.scheduled_end:
        ticket.scheduled_end = request.scheduled_end
    if request.parts_needed is not None:
        ticket.parts_needed = request.parts_needed

    await db.commit()
    await db.refresh(ticket)

    return {
        "ticket_id": str(ticket.id),
        "status": ticket.status,
        "message": "Ticket updated successfully",
    }
