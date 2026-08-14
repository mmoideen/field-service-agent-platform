"""Tests for parts procurement agent."""
import pytest

from backend.app.agents.parts_procurement import PartsProcurementAgent


@pytest.mark.asyncio
async def test_stock_below_reorder_point() -> None:
    """Test stock level evaluation when below reorder point."""
    agent = PartsProcurementAgent()

    result = agent._evaluate_stock_level(
        current_stock=3,
        reorder_point=10,
        reorder_qty=20,
    )

    assert result["should_order"] is True
    assert result["urgency_score"] > 0.5


@pytest.mark.asyncio
async def test_stock_out() -> None:
    """Test stock level evaluation when out of stock."""
    agent = PartsProcurementAgent()

    result = agent._evaluate_stock_level(
        current_stock=0,
        reorder_point=10,
        reorder_qty=20,
    )

    assert result["should_order"] is True
    assert result["urgency_score"] == 1.0


@pytest.mark.asyncio
async def test_stock_adequate() -> None:
    """Test stock level evaluation when adequate."""
    agent = PartsProcurementAgent()

    result = agent._evaluate_stock_level(
        current_stock=15,
        reorder_point=10,
        reorder_qty=20,
    )

    assert result["should_order"] is False
    assert result["urgency_score"] == 0.0


@pytest.mark.asyncio
async def test_order_quantity_calculation() -> None:
    """Test optimal order quantity calculation."""
    agent = PartsProcurementAgent()

    # Normal stable demand
    qty = agent._calculate_order_quantity(
        base_quantity=10,
        trend="stable",
        urgency=0.5,
    )
    assert qty == 10

    # Increasing demand
    qty_increase = agent._calculate_order_quantity(
        base_quantity=10,
        trend="increasing",
        urgency=0.5,
    )
    assert qty_increase > 10

    # High urgency
    qty_urgent = agent._calculate_order_quantity(
        base_quantity=10,
        trend="stable",
        urgency=0.9,
    )
    assert qty_urgent > 10


@pytest.mark.asyncio
async def test_vendor_evaluation() -> None:
    """Test vendor reliability scoring."""
    agent = PartsProcurementAgent()

    # Fast delivery
    fast_score = agent._evaluate_vendor("FastVendor", lead_time=2)
    assert fast_score > 0.9

    # Slow delivery
    slow_score = agent._evaluate_vendor("SlowVendor", lead_time=20)
    assert slow_score < 0.6

    assert fast_score > slow_score


@pytest.mark.asyncio
async def test_full_procurement_analysis() -> None:
    """Test complete procurement analysis."""
    agent = PartsProcurementAgent()

    context = {
        "part": {
            "quantity_in_stock": 2,
            "reorder_point": 10,
            "reorder_quantity": 20,
            "unit_price": 50.0,
            "vendor_name": "TestVendor",
            "lead_time_days": 5,
            "category": "critical",
        }
    }

    result = await agent.analyze(context)

    assert result["recommendation"]["should_order"] is True
    assert result["recommendation"]["urgency_level"] in ["critical", "high", "normal"]
    assert result["recommendation"]["estimated_cost"] > 0
    assert result["confidence_score"] > 0
