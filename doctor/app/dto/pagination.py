from typing import List, Annotated
from fastapi import Query
from pydantic import BaseModel

class PaginatedResult[T](BaseModel):
    total_count: int
    page_count: int
    page: int
    page_size: int
    data: List[T]


class PaginationQuery(BaseModel):
    page: int
    page_size: int

def pagination_query(
    page: Annotated[int, Query(description="Page number")] = 1,
    page_size: Annotated[int, Query(description="Page size")] = 20
) -> PaginationQuery:
    return PaginationQuery(page=page, page_size=page_size)
