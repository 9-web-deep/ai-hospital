from __future__ import annotations

import asyncio
import uuid
from typing import Any

from loguru import logger

from hymed_no_kafka.administrator.models import OperationJournal
from hymed_no_kafka.db import new_session
from hymed_no_kafka.event_queue import get_event_queue

_logger = logger.bind(tag="AdministratorEventBusService")


class EventBusService:
    def __init__(self):
        self._journal_queue: asyncio.Queue[OperationJournal] = asyncio.Queue(maxsize=1000)
        self._tasks: list[asyncio.Task] = []

    async def _journal_append_worker(self, worker_id: int):
        _logger.info(f"Journal worker {worker_id} startup")
        while True:
            journal = await self._journal_queue.get()
            try:
                async with new_session() as s:
                    s.add(journal)
                    await s.commit()
            except Exception as e:
                _logger.error(f"Journal worker {worker_id} exception: {e}")
            finally:
                self._journal_queue.task_done()

    async def _append_journal(self, data: Any):
        trace_id = data.get("trace_id")
        if isinstance(trace_id, str):
            trace_id = uuid.UUID(trace_id)

        operation_journal = OperationJournal(
            trace_id=trace_id,
            source=data.get("source", "Unknown"),
            user_id=data.get("user_id", ""),
            user_role=data.get("user_role", ""),
            action_code=data.get("action_code", "UNKNOWN"),
            status=data.get("status", 0),
            target_id=data.get("target_id", ""),
            target_role=data.get("target_role", ""),
            payload=data.get("payload") or {},
        )

        await self._journal_queue.put(operation_journal)

    async def _event_worker(self):
        queue = get_event_queue()
        _logger.info("Event worker looping (global queue)")
        while True:
            event = await queue.get()
            try:
                await self._append_journal(event)
            except Exception as e:
                _logger.error(f"Event worker exception: {e}")
            finally:
                queue.task_done()

    async def start(self):
        if self._tasks:
            return
        _logger.info("EventBusService startup")
        self._tasks.append(asyncio.create_task(self._event_worker()))
        self._tasks.extend(asyncio.create_task(self._journal_append_worker(i)) for i in range(4))

    async def stop(self):
        if not self._tasks:
            return
        _logger.info("EventBusService stop")
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()


_event_bus_service_singleton = EventBusService()


def get_event_bus_service() -> EventBusService:
    return _event_bus_service_singleton


__all__ = ["get_event_bus_service", "EventBusService"]

