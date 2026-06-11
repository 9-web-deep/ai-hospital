from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PingService:
    service_name: str


def get_ping_service() -> PingService:
    return PingService(service_name="customer")

