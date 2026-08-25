"""Redis client for caching and job queue."""

import redis.asyncio as aioredis

from backend.app.core.config import settings


class RedisClient:
    """Redis client wrapper for async operations."""

    def __init__(self) -> None:
        """Initialize Redis client."""
        self.redis: aioredis.Redis[str] | None = None

    async def connect(self) -> None:
        """Connect to Redis server."""
        self.redis = await aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self) -> None:
        """Disconnect from Redis server."""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> str | None:
        """Get value from Redis."""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        """Set value in Redis with optional expiration."""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        await self.redis.set(key, value, ex=ex)

    async def delete(self, key: str) -> None:
        """Delete key from Redis."""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        await self.redis.delete(key)

    async def push_job(self, queue_name: str, job_data: str) -> None:
        """Push job to queue."""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        await self.redis.lpush(queue_name, job_data)

    async def pop_job(self, queue_name: str, timeout: int = 0) -> str | None:
        """Pop job from queue with optional blocking."""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        result: tuple[str, str] | None = await self.redis.brpop(queue_name, timeout)
        if result:
            return result[1]
        return None


redis_client = RedisClient()
