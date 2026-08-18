"""Agent decision database model."""
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class AgentDecision(Base):
    """Agent decision audit log database model."""

    __tablename__ = "agent_decisions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    agent_name: Mapped[str] = mapped_column(String(100))
    decision_type: Mapped[str] = mapped_column(String(100))

    entity_id: Mapped[UUID]
    entity_type: Mapped[str] = mapped_column(String(50))

    reasoning: Mapped[str] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Float)
    recommendation: Mapped[dict[str, Any]] = mapped_column(JSON)

    status: Mapped[str] = mapped_column(String(20), default="pending")
    human_override_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    overridden_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
