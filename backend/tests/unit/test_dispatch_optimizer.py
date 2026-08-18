"""Tests for dispatch optimizer agent."""
from uuid import uuid4

import pytest

from backend.app.agents.dispatch_optimizer import DispatchOptimizerAgent
from backend.app.models.ticket import ServiceTicket


@pytest.mark.asyncio
async def test_dispatch_optimizer_calculates_skill_match() -> None:
    """Test that dispatch optimizer correctly calculates skill match."""
    agent = DispatchOptimizerAgent()

    required_skills = ["Elevator Repair", "Safety Compliance"]
    tech_skills = {
        "skills": [
            {"name": "Elevator Repair", "category": "Mechanical", "level": "expert"},
            {"name": "Safety Compliance", "category": "Regulatory", "level": "advanced"},
        ]
    }

    score = agent._calculate_skill_match(required_skills, tech_skills)
    assert score == 1.0


@pytest.mark.asyncio
async def test_dispatch_optimizer_partial_skill_match() -> None:
    """Test partial skill match scoring."""
    agent = DispatchOptimizerAgent()

    required_skills = ["Elevator Repair", "Hydraulic Systems", "Electrical Systems"]
    tech_skills = {
        "skills": [
            {"name": "Elevator Repair", "category": "Mechanical", "level": "expert"},
        ]
    }

    score = agent._calculate_skill_match(required_skills, tech_skills)
    assert abs(score - 0.333) < 0.01


@pytest.mark.asyncio
async def test_haversine_distance_calculation() -> None:
    """Test distance calculation between coordinates."""
    agent = DispatchOptimizerAgent()

    # San Francisco to Oakland (approximately 10 miles)
    sf_lat, sf_lon = 37.7749, -122.4194
    oak_lat, oak_lon = 37.8044, -122.2712

    distance = agent._haversine_distance(sf_lat, sf_lon, oak_lat, oak_lon)

    # Distance should be approximately 10-12 miles
    assert 8 < distance < 15


@pytest.mark.asyncio
async def test_distance_score_decreases_with_distance() -> None:
    """Test that proximity score decreases as distance increases."""
    agent = DispatchOptimizerAgent()

    # Create mock ticket
    ticket = ServiceTicket(
        id=uuid4(),
        title="Test",
        description="Test ticket",
        service_type="breakdown",
        priority="high",
        status="open",
        customer_name="Test Customer",
        customer_phone="555-0000",
        customer_email="test@test.com",
        location_address="100 Main St",
        location_city="San Francisco",
        location_state="CA",
        location_zip_code="94105",
        location_latitude=37.7749,
        location_longitude=-122.4194,
        required_skills=[],
        estimated_duration_hours=2.0,
    )

    # Nearby location (same coordinates)
    nearby_location = {"latitude": 37.7749, "longitude": -122.4194}
    nearby_score = agent._calculate_distance_score(nearby_location, ticket)

    # Far location (100+ miles away)
    far_location = {"latitude": 34.0522, "longitude": -118.2437}  # Los Angeles
    far_score = agent._calculate_distance_score(far_location, ticket)

    assert nearby_score > far_score
    assert nearby_score == 1.0
    assert far_score == 0.0
