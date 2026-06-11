import inspect
from typing import Any, Callable, Annotated
from fastapi import Request, Query

from sqlalchemy import Select
from sqlmodel import select, col, desc, asc

operators = {
    'eq': lambda field, val: field == val,
    'lt': lambda field, val: field < val,
    'gt': lambda field, val: field > val,
    'lte': lambda field, val: field <= val,
    'gte': lambda field, val: field >= val,
    'contains': lambda field, val: field.contains(val),
    'in': lambda field, val: field.in_(val),
}


def filter_factory(
    schema: dict[str, tuple[str, ...]],
    prefix: str = ''
) -> Callable:
    async def dependency(**kwargs):
        filters: list[tuple[str, str, Any]] = []

        for field_name, ops in schema.items():
            for op in ops:
                param_name = f"{prefix}{field_name}_{op}"
                value = kwargs.get(param_name)

                if value is not None:
                    filters.append((field_name, op, value))

        def apply(statement: Select, model: Any) -> Select:
            """
            将过滤条件应用到 SQLModel 查询语句中。
            """
            for field_name, op, val in filters:
                column = getattr(model, field_name)  # 获取模型列

                match op:
                    case "eq":
                        statement = statement.where(column == val)
                    case "lt":
                        statement = statement.where(column < val)
                    case "gt":
                        statement = statement.where(column > val)
                    case "like":
                        statement = statement.where(column.like(f"%{val}%"))
                    case "in":
                        statement = statement.where(column.in_(val.split(",")))
                    case "lte":
                        statement = statement.where(column <= val)
                    case "gte":
                        statement = statement.where(column >= val)

            return statement
        return apply

    # 为生成函数设置动态签名，以便 FastAPI 的 OpenAPI 文档能够正确识别参数
    params = []

    for field_name, ops in schema.items():
        for op in ops:
            param_name = f"{prefix}{field_name}_{op}"
            params.append(inspect.Parameter(
                param_name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Query(None, alias=param_name),
                annotation=str | None,
            ))

    dependency.__signature__ = inspect.Signature(params)
    return dependency


def sort_by_factory(
        allowed_fields: list[str],
        default: str | None = None
) -> Callable:
    async def dependency(
            sort_by: Annotated[
                str | None,
                Query(description=f"Allowed values: {', '.join(allowed_fields)}, descend with prefix '-'")
            ] = default
    ):
        def apply(statement: Select, model: Any) -> Select:
            if not sort_by:
                return statement
            is_desc = sort_by.startswith("-")
            field_name = sort_by[1:] if is_desc else sort_by
            if field_name not in allowed_fields:
                return statement
            column = getattr(model, field_name)
            order_func = desc if is_desc else asc
            return statement.order_by(order_func(column))
        return apply

    return dependency

__all__ = ['filter_factory', 'sort_by_factory']
