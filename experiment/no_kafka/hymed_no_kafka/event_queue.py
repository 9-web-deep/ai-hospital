from __future__ import annotations

import asyncio

from .config import EVENT_QUEUE_MAXSIZE

_event_queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=EVENT_QUEUE_MAXSIZE)


def get_event_queue() -> asyncio.Queue[dict]:
    return _event_queue


async def publish_event(event: dict) -> None:
    await _event_queue.put(event)


__all__ = ["get_event_queue", "publish_event"]

