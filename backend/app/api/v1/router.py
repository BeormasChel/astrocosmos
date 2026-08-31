"""Корневой роутер `/api/v1`."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    content,
    devices,
    health,
    observatory,
    scenarios,
    schedule,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
api_router.include_router(
    observatory.router, prefix="/observatory", tags=["observatory"]
)
