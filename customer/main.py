from fastapi import FastAPI

from .controllers.example_items import router as example_items_router
from .controllers.health import router as health_router
from .db import init_db

app = FastAPI(title="Hospital AI - 顾客端")
app.include_router(health_router)
app.include_router(example_items_router)


@app.on_event("startup")
def _startup() -> None:
    init_db()

