from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.db import get_session
from app.models import InfusionTask
from app.services.auth_service import verify_auth

router = APIRouter(
    prefix="",
    tags=["infusion_task"],
    dependencies=[Depends(verify_auth)],
)


class ChangeCurrentFluidRequest(BaseModel):
    medicine: str
    specification: str | None = None
    amount: int | None = None


@router.get("/infusion_tasks")
async def list_infusion_tasks(
    is_completed: bool | None = None,
    target_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    limit = max(1, min(int(limit), 200))
    offset = max(0, int(offset))

    stmt = select(InfusionTask)
    if is_completed is not None:
        stmt = stmt.where(InfusionTask.is_completed == is_completed)
    if target_id:
        stmt = stmt.where(InfusionTask.target_id == target_id)
    stmt = stmt.order_by(InfusionTask.status_updated_at.desc()).offset(offset).limit(limit)

    result = await session.exec(stmt)
    items = result.all()
    return {
        "items": [t.model_dump() for t in items],
        "limit": limit,
        "offset": offset,
    }


@router.post("/infusion_tasks/{task_id}/start")
async def start_infusion_task(
    task_id: str,
    session: AsyncSession = Depends(get_session),
):
    task = await session.get(InfusionTask, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Infusion task not found")

    if task.is_completed:
        return {"message": "ok", "task_id": task_id, "is_completed": True}

    if task.current_fluid is None:
        fluids = task.fluids or []
        if isinstance(fluids, list) and fluids:
            task.current_fluid = fluids[0]

    task.status = "started"
    task.status_updated_at = datetime.now(timezone.utc)
    session.add(task)
    await session.commit()
    return {"message": "ok", "task": task.model_dump()}


@router.post("/infusion_tasks/{task_id}/change")
async def change_infusion_task(
    task_id: str,
    payload: ChangeCurrentFluidRequest,
    session: AsyncSession = Depends(get_session),
):
    task = await session.get(InfusionTask, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Infusion task not found")
    if task.is_completed:
        return {"message": "ok", "task_id": task_id, "is_completed": True}

    medicine = (payload.medicine or "").strip()
    if not medicine:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="medicine is required")

    current_fluid: dict[str, Any] = {"medicine": medicine}
    if payload.specification:
        spec = payload.specification.strip()
        if spec:
            current_fluid["specification"] = spec
    if payload.amount is not None:
        current_fluid["amount"] = int(payload.amount)

    task.current_fluid = current_fluid
    task.status = "changed"
    task.status_updated_at = datetime.now(timezone.utc)
    session.add(task)
    await session.commit()
    return {"message": "ok", "task": task.model_dump()}


@router.post("/infusion_tasks/{task_id}/complete")
async def complete_infusion_task(
    task_id: str,
    session: AsyncSession = Depends(get_session),
):
    task = await session.get(InfusionTask, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Infusion task not found")

    if not task.is_completed:
        task.is_completed = True
        task.status = "completed"
        task.status_updated_at = datetime.now(timezone.utc)
        session.add(task)
        await session.commit()

    return {"message": "ok", "task_id": task_id, "is_completed": True}

