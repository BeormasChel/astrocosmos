"""Pydantic-схемы запросов и ответов API."""

from app.schemas.auth import LoginRequest, TokenResponse, UserPublic
from app.schemas.device import DevicePublic, HeartbeatResponse
from app.schemas.lesson import LessonPublic, LessonRunPublic
from app.schemas.material import MaterialPublic
from app.schemas.schedule import SchedulePublic
