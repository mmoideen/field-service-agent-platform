"""Tests that the ORM mappers resolve without importing every model module."""
from sqlalchemy.orm import configure_mappers

import backend.app.models  # noqa: F401  (imported for its mapper registration)
from backend.app.models import ServiceTicket


def test_mappers_configure() -> None:
    """Test that string-based relationships resolve from the models package alone."""
    configure_mappers()

    assert "warranty_claims" in ServiceTicket.__mapper__.relationships
