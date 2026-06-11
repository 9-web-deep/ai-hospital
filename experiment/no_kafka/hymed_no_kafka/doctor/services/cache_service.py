from __future__ import annotations

import time
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import AsyncIterator

import redis.asyncio as redis

from hymed_no_kafka.config import REDIS_URL


class InMemoryRedisLike:
    def __init__(self):
        self._data: dict[str, tuple[bytes, float | None]] = {}

    async def exists(self, key: str) -> bool:
        value = await self.get(key)
        return value is not None

    async def get(self, key: str) -> bytes | None:
        item = self._data.get(key)
        if not item:
            return None
        value, expire_at = item
        if expire_at is not None and time.time() >= expire_at:
            self._data.pop(key, None)
            return None
        return value

    async def set(self, name: str, value: str, ex: timedelta | int | None = None) -> bool:
        expire_at: float | None = None
        if isinstance(ex, timedelta):
            expire_at = time.time() + ex.total_seconds()
        elif isinstance(ex, int):
            expire_at = time.time() + ex

        self._data[name] = (value.encode("utf-8"), expire_at)
        return True

    async def close(self):
        return None


_in_memory_cache = InMemoryRedisLike()


@asynccontextmanager
async def new_cache_service() -> AsyncIterator[redis.Redis | InMemoryRedisLike]:
    if not REDIS_URL:
        yield _in_memory_cache
        return

    client = redis.from_url(REDIS_URL)
    try:
        yield client
    finally:
        close = getattr(client, "aclose", None)
        if callable(close):
            await close()
        else:
            await client.close()


async def get_cache_service():
    async with new_cache_service() as r:
        yield r


__all__ = ["get_cache_service", "new_cache_service"]
