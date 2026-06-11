import json
import uuid
import asyncio

from loguru import logger
from aiokafka import AIOKafkaConsumer
from typing import Any

from app.models import OperationJournal
from app.config import KAFKA_BOOTSTRAP_SERVER
from app.db import new_session

_logger = logger.bind(tag='EventBusService')
_topic = 'event_bus'
_group_id = 'Administrator'

class EventBusService:
    _journal_queue=asyncio.Queue(maxsize=1000)

    async def _journal_append_worker(self, worker_id: int):
        _logger.info(f'Worker {worker_id} startup')
        while True:
            operation_journal = await self._journal_queue.get()
            _logger.debug(f'Worker received journal: {operation_journal}')
            try:
                async with new_session() as s:
                    s.add(operation_journal)
                    await s.commit()
            except Exception as e:
                _logger.error(
                    f"Journal worker {worker_id} exception: {e}",
                )

    async def _append_journal(self, data: Any):
        trace_id = data.get("trace_id")
        if isinstance(trace_id, str):
            trace_id = uuid.UUID(trace_id)

        operation_journal = OperationJournal(
            trace_id=trace_id,
            source=data.get('source', 'Unknown'),
            user_id=data.get('user_id', ''),
            user_role=data.get('user_role', ''),
            action_code=data.get('action_code', 'UNKNOWN'),
            status=data.get('status', 0),
            target_id=data.get('target_id', ''),
            target_role=data.get('target_role', ''),
            payload=data.get('payload') or {},
        )

        await self._journal_queue.put(operation_journal)

    async def _worker_internal(self):
        consumer = AIOKafkaConsumer(
            _topic,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
            group_id=_group_id,            
            auto_offset_reset="earliest",  
            enable_auto_commit=True,       
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )

        await consumer.start()

        _logger.info('Worker looping')
        try: 
            async for msg in consumer:
                _logger.info(f'Worker received kafka: {msg}')
                await self._append_journal(msg.value)
        finally:
            await consumer.stop()

    async def worker(self):
        try:
            _logger.info('Worker startup')
            kafka_worker = asyncio.create_task(self._worker_loop())
            journal_workers = [
                asyncio.create_task(self._journal_append_worker(i)) for i in range(4)
            ]
            
            await kafka_worker
            for worker in journal_workers:
                worker.cancel()
            
        except asyncio.CancelledError:
            raise
        except Exception as e:
            _logger.error('Worker exception', exception = e)
        finally:
            _logger.info('Worker stop')

    async def _worker_loop(self):
        """
        Kafka 连接可能在容器启动早期尚未就绪（尤其是 compose 场景）。
        这里做无限重试，避免服务因 Kafka 短暂不可用而直接退出导致 Nginx 502。
        """
        while True:
            try:
                await self._worker_internal()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                _logger.error(f'Kafka worker exception: {e}; retrying in 2s')
                await asyncio.sleep(2)
        

_event_bus_service_singleton = EventBusService()

def get_event_bus_service() -> EventBusService:
    return _event_bus_service_singleton

__all__ = ['get_event_bus_service', 'EventBusService']
