from typing import Generator

import redis.asyncio as redis

from app.config import REDIS_URL

def new_cache_service() -> redis.Redis:
    return redis.from_url(REDIS_URL)

async def get_cache_service():
    async with new_cache_service() as r:
        yield r

__all__ = ['get_cache_service']
