from datetime import datetime, timezone

from fastapi import Depends, APIRouter
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import InfusionTask
from app.services.auth_service import User, verify_auth
from app.services.event_bus_service import get_event_bus, EventBusService, obtain_trace_id

router = APIRouter(
    prefix="",
    tags=["nurse"],
    dependencies=[Depends(verify_auth)]
)

class InfusionStartRequest(BaseModel):
    target_id: str
    opd_id: str
    initial_medicine: str
    specification: str
    task_id: str | None = None

class InfusionChangeRequest(BaseModel):
    target_id: str
    opd_id: str
    next_medicine: str
    task_id: str | None = None

class InfusionCompleteRequest(BaseModel):
    target_id: str
    opd_id: str
    task_id: str | None = None

class RehydrationRequest(BaseModel):
    target_id: str
    medicine: str
    specification: str

class AdditionRequest(BaseModel):
    target_id: str
    medicine: str
    specification: str

class DispensingRequest(BaseModel):
    target_id: str
    # 兼容旧参数：单个药品
    medicine: str | None = None
    specification: str | None = None

    # 新参数：药品列表（推荐）
    medicines: list[dict] | None = None

@router.post("/infusion/start")
async def record_infusion_start(
    payload: InfusionStartRequest,
    user: User = Depends(verify_auth),
    event_bus: EventBusService = Depends(get_event_bus),
    session: AsyncSession = Depends(get_session),
):
    """
    记录输液开始
    """
    # 对接输液任务：根据 task_id 或 target_id 找到最新未完成任务，并更新当前输液状态
    task: InfusionTask | None = None
    if payload.task_id:
        task = await session.get(InfusionTask, payload.task_id)
    if task is None:
        stmt = (
            select(InfusionTask)
            .where(InfusionTask.target_id == payload.target_id)
            .where(InfusionTask.is_completed == False)  # noqa: E712
            .order_by(InfusionTask.status_updated_at.desc())
            .limit(1)
        )
        task = (await session.exec(stmt)).first()

    if task is not None:
        task.current_fluid = {
            "medicine": payload.initial_medicine,
            "specification": payload.specification,
        }
        task.status = "started"
        task.status_updated_at = datetime.now(timezone.utc)
        session.add(task)
        await session.commit()

    await event_bus.send(obtain_trace_id(), {
        "source": "nurse",
        "action_code": "nurse_infusion_start",
        "user_id": user.user_id,
        "user_role": user.user_role,
        "status": 0,
        "target_id": payload.target_id,
        "target_role": "customer",
        "payload": {
            "opd_id": payload.opd_id,
            "medicine": payload.initial_medicine,
            "specification": payload.specification
        }
    })
    return {"message": "ok"}
    

@router.post("/infusion/change")
async def record_infusion_change(
    payload: InfusionChangeRequest,
    user: User = Depends(verify_auth),
    event_bus: EventBusService = Depends(get_event_bus),
    session: AsyncSession = Depends(get_session),
):
    """
    记录换液
    """
    task: InfusionTask | None = None
    if payload.task_id:
        task = await session.get(InfusionTask, payload.task_id)
    if task is None:
        stmt = (
            select(InfusionTask)
            .where(InfusionTask.target_id == payload.target_id)
            .where(InfusionTask.is_completed == False)  # noqa: E712
            .order_by(InfusionTask.status_updated_at.desc())
            .limit(1)
        )
        task = (await session.exec(stmt)).first()

    if task is not None:
        task.current_fluid = {
            "medicine": payload.next_medicine,
        }
        task.status = "changed"
        task.status_updated_at = datetime.now(timezone.utc)
        session.add(task)
        await session.commit()

    await event_bus.send(obtain_trace_id(), {
        "source": "nurse",
        "action_code": "nurse_infusion_change",
        "user_id": user.user_id,
        "user_role": user.user_role,
        "status": 0,
        "target_id": payload.target_id,
        "target_role": "customer",
        "payload": {
            "opd_id": payload.opd_id,
            "medicine": payload.next_medicine
        }
    })
    return {"message": "ok"}

@router.post("/infusion/complete")
async def record_infusion_complete(
    payload: InfusionCompleteRequest,
    user: User = Depends(verify_auth),
    event_bus: EventBusService = Depends(get_event_bus),
    session: AsyncSession = Depends(get_session),
):
    """
    记录输液完成
    """
    task: InfusionTask | None = None
    if payload.task_id:
        task = await session.get(InfusionTask, payload.task_id)
    if task is None:
        stmt = (
            select(InfusionTask)
            .where(InfusionTask.target_id == payload.target_id)
            .where(InfusionTask.is_completed == False)  # noqa: E712
            .order_by(InfusionTask.status_updated_at.desc())
            .limit(1)
        )
        task = (await session.exec(stmt)).first()

    if task is not None and not task.is_completed:
        task.is_completed = True
        task.status = "completed"
        task.status_updated_at = datetime.now(timezone.utc)
        session.add(task)
        await session.commit()

    await event_bus.send(obtain_trace_id(), {
        "source": "nurse",
        "action_code": "nurse_infusion_complete",
        "user_id": user.user_id,
        "user_role": user.user_role,
        "status": 0,
        "target_id": payload.target_id,
        "target_role": "customer",
        "payload": {
            "opd_id": payload.opd_id
        }
    })
    return {"message": "ok"}

@router.post("/request/rehydration")
async def request_rehydration(
    payload: RehydrationRequest,
    user: User = Depends(verify_auth),
    event_bus: EventBusService = Depends(get_event_bus)
):
    """
    请求补液
    """
    await event_bus.send(obtain_trace_id(), {
        "source": "nurse",
        "action_code": "nurse_request_rehydration",
        "user_id": user.user_id,
        "user_role": user.user_role,
        "status": 0,
        "target_id": payload.target_id,
        "target_role": "customer",
        "payload": {
            "medicine": payload.medicine,
            "specification": payload.specification
        }
    })
    return {"message": "ok"}

@router.post("/request/addition")
async def request_addition(
    payload: AdditionRequest,
    user: User = Depends(verify_auth),
    event_bus: EventBusService = Depends(get_event_bus)
):
    """
    请求加液
    """
    await event_bus.send(obtain_trace_id(), {
        "source": "nurse",
        "action_code": "nurse_request_addition",
        "user_id": user.user_id,
        "user_role": user.user_role,
        "status": 0,
        "target_id": payload.target_id,
        "target_role": "customer",
        "payload": {
            "medicine": payload.medicine,
            "specification": payload.specification
        }
    })
    return {"message": "ok"}

@router.post("/request/dispensing")
async def request_dispensing(
    payload: DispensingRequest,
    user: User = Depends(verify_auth),
    event_bus: EventBusService = Depends(get_event_bus)
):
    """
    请求配药（护士侧发起请求能力）
    """
    medicines: list[dict] = []
    if isinstance(payload.medicines, list) and payload.medicines:
        medicines = payload.medicines
    elif payload.medicine:
        medicines = [{"medicine": payload.medicine, "specification": payload.specification}]

    trace_id = obtain_trace_id()
    await event_bus.send(trace_id, {
        "source": "nurse",
        "action_code": "nurse_request_dispensing",
        "user_id": user.user_id,
        "user_role": user.user_role,
        "status": 0,
        "target_id": payload.target_id,
        "target_role": "customer",
        "payload": {
            "medicines": medicines,
        }
    })
    return {"message": "ok", "trace_id": trace_id}
