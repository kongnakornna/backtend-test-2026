from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "School API"
    # SQLite works out of the box; use postgresql+asyncpg://... in production.
    database_url: str = "sqlite+aiosqlite:///./school.db"
    sql_echo: bool = False
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
