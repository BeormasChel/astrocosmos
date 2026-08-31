"""Реестр и мониторинг комплексов."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.device import DevicePublic, HeartbeatResponse
from app.services import device_service

router = APIRouter()


@router.get("", response_model=list[DevicePublic])
async def list_devices(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[DevicePublic]:
    """Список комплексов зала."""

    items = await device_service.list_devices(session)
    return [DevicePublic.model_validate(item) for item in items]


@router.post("/{device_id}/heartbeat", response_model=HeartbeatResponse)
async def heartbeat(
    device_id: str,
    session: AsyncSession = Depends(get_db),
) -> HeartbeatResponse:
    """Агент киоска сообщает, что жив (на этапе A без отдельного ключа)."""

    device = await device_service.mark_heartbeat(session, device_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Неизвестный комплекс",
        )
    return HeartbeatResponse(
        id=device.id,
        status=device_service.compute_status(device),
    )
