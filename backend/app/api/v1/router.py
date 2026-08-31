"""Корневой роутер `/api/v1`."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    clocks,
    comfort,
    content,
    devices,
    hall,
    health,
    kiosk,
    observatory,
    scenarios,
    schedule,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(scenarios.router, prefix="/lessons", tags=["lessons"])
api_router.include_router(content.router, prefix="/materials", tags=["materials"])
api_router.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
api_router.include_router(hall.router, prefix="/hall", tags=["hall"])
api_router.include_router(kiosk.router, prefix="/kiosk", tags=["kiosk"])
api_router.include_router(clocks.router, prefix="/clocks", tags=["clocks"])
api_router.include_router(comfort.router, prefix="/comfort", tags=["comfort"])
api_router.include_router(
    observatory.router, prefix="/observatory", tags=["observatory"]
)
