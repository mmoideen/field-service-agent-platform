"""Core domain models for field service operations."""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class SkillLevel(str, Enum):
    """Technician skill proficiency levels."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ServiceType(str, Enum):
    """Types of service work."""
    PREVENTIVE_MAINTENANCE = "preventive_maintenance"
    BREAKDOWN = "breakdown"
    INSTALLATION = "installation"
    CALLBACK = "callback"
    INSPECTION = "inspection"


class TicketStatus(str, Enum):
    """Service ticket lifecycle states."""
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class TicketPriority(str, Enum):
    """Service ticket priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class WarrantyStatus(str, Enum):
    """Warranty claim status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    DISPUTED = "disputed"


class PartStatus(str, Enum):
    """Parts inventory status."""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    ON_ORDER = "on_order"
    DISCONTINUED = "discontinued"


class AgentDecisionStatus(str, Enum):
    """Agent decision lifecycle states."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    OVERRIDDEN = "overridden"


class Location(BaseModel):
    """Geographic location."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str
    city: str
    state: str
    zip_code: str


class Skill(BaseModel):
    """Technician skill definition."""
    name: str
    category: str
    level: SkillLevel


class Technician(BaseModel):
    """Field service technician."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: str
    phone: str
    skills: list[Skill]
    home_location: Location
    current_location: Optional[Location] = None
    is_available: bool = True
    max_jobs_per_day: int = 6
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ServiceTicket(BaseModel):
    """Service work order ticket."""
    id: UUID = Field(default_factory=uuid4)
    title: str
    description: str
    service_type: ServiceType
    priority: TicketPriority
    status: TicketStatus
    customer_name: str
    customer_phone: str
    customer_email: str
    location: Location
    required_skills: list[str]
    estimated_duration_hours: float
    assigned_technician_id: Optional[UUID] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    parts_needed: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WarrantyClaim(BaseModel):
    """Product warranty claim."""
    id: UUID = Field(default_factory=uuid4)
    ticket_id: UUID
    product_serial: str
    product_model: str
    purchase_date: datetime
    failure_date: datetime
    warranty_end_date: datetime
    failure_description: str
    status: WarrantyStatus
    coverage_percentage: float = Field(default=0.0, ge=0, le=100)
    estimated_cost: float
    approved_amount: Optional[float] = None
    rejection_reason: Optional[str] = None
    agent_confidence_score: Optional[float] = None
    reviewed_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Part(BaseModel):
    """Inventory part."""
    id: UUID = Field(default_factory=uuid4)
    part_number: str
    name: str
    description: str
    category: str
    unit_price: float
    quantity_in_stock: int
    reorder_point: int
    reorder_quantity: int
    status: PartStatus
    vendor_name: str
    vendor_part_number: str
    lead_time_days: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AgentDecision(BaseModel):
    """Record of an agent's decision for audit and override."""
    id: UUID = Field(default_factory=uuid4)
    agent_name: str
    decision_type: str
    entity_id: UUID
    entity_type: str
    reasoning: str
    confidence_score: float = Field(..., ge=0, le=1)
    recommendation: dict[str, object]
    status: AgentDecisionStatus = AgentDecisionStatus.PENDING
    human_override_reason: Optional[str] = None
    overridden_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Schedule(BaseModel):
    """Technician schedule entry."""
    id: UUID = Field(default_factory=uuid4)
    technician_id: UUID
    start_time: datetime
    end_time: datetime
    is_available: bool
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
