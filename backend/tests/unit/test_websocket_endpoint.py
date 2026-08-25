"""Tests for the dashboard WebSocket endpoint and broadcast helpers."""
import json

from fastapi import WebSocketDisconnect

from backend.app.api import websocket as websocket_module
from backend.app.api.websocket import (
    broadcast_agent_decision,
    broadcast_ticket_update,
    websocket_endpoint,
)


class ScriptedWebSocket:
    """WebSocket stand-in that replays a script of client messages."""

    def __init__(self, messages: list[str]) -> None:
        """Initialize with the messages the client will send."""
        self._messages = list(messages)
        self.sent: list[dict[str, str]] = []

    async def accept(self) -> None:
        """Accept the connection."""

    async def send_text(self, message: str) -> None:
        """Record a sent message."""
        self.sent.append(json.loads(message))

    async def receive_text(self) -> str:
        """Return the next scripted message, then disconnect."""
        if not self._messages:
            raise WebSocketDisconnect(code=1000)
        return self._messages.pop(0)


async def test_endpoint_confirms_connection_and_echoes() -> None:
    """Test that the endpoint confirms the connection, echoes, and cleans up."""
    socket = ScriptedWebSocket(["ping"])

    await websocket_endpoint(socket)  # type: ignore[arg-type]

    assert socket.sent[0]["type"] == "connection"
    assert socket.sent[1] == {"type": "echo", "message": "Received: ping"}
    assert websocket_module.manager.active_connections == []


async def test_broadcast_helpers_wrap_payloads() -> None:
    """Test that the broadcast helpers tag messages with their event type."""
    socket = ScriptedWebSocket([])
    await websocket_module.manager.connect(socket)  # type: ignore[arg-type]
    try:
        await broadcast_agent_decision({"decision_id": "abc"})
        await broadcast_ticket_update({"ticket_id": "def"})
    finally:
        websocket_module.manager.disconnect(socket)  # type: ignore[arg-type]

    assert socket.sent == [
        {"type": "agent_decision", "payload": {"decision_id": "abc"}},
        {"type": "ticket_update", "payload": {"ticket_id": "def"}},
    ]
