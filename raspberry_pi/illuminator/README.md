# Агент Иллюминатора (Raspberry Pi 5, 4K-видео через VLC)

Локальный плеер и MQTT-клиент. Контент читается с NFS (`/mnt/content/illuminator`).
Пульт посетителя — ESP32 в `microcontrollers/illuminator_remote/`.

При потере связи с ядром продолжает Attract Mode с локального кэша.
