import asyncio
import json
from typing import AsyncGenerator, Callable

from loguru import logger

from app.utils.dify_client import DifyClient
from app.config import DIFY_SERVER, DIFY_USER, DIFY_CHATFLOW_KEY

_logger = logger.bind(tag='AiService')


class AiService:
    def __init__(self):
        self.chat_client = DifyClient(base_url=DIFY_SERVER, api_key=DIFY_CHATFLOW_KEY)

    async def _chat_message_flow(self, message: str, conversation_id: str | None,
                                 user: str,
                                 event_callback: Callable[[dict], None]):
        _logger.info(f"Chat message: {message}, conversation_id: {conversation_id}, user: {user}")
        buffer = ""
        try:
            async for chunk in self.chat_client.send_message_stream(
                    query=message,
                    inputs={},
                    user=f"{DIFY_USER}-{user}",
                    conversation_id=conversation_id
            ):
                # 解码 Dify SSE 的每个 data 并 callback
                if not chunk:
                    continue
                buffer += chunk.decode("utf-8", errors="ignore")

                while "\n\n" in buffer:
                    raw_event, buffer = buffer.split("\n\n", 1)
                    raw_event = raw_event.strip()
                    if not raw_event:
                        continue

                    event_type = None
                    data_lines = []
                    for line in raw_event.splitlines():
                        if line.startswith("event:"):
                            event_type = line[len("event:"):].strip()
                        elif line.startswith("data:"):
                            data_lines.append(line[len("data:"):].lstrip())

                    if not data_lines:
                        continue

                    data_str = "\n".join(data_lines).strip()
                    if not data_str:
                        continue

                    if data_str == "[DONE]":
                        continue

                    try:
                        payload = json.loads(data_str)
                        if isinstance(payload, dict):
                            if event_type and "event" not in payload:
                                payload["event"] = event_type
                            event_callback(payload)
                        else:
                            event_callback({
                                "event": event_type or "agent_message",
                                "answer": str(payload),
                            })
                    except json.JSONDecodeError:
                        event_callback({
                            "event": event_type or "agent_message",
                            "answer": data_str,
                        })
        finally:
            event_callback({'event': 'message_end'})

    def chat_message(self,
                     message: str,
                     conversation_id: str | None = None,
                     user: str = 'unknown') -> AsyncGenerator[dict, None]:
        queue = asyncio.Queue(maxsize=512)

        async def queue_into_iterator():
            recorded_conversation_id: str | None = None
            while True:
                event = await queue.get()
                event_type = event['event']
                new_conversation_id = event.get('conversation_id')
                if new_conversation_id and not recorded_conversation_id:
                    recorded_conversation_id = new_conversation_id
                    yield {'event': 'conversation_id', 'conversation_id': new_conversation_id}

                if event_type == 'agent_message':
                    yield {'event': 'message', 'message': event['answer']}
                elif event_type == 'message_end':
                    break

                queue.task_done()

        def queue_enqueue(event: dict):
            queue.put_nowait(event)

        asyncio.create_task(self._chat_message_flow(message, conversation_id, user, queue_enqueue))

        return queue_into_iterator()


ai_service_singleton = AiService()


def get_ai_service() -> AiService:
    return ai_service_singleton


__all__ = ['get_ai_service', 'AiService']
