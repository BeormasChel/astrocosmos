"""Киоск иллюминатора и малого голобокса без JWT."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.services import holobox_service, illuminator_service
from app.services.material_service import MaterialError

router = APIRouter()


class IlluminatorClipPublic(BaseModel):
    """Ролик в окне или в Attract Mode."""

    clipKey: str
    title: str
    hasFile: bool
    videoUrl: str | None = None


class IlluminatorWindowPublic(BaseModel):
    """Что показывает иллюминатор прямо сейчас."""

    deviceId: str
    mode: str
    clip: IlluminatorClipPublic | None = None
    attract: list[IlluminatorClipPublic]


def _raise_material(error: MaterialError) -> None:
    """404/400 без стека."""

    raise HTTPException(status_code=error.status_code, detail=error.message) from error


class HoloboxSectionPublic(BaseModel):
    """Раздел малого голобокса: подпись и ролик."""

    id: str
    title: str
    hint: str
    hasFile: bool
    videoUrl: str | None = None


class HoloboxWindowPublic(BaseModel):
    """Что показывает малый голобокс: Attract или раздел занятия."""

    deviceId: str
    mode: str
    lessonLocked: bool
    idleSeconds: int
    section: HoloboxSectionPublic | None = None
    sections: list[HoloboxSectionPublic]


@router.get("/illuminator", response_model=IlluminatorWindowPublic)
async def illuminator_window(
    session: AsyncSession = Depends(get_db),
) -> IlluminatorWindowPublic:
    """Состояние окна. Без входа: киоск в зале на локальной сети."""

    data = await illuminator_service.illuminator_window_state(session)
    return IlluminatorWindowPublic.model_validate(data)


@router.get("/illuminator/media/{clip_key}")
async def illuminator_media(
    clip_key: str,
    session: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Отдать видеофайл ролика для HTML5-плеера."""

    try:
        material, path = await illuminator_service.open_illuminator_clip_file(
            session,
            clip_key,
        )
    except MaterialError as error:
        _raise_material(error)
    media_type = material.mime_type or "video/mp4"
    filename = material.original_name or path.name
    return FileResponse(
        path,
        media_type=media_type,
        filename=filename,
        content_disposition_type="inline",
    )


@router.get("/maly", response_model=HoloboxWindowPublic)
async def maly_holobox_window(
    session: AsyncSession = Depends(get_db),
) -> HoloboxWindowPublic:
    """Меню разделов и раздел занятия. Без JWT: киоск в зале."""

    data = await holobox_service.holobox_window_state(session)
    return HoloboxWindowPublic.model_validate(data)


@router.get("/maly/media/{section_id}")
async def maly_holobox_media(
    section_id: str,
    session: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Отдать видеофайл раздела для HTML5-плеера."""

    try:
        material, path = await holobox_service.open_holobox_section_file(
            session,
            section_id,
        )
    except MaterialError as error:
        _raise_material(error)
    media_type = material.mime_type or "video/mp4"
    filename = material.original_name or path.name
    return FileResponse(
        path,
        media_type=media_type,
        filename=filename,
        content_disposition_type="inline",
    )
