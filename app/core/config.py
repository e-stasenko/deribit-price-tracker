from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import AnyHttpUrl, RedisDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    app_title: str = "Трекер цен для биржи Deribit"
    description: str = "Трекер цен для биржи Deribit"

    # Postgress
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DRIVER: str = "psycopg2"

    DATABASE_URL_OVERRIDE: str | None = None

    # Redis
    REDIS_URL: RedisDsn

    # Deribit API
    DERIBIT_BASE_URL: AnyHttpUrl

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_URL_OVERRIDE:
            return self.DATABASE_URL_OVERRIDE

        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)
        host = self.POSTGRES_HOST
        port = self.POSTGRES_PORT
        db = quote_plus(self.POSTGRES_DB)
        driver = self.POSTGRES_DRIVER

        return f"postgresql+{driver}://{user}:{password}@{host}:{port}/{db}"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
