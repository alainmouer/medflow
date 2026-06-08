"""Redis cache / queue abstraction."""
from __future__ import annotations

from typing import Any

from app.core.config import settings

try:
    import redis.asyncio as aioredis

    _redis: aioredis.Redis | None = None
except Exception:  # pragma: no cover
    aioredis = None  # type: ignore[assignment]
    _redis = None


async def get_redis() -> Any | None:
    global _redis
    if aioredis is None or not settings.REDIS_URL:
        return None
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None
