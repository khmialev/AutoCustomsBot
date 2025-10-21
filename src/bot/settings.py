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

    # Proxy settings
    PROXY_HOST: str | None = Field(default=None, description="Proxy host")
    PROXY_PORT: str | None = Field(default=None, description="Proxy port")
    PROXY_USER: str | None = Field(default=None, description="Proxy user")
    PROXY_PASS: str | None = Field(default=None, description="Proxy password ")

    def get_proxy_url(self) -> str | None:
        if all(
            [self.PROXY_HOST, self.PROXY_PORT, self.PROXY_USER, self.PROXY_PASS]
        ):
            return f"https://{self.PROXY_USER}:{self.PROXY_PASS}@{self.PROXY_HOST}:{self.PROXY_PORT}"
        return None

    def get_proxy_config(self):
        if all(
            [self.PROXY_HOST, self.PROXY_PORT, self.PROXY_USER, self.PROXY_PASS]
        ):
            return {
                "server": f"http://{self.PROXY_HOST}:{self.PROXY_PORT}",
                "username": self.PROXY_USER,
                "password": self.PROXY_PASS,
            }
        return None

    AUCTION_BUTTON: float | None = Field(
        default=None, description="Coast auction button"
    )
    AUCTION_TAX: int | None = Field(default=None, description="Auction tax")
    DELIVERY: int | None = Field(default=None, description="Delivery")
    DECLARANTS: int | None = Field(default=None, description="Declarants")
    DISABLED_PERSON: int | None = Field(
        default=None, description="Disabled person"
    )

    EURO_USD: float | None = Field(
        default=None, description="Euro usd convertion"
    )  # temporary

    # Urls
    USD_URL: str | None = Field(default=None, description="Usd url")

    IAAI_SEARCH_URL: str | None = Field(
        default=None, description="Iaai search url"
    )
    IMAGE_URL: str | None = Field(default=None, description="Iaai iamge url")
    IAAI_IMAGE_URL: str | None = Field(
        default=None, description="Iaai iamge url"
    )
    IAAI_BASE_CAR_URL: str | None = Field(
        default=None, description="Iaai base car url"
    )

    COPART_LOT_IMAGES_URL: str | None = Field(
        default=None, description="Copart image url"
    )
    COPART_MAIN_URL: str | None = Field(
        default=None, description="Copart main url"
    )
    COPART_LOT_URL: str | None = Field(
        default=None, description="Copart lot url"
    )
    BIDCARS_TIPS: str | None = Field(default=None, description="Auction tax")

    AV_PAGE_URL: str | None = Field(default=None, description="Av page url")
    AV_BASE_URL: str | None = Field(default=None, description="Av base url")

    AV_STATISTIC_BASE_URl: str | None = Field(
        default=None, description="Av statistic url"
    )
    AV_STATISTIC_PATH: str | None = Field(
        default=None, description="Av statistic path"
    )
    AV_STATISTIC_BRAND_URl: str | None = Field(
        default=None, description="Av statistic brand url"
    )
    AV_STATISTIC_MODEL_URl: str | None = Field(
        default=None, description="Av statistic model url"
    )
    AV_STATISTIC_GENERATION_URl: str | None = Field(
        default=None, description="Av statistic generation url"
    )
    AV_STATISTIC_STATIC_URl: str | None = Field(
        default=None, description="Av statistic static url"
    )


@lru_cache()
def get_settings() -> Settings:
    """Returns a cached instance of the application settings."""
    return Settings()
