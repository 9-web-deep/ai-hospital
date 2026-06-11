from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from .config import DATABASE_URL, SQL_ECHO

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_async_engine(
    DATABASE_URL,
    echo=SQL_ECHO,
    connect_args=_connect_args,
)

_sessionmaker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def new_session() -> AsyncSession:
    return _sessionmaker()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with _sessionmaker() as session:
        yield session


async def init_db() -> None:
    # 仅用于实验版本：启动时自动建表（避免依赖 alembic）
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

