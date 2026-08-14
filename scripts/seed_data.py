"""Seed database with realistic field service demo data."""
import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from backend.app.core.database import async_session_maker, engine
from backend.app.core.database import Base
from backend.app.models.part import Part
from backend.app.models.technician import Technician
from backend.app.models.ticket import ServiceTicket
from backend.app.models.warranty import WarrantyClaim


async def create_tables() -> None:
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_technicians() -> list[str]:
    """Seed technicians with skills and locations."""
    technicians_data = [
        {
            "name": "Sarah Chen",
            "email": "sarah.chen@fieldservice.com",
            "phone": "555-0101",
            "skills": {
                "skills": [
                    {"name": "Elevator Repair", "category": "Mechanical", "level": "expert"},
                    {"name": "Hydraulic Systems", "category": "Mechanical", "level": "advanced"},
                    {"name": "Safety Compliance", "category": "Regulatory", "level": "expert"},
                ]
            },
            "home_location": {
                "latitude": 37.7749,
                "longitude": -122.4194,
                "address": "123 Market St, San Francisco, CA 94102",
            },
        },
        {
            "name": "Marcus Thompson",
            "email": "marcus.t@fieldservice.com",
            "phone": "555-0102",
            "skills": {
                "skills": [
                    {"name": "Elevator Repair", "category": "Mechanical", "level": "advanced"},
                    {"name": "Electrical Systems", "category": "Electrical", "level": "expert"},
                    {"name": "Modernization", "category": "Installation", "level": "intermediate"},
                ]
            },
            "home_location": {
                "latitude": 37.8044,
                "longitude": -122.2712,
                "address": "456 Broadway, Oakland, CA 94612",
            },
        },
        {
            "name": "Jennifer Kim",
            "email": "j.kim@fieldservice.com",
            "phone": "555-0103",
            "skills": {
                "skills": [
                    {"name": "Preventive Maintenance", "category": "Maintenance", "level": "expert"},
                    {"name": "Diagnostics", "category": "Technical", "level": "advanced"},
                ]
            },
            "home_location": {
                "latitude": 37.3382,
                "longitude": -121.8863,
                "address": "789 First St, San Jose, CA 95113",
            },
        },
    ]

    technician_ids = []
    async with async_session_maker() as session:
        for tech_data in technicians_data:
            tech = Technician(**tech_data, is_available=True)
            session.add(tech)
            technician_ids.append(str(tech.id))

        await session.commit()

    print(f"Seeded {len(technicians_data)} technicians")
    return technician_ids


async def seed_tickets(technician_ids: list[str]) -> list[str]:
    """Seed service tickets with various statuses."""
    tickets_data = [
        {
            "title": "Emergency elevator stuck on floor 12",
            "description": "Passenger elevator stuck between floors 12 and 13. 3 people trapped.",
            "service_type": "breakdown",
            "priority": "critical",
            "status": "open",
            "customer_name": "Downtown Office Tower",
            "customer_phone": "555-1001",
            "customer_email": "facility@downtowntower.com",
            "location_address": "100 Main St",
            "location_city": "San Francisco",
            "location_state": "CA",
            "location_zip_code": "94105",
            "location_latitude": 37.7897,
            "location_longitude": -122.3972,
            "required_skills": ["Elevator Repair", "Safety Compliance"],
            "estimated_duration_hours": 4.0,
        },
        {
            "title": "Scheduled preventive maintenance",
            "description": "Quarterly PM for all 6 elevators in building.",
            "service_type": "preventive_maintenance",
            "priority": "medium",
            "status": "assigned",
            "customer_name": "Tech Plaza",
            "customer_phone": "555-1002",
            "customer_email": "ops@techplaza.com",
            "location_address": "500 Market St",
            "location_city": "San Francisco",
            "location_state": "CA",
            "location_zip_code": "94102",
            "location_latitude": 37.7625,
            "location_longitude": -122.4155,
            "required_skills": ["Preventive Maintenance"],
            "estimated_duration_hours": 6.0,
            "assigned_technician_id": technician_ids[0] if technician_ids else None,
            "scheduled_start": datetime.utcnow() + timedelta(days=1),
        },
        {
            "title": "Door sensor malfunction",
            "description": "Elevator doors not closing properly, sensor may need replacement.",
            "service_type": "breakdown",
            "priority": "high",
            "status": "open",
            "customer_name": "Medical Center West",
            "customer_phone": "555-1003",
            "customer_email": "maintenance@medwest.org",
            "location_address": "200 Health Blvd",
            "location_city": "Oakland",
            "location_state": "CA",
            "location_zip_code": "94607",
            "location_latitude": 37.8100,
            "location_longitude": -122.2620,
            "required_skills": ["Electrical Systems", "Diagnostics"],
            "estimated_duration_hours": 2.5,
        },
    ]

    ticket_ids = []
    async with async_session_maker() as session:
        for ticket_data in tickets_data:
            if "assigned_technician_id" in ticket_data and ticket_data["assigned_technician_id"]:
                ticket_data["assigned_technician_id"] = uuid4()  # Convert to UUID

            ticket = ServiceTicket(**ticket_data)
            session.add(ticket)
            ticket_ids.append(str(ticket.id))

        await session.commit()

    print(f"Seeded {len(tickets_data)} service tickets")
    return ticket_ids


