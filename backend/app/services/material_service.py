"""Каталог материалов: метаданные в БД, файлы на диске."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.constants import (
    ALLOWED_IMAGE_MIME,
    ALLOWED_VIDEO_MIME,
    MATERIAL_KIND_LABELS,
    MATERIAL_KIND_SCIENTIST,
    MATERIAL_KIND_TEXT,
    MATERIAL_KIND_VIDEO,
    MATERIAL_KINDS,
    MAX_UPLOAD_BYTES,
    RFID_HEX_CHARS,
)
from app.models.device import Device
from app.models.material import Material

VIDEO_SUFFIXES = {".mp4", ".webm", ".mov"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
CLIP_KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,62}$")


class MaterialError(Exception):
    """Ошибка сохранения материала с текстом для педагога."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def resolve_media_root() -> Path:
    """Папка файлов: локально рядом с БД, в зале — NFS.

    Returns:
        Абсолютный путь; каталог создаётся при отсутствии.
    """

    raw = Path(get_settings().media_root)
    path = raw if raw.is_absolute() else (Path.cwd() / raw).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def normalize_optional(value: str | None) -> str | None:
    """Пустую строку из формы превратить в None."""

    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def normalize_rfid(raw: str | None) -> str | None:
    """Оставить только HEX UID метки PN532.

    Args:
        raw: Строка с пробелами, двоеточиями или как есть.

    Returns:
        Верхний регистр без разделителей или None.
    """

    cleaned_source = normalize_optional(raw)
    if cleaned_source is None:
        return None
    hex_only = "".join(ch for ch in cleaned_source.upper() if ch in RFID_HEX_CHARS)
    return hex_only or None


def normalize_clip_key(raw: str | None) -> str | None:
    """Короткий ключ ролика для команды занятия (например welcome)."""

    value = normalize_optional(raw)
    if value is None:
        return None
    slug = value.strip().lower().replace(" ", "_")
    if not CLIP_KEY_PATTERN.match(slug):
        raise MaterialError(
            "Короткое имя ролика — латиница, цифры, дефис или подчёркивание "
            "(например welcome или impact)"
        )
    return slug


def _file_path(stored_name: str) -> Path:
    """Полный путь к сохранённому файлу."""

    return resolve_media_root() / stored_name


def material_to_dict(item: Material) -> dict:
    """Собрать JSON карточки для пульта."""

    device_name = "Все комплексы"
    if item.device is not None:
        device_name = item.device.name
    elif item.device_id:
        device_name = item.device_id
    return {
        "id": item.id,
        "kind": item.kind,
        "kindLabel": MATERIAL_KIND_LABELS.get(item.kind, item.kind),
        "title": item.title,
        "body": item.body,
        "deviceId": item.device_id,
        "deviceName": device_name,
        "clipKey": item.clip_key,
        "rfidUid": item.rfid_uid,
        "hasFile": bool(item.stored_name),
        "originalName": item.original_name,
        "mimeType": item.mime_type,
        "byteSize": item.byte_size,
        "createdBy": item.created_by,
        "createdAt": item.created_at.isoformat(),
    }


async def _ensure_device(session: AsyncSession, device_id: str | None) -> str | None:
    """Проверить, что комплекс есть в реестре, либо вернуть None для всех залов."""

    if device_id is None:
        return None
    device = await session.get(Device, device_id)
    if device is None:
        raise MaterialError("Такого комплекса нет в зале")
    return device_id


async def _assert_rfid_free(
    session: AsyncSession,
    rfid_uid: str | None,
    skip_id: str | None = None,
) -> None:
    """Одна метка — один учёный."""

    if rfid_uid is None:
        return
    query = select(Material.id).where(Material.rfid_uid == rfid_uid)
    if skip_id is not None:
        query = query.where(Material.id != skip_id)
    taken = await session.scalar(query)
    if taken is not None:
        raise MaterialError("Эта метка уже привязана к другому учёному", status_code=409)


def _suffix_and_mime(upload: UploadFile) -> tuple[str, str]:
    """Определить расширение и тип по имени файла и заголовку."""

    filename = upload.filename or "file"
    suffix = Path(filename).suffix.lower()
    mime = (upload.content_type or "").split(";")[0].strip().lower()
    if suffix in VIDEO_SUFFIXES or mime in ALLOWED_VIDEO_MIME:
        if suffix not in VIDEO_SUFFIXES:
            suffix = ".mp4"
        if mime not in ALLOWED_VIDEO_MIME:
            mime = "video/mp4"
        return suffix, mime
    if suffix in IMAGE_SUFFIXES or mime in ALLOWED_IMAGE_MIME:
        if suffix not in IMAGE_SUFFIXES:
            suffix = ".jpg"
        if mime not in ALLOWED_IMAGE_MIME:
            mime = "image/jpeg"
        return suffix, mime
    raise MaterialError("Нужен ролик (mp4, webm) или картинка (jpg, png, webp)")


