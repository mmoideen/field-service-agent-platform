"""Dispatch optimization agent for technician assignment and routing."""
import math
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.agents.base import BaseAgent
from backend.app.models.technician import Technician
from backend.app.models.ticket import ServiceTicket


class DispatchOptimizerAgent(BaseAgent):
    """Agent that optimizes technician dispatch and routing."""

    def __init__(self) -> None:
        """Initialize dispatch optimizer agent."""
        super().__init__(
            name="DispatchOptimizerAgent",
            decision_type="technician_assignment",
        )

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Analyze ticket and recommend optimal technician assignment.

        Args:
            context: Must contain 'ticket' (ServiceTicket) and 'db' (AsyncSession).

        Returns:
            Dictionary with reasoning, confidence_score, and recommendation.
        """
        ticket: ServiceTicket = context["ticket"]
        db: AsyncSession = context["db"]

        result = await db.execute(
            select(Technician).where(Technician.is_available == True)  # noqa: E712
        )
        available_techs = result.scalars().all()

        if not available_techs:
            return {
                "reasoning": "No technicians currently available for assignment.",
                "confidence_score": 0.0,
                "recommendation": {
                    "technician_id": None,
                    "estimated_arrival": None,
                    "route_score": 0.0,
                },
            }

        best_tech = None
        best_score = 0.0
        analysis_points = []

        for tech in available_techs:
            score_factors = {}

            skill_match = self._calculate_skill_match(
                ticket.required_skills, tech.skills
            )
            score_factors["skill_match"] = skill_match

            distance_score = self._calculate_distance_score(
                tech.home_location, ticket
            )
            score_factors["proximity"] = distance_score

            workload_score = self._calculate_workload_score(tech)
            score_factors["workload"] = workload_score

            overall_score = self._calculate_confidence(score_factors)

            if overall_score > best_score:
                best_score = overall_score
                best_tech = tech

        if best_tech:
            travel_time = self._estimate_travel_time(
                best_tech.home_location, ticket
            )
            estimated_arrival = datetime.utcnow() + travel_time

            analysis_points.append(
                f"Selected {best_tech.name} based on skill match, proximity, and current workload."
            )
            analysis_points.append(
                f"Estimated travel time: {travel_time.seconds // 60} minutes."
            )
            analysis_points.append(
                f"Overall confidence score: {best_score:.2f}"
            )

            return {
                "reasoning": self._format_reasoning(analysis_points),
                "confidence_score": best_score,
                "recommendation": {
                    "technician_id": str(best_tech.id),
                    "technician_name": best_tech.name,
                    "estimated_arrival": estimated_arrival.isoformat(),
                    "route_score": best_score,
                },
            }

        return {
            "reasoning": "No suitable technician found for this ticket.",
            "confidence_score": 0.0,
            "recommendation": {
                "technician_id": None,
                "estimated_arrival": None,
                "route_score": 0.0,
            },
        }

    def _calculate_skill_match(
        self, required: list[str], tech_skills: dict[str, Any]
    ) -> float:
        """Calculate how well technician skills match requirements.

        Args:
            required: List of required skill names.
            tech_skills: Technician's skills dictionary.

        Returns:
            Skill match score between 0 and 1.
        """
        if not required:
            return 1.0

        tech_skill_names = {skill["name"] for skill in tech_skills.get("skills", [])}
        matches = sum(1 for skill in required if skill in tech_skill_names)

        return matches / len(required)

    def _calculate_distance_score(
        self, tech_location: dict[str, Any], ticket: ServiceTicket
    ) -> float:
        """Calculate proximity score based on distance.

        Args:
            tech_location: Technician home location.
            ticket: Service ticket with location.

        Returns:
            Proximity score between 0 and 1.
        """
        tech_lat = tech_location.get("latitude", 0)
        tech_lon = tech_location.get("longitude", 0)

        distance = self._haversine_distance(
            tech_lat, tech_lon,
            ticket.location_latitude, ticket.location_longitude
        )

        # Score decreases with distance. Max score at 0 miles, 0 at 100+ miles.
        if distance >= 100:
            return 0.0

        return 1.0 - (distance / 100)

    def _haversine_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two coordinates in miles.

        Args:
            lat1: First latitude.
            lon1: First longitude.
            lat2: Second latitude.
            lon2: Second longitude.

        Returns:
            Distance in miles.
        """
        R = 3959  # Earth radius in miles

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _calculate_workload_score(self, tech: Technician) -> float:
        """Calculate workload score based on current job load.

        Args:
            tech: Technician model.

        Returns:
            Workload score between 0 and 1.
        """
        # For this implementation, we assume lighter workload is better.
        # In production, this would query current assignments.
        return 0.8

    def _estimate_travel_time(
        self, tech_location: dict[str, Any], ticket: ServiceTicket
    ) -> timedelta:
        """Estimate travel time to ticket location.

        Args:
            tech_location: Technician location.
            ticket: Service ticket.

        Returns:
            Estimated travel time.
        """
        distance = self._haversine_distance(
            tech_location.get("latitude", 0),
            tech_location.get("longitude", 0),
            ticket.location_latitude,
            ticket.location_longitude,
        )

        # Assume average speed of 30 mph
        hours = distance / 30
        return timedelta(hours=hours)
