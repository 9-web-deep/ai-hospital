from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from hymed_no_kafka.administrator.controllers.health import router as administrator_health_router
from hymed_no_kafka.administrator.controllers.operation_journal import router as operation_journal_router
from hymed_no_kafka.administrator.services.event_bus import get_event_bus_service
from hymed_no_kafka.db import init_db
from hymed_no_kafka.doctor.controllers.doctor import router as doctor_router
from hymed_no_kafka.doctor.controllers.health import router as doctor_health_router
from hymed_no_kafka.nurse.controllers.chat import router as nurse_chat_router
from hymed_no_kafka.nurse.controllers.health import router as nurse_health_router
from hymed_no_kafka.nurse.controllers.nurse import router as nurse_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()

    event_bus_service = get_event_bus_service()
    await event_bus_service.start()
    try:
        yield
    finally:
        await event_bus_service.stop()


app = FastAPI(
    title="Hospital AI - 三合一（no_kafka）",
    lifespan=lifespan,
    swagger_ui_parameters={"url": "./openapi.json"},
)

# Global health (方便探活)
@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "service": "no_kafka_all_in_one"}


# 管理端
app.include_router(administrator_health_router, prefix="/api/administrator")
app.include_router(operation_journal_router, prefix="/api/administrator")

# 护士端
app.include_router(nurse_health_router, prefix="/api/nurse")
app.include_router(nurse_router, prefix="/api/nurse")
app.include_router(nurse_chat_router, prefix="/api/nurse")

# 医生端
app.include_router(doctor_health_router, prefix="/api/doctor")
app.include_router(doctor_router, prefix="/api/doctor")

