"""Загрузка конфигурации из переменных окружения."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения, читаемые из `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Astrocosmos"
    app_env: str = "development"
    app_debug: bool = True
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 480

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "astrocosmos"
    postgres_user: str = "astrocosmos"
    postgres_password: str = "change-me"

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_username: str = ""
    mqtt_password: str = ""
    mqtt_topic_prefix: str = "astroc"

    media_root: str = "/media/content"

    observatory_api_base_url: str = "http://localhost:8080/api"
    observatory_api_token: str = ""
    observatory_timeout_seconds: int = 15
    observatory_webhook_secret: str = ""

    @property
    def database_url(self) -> str:
        """Синхронный URL SQLAlchemy (для Alembic)."""

        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Вернуть кэшированный экземпляр настроек."""

    return Settings()
