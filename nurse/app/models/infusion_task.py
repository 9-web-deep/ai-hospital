from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, JSON, String
from sqlmodel import Field, SQLModel


class InfusionTask(SQLModel, table=True):
    """
    输液任务（护士端落库）

    字段约束按需求最小实现：
    - task_id: 任务 ID（来自事件 trace_id）
    - time: 任务创建时间
    - target_id/target_role: 输液对象（必须为 customer）
    - fluids: 需要输的液体列表（JSON）
    - current_fluid: 当前正在输的液（JSON，可空）
    - is_completed: 是否完成
    - status: 最近一次状态（created/started/changed/completed）
    - status_updated_at: 最近一次状态更新时间
    """

    __tablename__ = "infusion_task"

    task_id: str = Field(sa_column=Column(String(36), primary_key=True))
    time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    target_id: str = Field(sa_column=Column(String(50), nullable=False))
    target_role: str = Field(sa_column=Column(String(20), nullable=False))

    fluids: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    current_fluid: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON, nullable=True))

    is_completed: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
    status: str = Field(default="created", sa_column=Column(String(30), nullable=False))
    status_updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

