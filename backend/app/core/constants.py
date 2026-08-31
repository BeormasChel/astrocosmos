"""Именованные константы проекта (без магических строк в коде)."""

MQTT_TOPIC_PREFIX = "astroc"

# Комплексы 1–6 в реестре. Тумба RFID — периферия большого голобокса.
DEVICE_MALY_GOLOBOX = "maly_golobox"
DEVICE_BOLSHOY_GOLOBOX = "bolshoy_golobox"
DEVICE_DESKTOP_DIPTYCH = "desktop_diptych"
DEVICE_PLANET_CLOCK = "planet_clock"
DEVICE_ILLUMINATOR = "illuminator"
DEVICE_ASTROVIZOR = "astrovizor"
DEVICE_OBSERVATORY = "observatory"

# Комплексы зала 1–6. Обсерватория и тумба сюда не входят.
HALL_DEVICE_IDS = (
    DEVICE_MALY_GOLOBOX,
    DEVICE_BOLSHOY_GOLOBOX,
    DEVICE_DESKTOP_DIPTYCH,
    DEVICE_PLANET_CLOCK,
    DEVICE_ILLUMINATOR,
    DEVICE_ASTROVIZOR,
)

RFID_READER_PN532 = "pn532"

# Роли пользователей (см. docs/context/05_glossary.md).
ROLE_ADMIN = "admin"
ROLE_EDUCATOR = "educator"
ROLE_ATTENDANT = "attendant"

DEVICE_OFFLINE_AFTER_SECONDS = 30

# Режимы астрономических часов (MQTT set_mode и пульт педагога).
CLOCK_MODE_IDLE = "idle"
CLOCK_MODE_COMPARE = "compare"
CLOCK_MODE_RETROGRADE = "retrograde"
CLOCK_MODE_JUPITER = "jupiter"
CLOCK_MODES = (
    CLOCK_MODE_IDLE,
    CLOCK_MODE_COMPARE,
    CLOCK_MODE_RETROGRADE,
    CLOCK_MODE_JUPITER,
)
CLOCK_EXTRAS_MODE_KEY = "clockMode"

# Виды материалов в пульте педагога (не «CMS»).
MATERIAL_KIND_VIDEO = "video"
MATERIAL_KIND_TEXT = "text"
MATERIAL_KIND_SCIENTIST = "scientist"
MATERIAL_KINDS = (
    MATERIAL_KIND_VIDEO,
    MATERIAL_KIND_TEXT,
    MATERIAL_KIND_SCIENTIST,
)
MATERIAL_KIND_LABELS = {
    MATERIAL_KIND_VIDEO: "Ролик",
    MATERIAL_KIND_TEXT: "Текст",
    MATERIAL_KIND_SCIENTIST: "Учёный",
}

# Загрузка роликов: верхняя граница, чтобы один файл не забил диск стенда.
MAX_UPLOAD_BYTES = 200 * 1024 * 1024
ALLOWED_VIDEO_MIME = frozenset({"video/mp4", "video/webm", "video/quicktime"})
ALLOWED_IMAGE_MIME = frozenset({"image/jpeg", "image/png", "image/webp"})
RFID_HEX_CHARS = "0123456789ABCDEF"

# Расписание зала: локальное время Челябинска, без cron в UI.
HALL_TIMEZONE = "Asia/Yekaterinburg"
WEEKDAY_LABELS = (
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье",
)
SCHEDULE_ACTOR = "schedule"
SCHEDULE_GRACE_SECONDS = 90

# Разделы малого голобокса (ключ совпадает с clip_key ролика и MQTT open_section).
HOLOBOX_IDLE_SECONDS = 60
HOLOBOX_SECTION_INTRO = "intro"
HOLOBOX_SECTION_STRUCTURE = "structure"
HOLOBOX_SECTION_FALL = "fall"
HOLOBOX_SECTION_HISTORY = "history"
HOLOBOX_SECTION_MAP = "map"
HOLOBOX_SECTION_COMPARE = "compare"