def _validate_file_for_kind(kind: str, suffix: str, mime: str) -> None:
    """Ролику — видео, учёному — фото или ролик, тексту файл не нужен."""

    is_video = suffix in VIDEO_SUFFIXES or mime in ALLOWED_VIDEO_MIME
    is_image = suffix in IMAGE_SUFFIXES or mime in ALLOWED_IMAGE_MIME
    if kind == MATERIAL_KIND_TEXT:
        raise MaterialError("К тексту файл не прикладывают — напишите его в поле ниже")
    if kind == MATERIAL_KIND_VIDEO and not is_video:
        raise MaterialError("Для ролика загрузите видеофайл (лучше mp4)")
    if kind == MATERIAL_KIND_SCIENTIST and not (is_video or is_image):
        raise MaterialError("Для учёного можно приложить портрет или короткий ролик")


async def _store_upload(material_id: str, kind: str, upload: UploadFile) -> tuple[str, str, str, int]:
    """Записать файл на диск и вернуть имя, оригинал, mime, размер."""

    suffix, mime = _suffix_and_mime(upload)
    _validate_file_for_kind(kind, suffix, mime)
    stored_name = f"{material_id}{suffix}"
    destination = _file_path(stored_name)
    size = 0
    try:
        with destination.open("wb") as out:
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise MaterialError("Файл больше 200 МБ — такой на стенд не кладём")
                out.write(chunk)
    except MaterialError:
        destination.unlink(missing_ok=True)
        raise
    if size == 0:
        destination.unlink(missing_ok=True)
        raise MaterialError("Файл пустой")
    original = Path(upload.filename or stored_name).name
    return stored_name, original, mime, size


def _unlink_stored(stored_name: str | None) -> None:
    """Удалить файл с диска, если он был."""

    if not stored_name:
        return
    _file_path(stored_name).unlink(missing_ok=True)


async def list_materials(
    session: AsyncSession,
    kind: str | None = None,
    device_id: str | None = None,
) -> list[dict]:
    """Список материалов, новые сверху.

    Args:
        session: Сессия БД.
        kind: video / text / scientist или все.
        device_id: Комплекс или все.

    Returns:
        Карточки для пульта.
    """

    query = select(Material).options(selectinload(Material.device))
    if kind:
        if kind not in MATERIAL_KINDS:
            raise MaterialError("Неизвестный вид материала")
        query = query.where(Material.kind == kind)
    if device_id:
        query = query.where(Material.device_id == device_id)
    query = query.order_by(Material.created_at.desc())
    result = await session.scalars(query)
    return [material_to_dict(item) for item in result.all()]


async def get_material(session: AsyncSession, material_id: str) -> Material | None:
    """Найти материал по id."""

    return await session.scalar(
        select(Material)
        .options(selectinload(Material.device))
        .where(Material.id == material_id)
    )


async def get_clip_for_device(
    session: AsyncSession,
    clip_key: str,
    device_id: str,
) -> Material | None:
    """Найти ролик по короткому ключу занятия для комплекса.

    Args:
        session: Сессия БД.
        clip_key: Ключ из команды play (welcome, impact).
        device_id: Комплекс, для которого ищем ролик.

    Returns:
        Материал или None.
    """

    return await session.scalar(
        select(Material)
        .options(selectinload(Material.device))
        .where(
            Material.kind == MATERIAL_KIND_VIDEO,
            Material.clip_key == clip_key,
            or_(Material.device_id == device_id, Material.device_id.is_(None)),
        )
        .order_by(Material.created_at.desc())
    )


async def list_video_clips_for_device(session: AsyncSession, device_id: str) -> list[Material]:
    """Ролики комплекса для Attract Mode (с ключом клипа)."""

    result = await session.scalars(
        select(Material)
        .options(selectinload(Material.device))
        .where(
            Material.kind == MATERIAL_KIND_VIDEO,
            Material.clip_key.is_not(None),
            or_(Material.device_id == device_id, Material.device_id.is_(None)),
        )
        .order_by(Material.title)
    )
    return list(result.all())


def open_material_file(item: Material) -> Path:
    """Путь к файлу для отдачи в HTTP.

    Raises:
        MaterialError: Файла нет.
    """

    if not item.stored_name:
        raise MaterialError("К этому материалу файл ещё не приложили", status_code=404)
    path = _file_path(item.stored_name)
    if not path.is_file():
        raise MaterialError("Файл пропал с диска сервера", status_code=404)
    return path


