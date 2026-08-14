"""Warranty claim triage and assessment agent."""
from datetime import datetime, timedelta
from typing import Any

from backend.app.agents.base import BaseAgent


class WarrantyTriageAgent(BaseAgent):
    """Agent that triages warranty claims and determines coverage."""

    def __init__(self) -> None:
        """Initialize warranty triage agent."""
        super().__init__(
            name="WarrantyTriageAgent",
            decision_type="warranty_assessment",
        )

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Analyze warranty claim and recommend coverage decision.

        Args:
            context: Must contain warranty claim details.

        Returns:
            Dictionary with reasoning, confidence_score, and recommendation.
        """
        claim_data = context["claim"]
        analysis_points = []
        score_factors = {}

        # Check if claim is within warranty period
        warranty_valid = self._check_warranty_validity(
            claim_data["failure_date"],
            claim_data["warranty_end_date"],
        )
        score_factors["warranty_valid"] = 1.0 if warranty_valid else 0.0

        if warranty_valid:
            analysis_points.append(
                "Claim filed within valid warranty period."
            )
        else:
            days_expired = (
                claim_data["failure_date"] - claim_data["warranty_end_date"]
            ).days
            analysis_points.append(
                f"Warranty expired {days_expired} days before failure."
            )

        # Analyze failure description for coverage eligibility
        failure_coverage = self._analyze_failure_type(
            claim_data["failure_description"]
        )
        score_factors["failure_coverage"] = failure_coverage

        if failure_coverage > 0.7:
            analysis_points.append(
                "Failure type typically covered under standard warranty."
            )
        elif failure_coverage > 0.3:
            analysis_points.append(
                "Failure type may have limited coverage. Requires review."
            )
        else:
            analysis_points.append(
                "Failure type typically not covered (user error or abuse)."
            )

        # Check claim timing
        timing_score = self._analyze_claim_timing(
            claim_data["failure_date"],
            datetime.utcnow(),
        )
        score_factors["timing"] = timing_score

        # Calculate overall confidence and recommendation
        confidence = self._calculate_confidence(score_factors)

        if warranty_valid and failure_coverage > 0.7:
            status = "approved"
            coverage_pct = 100.0
            risk_factors = []
        elif warranty_valid and failure_coverage > 0.3:
            status = "pending"
            coverage_pct = 50.0
            risk_factors = ["Requires manual review of failure cause"]
        else:
            status = "rejected"
            coverage_pct = 0.0
            risk_factors = [
                "Warranty expired" if not warranty_valid else "Failure not covered"
            ]

        return {
            "reasoning": self._format_reasoning(analysis_points),
            "confidence_score": confidence,
            "recommendation": {
                "status": status,
                "coverage_percentage": coverage_pct,
                "estimated_cost": claim_data.get("estimated_cost", 0.0),
                "approved_amount": (
                    claim_data.get("estimated_cost", 0.0) * coverage_pct / 100
                ),
                "risk_factors": risk_factors,
            },
        }

    def _check_warranty_validity(
        self, failure_date: datetime, warranty_end: datetime
    ) -> bool:
        """Check if failure occurred within warranty period.

        Args:
            failure_date: Date of failure.
            warranty_end: Warranty end date.

        Returns:
            True if claim is within warranty period.
        """
        return failure_date <= warranty_end

    def _analyze_failure_type(self, description: str) -> float:
        """Analyze failure description to determine coverage likelihood.

        Args:
            description: Failure description text.

        Returns:
            Coverage score between 0 and 1.
        """
        description_lower = description.lower()

        # Keywords indicating likely coverage
        covered_keywords = [
            "defect", "malfunction", "stopped working", "broken",
            "failure", "not responding", "error code"
        ]

        # Keywords indicating likely non-coverage
        excluded_keywords = [
            "dropped", "water damage", "abuse", "misuse",
            "neglect", "unauthorized", "modification"
        ]

        covered_matches = sum(
            1 for kw in covered_keywords if kw in description_lower
        )
        excluded_matches = sum(
            1 for kw in excluded_keywords if kw in description_lower
        )

        if excluded_matches > 0:
            return 0.2

        if covered_matches > 0:
            return 0.9

        # Default to moderate coverage if no clear indicators
        return 0.5

    def _analyze_claim_timing(
        self, failure_date: datetime, claim_date: datetime
    ) -> float:
        """Analyze timing between failure and claim filing.

        Args:
            failure_date: Date of failure.
            claim_date: Date claim was filed.

        Returns:
            Timing score between 0 and 1.
        """
        days_elapsed = (claim_date - failure_date).days

        # Immediate claims are most credible
        if days_elapsed <= 7:
            return 1.0
        elif days_elapsed <= 30:
            return 0.8
        elif days_elapsed <= 90:
            return 0.6
        else:
            return 0.4
