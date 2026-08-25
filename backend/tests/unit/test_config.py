"""Tests for application settings parsing."""
from backend.app.core.config import Settings


def test_cors_origins_accepts_comma_separated_value() -> None:
    """Test that the comma-separated CORS_ORIGINS format from .env.example parses."""
    settings = Settings(cors_origins="http://localhost:5173, https://app.example.com")

    assert settings.cors_origins == ["http://localhost:5173", "https://app.example.com"]


def test_cors_origins_accepts_json_value() -> None:
    """Test that a JSON list value is still supported."""
    settings = Settings(cors_origins='["https://app.example.com"]')

    assert settings.cors_origins == ["https://app.example.com"]


def test_cors_origins_accepts_list_value() -> None:
    """Test that an explicit list is passed through unchanged."""
    settings = Settings(cors_origins=["https://app.example.com"])

    assert settings.cors_origins == ["https://app.example.com"]


def test_is_development_reflects_environment() -> None:
    """Test the development flag derived from the environment name."""
    assert Settings(environment="development").is_development is True
    assert Settings(environment="production").is_development is False
