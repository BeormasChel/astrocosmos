"""Точка входа агента интерактивной тумбы. Заглушка."""

from raspberry_pi.shared.config import DeviceConfig


def main() -> None:
    """Запустить агент тумбы (заглушка)."""

    config = DeviceConfig.from_env()
    print(f"Pedestal agent stub, device_id={config.device_id}")


if __name__ == "__main__":
    main()
