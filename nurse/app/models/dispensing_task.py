from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, JSON, String
from sqlmodel import Field, SQLModel


class DispensingTask(SQLModel, table=True):
    """
    配药任务（护士端落库）

    字段约束按需求最小实现：
    - task_id: 任务 ID（来自事件 trace_id）
    - time: 任务创建时间（来自事件 timestamp 或落库时生成）
    - user_id: 事件发起者 user_id（医生端则为开方医生）
    - user_role: 事件发起者 user_role（用于区分用户类型）
    - medicines: 要配的药列表（JSON）
    - is_completed: 是否完成配药
    """

    __tablename__ = "dispensing_task"

    task_id: str = Field(sa_column=Column(String(36), primary_key=True))
    time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    user_id: str = Field(sa_column=Column(String(50), nullable=False))
    user_role: str = Field(sa_column=Column(String(20), nullable=False))
    medicines: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    is_completed: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
