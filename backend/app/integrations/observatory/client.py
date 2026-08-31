"""HTTP-клиент обсерваторного «Диптиха».

Контракт эндпоинтов описан в docs/integration/observatory_api.md.
Реальные пути уточняются, когда будет предоставлена спецификация API.
"""

from __future__ import annotations

import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ObservatoryClient:
    """Синхронный/асинхронный адаптер к REST API обсерватории."""

    def __init__(self) -> None:
        self._settings = get_settings()

    async def get_status(self) -> dict:
        """Запросить состояние купола, телескопа и метеодатчиков.

        Returns:
            JSON статуса. Пока возвращает заглушку, если API недоступно.
        """

        url = f"{self._settings.observatory_api_base_url.rstrip('/')}/status"
        headers = {}
        if self._settings.observatory_api_token:
            headers["Authorization"] = f"Bearer {self._settings.observatory_api_token}"

        timeout = self._settings.observatory_timeout_seconds
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            logger.warning("Обсерватория недоступна: %s", exc)
            return {"available": False, "error": str(exc)}
