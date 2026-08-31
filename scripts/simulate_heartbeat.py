"""Эмулятор heartbeat комплексов без железа.

Ядро само пульсирует зал, если HALL_EMULATOR_ENABLED=true.
Этот скрипт — разовый или циклический пульс с другой машины.

Примеры:
  python scripts/simulate_heartbeat.py
  python scripts/simulate_heartbeat.py --loop
  python scripts/simulate_heartbeat.py maly_golobox illuminator
"""

from __future__ import annotations

import argparse
import time

import httpx

DEFAULT_DEVICES = [
    "maly_golobox",
    "bolshoy_golobox",
    "desktop_diptych",
    "planet_clock",
    "illuminator",
    "astrovizor",
]
BASE_URL = "http://127.0.0.1:8000/api/v1"
LOOP_SECONDS = 10


def pulse(client: httpx.Client, device_ids: list[str]) -> None:
    """Отправить heartbeat выбранным комплексам."""

    for device_id in device_ids:
        response = client.post(f"{BASE_URL}/devices/{device_id}/heartbeat")
        print(device_id, response.status_code, response.text)


def main() -> None:
    """Разовый пульс или цикл, пока не остановят."""

    parser = argparse.ArgumentParser(description="Heartbeat комплексов зала без железа")
    parser.add_argument("devices", nargs="*", help="id комплексов, по умолчанию все шесть")
    parser.add_argument(
        "--loop",
        action="store_true",
        help="повторять каждые 10 секунд",
    )
    args = parser.parse_args()
    device_ids = args.devices or DEFAULT_DEVICES

    with httpx.Client(timeout=5.0) as client:
        while True:
            pulse(client, device_ids)
            if not args.loop:
                break
            time.sleep(LOOP_SECONDS)


if __name__ == "__main__":
    main()
