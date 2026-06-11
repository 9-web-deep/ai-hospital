from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import BigInteger, Boolean, Column, DateTime, JSON, SmallInteger, String
from sqlmodel import Field, SQLModel


class OperationJournal(SQLModel, table=True):
    __tablename__ = "operation_journal"

    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True))
    trace_id: uuid.UUID = Field(index=True, nullable=False)
    source: str = Field(sa_column=Column(String(20), nullable=False))
    user_id: str = Field(sa_column=Column(String(50), nullable=False))
    user_role: str = Field(sa_column=Column(String(20), nullable=False))

    action_code: str = Field(sa_column=Column(String(30), nullable=False))
    time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    status: int = Field(sa_column=Column(SmallInteger, nullable=False))

    is_deleted: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
    target_id: str = Field(sa_column=Column(String(50), nullable=False))
    target_role: str = Field(sa_column=Column(String(20), nullable=False))
    payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))

