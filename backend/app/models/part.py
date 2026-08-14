"""Parts inventory database model."""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class Part(Base):
    """Parts inventory database model."""

    __tablename__ = "parts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    part_number: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100))

    unit_price: Mapped[float] = mapped_column(Float)
    quantity_in_stock: Mapped[int] = mapped_column(Integer, default=0)
    reorder_point: Mapped[int] = mapped_column(Integer)
    reorder_quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20))

    vendor_name: Mapped[str] = mapped_column(String(255))
    vendor_part_number: Mapped[str] = mapped_column(String(100))
    lead_time_days: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
