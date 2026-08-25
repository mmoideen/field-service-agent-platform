"""Tests for the Redis client wrapper."""
from typing import Any

import pytest

from backend.app.core import redis_client as redis_module
from backend.app.core.redis_client import RedisClient


class FakeRedis:
    """In-memory stand-in for the async Redis client."""

    def __init__(self) -> None:
        """Initialize the fake store."""
        self.values: dict[str, str] = {}
        self.queues: dict[str, list[str]] = {}
        self.closed = False

    async def get(self, key: str) -> str | None:
        """Return a stored value."""
        return self.values.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        """Store a value."""
        self.values[key] = value

    async def delete(self, key: str) -> None:
        """Remove a value."""
        self.values.pop(key, None)

    async def lpush(self, queue_name: str, job_data: str) -> None:
        """Push a job onto a queue."""
        self.queues.setdefault(queue_name, []).insert(0, job_data)

    async def brpop(self, queue_name: str, timeout: int = 0) -> tuple[str, str] | None:
        """Pop a job from the tail of a queue."""
        queue = self.queues.get(queue_name)
        if not queue:
            return None
        return queue_name, queue.pop()

    async def close(self) -> None:
        """Mark the connection as closed."""
        self.closed = True


@pytest.fixture
def connected_client(monkeypatch: pytest.MonkeyPatch) -> tuple[RedisClient, FakeRedis]:
    """Provide a RedisClient wired to a fake backend."""
    fake = FakeRedis()

    async def fake_from_url(url: str, **kwargs: Any) -> FakeRedis:
        return fake

    monkeypatch.setattr(redis_module.aioredis, "from_url", fake_from_url)
    client = RedisClient()
    client.redis = fake  # type: ignore[assignment]
    return client, fake


async def test_connect_and_disconnect(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that connect builds a client and disconnect closes it."""
    fake = FakeRedis()

    async def fake_from_url(url: str, **kwargs: Any) -> FakeRedis:
        return fake

    monkeypatch.setattr(redis_module.aioredis, "from_url", fake_from_url)
    client = RedisClient()

    await client.connect()
    await client.disconnect()

    assert fake.closed is True


async def test_value_and_queue_round_trip(
    connected_client: tuple[RedisClient, FakeRedis],
) -> None:
    """Test the get/set/delete and job queue helpers."""
    client, _ = connected_client

    await client.set("key", "value", ex=60)
    assert await client.get("key") == "value"
    await client.delete("key")
    assert await client.get("key") is None

    await client.push_job("jobs", "payload")
    assert await client.pop_job("jobs") == "payload"
    assert await client.pop_job("jobs") is None


async def test_operations_require_connection() -> None:
    """Test that every operation fails loudly before connecting."""
    client = RedisClient()

    with pytest.raises(RuntimeError, match="not connected"):
        await client.get("key")
    with pytest.raises(RuntimeError, match="not connected"):
        await client.set("key", "value")
    with pytest.raises(RuntimeError, match="not connected"):
        await client.delete("key")
    with pytest.raises(RuntimeError, match="not connected"):
        await client.push_job("jobs", "payload")
    with pytest.raises(RuntimeError, match="not connected"):
        await client.pop_job("jobs")