async def create_material(
    session: AsyncSession,
    *,
    title: str,
    kind: str,
    created_by: str,
    device_id: str | None = None,
    body: str | None = None,
    clip_key: str | None = None,
    rfid_uid: str | None = None,
    upload: UploadFile | None = None,
) -> dict:
    """Создать материал и при желании сохранить файл.

    Args:
        session: Сессия БД.
        title: Человеческое имя («Вид с МКС»).
        kind: video, text или scientist.
        created_by: Логин педагога.
        device_id: Комплекс или все залы.
        body: Текст факта или биографии.
        clip_key: Ключ для команды play.
        rfid_uid: UID метки фигурки.
        upload: Необязательный файл.

    Returns:
        Карточка материала.
    """

    clean_title = (title or "").strip()
    if not clean_title:
        raise MaterialError("Дайте материалу понятное имя")
    if kind not in MATERIAL_KINDS:
        raise MaterialError("Выберите вид: ролик, текст или учёный")

    # Нормализуем поля формы и проверяем комплекс и метку.
    clean_device = await _ensure_device(session, normalize_optional(device_id))
    clean_body = normalize_optional(body)
    clean_clip = normalize_clip_key(clip_key)
    clean_rfid = normalize_rfid(rfid_uid)
    if kind == MATERIAL_KIND_SCIENTIST and not clean_rfid:
        raise MaterialError("Для учёного укажите UID метки с фигурки")
    if kind != MATERIAL_KIND_SCIENTIST and clean_rfid:
        raise MaterialError("Метку RFID привязывают только к учёному")
    if kind == MATERIAL_KIND_TEXT and not clean_body:
        raise MaterialError("Напишите текст, который увидят на комплексе")
    await _assert_rfid_free(session, clean_rfid)

    material_id = str(uuid.uuid4())
    stored_name = None
    original_name = None
    mime_type = None
    byte_size = None
    has_upload = upload is not None and bool(upload.filename)
    if has_upload:
        stored_name, original_name, mime_type, byte_size = await _store_upload(
            material_id, kind, upload
        )

    item = Material(
        id=material_id,
        kind=kind,
        title=clean_title,
        body=clean_body,
        device_id=clean_device,
        clip_key=clean_clip,
        rfid_uid=clean_rfid,
        stored_name=stored_name,
        original_name=original_name,
        mime_type=mime_type,
        byte_size=byte_size,
        created_by=created_by,
        created_at=datetime.now(timezone.utc),
    )
    session.add(item)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise MaterialError("Эта метка уже привязана к другому учёному", status_code=409) from None
    loaded = await get_material(session, material_id)
    assert loaded is not None
    return material_to_dict(loaded)


async def update_material(
    session: AsyncSession,
    material_id: str,
    *,
    title: str | None = None,
    device_id: str | None = None,
    body: str | None = None,
    clip_key: str | None = None,
    rfid_uid: str | None = None,
    upload: UploadFile | None = None,
    clear_device: bool = False,
) -> dict:
    """Обновить метаданные и при желании заменить файл."""

    item = await get_material(session, material_id)
    if item is None:
        raise MaterialError("Такого материала нет", status_code=404)

    if title is not None:
        clean_title = title.strip()
        if not clean_title:
            raise MaterialError("Дайте материалу понятное имя")
        item.title = clean_title
    if body is not None:
        item.body = normalize_optional(body)
        if item.kind == MATERIAL_KIND_TEXT and not item.body:
            raise MaterialError("Напишите текст, который увидят на комплексе")
    if clip_key is not None:
        item.clip_key = normalize_clip_key(clip_key)
    if rfid_uid is not None:
        clean_rfid = normalize_rfid(rfid_uid)
        if item.kind == MATERIAL_KIND_SCIENTIST and not clean_rfid:
            raise MaterialError("Для учёного укажите UID метки с фигурки")
        if item.kind != MATERIAL_KIND_SCIENTIST and clean_rfid:
            raise MaterialError("Метку RFID привязывают только к учёному")
        await _assert_rfid_free(session, clean_rfid, skip_id=item.id)
        item.rfid_uid = clean_rfid
    if clear_device:
        item.device_id = None
    elif device_id is not None:
        item.device_id = await _ensure_device(session, normalize_optional(device_id))

    has_upload = upload is not None and bool(upload.filename)
    if has_upload:
        stored_name, original_name, mime_type, byte_size = await _store_upload(
            item.id, item.kind, upload
        )
        if item.stored_name and item.stored_name != stored_name:
            _unlink_stored(item.stored_name)
        item.stored_name = stored_name
        item.original_name = original_name
        item.mime_type = mime_type
        item.byte_size = byte_size

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise MaterialError("Эта метка уже привязана к другому учёному", status_code=409) from None
    loaded = await get_material(session, material_id)
    assert loaded is not None
    return material_to_dict(loaded)


async def delete_material(session: AsyncSession, material_id: str) -> None:
    """Удалить карточку и файл с диска."""

    item = await get_material(session, material_id)
    if item is None:
        raise MaterialError("Такого материала нет", status_code=404)
    _unlink_stored(item.stored_name)
    await session.delete(item)
    await session.commit()
