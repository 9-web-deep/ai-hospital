from fastapi import APIRouter, Depends

from ..services.ping import PingService, get_ping_service

router = APIRouter(tags=["health"])


@router.get("/health")
def health(ping: PingService = Depends(get_ping_service)) -> dict:
    return {"status": "ok", "service": ping.service_name}

