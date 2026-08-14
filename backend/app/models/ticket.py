"""Service ticket database model."""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ARRAY, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base

if TYPE_CHECKING:
    from backend.app.models.warranty import WarrantyClaim


class ServiceTicket(Base):
    """Service ticket database model."""

    __tablename__ = "service_tickets"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    service_type: Mapped[str] = mapped_column(String(50))
    priority: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="open")

    customer_name: Mapped[str] = mapped_column(String(255))
    customer_phone: Mapped[str] = mapped_column(String(50))
    customer_email: Mapped[str] = mapped_column(String(255))

    location_address: Mapped[str] = mapped_column(String(255))
    location_city: Mapped[str] = mapped_column(String(100))
    location_state: Mapped[str] = mapped_column(String(50))
    location_zip_code: Mapped[str] = mapped_column(String(20))
    location_latitude: Mapped[float] = mapped_column(Float)
    location_longitude: Mapped[float] = mapped_column(Float)

    required_skills: Mapped[list[str]] = mapped_column(ARRAY(String))
    estimated_duration_hours: Mapped[float] = mapped_column(Float)

    assigned_technician_id: Mapped[UUID | None] = mapped_column(nullable=True)
    scheduled_start: Mapped[datetime | None] = mapped_column(nullable=True)
    scheduled_end: Mapped[datetime | None] = mapped_column(nullable=True)
    actual_start: Mapped[datetime | None] = mapped_column(nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(nullable=True)

    parts_needed: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    warranty_claims: Mapped[list["WarrantyClaim"]] = relationship(
        "WarrantyClaim", back_populates="ticket"
    )
