from functools import lru_cache
from typing import Iterable

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost:5432/foodtracker"
    fixed_user_id: str = "00000000-0000-0000-0000-000000000001"
    recognition_stub_enabled: bool = True

    env: str = Field("development", env=("ENV", "APP_ENV"))
    log_level: str = "INFO"
    cors_origins: str | None = Field(None, env="CORS_ORIGINS")
    enable_docs: bool = Field(True, env="ENABLE_DOCS")

    db_pool_min_size: int = Field(1, env="DB_POOL_MIN_SIZE")
    db_pool_max_size: int = Field(5, env="DB_POOL_MAX_SIZE")
    db_pool_timeout: float = Field(5.0, env="DB_POOL_TIMEOUT")
    db_command_timeout: float = Field(10.0, env="DB_COMMAND_TIMEOUT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def is_production(self) -> bool:
        return self.env.lower() == "production"

    @property
    def parsed_cors_origins(self) -> list[str]:
        if not self.cors_origins:
            return []

        origins: list[str] = []
        for origin in self.cors_origins.split(","):
            candidate = origin.strip()
            if candidate:
                origins.append(candidate)
        return origins


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
