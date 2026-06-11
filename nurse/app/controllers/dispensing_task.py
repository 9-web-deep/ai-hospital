from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.db import get_session
from app.models import DispensingTask
from app.services.auth_service import User, verify_auth
from app.services.event_bus_service import EventBusService, get_event_bus, obtain_trace_id

router = APIRouter(
    prefix="",
    tags=["dispensing_task"],
    dependencies=[Depends(verify_auth)],
)


@router.get("/dispensing_tasks")
async def list_dispensing_tasks(
    is_completed: bool | None = None,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    limit = max(1, min(int(limit), 200))
    offset = max(0, int(offset))

    stmt = select(DispensingTask)
    if is_completed is not None:
        stmt = stmt.where(DispensingTask.is_completed == is_completed)
    stmt = stmt.order_by(DispensingTask.time.desc()).offset(offset).limit(limit)

    result = await session.exec(stmt)
    items = result.all()
    return {
        "items": [t.model_dump() for t in items],
        "limit": limit,
        "offset": offset,
    }


@router.post("/dispensing_tasks/{task_id}/complete")
async def complete_dispensing_task(
    task_id: str,
    user: User = Depends(verify_auth),
    session: AsyncSession = Depends(get_session),
    event_bus: EventBusService = Depends(get_event_bus),
):
    task = await session.get(DispensingTask, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispensing task not found")

    if not task.is_completed:
        task.is_completed = True
        session.add(task)
        await session.commit()

        # 可选：发一条完成事件，便于管理端审计
        await event_bus.send(obtain_trace_id(), {
            "source": "nurse",
            "action_code": "nurse_dispensing_task_complete",
            "user_id": user.user_id,
            "user_role": user.user_role,
            "status": 0,
            "target_id": task_id,
            "target_role": "DISPENSING_TASK",
            "payload": {},
        })

    return {"message": "ok", "task_id": task_id, "is_completed": True}
