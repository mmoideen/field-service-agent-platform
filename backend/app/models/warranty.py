"""Warranty claim database model."""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base

if TYPE_CHECKING:
    from backend.app.models.ticket import ServiceTicket


class WarrantyClaim(Base):
    """Warranty claim database model."""

    __tablename__ = "warranty_claims"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    ticket_id: Mapped[UUID] = mapped_column(ForeignKey("service_tickets.id"))

    product_serial: Mapped[str] = mapped_column(String(100))
    product_model: Mapped[str] = mapped_column(String(100))

    purchase_date: Mapped[datetime]
    failure_date: Mapped[datetime]
    warranty_end_date: Mapped[datetime]
    failure_description: Mapped[str] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(20), default="pending")
    coverage_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_cost: Mapped[float] = mapped_column(Float)
    approved_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    agent_confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    ticket: Mapped["ServiceTicket"] = relationship(
        "ServiceTicket", back_populates="warranty_claims"
    )