async def seed_warranty_claims(ticket_ids: list[str]) -> None:
    """Seed warranty claims for some tickets."""
    if not ticket_ids:
        print("No tickets to create warranty claims for")
        return

    claims_data = [
        {
            "ticket_id": ticket_ids[0] if len(ticket_ids) > 0 else uuid4(),
            "product_serial": "ELV-2023-4512",
            "product_model": "Otis Gen2",
            "purchase_date": datetime.utcnow() - timedelta(days=500),
            "failure_date": datetime.utcnow() - timedelta(days=2),
            "warranty_end_date": datetime.utcnow() + timedelta(days=100),
            "failure_description": "Main drive belt failed due to manufacturing defect",
            "status": "pending",
            "estimated_cost": 1500.00,
        },
        {
            "ticket_id": ticket_ids[1] if len(ticket_ids) > 1 else uuid4(),
            "product_serial": "ELV-2021-3301",
            "product_model": "Schindler 3300",
            "purchase_date": datetime.utcnow() - timedelta(days=1200),
            "failure_date": datetime.utcnow() - timedelta(days=5),
            "warranty_end_date": datetime.utcnow() - timedelta(days=100),
            "failure_description": "Control board failure, possibly water damage",
            "status": "pending",
            "estimated_cost": 2200.00,
        },
    ]

    async with async_session_maker() as session:
        for claim_data in claims_data:
            claim = WarrantyClaim(**claim_data)
            session.add(claim)

        await session.commit()

    print(f"Seeded {len(claims_data)} warranty claims")


async def seed_parts() -> None:
    """Seed parts inventory."""
    parts_data = [
        {
            "part_number": "BLT-DR-2000",
            "name": "Main Drive Belt",
            "description": "Reinforced drive belt for hydraulic elevators",
            "category": "Mechanical",
            "unit_price": 450.00,
            "quantity_in_stock": 3,
            "reorder_point": 5,
            "reorder_quantity": 10,
            "status": "low_stock",
            "vendor_name": "ElevatorParts Inc",
            "vendor_part_number": "EPD-2000",
            "lead_time_days": 5,
        },
        {
            "part_number": "SNS-DR-450",
            "name": "Door Sensor Assembly",
            "description": "Infrared door safety sensor with mounting bracket",
            "category": "Electrical",
            "unit_price": 180.00,
            "quantity_in_stock": 12,
            "reorder_point": 8,
            "reorder_quantity": 15,
            "status": "in_stock",
            "vendor_name": "SafeSense Systems",
            "vendor_part_number": "SS-DS-450",
            "lead_time_days": 3,
        },
        {
            "part_number": "CTL-BRD-800",
            "name": "Main Control Board",
            "description": "Programmable logic controller for elevator operation",
            "category": "Electronics",
            "unit_price": 1200.00,
            "quantity_in_stock": 1,
            "reorder_point": 2,
            "reorder_quantity": 5,
            "status": "low_stock",
            "vendor_name": "ControlTech Solutions",
            "vendor_part_number": "CTS-MCB-800",
            "lead_time_days": 10,
        },
        {
            "part_number": "HYD-OIL-55G",
            "name": "Hydraulic Oil (55 gal)",
            "description": "Premium synthetic hydraulic oil for elevator systems",
            "category": "Fluids",
            "unit_price": 320.00,
            "quantity_in_stock": 0,
            "reorder_point": 3,
            "reorder_quantity": 6,
            "status": "out_of_stock",
            "vendor_name": "HydroSupply Co",
            "vendor_part_number": "HS-HO-55G",
            "lead_time_days": 2,
        },
    ]

    async with async_session_maker() as session:
        for part_data in parts_data:
            part = Part(**part_data)
            session.add(part)

        await session.commit()

    print(f"Seeded {len(parts_data)} parts")


async def main() -> None:
    """Run all seed functions."""
    print("Starting database seeding...")

    await create_tables()
    print("Database tables created")

    technician_ids = await seed_technicians()
    ticket_ids = await seed_tickets(technician_ids)
    await seed_warranty_claims(ticket_ids)
    await seed_parts()

    print("\nDatabase seeding completed successfully!")
    print("\nYou can now:")
    print("1. Start the backend: make run")
    print("2. Start the frontend: make run-frontend")
    print("3. Access the dashboard at http://localhost:5173")


if __name__ == "__main__":
    asyncio.run(main())
