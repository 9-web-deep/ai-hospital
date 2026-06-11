from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.controllers.health import router as health_router
from app.services.event_bus_service import get_event_bus
from app.controllers.doctor import router as doctor_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    event_bus = get_event_bus()
    await event_bus.start()
    yield
    # Shutdown
    await event_bus.stop()


app = FastAPI(title="Hospital AI - 医生端", lifespan=lifespan, swagger_ui_parameters={'url': './openapi.json'})
app.include_router(health_router)
app.include_router(doctor_router)
