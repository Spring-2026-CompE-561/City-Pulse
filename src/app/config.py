"""Application configuration."""

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings loaded from environment or .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    debug: bool = False
    # Use DATABASE_URL for full URL, or set MYSQL_* to build MySQL URL
    database_url: str | None = None
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "ulises"
    mysql_password: str = "Lilacw@v2020"
    mysql_database: str = "city_pulse"

    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    @model_validator(mode="after")
    def set_database_url(self) -> "Settings":
        if self.database_url is None or self.database_url == "":
            # Build MySQL URL from components (url-encode password for special chars)
            from urllib.parse import quote_plus
            password = quote_plus(self.mysql_password) if self.mysql_password else ""
            self.database_url = (
                f"mysql+asyncmy://{self.mysql_user}:{password}"
                f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"
            )
        return self


settings = Settings()
