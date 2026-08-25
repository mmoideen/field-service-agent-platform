"""Integration tests for the parts endpoints and procurement agent wiring."""
from uuid import uuid4

from httpx import AsyncClient

from backend.app.models import Part


async def test_list_parts_with_low_stock_filter(client: AsyncClient, part: Part) -> None:
    """Test listing parts and filtering to low stock items."""
    listing = await client.get("/api/parts/")
    low_stock = await client.get("/api/parts/", params={"low_stock_only": True})

    assert listing.json()["total"] == 1
    assert low_stock.json()["parts"][0]["part_number"] == part.part_number


async def test_get_part(client: AsyncClient, part: Part) -> None:
    """Test reading a single part."""
    response = await client.get(f"/api/parts/{part.id}")

    assert response.status_code == 200
    assert response.json()["vendor_name"] == part.vendor_name


async def test_get_part_missing_returns_404(client: AsyncClient) -> None:
    """Test that an unknown part id returns a 404."""
    response = await client.get(f"/api/parts/{uuid4()}")

    assert response.status_code == 404


async def test_check_procurement_recommends_order(client: AsyncClient, part: Part) -> None:
    """Test that a part below its reorder point triggers an order recommendation."""
    response = await client.post(f"/api/parts/{part.id}/check-procurement")

    assert response.status_code == 200
    recommendation = response.json()["agent_recommendation"]
    assert recommendation["should_order"] is True
    assert recommendation["recommended_quantity"] > 0
    assert recommendation["estimated_cost"] > 0
    assert recommendation["urgency_level"]


async def test_check_procurement_missing_returns_404(client: AsyncClient) -> None:
    """Test that procurement checks on an unknown part return a 404."""
    response = await client.post(f"/api/parts/{uuid4()}/check-procurement")

    assert response.status_code == 404
