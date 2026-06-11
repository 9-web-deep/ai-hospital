from __future__ import annotations

import math
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from hymed_no_kafka.db import get_session
from hymed_no_kafka.dto.pagination import PaginatedResult, PaginationQuery, pagination_query
from hymed_no_kafka.administrator.models.operation_journal import OperationJournal
from hymed_no_kafka.utils.crud import filter_factory, sort_by_factory

router = APIRouter(prefix="/operation-journals", tags=["operation_journals"])

operation_journal_filter = filter_factory(
    {
        "id": ("eq", "in"),
        "trace_id": ("eq", "in"),
        "user_id": ("eq", "in"),
        "user_role": ("eq", "in"),
        "action_code": ("eq", "in"),
        "time": ("eq", "lt", "gt", "in", "gte", "lte"),
        "status": ("eq", "in"),
        "target_id": ("eq", "in"),
        "target_role": ("eq", "in"),
    }
)


@router.get("/", response_model=PaginatedResult[OperationJournal])
async def query_operation_journal(
    pagination: PaginationQuery = Depends(pagination_query),
    apply_filter: Callable = Depends(operation_journal_filter),
    apply_sort: Callable = Depends(sort_by_factory(["id", "time"])),
    session: AsyncSession = Depends(get_session),
) -> PaginatedResult[OperationJournal]:
    statement = select(OperationJournal).where(OperationJournal.is_deleted == False)
    statement = apply_filter(statement, OperationJournal)

    count_statement = select(func.count()).select_from(statement.subquery())
    total_count = (await session.exec(count_statement)).one()

    statement = apply_sort(statement, OperationJournal)
    statement = statement.offset((pagination.page - 1) * pagination.page_size).limit(pagination.page_size)

    results = await session.exec(statement)
    data = results.all()

    return PaginatedResult(
        total_count=total_count,
        page_count=math.ceil(total_count / pagination.page_size) if pagination.page_size > 0 else 0,
        page=pagination.page,
        page_size=pagination.page_size,
        data=data,
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_operation_journal(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    journal = await session.get(OperationJournal, id)
    if not journal or journal.is_deleted:
        raise HTTPException(status_code=404, detail="Operation journal not found")

    journal.is_deleted = True
    session.add(journal)
    await session.commit()
    return None

