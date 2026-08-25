"""Tests for the WebSocket connection manager."""
import pytest

from backend.app.api.websocket import ConnectionManager


class FakeWebSocket:
    """Minimal WebSocket stand-in that records sent messages."""

    def __init__(self, fail_on_send: bool = False) -> None:
        """Initialize the fake socket."""
        self.fail_on_send = fail_on_send
        self.accepted = False
        self.sent: list[str] = []

    async def accept(self) -> None:
        """Record that the connection was accepted."""
        self.accepted = True

    async def send_text(self, message: str) -> None:
        """Record a sent message or simulate a dead connection."""
        if self.fail_on_send:
            raise RuntimeError("connection closed")
        self.sent.append(message)


@pytest.mark.asyncio
async def test_connect_accepts_and_tracks_connection() -> None:
    """Test that connecting accepts the socket and tracks it."""
    manager = ConnectionManager()
    socket = FakeWebSocket()

    await manager.connect(socket)  # type: ignore[arg-type]

    assert socket.accepted is True
    assert manager.active_connections == [socket]


@pytest.mark.asyncio
async def test_disconnect_is_idempotent() -> None:
    """Test that disconnecting an unknown socket does not raise."""
    manager = ConnectionManager()
    socket = FakeWebSocket()

    await manager.connect(socket)  # type: ignore[arg-type]
    manager.disconnect(socket)  # type: ignore[arg-type]
    manager.disconnect(socket)  # type: ignore[arg-type]

    assert manager.active_connections == []


@pytest.mark.asyncio
async def test_broadcast_drops_dead_connections() -> None:
    """Test that a failing connection is removed and others still receive."""
    manager = ConnectionManager()
    healthy = FakeWebSocket()
    dead = FakeWebSocket(fail_on_send=True)

    await manager.connect(healthy)  # type: ignore[arg-type]
    await manager.connect(dead)  # type: ignore[arg-type]
    await manager.broadcast({"type": "agent_decision", "payload": {}})

    assert manager.active_connections == [healthy]
    assert healthy.sent == ['{"type": "agent_decision", "payload": {}}']
