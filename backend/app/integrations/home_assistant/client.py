"""HTTP-адаптер Home Assistant.

Вызывается из сценариев и с настольного Диптиха. Купол не трогаем.
"""

from __future__ import annotations

import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class HomeAssistantClient:
    """Вызов сервисов HA. Если база URL пустая — no-op."""

    def __init__(self) -> None:
        self._settings = get_settings()

    @property
    def enabled(self) -> bool:
        """Проверить, задан ли адрес HA."""

        return bool(getattr(self._settings, "ha_base_url", ""))

    async def call_service(self, domain: str, service: str, payload: dict) -> dict:
        """Вызвать `/api/services/{domain}/{service}`.

        Args:
            domain: Например ``light`` или ``cover``.
            service: Например ``turn_off``.
            payload: Тело JSON (entity_id и параметры).

        Returns:
            Ответ HA или пометку, что интеграция выключена.
        """

        base = getattr(self._settings, "ha_base_url", "")
        if not base:
            logger.info("Home Assistant не настроен, шаг комфорта пропущен")
            return {"ok": True, "skipped": True}

        url = f"{base.rstrip('/')}/api/services/{domain}/{service}"
        token = getattr(self._settings, "ha_token", "")
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return {"ok": True, "data": response.json()}
