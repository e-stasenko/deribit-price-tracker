from functools import lru_cache
from pydantic import AnyHttpUrl, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Postgress
    POSTGRES_USER: str
    POSTGRES_PASSWORD:  str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # Redis
    REDIS_URL: RedisDsn

    # Deribit API
    DERIBIT_BASE_URL: AnyHttpUrl

    #App
    POLL_INTERVAL_MINUTES: int = 1

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
