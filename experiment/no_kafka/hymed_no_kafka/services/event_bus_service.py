from __future__ import annotations

import time
from typing import Any
from uuid import uuid4

from hymed_no_kafka.event_queue import publish_event


def obtain_trace_id() -> str:
    return str(uuid4())


class EventBusService:
    """
    no_kafka 事件总线服务：用进程内全局队列代替 Kafka topic。
    """

    async def start(self):
        return None

    async def stop(self):
        return None

    async def send(self, trace_id: str, data: Any):
        copied_data = {**data, **{"trace_id": trace_id, "timestamp": int(time.time())}}
        await publish_event(copied_data)


_event_bus_instance = EventBusService()


def get_event_bus() -> EventBusService:
    return _event_bus_instance


__all__ = ["get_event_bus", "EventBusService", "obtain_trace_id"]

