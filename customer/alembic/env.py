from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config_path = Path(config.config_file_name).resolve() if config.config_file_name else None
service_dir = config_path.parent if config_path else Path.cwd()
project_root = service_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

default_db_url = f"sqlite:///{(service_dir / 'app.db').as_posix()}"
db_url = os.getenv("DATABASE_URL", default_db_url)
config.set_main_option("sqlalchemy.url", db_url)

import customer.models  # noqa: F401

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
