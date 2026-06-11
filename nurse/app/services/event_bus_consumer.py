from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any

from aiokafka import AIOKafkaConsumer
from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.config import KAFKA_BOOTSTRAP_SERVER
from app.db import new_session
from app.models import DispensingTask, InfusionTask

_logger = logger.bind(tag="EventBusConsumer")

_TOPIC = "event_bus"
_GROUP_ID = "Nurse"

_ACTION_DOCTOR_DISPENSING_CREATE = "doctor_dispensing_task_create"
_ACTION_NURSE_REQUEST_DISPENSING = "nurse_request_dispensing"
_ACTION_DOCTOR_INFUSION_CREATE = "doctor_infusion_task_create"


class EventBusConsumer:
    """
    护士端 Kafka 事件消费者（合并版）：
    - 单个 consumer 订阅 event_bus，按 action_code 分发到不同处理逻辑
    - 避免多个 consumer 共用一个 group_id 时“抢分区+过滤+提交 offset”导致丢消息
    """

    def __init__(self, bootstrap_servers: str = KAFKA_BOOTSTRAP_SERVER):
        self._bootstrap_servers = bootstrap_servers

    @staticmethod
    def _get_task_id(data: dict[str, Any]) -> str | None:
        task_id = data.get("trace_id")
        if isinstance(task_id, str) and task_id:
            return task_id
        return None

    @staticmethod
    def _get_created_time(data: dict[str, Any]) -> datetime:
        ts = data.get("timestamp")
        if isinstance(ts, int):
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        return datetime.now(timezone.utc)

    async def _handle_dispensing_create(self, data: dict[str, Any]) -> None:
        task_id = self._get_task_id(data)
        if not task_id:
            return

        created_time = self._get_created_time(data)

        payload = data.get("payload") or {}
        medicines = payload.get("medicines") or []
        if not isinstance(medicines, list):
            medicines = []

        user_id = data.get("user_id", "")
        if not isinstance(user_id, str):
            user_id = str(user_id)
        user_role = data.get("user_role", "")
        if not isinstance(user_role, str):
            user_role = str(user_role)

        task = DispensingTask(
            task_id=task_id,
            time=created_time,
            user_id=user_id,
            user_role=user_role,
            medicines=medicines,
            is_completed=False,
        )

        async with new_session() as s:
            s.add(task)
            try:
                await s.commit()
            except IntegrityError:
                await s.rollback()

    async def _handle_infusion_create(self, data: dict[str, Any]) -> None:
        task_id = self._get_task_id(data)
        if not task_id:
            return

        target_id = data.get("target_id")
        if not isinstance(target_id, str) or not target_id:
            return
        if data.get("target_role") != "customer":
            return

        created_time = self._get_created_time(data)

        payload = data.get("payload") or {}
        fluids = payload.get("fluids") or []
        if not isinstance(fluids, list):
            fluids = []

        task = InfusionTask(
            task_id=task_id,
            time=created_time,
            target_id=target_id,
            target_role="customer",
            fluids=fluids,
            current_fluid=None,
            is_completed=False,
            status="created",
            status_updated_at=created_time,
        )

        async with new_session() as s:
            s.add(task)
            try:
                await s.commit()
            except IntegrityError:
                await s.rollback()

    async def _dispatch(self, data: dict[str, Any]) -> None:
        action_code = data.get("action_code")
        if action_code == _ACTION_DOCTOR_DISPENSING_CREATE:
            await self._handle_dispensing_create(data)
        elif action_code == _ACTION_NURSE_REQUEST_DISPENSING:
            await self._handle_dispensing_create(data)
        elif action_code == _ACTION_DOCTOR_INFUSION_CREATE:
            await self._handle_infusion_create(data)

    async def worker(self) -> None:
        if not self._bootstrap_servers:
            _logger.warning("KAFKA_BOOTSTRAP_SERVER is empty, event bus consumer will not start.")
            return

        consumer = AIOKafkaConsumer(
            _TOPIC,
            bootstrap_servers=self._bootstrap_servers,
            group_id=_GROUP_ID,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )

        await consumer.start()
        _logger.info("Event bus consumer started.")
        try:
            async for msg in consumer:
                value = msg.value
                if not isinstance(value, dict):
                    continue
                await self._dispatch(value)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            _logger.error(f"Event bus consumer error: {e}")
        finally:
            await consumer.stop()
            _logger.info("Event bus consumer stopped.")


_event_bus_consumer_singleton = EventBusConsumer()


def get_event_bus_consumer() -> EventBusConsumer:
    return _event_bus_consumer_singleton


__all__ = ["EventBusConsumer", "get_event_bus_consumer"]

