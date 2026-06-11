from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.controllers.health import router as health_router
from app.controllers.nurse import router as nurse_router
from app.services.event_bus_service import get_event_bus
from app.controllers.chat import router as chat_router
from app.controllers.dispensing_task import router as dispensing_task_router
from app.controllers.infusion_task import router as infusion_task_router
from app.services.event_bus_consumer import get_event_bus_consumer
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    event_bus = get_event_bus()
    await event_bus.start()

    consumer = get_event_bus_consumer()
    consumer_worker_task = asyncio.create_task(consumer.worker())
    yield
    # Shutdown
    consumer_worker_task.cancel()
    await event_bus.stop()


app = FastAPI(title="Hospital AI - 护士端", lifespan=lifespan, swagger_ui_parameters={'url': './openapi.json'})
app.include_router(health_router)
app.include_router(nurse_router)
app.include_router(chat_router)
app.include_router(dispensing_task_router)
app.include_router(infusion_task_router)
