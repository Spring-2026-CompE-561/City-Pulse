"""
Application configuration.

What lives here
- A Pydantic `Settings` object that loads config from environment
  variables (and `.env`).
- Database connection configuration:
  - Either a full `DATABASE_URL`, or MySQL parts (`MYSQL_HOST`, etc.)
    that are composed into a URL.
- Auth token expiration configuration.

Called by / import relationships
- Imported by most of the backend (`app.database`, `app.auth`,
  `app.main`) as `from app.config import settings`.
- `settings.database_url` is used to create the SQLAlchemy engine in
  `app.database`.
"""

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    App settings loaded from environment or `.env`.

    Notes
    - Fields are type-validated by Pydantic at startup/import time.
    - Unknown env vars are ignored (`extra="ignore"`).
    - `set_database_url` runs after validation to ensure
      `database_url` is always set.
    """

    # Pydantic Settings config:
    # - load from `.env` if present
    # - ignore extra/unknown environment variables
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Debug mode toggles verbose error details and SQLAlchemy echo logging.
    debug: bool = False
    # Use `DATABASE_URL` for a full URL, or set `MYSQL_*` to build a MySQL URL.
    database_url: str | None = None
    mysql_host: str | None = None
    mysql_port: int | None = None
    mysql_user: str | None = None
    mysql_password: str | None = None
    mysql_database: str | None = None

    # Token lifetimes (used by `app.auth` when minting tokens).
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    # JWT signing configuration.
    jwt_secret_key: str | None = None
    jwt_algorithm: str = "HS256"
    # CORS configuration.
    cors_allow_origins: str = "*"

    @model_validator(mode="after")
    def set_database_url(self) -> "Settings":
        """
        Ensure `database_url` is set after validation.

        Called by
        - Pydantic after it has populated the fields from env/.env.

        Used by
        - `app.database` which reads `settings.database_url` to create
          the engine.
        """
        if self.database_url is None or self.database_url == "":
            required_mysql_parts = {
                "MYSQL_HOST": self.mysql_host,
                "MYSQL_PORT": self.mysql_port,
                "MYSQL_USER": self.mysql_user,
                "MYSQL_PASSWORD": self.mysql_password,
                "MYSQL_DATABASE": self.mysql_database,
            }
            missing = [
                key for key, value in required_mysql_parts.items()
                if value is None or value == ""
            ]
            if missing:
                missing_csv = ", ".join(missing)
                raise ValueError(
                    "Missing database configuration. Set DATABASE_URL, "
                    f"or provide all MYSQL_* values. Missing: {missing_csv}"
                )

            # Build MySQL URL from components.
            # Password is URL-encoded to handle special characters safely.
            from urllib.parse import quote_plus
            password = (
                quote_plus(self.mysql_password) if self.mysql_password else ""
            )
            self.database_url = (
                f"mysql+asyncmy://{self.mysql_user}:{password}"
                f"@{self.mysql_host}:{self.mysql_port}/"
                f"{self.mysql_database}?charset=utf8mb4"
            )
        if self.jwt_secret_key is None or self.jwt_secret_key == "":
            raise ValueError(
                "Missing JWT configuration. Set JWT_SECRET_KEY in the environment."
            )

        return self

    def cors_allow_origins_list(self) -> list[str]:
        """
        Return CORS origins as a normalized list.

        Supports either:
        - "*" (allow all), or
        - Comma-separated origins, e.g. "http://localhost:3000,https://example.com".
        """
        raw = self.cors_allow_origins.strip()
        if not raw:
            return ["*"]
        if raw == "*":
            return ["*"]
        return [part.strip() for part in raw.split(",") if part.strip()]


# Singleton settings object used throughout the backend.
# Import pattern used everywhere: `from app.config import settings`
settings = Settings()
