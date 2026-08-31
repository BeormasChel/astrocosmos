"""Точка входа агента Иллюминатора. Реализация — этап подключения комплекса."""

from raspberry_pi.shared.config import DeviceConfig


def main() -> None:
    """Запустить kiosk-агент (заглушка)."""

    config = DeviceConfig.from_env()
    print(f"Illuminator agent stub, device_id={config.device_id}")


if __name__ == "__main__":
    main()
