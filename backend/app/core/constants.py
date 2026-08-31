"""Именованные константы проекта (без магических строк в коде)."""

MQTT_TOPIC_PREFIX = "astroc"

# Идентификаторы комплексов в реестре устройств.
DEVICE_PLANET_CLOCK = "planet_clock"
DEVICE_DESKTOP_DIPTYCH = "desktop_diptych"
DEVICE_MALY_GOLOBOX = "maly_golobox"
DEVICE_BOLSHOY_GOLOBOX = "bolshoy_golobox"
DEVICE_ILLUMINATOR = "illuminator"
DEVICE_ASTROVIZOR = "astrovizor"
DEVICE_PEDESTAL = "pedestal"
DEVICE_OBSERVATORY = "observatory"

# Роли пользователей (см. docs/context/05_glossary.md).
ROLE_ADMIN = "admin"
ROLE_EDUCATOR = "educator"
ROLE_ATTENDANT = "attendant"

# Интервал, после которого устройство считается офлайн (секунды).
DEVICE_OFFLINE_AFTER_SECONDS = 30
