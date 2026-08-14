"""API request and response schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from packages.domain.models import (
    AgentDecisionStatus,
    PartStatus,
    ServiceType,
    SkillLevel,
    TicketPriority,
    TicketStatus,
    WarrantyStatus,
)


class CreateTicketRequest(BaseModel):
    """Request to create a new service ticket."""
    title: str
    description: str
    service_type: ServiceType
    priority: TicketPriority
    customer_name: str
    customer_phone: str
    customer_email: str
    location_address: str
    location_city: str
    location_state: str
    location_zip_code: str
    location_latitude: float
    location_longitude: float
    required_skills: list[str]
    estimated_duration_hours: float


class UpdateTicketRequest(BaseModel):
    """Request to update a service ticket."""
    status: Optional[TicketStatus] = None
    assigned_technician_id: Optional[UUID] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    parts_needed: Optional[list[str]] = None


class CreateWarrantyClaimRequest(BaseModel):
    """Request to create a warranty claim."""
    ticket_id: UUID
    product_serial: str
    product_model: str
    purchase_date: datetime
    failure_date: datetime
    warranty_end_date: datetime
    failure_description: str


class UpdateWarrantyClaimRequest(BaseModel):
    """Request to update a warranty claim."""
    status: Optional[WarrantyStatus] = None
    approved_amount: Optional[float] = None
    rejection_reason: Optional[str] = None


class AgentDecisionResponse(BaseModel):
    """Response containing an agent decision."""
    id: UUID
    agent_name: str
    decision_type: str
    entity_id: UUID
    entity_type: str
    reasoning: str
    confidence_score: float
    recommendation: dict[str, object]
    status: AgentDecisionStatus
    created_at: datetime


class OverrideDecisionRequest(BaseModel):
    """Request to override an agent decision."""
    override_reason: str
    overridden_by: str
    new_values: Optional[dict[str, object]] = None


class DispatchRecommendation(BaseModel):
    """Dispatch agent recommendation."""
    ticket_id: UUID
    recommended_technician_id: UUID
    confidence_score: float
    reasoning: str
    estimated_arrival_time: datetime
    route_optimization_score: float


class WarrantyTriageResponse(BaseModel):
    """Warranty triage agent response."""
    claim_id: UUID
    recommended_status: WarrantyStatus
    coverage_percentage: float
    confidence_score: float
    reasoning: str
    estimated_cost: float
    risk_factors: list[str]


class ScheduleOptimization(BaseModel):
    """Schedule optimization result."""
    technician_id: UUID
    date: datetime
    recommended_jobs: list[UUID]
    utilization_percentage: float
    travel_time_hours: float
    work_time_hours: float


class PartsProcurementRecommendation(BaseModel):
    """Parts procurement agent recommendation."""
    part_id: UUID
    recommended_order_quantity: int
    vendor_name: str
    estimated_cost: float
    confidence_score: float
    reasoning: str
    urgency_level: str


class TechnicianAvailability(BaseModel):
    """Technician availability status."""
    technician_id: UUID
    technician_name: str
    is_available: bool
    current_location: Optional[dict[str, object]] = None
    jobs_today: int
    next_available: Optional[datetime] = None


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_tickets_open: int
    total_tickets_today: int
    technicians_available: int
    technicians_total: int
    warranty_claims_pending: int
    parts_low_stock: int
    average_response_time_hours: float


class WebSocketMessage(BaseModel):
    """WebSocket message format."""
    type: str
    payload: dict[str, object]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
