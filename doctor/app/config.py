from __future__ import annotations

import os
from pathlib import Path

SERVICE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{(SERVICE_DIR / "app.db").as_posix()}")
SQL_ECHO = os.getenv("SQL_ECHO") == "1"

ASSETS_DIR = SERVICE_DIR / "assets"

KAFKA_BOOTSTRAP_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVER', '')
DIFY_SERVER = os.getenv('DIFY_SERVER', '')
DIFY_USER = os.getenv('DIFY_USER', 'doctor-side')
DIFY_CT_WORKFLOW_KEY = os.getenv('DIFY_CT_WORKFLOW_KEY', '')

REDIS_URL = os.getenv('REDIS_URL', '')

ASSETS_DIR.mkdir(exist_ok=True)