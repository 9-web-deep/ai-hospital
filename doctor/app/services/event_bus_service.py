import json
import time
import asyncio
import logging
from typing import Any
from uuid import uuid4

from aiokafka import AIOKafkaProducer
from app.config import KAFKA_BOOTSTRAP_SERVER

_topic = "event_bus"
_logger = logging.getLogger(__name__)


def obtain_trace_id() -> str:
    return str(uuid4())

class EventBusService:
    """
    Kafka 事件总线服务。
    """

    def __init__(self, bootstrap_servers: str = KAFKA_BOOTSTRAP_SERVER):
        self._bootstrap_servers = bootstrap_servers
        self._producer: AIOKafkaProducer | None = None

    async def start(self, retries: int = 30, retry_delay_seconds: float = 1.0):
        """启动 Kafka 生产者"""
        if not self._bootstrap_servers:
            _logger.warning("KAFKA_BOOTSTRAP_SERVER is empty, kafka producer will not start.")
            return

        if self._producer is None:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self._bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                linger_ms=10, 
                max_batch_size=65536, # 64KB
                max_request_size=5242880
            )
            for attempt in range(1, retries + 1):
                try:
                    await self._producer.start()
                    return
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    if attempt >= retries:
                        _logger.exception("Kafka producer start failed after %s attempts: %s", retries, e)
                        try:
                            await self._producer.stop()
                        except Exception:
                            pass
                        self._producer = None
                        return
                    _logger.warning(
                        "Kafka producer start failed (attempt %s/%s): %s; retrying in %ss",
                        attempt,
                        retries,
                        e,
                        retry_delay_seconds,
                    )
                    await asyncio.sleep(retry_delay_seconds)

    async def stop(self):
        """停止 Kafka 生产者"""
        if self._producer:
            await self._producer.stop()
            self._producer = None

    async def send(self, trace_id: str, data: Any):
        """
        向硬编码的 'event_bus' topic 发送 JSON 广播事件。
        """
        if self._producer is None:
            await self.start()
        if self._producer is None:
            raise RuntimeError("Kafka producer is not available")

        copied_data = {**data, **{"trace_id": trace_id, 'timestamp': int(time.time())}}

        # 广播至指定 topic
        await self._producer.send(_topic, copied_data)


# 默认服务实例
_event_bus_instance = EventBusService()


def get_event_bus() -> EventBusService:
    """获取 EventBusService 依赖注入实例"""
    return _event_bus_instance
