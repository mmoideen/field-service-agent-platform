"""Application configuration."""

import json
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    # Database
    database_url: str = "postgresql://fieldservice:fieldservice@localhost:5432/fieldservice"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # Agent Configuration
    agent_max_retries: int = 3
    agent_timeout_seconds: int = 300
    agent_confidence_threshold: float = 0.75
    human_override_enabled: bool = True

    # External Integrations
    mcp_enabled: bool = True
    mcp_server_url: str = "http://localhost:3001"
    calendar_integration: str = "mock"
    crm_integration: str = "mock"
    inventory_integration: str = "mock"

    # Logging
    log_level: str = "INFO"
    audit_log_enabled: bool = True

    # Environment
    environment: str = "development"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: object) -> object:
        """Parse CORS_ORIGINS as a comma-separated list (as in .env.example) or JSON."""
        if not isinstance(value, str):
            return value

        stripped = value.strip()
        if stripped.startswith("["):
            return json.loads(stripped)
        return [origin.strip() for origin in stripped.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"


settings = Settings()
