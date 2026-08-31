"""Материалы зала: ролики, тексты, учёные и RFID-метки."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db, require_material_edit
from app.models.user import User
from app.schemas.material import MaterialPublic
from app.services import material_service
from app.services.material_service import MaterialError

router = APIRouter()


def _raise_material_error(error: MaterialError) -> None:
    """Передать текст ошибки педагогу без стека."""

    raise HTTPException(status_code=error.status_code, detail=error.message) from error


@router.get("", response_model=list[MaterialPublic])
async def list_materials(
    kind: str | None = None,
    device_id: str | None = None,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[MaterialPublic]:
    """Список материалов с фильтрами по виду и комплексу."""

    try:
        items = await material_service.list_materials(session, kind=kind, device_id=device_id)
    except MaterialError as error:
        _raise_material_error(error)
    return [MaterialPublic.model_validate(item) for item in items]


@router.get("/{material_id}", response_model=MaterialPublic)
async def get_material(
    material_id: str,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> MaterialPublic:
    """Одна карточка материала."""

    item = await material_service.get_material(session, material_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Такого материала нет")
    return MaterialPublic.model_validate(material_service.material_to_dict(item))


@router.get("/{material_id}/file")
async def download_material_file(
    material_id: str,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> FileResponse:
    """Отдать файл ролика или портрета (нужен вход в пульт)."""

    item = await material_service.get_material(session, material_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Такого материала нет")
    try:
        path = material_service.open_material_file(item)
    except MaterialError as error:
        _raise_material_error(error)
    media_type = item.mime_type or "application/octet-stream"
    filename = item.original_name or path.name
    return FileResponse(
        path,
        media_type=media_type,
        filename=filename,
        content_disposition_type="inline",
    )


@router.post("", response_model=MaterialPublic, status_code=201)
async def create_material(
    title: str = Form(...),
    kind: str = Form(...),
    device_id: str | None = Form(None),
    body: str | None = Form(None),
    clip_key: str | None = Form(None),
    rfid_uid: str | None = Form(None),
    file: UploadFile | None = File(None),
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_material_edit),
) -> MaterialPublic:
    """Добавить материал. Ролик можно сохранить без файла и догрузить позже."""

    try:
        data = await material_service.create_material(
            session,
            title=title,
            kind=kind,
            created_by=user.login,
            device_id=device_id,
            body=body,
            clip_key=clip_key,
            rfid_uid=rfid_uid,
            upload=file,
        )
    except MaterialError as error:
        _raise_material_error(error)
    return MaterialPublic.model_validate(data)


@router.patch("/{material_id}", response_model=MaterialPublic)
async def update_material(
    material_id: str,
    title: str | None = Form(None),
    device_id: str | None = Form(None),
    body: str | None = Form(None),
    clip_key: str | None = Form(None),
    rfid_uid: str | None = Form(None),
    file: UploadFile | None = File(None),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_material_edit),
) -> MaterialPublic:
    """Исправить имя, текст, метку или заменить файл."""

    # Пустой device_id в форме значит «все комплексы», а не «не трогать».
    clear_device = device_id is not None and device_id.strip() == ""
    try:
        data = await material_service.update_material(
            session,
            material_id,
            title=title,
            device_id=None if clear_device else device_id,
            body=body,
            clip_key=clip_key,
            rfid_uid=rfid_uid,
            upload=file,
            clear_device=clear_device,
        )
    except MaterialError as error:
        _raise_material_error(error)
    return MaterialPublic.model_validate(data)


@router.delete("/{material_id}", status_code=204)
async def delete_material(
    material_id: str,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_material_edit),
) -> None:
    """Убрать материал с полки и файл с диска."""

    try:
        await material_service.delete_material(session, material_id)
    except MaterialError as error:
        _raise_material_error(error)
