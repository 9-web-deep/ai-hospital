from __future__ import annotations

import os
from pathlib import Path

SERVICE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{(SERVICE_DIR / 'app.db').as_posix()}")
SQL_ECHO = os.getenv("SQL_ECHO") == "1"

# 兼容原项目 env（本实验版本不再使用 Kafka）
KAFKA_BOOTSTRAP_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVER", "")

# Dify（护士聊天 / 医生 CT workflow）
DIFY_SERVER = os.getenv("DIFY_SERVER", "")
DIFY_USER = os.getenv("DIFY_USER", "no_kafka")
DIFY_CHATFLOW_KEY = os.getenv("DIFY_CHATFLOW_KEY", "")
DIFY_CT_WORKFLOW_KEY = os.getenv("DIFY_CT_WORKFLOW_KEY", "")

# Doctor assets/cache
ASSETS_DIR = SERVICE_DIR / "assets"
REDIS_URL = os.getenv("REDIS_URL", "")

# 全局事件队列
EVENT_QUEUE_MAXSIZE = int(os.getenv("EVENT_QUEUE_MAXSIZE", "10000"))

ASSETS_DIR.mkdir(exist_ok=True)

