"""Technician API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.models.technician import Technician

router = APIRouter()


@router.get("/")
async def list_technicians(
    available_only: bool = False,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List all technicians with optional availability filter."""
    query = select(Technician)
    if available_only:
        query = query.where(Technician.is_available == True)  # noqa: E712

    result = await db.execute(query)
    technicians = result.scalars().all()

    return {
        "technicians": [
            {
                "id": str(t.id),
                "name": t.name,
                "email": t.email,
                "phone": t.phone,
                "is_available": t.is_available,
                "skills": t.skills,
                "home_location": t.home_location,
                "current_location": t.current_location,
            }
            for t in technicians
        ],
        "total": len(technicians),
    }


@router.get("/{technician_id}")
async def get_technician(
    technician_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get a specific technician by ID."""
    technician = await db.get(Technician, technician_id)
    if not technician:
        raise HTTPException(status_code=404, detail="Technician not found")

    return {
        "id": str(technician.id),
        "name": technician.name,
        "email": technician.email,
        "phone": technician.phone,
        "skills": technician.skills,
        "home_location": technician.home_location,
        "current_location": technician.current_location,
        "is_available": technician.is_available,
        "max_jobs_per_day": technician.max_jobs_per_day,
        "created_at": technician.created_at.isoformat(),
    }


@router.patch("/{technician_id}/availability")
async def update_availability(
    technician_id: UUID,
    is_available: bool,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Update technician availability status."""
    technician = await db.get(Technician, technician_id)
    if not technician:
        raise HTTPException(status_code=404, detail="Technician not found")

    technician.is_available = is_available
    await db.commit()

    return {
        "technician_id": str(technician.id),
        "is_available": is_available,
        "message": "Availability updated successfully",
    }
