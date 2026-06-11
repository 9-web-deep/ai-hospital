from __future__ import annotations

import redis.asyncio as redis
from fastapi import Depends, APIRouter, File, UploadFile, Form

from hymed_no_kafka.config import ASSETS_DIR
from hymed_no_kafka.doctor.services.ai_service import AiService, get_ai_service, AiCtAnalyzeContext
from hymed_no_kafka.doctor.services.auth_service import User, verify_auth
from hymed_no_kafka.doctor.services.cache_service import get_cache_service
from hymed_no_kafka.services.event_bus_service import obtain_trace_id, get_event_bus, EventBusService

router = APIRouter(prefix="", tags=["doctor"], dependencies=[Depends(verify_auth)])

@router.get("/custom_event_test")
async def custom_event_test(
    user: User = Depends(verify_auth),
    event_bus: EventBusService = Depends(get_event_bus),
):
    trace_id = obtain_trace_id()
    await event_bus.send(
        trace_id,
        {
            "source": "doctor",
            "action": "doctor_custom_test",
            "action_code": "doctor_custom_test",
            "user_id": user.user_id,
            "user_role": user.user_role,
            "status": 0,
            "target_id": user.user_id,
            "target_role": "DOCTOR",
            "payload": {"message": "custom_event_test"},
        },
    )
    return {"message": "ok", "trace_id": trace_id}


@router.post("/ai-report")
async def ai_report(
    target_id: str = Form(...),
    opd_id: str = Form(...),
    doctor_note: str | None = Form(None),
    image: UploadFile = File(...),
    user: User = Depends(verify_auth),
    ai_service: AiService = Depends(get_ai_service),
):
    trace_id = obtain_trace_id()

    images_dir = ASSETS_DIR / "images"
    images_dir.mkdir(exist_ok=True)

    suffix = ""
    if image.filename and "." in image.filename:
        suffix = "." + image.filename.rsplit(".", 1)[1]
    image_path = images_dir / f"{trace_id}{suffix}"

    content = await image.read()
    with open(image_path, "wb") as f:
        f.write(content)
    await image.close()

    context = AiCtAnalyzeContext(
        target_id=target_id,
        opd_id=opd_id,
        trace_id=trace_id,
        user_id=user.user_id,
        user_role=user.user_role,
        doctor_note=doctor_note or "",
    )

    ai_service.ai_ct_analyze(str(image_path), context)
    return {"message": "ok", "trace_id": trace_id}


@router.get("/poll")
async def check_ai_response(
    trace_id: str,
    redis_client: redis.Redis = Depends(get_cache_service),
):
    if not await redis_client.exists(trace_id):
        return {"data": None}

    data = await redis_client.get(trace_id)
    return {"data": data}
