import asyncio
from typing import Callable

from fastapi import Depends, APIRouter
from fastapi.sse import EventSourceResponse
from loguru import logger
from pydantic import BaseModel

from app.services.ai_service import AiService
from app.services.auth_service import User, verify_auth
from app.services.event_bus_service import get_event_bus, EventBusService, obtain_trace_id

_logger = logger.bind(tag="ChatController")

router = APIRouter(
    prefix="",
    tags=["nurse"],
    dependencies=[Depends(verify_auth)]
)


class NurseChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

@router.post("/chat", response_class=EventSourceResponse)
async def nurse_chat(
        payload: NurseChatRequest,
        user: User = Depends(verify_auth),
        event_bus: EventBusService = Depends(get_event_bus),
        ai_service: AiService = Depends(AiService)
):
    """
    护士对话开始
    """
    trace_id = obtain_trace_id()

    async def non_cancellable(output: Callable[[dict], None], finish: Callable[[], None]):
        event_conversation_id = payload.conversation_id if payload.conversation_id else 'EMPTY'
        await event_bus.send(trace_id, {
            "source": "nurse",
            "action_code": "nurse_chat_begin",
            "user_id": user.user_id,
            "user_role": user.user_role,
            "status": 0,
            "target_id": event_conversation_id,
            "target_role": "CONVERSATION",
            "payload": {
                "input": payload.message
            }
        })

        response = ''


        try:
            async for chunk in ai_service.chat_message(payload.message, payload.conversation_id, user.user_id):
                output(chunk)
                if chunk['event'] == 'message':
                    response += chunk['message']
                elif chunk['event'] == 'conversation_id':
                    event_conversation_id = chunk['conversation_id']
        finally:
            finish()

        await event_bus.send(trace_id, {
            "source": "nurse",
            "action_code": "nurse_chat_end",
            "user_id": user.user_id,
            "user_role": user.user_role,
            "status": 0,
            "target_id": event_conversation_id,
            "target_role": "CONVERSATION",
            "payload": {
                "output": response
            }
        })

    queue = asyncio.Queue()
    stop_signal = object()

    def output(chunk: dict):
        _logger.info(f"Chunk: {chunk}")
        queue.put_nowait(chunk)

    def finish():
        queue.put_nowait(stop_signal)

    asyncio.create_task(non_cancellable(output, finish))

    while True:
        event = await queue.get()
        # _logger.debug(f'SSE Chunk: {chunk}')
        if event is stop_signal:
            break
        yield event
        queue.task_done()