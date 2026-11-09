from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings, read from SEWSURE_* environment variables (or a local .env)."""

    model_config = SettingsConfigDict(env_prefix="SEWSURE_", env_file=".env", extra="ignore")

    environment: str = "local"
    database_url: str = "postgresql+psycopg://sewsure:change-me@localhost:5432/sewsure"
    job_max_attempts: int = 3
    # Provisional placeholder pending N4 calibration work; not an accuracy claim.
    ruler_tolerance_mm: float = 2.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
