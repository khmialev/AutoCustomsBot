from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.bot.constants.paths import ENV_PATH


class Settings(BaseSettings):
    # Telegram bot settings
    TELEGRAM_API_TOKEN: str | None = Field(
        None, description="Telegram Bot API Token"
    )
    TELEGRAM_ADMIN_ID: int | None = Field(
        None, description="Telegram Admin User ID for receiving error reports"
    )
    REQUEST_TIMEOUT: int = Field(
        default=15,
        description="Request timeout in seconds for Telegram API calls",
    )

    # Database settings
    PG_HOST: str | None = Field(
        default=None, description="Database server host"
    )
    PG_USER: str | None = Field(default=None, description="Database user")
    PG_PASS: str | None = Field(default=None, description="Database password")
    PG_PORT: int = Field(default=5432, description="Database server port")
    PG_DB_NAME: str | None = Field(default=None, description="Database name")

    DEBUG: bool = Field(default=False, description="Debug mode")

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
    )

    def get_db_engine_link(self) -> str | None:
        if all([self.PG_HOST, self.PG_USER, self.PG_PASS, self.PG_DB_NAME]):
            return f"postgresql+asyncpg://{self.PG_USER}:{self.PG_PASS}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB_NAME}"
        return None


@lru_cache()
def get_settings() -> Settings:
    """Returns a cached instance of the application settings."""
    return Settings()
