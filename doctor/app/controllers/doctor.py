from typing import Annotated

import redis
from fastapi import Header, Depends, HTTPException, APIRouter, File, UploadFile, Form
from pydantic import BaseModel
from starlette import status

from app.config import ASSETS_DIR
from app.services.ai_service import AiService, get_ai_service, AiCtAnalyzeContext
from app.services.auth_service import get_auth_service, IAuthService, User
from app.services.cache_service import get_cache_service
from app.services.event_bus_service import obtain_trace_id, get_event_bus, EventBusService
from app.services.patient_context_service import get_patient_context_service, IPatientContextService


async def verify_auth(
        authorization: str = Header(..., description="HTTP Auth Header"),
        auth_service: IAuthService = Depends(get_auth_service)
) -> User:
    """
    Middleware/Dependency to verify token and return User.
    """
    if not await auth_service.validate(authorization):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    return await auth_service.get_user(authorization)


router = APIRouter(
    prefix="",
    tags=["doctor"],
    dependencies=[Depends(verify_auth)]
)

@router.get("/custom_event_test")
async def custom_event_test(
        user: User = Depends(verify_auth),
        event_bus: EventBusService = Depends(get_event_bus),
):
    trace_id = obtain_trace_id()
    await event_bus.send(trace_id, {
        "source": "doctor",
        "action": "doctor_custom_test",
        "action_code": "doctor_custom_test",
        "user_id": user.user_id,
        "user_role": user.user_role,
        "status": 0,
        "target_id": user.user_id,
        "target_role": "DOCTOR",
        "payload": {
            "message": "custom_event_test"
        }
    })
    return {"message": "ok", "trace_id": trace_id}


class AiCtAnalyzeRequest(BaseModel):
    target_id: str
    opd_id: str
    doctor_note: str | None
    image: UploadFile = File(...),


class DispensingMedicineItem(BaseModel):
    medicine: str
    specification: str | None = None
    amount: int | None = None


class CreateDispensingTaskRequest(BaseModel):
    medicines: list[DispensingMedicineItem]


class InfusionFluidItem(BaseModel):
    medicine: str
    specification: str | None = None
    amount: int | None = None


class CreateInfusionTaskRequest(BaseModel):
    fluids: list[InfusionFluidItem]


@router.post("/ai-report")
async def ai_report(
        payload: Annotated[AiCtAnalyzeRequest, Form()],
        user: User = Depends(verify_auth),
        ai_service: AiService = Depends(get_ai_service)
):
    """
    医生请求AI生成CT报告
    """
    trace_id = obtain_trace_id()

    # 用户应当上传一个文件，存入 ASSETS_DIR 下的 images，文件名为 `trace_id`
    images_dir = ASSETS_DIR / "images"
    images_dir.mkdir(exist_ok=True)

    image = payload.image

    suffix = ""
    if image.filename and "." in image.filename:
        suffix = "." + image.filename.rsplit(".", 1)[1]
    image_path = images_dir / f"{trace_id}{suffix}"
    content = await image.read()
    with open(image_path, "wb") as f:
        f.write(content)
    await image.close()

    # 调用 ai_service 的 ai_ct_analyze，将用户上传文件的送给 AI 分析
    context = AiCtAnalyzeContext(**payload.model_dump(), user_id=user.user_id, user_role=user.user_role,
                                 trace_id=trace_id)

    ai_service.ai_ct_analyze(str(image_path), context)

    return {"message": "ok", "trace_id": trace_id}


@router.get("/poll")
async def check_ai_response(
        trace_id: str,
        redis_client: redis.Redis = Depends(get_cache_service)
):
    """
    根据 trace_id 查询结果，该接口应以 5~10s 的速率轮询
    """
    if not await redis_client.exists(trace_id):
        return {"data": None}

    data = await redis_client.get(trace_id)
    return {"data": data}


@router.post("/dispensing_tasks")
async def create_dispensing_task(
        payload: CreateDispensingTaskRequest,
        user: User = Depends(verify_auth),
        event_bus: EventBusService = Depends(get_event_bus),
        patient_context: IPatientContextService = Depends(get_patient_context_service),
):
    """
    医生端下发配药任务：
    - 生成 task_id（使用 trace_id）
    - 发送 Kafka 事件，护士端消费后落库为配药任务
    """
    if user.user_role != "doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctor can create dispensing task")

    task_id = obtain_trace_id()
    patient = await patient_context.get_current_patient(doctor_user_id=user.user_id)
    await event_bus.send(task_id, {
        "source": "doctor",
        "action_code": "doctor_dispensing_task_create",
        "user_id": user.user_id,
        "user_role": user.user_role,
        "status": 0,
        "target_id": patient.user_id,
        "target_role": patient.user_role,
        "payload": {
            "medicines": [m.model_dump() for m in payload.medicines],
        }
    })
    return {"message": "ok", "task_id": task_id, "patient_id": patient.user_id}


@router.post("/infusion_tasks")
async def create_infusion_task(
        payload: CreateInfusionTaskRequest,
        user: User = Depends(verify_auth),
        event_bus: EventBusService = Depends(get_event_bus),
        patient_context: IPatientContextService = Depends(get_patient_context_service),
):
    """
    医生端下发输液任务：
    - 获取当前就诊病人（target_id/target_role=customer）
    - 发送 Kafka 事件，护士端消费后落库为输液任务
    """
    if user.user_role != "doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctor can create infusion task")

    trimmed = [
        {
            "medicine": (f.medicine or "").strip(),
            "specification": (f.specification or "").strip() or None,
            "amount": f.amount if isinstance(f.amount, int) else None,
        }
        for f in payload.fluids
        if f and (f.medicine or "").strip()
    ]
    if not trimmed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="fluids is empty")

    task_id = obtain_trace_id()
    patient = await patient_context.get_current_patient(doctor_user_id=user.user_id)

    await event_bus.send(task_id, {
        "source": "doctor",
        "action_code": "doctor_infusion_task_create",
        "user_id": user.user_id,
        "user_role": user.user_role,
        "status": 0,
        "target_id": patient.user_id,
        "target_role": patient.user_role,
        "payload": {
            "fluids": trimmed,
        }
    })

    return {"message": "ok", "task_id": task_id, "patient_id": patient.user_id}
