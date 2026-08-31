"""Агент большого голобокса и RFID тумбы (PN532). Заглушка до этапа E."""

from raspberry_pi.shared.config import DeviceConfig


def main() -> None:
    """Запустить агент (заглушка)."""

    config = DeviceConfig.from_env()
    print(f"bolshoy_golobox agent stub, device_id={config.device_id}")


if __name__ == "__main__":
    main()
