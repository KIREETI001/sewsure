from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings, read from SEWSURE_* environment variables (or a local .env)."""

    model_config = SettingsConfigDict(env_prefix="SEWSURE_", env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://sewsure:change-me@localhost:5432/sewsure"
    # Azure: set all four to use Entra tokens instead of database_url (password auth is off).
    postgres_host: str = ""
    postgres_db: str = ""
    postgres_user: str = ""
    managed_identity_client_id: str = ""
    # Bearer token verification. Requests are rejected until all three are set.
    auth_issuer: str = ""
    auth_audience: str = ""
    auth_jwks_url: str = ""
    job_max_attempts: int = 3
    # A queued or running job untouched for this long lost its process (scale to zero, restart).
    job_abandoned_after_seconds: int = 600
    # Provisional placeholder pending N4 calibration work; not an accuracy claim.
    ruler_tolerance_mm: float = 2.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
