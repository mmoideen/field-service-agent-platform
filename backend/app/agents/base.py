"""Base agent class with governance hooks."""
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.models.agent_decision import AgentDecision


class BaseAgent(ABC):
    """Base class for all field service agents with governance and audit."""

    def __init__(self, name: str, decision_type: str) -> None:
        """Initialize base agent.

        Args:
            name: Agent name for identification and logging.
            decision_type: Type of decision this agent makes.
        """
        self.name = name
        self.decision_type = decision_type
        self.max_retries = settings.agent_max_retries
        self.confidence_threshold = settings.agent_confidence_threshold

    @abstractmethod
    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Analyze the context and generate a recommendation.

        Args:
            context: Input context for the agent to analyze.

        Returns:
            Dictionary containing reasoning, confidence_score, and recommendation.
        """
        pass

    async def execute(
        self,
        entity_id: UUID,
        entity_type: str,
        context: dict[str, Any],
        db: AsyncSession,
    ) -> AgentDecision:
        """Execute the agent workflow with governance hooks.

        Args:
            entity_id: ID of the entity being processed.
            entity_type: Type of entity being processed.
            context: Input context for analysis.
            db: Database session for recording decisions.

        Returns:
            AgentDecision record with the agent's recommendation.
        """
        result = await self.analyze(context)

        decision = AgentDecision(
            agent_name=self.name,
            decision_type=self.decision_type,
            entity_id=entity_id,
            entity_type=entity_type,
            reasoning=result["reasoning"],
            confidence_score=result["confidence_score"],
            recommendation=result["recommendation"],
            status="pending",
        )

        db.add(decision)
        await db.commit()
        await db.refresh(decision)

        return decision

    async def override_decision(
        self,
        decision_id: UUID,
        override_reason: str,
        overridden_by: str,
        db: AsyncSession,
    ) -> AgentDecision:
        """Override an agent decision with human judgment.

        Args:
            decision_id: ID of the decision to override.
            override_reason: Reason for the override.
            overridden_by: User who performed the override.
            db: Database session.

        Returns:
            Updated AgentDecision record.
        """
        result = await db.get(AgentDecision, decision_id)
        if not result:
            raise ValueError(f"Decision {decision_id} not found")

        result.status = "overridden"
        result.human_override_reason = override_reason
        result.overridden_by = overridden_by
        result.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(result)

        return result

    def _calculate_confidence(self, factors: dict[str, float]) -> float:
        """Calculate weighted confidence score from multiple factors.

        Args:
            factors: Dictionary of factor names to scores (0-1).

        Returns:
            Weighted average confidence score.
        """
        if not factors:
            return 0.0

        total_weight = len(factors)
        weighted_sum = sum(factors.values())

        return weighted_sum / total_weight

    def _format_reasoning(self, analysis_points: list[str]) -> str:
        """Format reasoning points into a coherent explanation.

        Args:
            analysis_points: List of analysis points.

        Returns:
            Formatted reasoning text.
        """
        return " ".join(analysis_points)
