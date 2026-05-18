from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for AutoTrain Data Forge."""

    model_config = SettingsConfigDict(env_prefix="ADF_", env_file=".env", extra="ignore")

    env: str = "local"
    default_user_agent: str = "AutoTrainDataForge/0.1"
    request_timeout_seconds: float = 15.0
    max_image_bytes: int = 5_000_000


@lru_cache
def get_settings() -> Settings:
    return Settings()

