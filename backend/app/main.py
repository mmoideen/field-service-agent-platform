"""FastAPI application entry point."""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import agent_decisions, parts, technicians, tickets, warranty, websocket
from backend.app.core.config import settings
from backend.app.core.database import engine
from backend.app.core.redis_client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application lifespan events."""
    # Startup
    await redis_client.connect()
    yield
    # Shutdown
    await redis_client.disconnect()
    await engine.dispose()


app = FastAPI(
    title="Field Service Agent Platform",
    description="Agentic platform for workforce management and field service operations",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
app.include_router(technicians.router, prefix="/api/technicians", tags=["technicians"])
app.include_router(warranty.router, prefix="/api/warranty", tags=["warranty"])
app.include_router(parts.router, prefix="/api/parts", tags=["parts"])
app.include_router(agent_decisions.router, prefix="/api/decisions", tags=["decisions"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "name": "Field Service Agent Platform",
        "version": "0.1.0",
        "status": "operational",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
