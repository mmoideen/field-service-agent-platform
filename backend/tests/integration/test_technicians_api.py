"""Integration tests for the technician endpoints."""
from uuid import uuid4

from httpx import AsyncClient

from backend.app.models import Technician


async def test_list_technicians_with_availability_filter(
    client: AsyncClient, technician: Technician
) -> None:
    """Test listing technicians and filtering to available ones."""
    listing = await client.get("/api/technicians/")
    available = await client.get("/api/technicians/", params={"available_only": True})

    assert listing.json()["total"] == 1
    assert listing.json()["technicians"][0]["name"] == technician.name
    assert available.json()["total"] == 1


async def test_get_technician(client: AsyncClient, technician: Technician) -> None:
    """Test reading a single technician."""
    response = await client.get(f"/api/technicians/{technician.id}")

    assert response.status_code == 200
    assert response.json()["skills"] == technician.skills


async def test_get_technician_missing_returns_404(client: AsyncClient) -> None:
    """Test that an unknown technician id returns a 404."""
    response = await client.get(f"/api/technicians/{uuid4()}")

    assert response.status_code == 404


async def test_update_availability(client: AsyncClient, technician: Technician) -> None:
    """Test toggling technician availability."""
    response = await client.patch(
        f"/api/technicians/{technician.id}/availability",
        params={"is_available": False},
    )

    assert response.status_code == 200
    assert response.json()["is_available"] is False

    available = await client.get("/api/technicians/", params={"available_only": True})
    assert available.json()["total"] == 0


async def test_update_availability_missing_returns_404(client: AsyncClient) -> None:
    """Test that updating an unknown technician returns a 404."""
    response = await client.patch(
        f"/api/technicians/{uuid4()}/availability", params={"is_available": True}
    )

    assert response.status_code == 404
