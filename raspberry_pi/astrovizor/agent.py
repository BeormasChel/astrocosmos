"""Точка входа агента Астровизора. Заглушка."""

from raspberry_pi.shared.config import DeviceConfig


def main() -> None:
    """Запустить агент уличного киоска (заглушка)."""

    config = DeviceConfig.from_env()
    print(f"Astrovizor agent stub, device_id={config.device_id}")


if __name__ == "__main__":
    main()
