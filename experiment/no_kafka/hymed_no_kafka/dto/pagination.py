from __future__ import annotations

from typing import Generic, List, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResult(BaseModel, Generic[T]):
    total_count: int
    page_count: int
    page: int
    page_size: int
    data: List[T]


class PaginationQuery(BaseModel):
    page: int = Query(1, ge=1)
    page_size: int = Query(10, ge=1, le=100)


def pagination_query(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> PaginationQuery:
    return PaginationQuery(page=page, page_size=page_size)

