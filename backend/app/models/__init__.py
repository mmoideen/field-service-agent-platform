"""Database models.

Every model is re-exported here so importing this package registers all mappers
with the declarative base. Without it, string-based relationships (for example
``ServiceTicket.warranty_claims``) fail to resolve.
"""
from backend.app.models.agent_decision import AgentDecision
from backend.app.models.part import Part
from backend.app.models.technician import Technician
from backend.app.models.ticket import ServiceTicket
from backend.app.models.warranty import WarrantyClaim

__all__ = [
    "AgentDecision",
    "Part",
    "ServiceTicket",
    "Technician",
    "WarrantyClaim",
]
