from fastapi import Depends, APIRouter
from pydantic import BaseModel

from hymed_no_kafka.nurse.services.auth_service import User, verify_auth
from hymed_no_kafka.services.event_bus_service import get_event_bus, EventBusService, obtain_trace_id

router = APIRouter(
    prefix="",
    tags=["nurse"],
    dependencies=[Depends(verify_auth)],
)


class InfusionStartRequest(BaseModel):
    target_id: str
    opd_id: str
    initial_medicine: str
    specification: str


class InfusionChangeRequest(BaseModel):
    target_id: str
    opd_id: str
    next_medicine: str


class InfusionCompleteRequest(BaseModel):
    target_id: str
    opd_id: str


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
    medicine: str
    specification: str


@router.post("/infusion/start")
async def record_infusion_start(
    payload: InfusionStartRequest,
    user: User = Depends(verify_auth),
    event_bus: EventBusService = Depends(get_event_bus),
):
    await event_bus.send(
        obtain_trace_id(),
        {
            "source": "nurse",
            "action_code": "nurse_infusion_start",
            "user_id": user.user_id,
            "user_role": user.user_role,
            "status": 0,
            "target_id": payload.target_id,
            "target_role": "PATIENT",
            "payload": {
                "opd_id": payload.opd_id,
                "medicine": payload.initial_medicine,
                "specification": payload.specification,
            },
        },
    )
    return {"message": "ok"}


@router.post("/infusion/change")
async def record_infusion_change(
    payload: InfusionChangeRequest,
    user: User = Depends(verify_auth),
    event_bus: EventBusService = Depends(get_event_bus),
):
    await event_bus.send(
        obtain_trace_id(),
        {
            "source": "nurse",
            "action_code": "nurse_infusion_change",
            "user_id": user.user_id,
            "user_role": user.user_role,
            "status": 0,
            "target_id": payload.target_id,
            "target_role": "PATIENT",
            "payload": {
                "opd_id": payload.opd_id,
                "medicine": payload.next_medicine,
            },
        },
    )
    return {"message": "ok"}


@router.post("/infusion/complete")
async def record_infusion_complete(
    payload: InfusionCompleteRequest,
    user: User = Depends(verify_auth),
    event_bus: EventBusService = Depends(get_event_bus),
):
    await event_bus.send(
        obtain_trace_id(),
        {
            "source": "nurse",
            "action_code": "nurse_infusion_complete",
            "user_id": user.user_id,
            "user_role": user.user_role,
            "status": 0,
            "target_id": payload.target_id,
            "target_role": "PATIENT",
            "payload": {"opd_id": payload.opd_id},
        },
    )
    return {"message": "ok"}


@router.post("/request/rehydration")
async def request_rehydration(
    payload: RehydrationRequest,
    user: User = Depends(verify_auth),
    event_bus: EventBusService = Depends(get_event_bus),
):
    await event_bus.send(
        obtain_trace_id(),
        {
            "source": "nurse",
            "action_code": "nurse_request_rehydration",
            "user_id": user.user_id,
            "user_role": user.user_role,
            "status": 0,
            "target_id": payload.target_id,
            "target_role": "PATIENT",
            "payload": {"medicine": payload.medicine, "specification": payload.specification},
        },
    )
    return {"message": "ok"}


@router.post("/request/addition")
async def request_addition(
    payload: AdditionRequest,
    user: User = Depends(verify_auth),
    event_bus: EventBusService = Depends(get_event_bus),
):
    await event_bus.send(
        obtain_trace_id(),
        {
            "source": "nurse",
            "action_code": "nurse_request_addition",
            "user_id": user.user_id,
            "user_role": user.user_role,
            "status": 0,
            "target_id": payload.target_id,
            "target_role": "PATIENT",
            "payload": {"medicine": payload.medicine, "specification": payload.specification},
        },
    )
    return {"message": "ok"}


@router.post("/request/dispensing")
async def request_dispensing(
    payload: DispensingRequest,
    user: User = Depends(verify_auth),
    event_bus: EventBusService = Depends(get_event_bus),
):
    await event_bus.send(
        obtain_trace_id(),
        {
            "source": "nurse",
            "action_code": "nurse_request_dispensing",
            "user_id": user.user_id,
            "user_role": user.user_role,
            "status": 0,
            "target_id": payload.target_id,
            "target_role": "PATIENT",
            "payload": {"medicine": payload.medicine, "specification": payload.specification},
        },
    )
    return {"message": "ok"}

