"""Shared fixtures for the backend test suite.

Integration tests run against a real PostgreSQL database because the models use
PostgreSQL-specific column types (``ARRAY``). The database name is derived from
``DATABASE_URL`` with a ``_test`` suffix so a development database is never
dropped. Tests are skipped when no server is reachable.
"""
import asyncio
from collections.abc import AsyncGenerator, Generator
from datetime import datetime, timedelta
from urllib.parse import urlsplit, urlunsplit

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from backend.app.core.config import settings
from backend.app.core.database import Base, get_db
from backend.app.main import app
from backend.app.models import Part, ServiceTicket, Technician


def _test_database_url() -> str:
    """Build an asyncpg URL pointing at a dedicated test database."""
    url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    parts = urlsplit(url)
    name = parts.path.lstrip("/") or "fieldservice"
    if not name.endswith("_test"):
        name = f"{name}_test"
    return urlunsplit((parts.scheme, parts.netloc, f"/{name}", parts.query, parts.fragment))


TEST_DATABASE_URL = _test_database_url()


def _engine() -> AsyncEngine:
    """Create a pooling-free engine for the test database."""
    return create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)


async def _create_schema() -> None:
    """Drop and recreate every table in the test database."""
    engine = _engine()
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)
    finally:
        await engine.dispose()


async def _truncate_tables() -> None:
    """Remove all rows so each test starts from a known state."""
    engine = _engine()
    tables = ", ".join(table.name for table in Base.metadata.sorted_tables)
    try:
        async with engine.begin() as connection:
            await connection.execute(text(f"TRUNCATE {tables} CASCADE"))
    finally:
        await engine.dispose()


@pytest.fixture(scope="session")
def database() -> Generator[None, None, None]:
    """Prepare the schema once per session, skipping when PostgreSQL is absent."""
    try:
        asyncio.run(_create_schema())
    except (SQLAlchemyError, OSError) as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"PostgreSQL is not available at {TEST_DATABASE_URL}: {exc}")
    yield


@pytest_asyncio.fixture
async def db_session(database: None) -> AsyncGenerator[AsyncSession, None]:
    """Provide a session against the test database and clean up afterwards."""
    engine = _engine()
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    await engine.dispose()
    await _truncate_tables()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTP client whose requests share the test session."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def technician(db_session: AsyncSession) -> Technician:
    """Create an available technician with matching skills."""
    record = Technician(
        name="Ada Tester",
        email="ada@example.com",
        phone="+1-415-555-0100",
        skills={"hvac": "senior", "electrical": "intermediate"},
        home_location={"latitude": 37.7749, "longitude": -122.4194, "city": "San Francisco"},
        current_location={"latitude": 37.7749, "longitude": -122.4194},
        is_available=True,
        max_jobs_per_day=5,
    )
    db_session.add(record)
    await db_session.commit()
    await db_session.refresh(record)
    return record


@pytest_asyncio.fixture
async def part(db_session: AsyncSession) -> Part:
    """Create a part that is below its reorder point."""
    record = Part(
        part_number="TEST-001",
        name="Compressor Valve",
        description="Replacement valve",
        category="hvac",
        unit_price=125.5,
        quantity_in_stock=2,
        reorder_point=10,
        reorder_quantity=25,
        status="low_stock",
        vendor_name="Acme Supply",
        vendor_part_number="ACME-VLV-9",
        lead_time_days=4,
    )
    db_session.add(record)
    await db_session.commit()
    await db_session.refresh(record)
    return record


@pytest_asyncio.fixture
async def ticket(db_session: AsyncSession) -> ServiceTicket:
    """Create an open service ticket."""
    record = ServiceTicket(
        title="No cooling",
        description="Rooftop unit fails to cool",
        service_type="breakdown",
        priority="high",
        status="open",
        customer_name="Globex",
        customer_phone="+1-415-555-0111",
        customer_email="facilities@globex.example",
        location_address="1 Market St",
        location_city="San Francisco",
        location_state="CA",
        location_zip_code="94105",
        location_latitude=37.7936,
        location_longitude=-122.3965,
        required_skills=["hvac"],
        estimated_duration_hours=2.5,
        scheduled_start=datetime.utcnow() + timedelta(hours=1),
    )
    db_session.add(record)
    await db_session.commit()
    await db_session.refresh(record)
    return record
