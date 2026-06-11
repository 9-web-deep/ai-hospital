from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from app.controllers.health import router as health_router
from app.controllers.operation_journal import router as operation_journal_router
from app.services.event_bus import get_event_bus_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    event_bus_service = get_event_bus_service()
    event_bus_worker_task = asyncio.create_task(event_bus_service.worker())

    yield

    # Shutdown
    event_bus_worker_task.cancel()


app = FastAPI(title="Hospital AI - 管理端", lifespan=lifespan, swagger_ui_parameters={'url': './openapi.json'})
app.include_router(health_router)
app.include_router(operation_journal_router)
