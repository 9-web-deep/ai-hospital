import asyncio
from datetime import timedelta

from pydantic import BaseModel

from app.services.cache_service import get_cache_service, new_cache_service
from app.services.event_bus_service import get_event_bus
from app.utils.dify_client import DifyClient
from app.config import DIFY_SERVER, DIFY_CT_WORKFLOW_KEY, DIFY_USER
from loguru import logger

_logger = logger.bind(tag='AiService')


class AiCtAnalyzeContext(BaseModel):
    target_id: str
    opd_id: str
    trace_id: str
    user_id: str
    user_role: str
    doctor_note: str


class AiService:
    def __init__(self):
        self.ct_workflow = DifyClient(DIFY_SERVER, DIFY_CT_WORKFLOW_KEY, timeout=180)

    async def _ai_ct_analyze_invoke(self, image_file_path: str, doctor_note: str):
        prompt = '请使用中文描述下这个图像并给出你的诊断结果'

        upload_result = await self.ct_workflow.upload_file(image_file_path, user=DIFY_USER)
        upload_id = None
        if isinstance(upload_result, dict):
            upload_id = upload_result.get("id")

        if not upload_id:
            raise RuntimeError(f"Failed to upload file: {upload_result}")

        workflow_result = await self.ct_workflow.send_message(
            query=prompt,
            inputs={
                "doctor_note": doctor_note
            },
            files=[
                {
                    "type": "image",
                    "transfer_method": "local_file",
                    "upload_file_id": upload_id,
                }
            ],
            user=DIFY_USER
        )

        if not isinstance(workflow_result, dict):
            return str(workflow_result)

        return str(workflow_result.get('answer'))

    async def _ai_ct_analyze_task(self, image_file_path: str, context: AiCtAnalyzeContext) -> str:
        event_bus = get_event_bus()

        await event_bus.send(context.trace_id, {
            "source": "doctor",
            "action_code": "doctor_ai_analyze_begin",
            "user_id": context.user_id,
            "user_role": context.user_role,
            "status": 0,
            "target_id": context.target_id,
            "target_role": "PATIENT",
            "payload": {
                "opd_id": context.opd_id,
                "doctor_note": context.doctor_note,
            }
        })

        try:
            result = await self._ai_ct_analyze_invoke(image_file_path, context.doctor_note)
            await event_bus.send(context.trace_id, {
                "source": "doctor",
                "action_code": "doctor_ai_analyze_end",
                "user_id": context.user_id,
                "user_role": context.user_role,
                "status": 0,
                "target_id": context.target_id,
                "target_role": "PATIENT",
                "payload": {
                    "opd_id": context.opd_id,
                    "result": result
                }
            })

        except Exception as e:
            _logger.error(f'Failed to invoke ct analyze: {e}')
            await event_bus.send(context.trace_id, {
                "source": "doctor",
                "action_code": "doctor_ai_analyze_end",
                "user_id": context.user_id,
                "user_role": context.user_role,
                "status": 1,
                "target_id": context.target_id,
                "target_role": "PATIENT",
                "payload": {
                    "opd_id": context.opd_id,
                    "result": None
                }
            })
            result = '<FAILED>'

        try:
            async with new_cache_service() as r:
                await r.set(name=context.trace_id, value=result, ex=timedelta(seconds=180))
        except Exception as e:
            _logger.error(f'Failed to push ai result: {e}')

        return result

    def ai_ct_analyze(self, image_file_path: str, context: AiCtAnalyzeContext) -> asyncio.Task[str]:
        return asyncio.create_task(self._ai_ct_analyze_task(image_file_path, context))


ai_service_singleton = AiService()


def get_ai_service() -> AiService:
    return ai_service_singleton


__all__ = ['get_ai_service', 'AiService', 'AiCtAnalyzeContext']
