"""Tests for warranty triage agent."""
from datetime import datetime, timedelta

import pytest

from backend.app.agents.warranty_triage import WarrantyTriageAgent


@pytest.mark.asyncio
async def test_warranty_within_period() -> None:
    """Test warranty claim within valid period."""
    agent = WarrantyTriageAgent()

    now = datetime.utcnow()
    failure_date = now - timedelta(days=10)
    warranty_end = now + timedelta(days=100)

    is_valid = agent._check_warranty_validity(failure_date, warranty_end)
    assert is_valid is True


@pytest.mark.asyncio
async def test_warranty_expired() -> None:
    """Test expired warranty claim."""
    agent = WarrantyTriageAgent()

    now = datetime.utcnow()
    failure_date = now - timedelta(days=10)
    warranty_end = now - timedelta(days=50)

    is_valid = agent._check_warranty_validity(failure_date, warranty_end)
    assert is_valid is False


@pytest.mark.asyncio
async def test_failure_type_covered() -> None:
    """Test failure description indicating coverage."""
    agent = WarrantyTriageAgent()

    description = "Product stopped working due to manufacturing defect in motor"
    score = agent._analyze_failure_type(description)

    assert score > 0.7


@pytest.mark.asyncio
async def test_failure_type_excluded() -> None:
    """Test failure description indicating exclusion."""
    agent = WarrantyTriageAgent()

    description = "Device was dropped and has visible water damage from misuse"
    score = agent._analyze_failure_type(description)

    assert score < 0.3


@pytest.mark.asyncio
async def test_claim_timing_immediate() -> None:
    """Test claim filed immediately after failure."""
    agent = WarrantyTriageAgent()

    failure_date = datetime.utcnow() - timedelta(days=2)
    claim_date = datetime.utcnow()

    score = agent._analyze_claim_timing(failure_date, claim_date)
    assert score == 1.0


@pytest.mark.asyncio
async def test_claim_timing_delayed() -> None:
    """Test claim filed long after failure."""
    agent = WarrantyTriageAgent()

    failure_date = datetime.utcnow() - timedelta(days=200)
    claim_date = datetime.utcnow()

    score = agent._analyze_claim_timing(failure_date, claim_date)
    assert score < 0.5


@pytest.mark.asyncio
async def test_full_analysis_approved() -> None:
    """Test complete analysis resulting in approval."""
    agent = WarrantyTriageAgent()

    now = datetime.utcnow()
    context = {
        "claim": {
            "failure_date": now - timedelta(days=5),
            "warranty_end_date": now + timedelta(days=100),
            "failure_description": "Motor failed due to manufacturing defect",
            "estimated_cost": 500.0,
        }
    }

    result = await agent.analyze(context)

    assert result["confidence_score"] > 0.7
    assert result["recommendation"]["status"] == "approved"
    assert result["recommendation"]["coverage_percentage"] == 100.0


@pytest.mark.asyncio
async def test_full_analysis_rejected() -> None:
    """Test complete analysis resulting in rejection."""
    agent = WarrantyTriageAgent()

    now = datetime.utcnow()
    context = {
        "claim": {
            "failure_date": now - timedelta(days=5),
            "warranty_end_date": now - timedelta(days=50),
            "failure_description": "Device dropped and water damaged",
            "estimated_cost": 500.0,
        }
    }

    result = await agent.analyze(context)

    assert result["recommendation"]["status"] == "rejected"
    assert result["recommendation"]["coverage_percentage"] == 0.0
