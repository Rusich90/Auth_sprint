from pydantic import BaseSettings, Field

from app.core.config import RedisSettings, SQLAlchemySettings


class TestSettings(BaseSettings):
    """Represents Test settings."""

    redis_settings: RedisSettings = RedisSettings()
    postgres_settings = SQLAlchemySettings = SQLAlchemySettings()

    test_url: str = Field("http://127.0.0.1:3000", env="TEST_URL")
    ping_backoff_timeout: int = Field(30, env="PING_BACKOFF_TIMEOUT")
