"""WebSocket endpoint for real-time dashboard updates."""
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections for real-time updates."""

    def __init__(self) -> None:
        """Initialize connection manager."""
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and store a new WebSocket connection.

        Args:
            websocket: WebSocket connection to accept.
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection to remove.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        """Send a message to a specific connection.

        Args:
            message: Message to send.
            websocket: Target WebSocket connection.
        """
        await websocket.send_text(message)

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Broadcast a message to all connected clients.

        Args:
            message: Message dictionary to broadcast.
        """
        message_str = json.dumps(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message_str)
            except Exception:
                # The client went away without a clean disconnect; drop it so the
                # connection list does not grow unboundedly.
                self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/dashboard")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time dashboard updates.

    Args:
        websocket: WebSocket connection.
    """
    await manager.connect(websocket)
    try:
        # Send initial connection confirmation
        await manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "message": "Connected to Field Service Agent Platform",
            }),
            websocket,
        )

        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()

            # Echo back for now (in production, handle different message types)
            await manager.send_personal_message(
                json.dumps({
                    "type": "echo",
                    "message": f"Received: {data}",
                }),
                websocket,
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def broadcast_agent_decision(decision_data: dict[str, Any]) -> None:
    """Broadcast agent decision to all connected clients.

    Args:
        decision_data: Agent decision data to broadcast.
    """
    await manager.broadcast({
        "type": "agent_decision",
        "payload": decision_data,
    })


async def broadcast_ticket_update(ticket_data: dict[str, Any]) -> None:
    """Broadcast ticket update to all connected clients.

    Args:
        ticket_data: Ticket data to broadcast.
    """
    await manager.broadcast({
        "type": "ticket_update",
        "payload": ticket_data,
    })
