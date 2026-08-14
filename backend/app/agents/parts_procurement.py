"""Parts procurement and inventory management agent."""
from typing import Any

from backend.app.agents.base import BaseAgent


class PartsProcurementAgent(BaseAgent):
    """Agent that manages parts inventory and procurement decisions."""

    def __init__(self) -> None:
        """Initialize parts procurement agent."""
        super().__init__(
            name="PartsProcurementAgent",
            decision_type="parts_procurement",
        )

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Analyze parts inventory and recommend procurement action.

        Args:
            context: Must contain part inventory data.

        Returns:
            Dictionary with reasoning, confidence_score, and recommendation.
        """
        part_data = context["part"]
        analysis_points = []
        score_factors = {}

        # Check current stock level against reorder point
        stock_status = self._evaluate_stock_level(
            part_data["quantity_in_stock"],
            part_data["reorder_point"],
            part_data["reorder_quantity"],
        )
        score_factors["stock_urgency"] = stock_status["urgency_score"]

        analysis_points.append(stock_status["analysis"])

        # Analyze historical usage patterns (simulated for now)
        usage_pattern = self._analyze_usage_pattern(part_data)
        score_factors["usage_confidence"] = usage_pattern["confidence"]

        analysis_points.append(usage_pattern["analysis"])

        # Evaluate vendor reliability and lead time
        vendor_score = self._evaluate_vendor(
            part_data["vendor_name"],
            part_data["lead_time_days"],
        )
        score_factors["vendor_reliability"] = vendor_score

        # Calculate order quantity
        recommended_quantity = self._calculate_order_quantity(
            part_data["reorder_quantity"],
            usage_pattern["trend"],
            stock_status["urgency_score"],
        )

        estimated_cost = recommended_quantity * part_data["unit_price"]

        confidence = self._calculate_confidence(score_factors)

        urgency_level = "critical" if stock_status["urgency_score"] > 0.8 else (
            "high" if stock_status["urgency_score"] > 0.5 else "normal"
        )

        return {
            "reasoning": self._format_reasoning(analysis_points),
            "confidence_score": confidence,
            "recommendation": {
                "should_order": stock_status["should_order"],
                "recommended_quantity": recommended_quantity,
                "vendor_name": part_data["vendor_name"],
                "estimated_cost": estimated_cost,
                "urgency_level": urgency_level,
                "expected_delivery_days": part_data["lead_time_days"],
            },
        }

    def _evaluate_stock_level(
        self, current_stock: int, reorder_point: int, reorder_qty: int
    ) -> dict[str, Any]:
        """Evaluate current stock level and urgency.

        Args:
            current_stock: Current quantity in stock.
            reorder_point: Reorder threshold.
            reorder_qty: Standard reorder quantity.

        Returns:
            Dictionary with urgency score and analysis.
        """
        if current_stock == 0:
            return {
                "should_order": True,
                "urgency_score": 1.0,
                "analysis": f"Part is out of stock. Immediate reorder required.",
            }
        elif current_stock < reorder_point:
            urgency = 1.0 - (current_stock / reorder_point)
            return {
                "should_order": True,
                "urgency_score": urgency,
                "analysis": (
                    f"Stock level ({current_stock}) below reorder point "
                    f"({reorder_point}). Reorder recommended."
                ),
            }
        else:
            return {
                "should_order": False,
                "urgency_score": 0.0,
                "analysis": f"Stock level ({current_stock}) adequate.",
            }

    def _analyze_usage_pattern(self, part_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze historical usage patterns to predict future needs.

        Args:
            part_data: Part inventory data.

        Returns:
            Dictionary with trend and confidence.
        """
        # In production, this would analyze actual usage history.
        # For now, we simulate based on category.
        category = part_data.get("category", "general")

        if category in ["critical", "high_usage"]:
            return {
                "trend": "increasing",
                "confidence": 0.85,
                "analysis": "High usage category with steady demand pattern.",
            }
        elif category == "seasonal":
            return {
                "trend": "variable",
                "confidence": 0.65,
                "analysis": "Seasonal demand pattern detected.",
            }
        else:
            return {
                "trend": "stable",
                "confidence": 0.75,
                "analysis": "Stable usage pattern with predictable demand.",
            }

    def _evaluate_vendor(self, vendor_name: str, lead_time: int) -> float:
        """Evaluate vendor reliability.

        Args:
            vendor_name: Vendor name.
            lead_time: Lead time in days.

        Returns:
            Vendor reliability score between 0 and 1.
        """
        # In production, this would query vendor performance metrics.
        # Penalize very long lead times.
        if lead_time <= 3:
            return 0.95
        elif lead_time <= 7:
            return 0.85
        elif lead_time <= 14:
            return 0.70
        else:
            return 0.50

    def _calculate_order_quantity(
        self, base_quantity: int, trend: str, urgency: float
    ) -> int:
        """Calculate optimal order quantity.

        Args:
            base_quantity: Standard reorder quantity.
            trend: Usage trend (increasing, stable, decreasing).
            urgency: Urgency score.

        Returns:
            Recommended order quantity.
        """
        quantity = base_quantity

        if trend == "increasing":
            quantity = int(quantity * 1.5)
        elif trend == "decreasing":
            quantity = int(quantity * 0.75)

        if urgency > 0.8:
            # Add buffer for critical situations
            quantity = int(quantity * 1.2)

        return max(quantity, 1)
