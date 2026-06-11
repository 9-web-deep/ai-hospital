from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

SERVICE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = SERVICE_DIR / "app.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO") == "1",
    connect_args=_connect_args,
)


def init_db() -> None:
    if os.getenv("CREATE_TABLES_ON_STARTUP") == "1":
        import customer.models  # noqa: F401

        SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

