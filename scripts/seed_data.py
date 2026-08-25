"""Create the database schema and seed demo field service data.

Run with ``make seed``. Safe to re-run: seeding is skipped when technicians
already exist.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select

from backend.app.core.database import Base, async_session_maker, engine
from backend.app.models import Part, ServiceTicket, Technician, WarrantyClaim

TECHNICIANS: list[dict[str, Any]] = [
    {
        "name": "Alicia Nguyen",
        "email": "alicia.nguyen@example.com",
        "phone": "+1-415-555-0111",
        "skills": {
            "skills": [
                {"name": "Elevator Repair", "category": "Mechanical", "level": "expert"},
                {"name": "Safety Compliance", "category": "Regulatory", "level": "advanced"},
            ]
        },
        "home_location": {
            "address": "1 Market St",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94105",
            "latitude": 37.7936,
            "longitude": -122.3965,
        },
        "is_available": True,
        "max_jobs_per_day": 6,
    },
    {
        "name": "Marcus Boyd",
        "email": "marcus.boyd@example.com",
        "phone": "+1-510-555-0122",
        "skills": {
            "skills": [
                {"name": "Hydraulic Systems", "category": "Mechanical", "level": "expert"},
                {"name": "Elevator Repair", "category": "Mechanical", "level": "intermediate"},
            ]
        },
        "home_location": {
            "address": "1200 Broadway",
            "city": "Oakland",
            "state": "CA",
            "zip_code": "94612",
            "latitude": 37.8044,
            "longitude": -122.2712,
        },
        "is_available": True,
        "max_jobs_per_day": 5,
    },
    {
        "name": "Priya Raman",
        "email": "priya.raman@example.com",
        "phone": "+1-650-555-0133",
        "skills": {
            "skills": [
                {"name": "Electrical Systems", "category": "Electrical", "level": "advanced"},
                {"name": "Controller Diagnostics", "category": "Electrical", "level": "expert"},
            ]
        },
        "home_location": {
            "address": "500 El Camino Real",
            "city": "Santa Clara",
            "state": "CA",
            "zip_code": "95050",
            "latitude": 37.3496,
            "longitude": -121.9390,
        },
        "is_available": False,
        "max_jobs_per_day": 6,
    },
]

PARTS: list[dict[str, Any]] = [
    {
        "part_number": "ELV-HYD-100",
        "name": "Hydraulic Pump Assembly",
        "description": "Replacement hydraulic pump for low-rise elevator systems.",
        "category": "Hydraulics",
        "unit_price": 1450.00,
        "quantity_in_stock": 12,
        "reorder_point": 5,
        "reorder_quantity": 10,
        "status": "in_stock",
        "vendor_name": "LiftParts Direct",
        "vendor_part_number": "LP-HYD-100",
        "lead_time_days": 7,
    },
    {
        "part_number": "ELV-CTL-220",
        "name": "Controller Board",
        "description": "Main controller board for traction elevator cabinets.",
        "category": "Electronics",
        "unit_price": 890.00,
        "quantity_in_stock": 3,
        "reorder_point": 6,
        "reorder_quantity": 12,
        "status": "low_stock",
        "vendor_name": "Vertical Systems Supply",
        "vendor_part_number": "VSS-CTL-220",
        "lead_time_days": 14,
    },
    {
        "part_number": "ELV-DOR-045",
        "name": "Door Operator Belt",
        "description": "Drive belt for automatic door operators.",
        "category": "Doors",
        "unit_price": 75.50,
        "quantity_in_stock": 0,
        "reorder_point": 10,
        "reorder_quantity": 25,
        "status": "out_of_stock",
        "vendor_name": "LiftParts Direct",
        "vendor_part_number": "LP-DOR-045",
        "lead_time_days": 3,
    },
]


def _tickets(now: datetime) -> list[dict[str, Any]]:
    """Build demo service tickets covering the main service types."""
    return [
        {
            "title": "Elevator stuck between floors",
            "description": "Car 2 is stuck between floors 4 and 5 with no passengers inside.",
            "service_type": "breakdown",
            "priority": "critical",
            "status": "open",
            "customer_name": "Bayview Tower HOA",
            "customer_phone": "+1-415-555-0180",
            "customer_email": "facilities@bayviewtower.example.com",
            "location_address": "300 Beale St",
            "location_city": "San Francisco",
            "location_state": "CA",
            "location_zip_code": "94105",
            "location_latitude": 37.7887,
            "location_longitude": -122.3899,
            "required_skills": ["Elevator Repair", "Safety Compliance"],
            "estimated_duration_hours": 3.0,
        },
        {
            "title": "Quarterly preventive maintenance",
            "description": "Scheduled inspection and lubrication for two traction units.",
            "service_type": "preventive_maintenance",
            "priority": "medium",
            "status": "open",
            "customer_name": "Lakeside Offices",
            "customer_phone": "+1-510-555-0190",
            "customer_email": "ops@lakesideoffices.example.com",
            "location_address": "1900 Lakeshore Ave",
            "location_city": "Oakland",
            "location_state": "CA",
            "location_zip_code": "94606",
            "location_latitude": 37.8016,
            "location_longitude": -122.2585,
            "required_skills": ["Elevator Repair"],
            "estimated_duration_hours": 4.0,
            "scheduled_start": now + timedelta(days=2),
            "scheduled_end": now + timedelta(days=2, hours=4),
        },
        {
            "title": "Callback: door closes too fast",
            "description": "Follow-up visit after door operator replacement last week.",
            "service_type": "callback",
            "priority": "high",
            "status": "assigned",
            "customer_name": "Peninsula Medical Center",
            "customer_phone": "+1-650-555-0170",
            "customer_email": "engineering@penmed.example.com",
            "location_address": "820 Middlefield Rd",
            "location_city": "Palo Alto",
            "location_state": "CA",
            "location_zip_code": "94301",
            "location_latitude": 37.4419,
            "location_longitude": -122.1430,
            "required_skills": ["Controller Diagnostics"],
            "estimated_duration_hours": 2.0,
        },
    ]


def _warranty_claims(ticket: ServiceTicket, now: datetime) -> list[dict[str, Any]]:
    """Build demo warranty claims covering an in-period and an expired claim."""
    return [
        {
            "ticket_id": ticket.id,
            "product_serial": "SN-88213-A",
            "product_model": "TractionPro 400",
            "purchase_date": now - timedelta(days=200),
            "failure_date": now - timedelta(days=5),
            "warranty_end_date": now + timedelta(days=165),
            "failure_description": "Manufacturing defect in the hoist motor bearing.",
            "status": "pending",
            "estimated_cost": 2400.00,
        },
        {
            "ticket_id": ticket.id,
            "product_serial": "SN-41190-C",
            "product_model": "HydroLift 200",
            "purchase_date": now - timedelta(days=1500),
            "failure_date": now - timedelta(days=10),
            "warranty_end_date": now - timedelta(days=400),
            "failure_description": "Seal failure after the warranty period expired.",
            "status": "pending",
            "estimated_cost": 1100.00,
        },
    ]


async def seed() -> None:
    """Create tables if needed and insert demo data."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    now = datetime.utcnow()

    async with async_session_maker() as session:
        existing = await session.execute(select(Technician.id).limit(1))
        if existing.first() is not None:
            print("Demo data already present; skipping seed.")
            await engine.dispose()
            return

        session.add_all([Technician(**row) for row in TECHNICIANS])
        session.add_all([Part(**row) for row in PARTS])

        tickets = [ServiceTicket(**row) for row in _tickets(now)]
        session.add_all(tickets)
        await session.flush()

        claims = _warranty_claims(tickets[0], now)
        session.add_all([WarrantyClaim(**row) for row in claims])
        await session.commit()

    print(
        f"Seeded {len(TECHNICIANS)} technicians, {len(PARTS)} parts, "
        f"{len(tickets)} service tickets, and {len(claims)} warranty claims."
    )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
