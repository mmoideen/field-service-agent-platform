"""Technician database model."""
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class Technician(Base):
    """Technician database model."""

    __tablename__ = "technicians"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str] = mapped_column(String(50))

    skills: Mapped[dict[str, Any]] = mapped_column(JSON)
    home_location: Mapped[dict[str, Any]] = mapped_column(JSON)
    current_location: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    max_jobs_per_day: Mapped[int] = mapped_column(Integer, default=6)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
