"""Агент иллюминатора: heartbeat ядру и запуск Chromium kiosk.

Программный плеер — React в ``kiosk/`` на порту 3001.
Пульт ESP32 остаётся заглушкой до отдельного этапа прошивки.

Пример запуска с корня репозитория::

    set DEVICE_ID=illuminator
    set CORE_URL=http://127.0.0.1:8000
    python -m raspberry_pi.illuminator.agent

На Pi окно::

    chromium --kiosk --app=http://127.0.0.1:3001/?kiosk
"""

from __future__ import annotations

import logging
import os
import time
import urllib.error
import urllib.request

from raspberry_pi.shared.config import DeviceConfig

HEARTBEAT_SEC = 10
DEFAULT_CORE_URL = "http://127.0.0.1:8000"
DEVICE_ID = "illuminator"
CHROMIUM_HINT = "chromium --kiosk --app=http://127.0.0.1:3001/?kiosk"

logger = logging.getLogger(__name__)


def send_heartbeat(core_url: str) -> None:
    """Сообщить ядру, что иллюминатор на связи.

    Args:
        core_url: Базовый URL FastAPI без завершающего слэша.
    """

    url = f"{core_url.rstrip('/')}/api/v1/devices/{DEVICE_ID}/heartbeat"
    request = urllib.request.Request(url, data=b"", method="POST")
    with urllib.request.urlopen(request, timeout=5):
        return


def main() -> None:
    """Цикл heartbeat; Chromium запускает оператор или systemd."""

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    config = DeviceConfig.from_env()
    core_url = os.getenv("CORE_URL", DEFAULT_CORE_URL)

    # DEVICE_ID в env должен совпадать с реестром, но этот агент всегда пингует иллюминатор.
    logger.info(
        "Illuminator agent device_id=%s (env=%s) core=%s. Kiosk: %s",
        DEVICE_ID,
        config.device_id,
        core_url,
        CHROMIUM_HINT,
    )

    while True:
        try:
            send_heartbeat(core_url)
        except urllib.error.URLError as error:
            logger.warning("Heartbeat не прошёл: %s", error)
        time.sleep(HEARTBEAT_SEC)


if __name__ == "__main__":
    main()
