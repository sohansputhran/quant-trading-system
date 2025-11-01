from __future__ import annotations
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv, find_dotenv

# Load nearest .env file (works from anywhere)
load_dotenv(find_dotenv(usecwd=True))


class Settings(BaseSettings):
    """
    Central configuration for all API keys and environment-level constants.
    Uses pydantic-settings (v2) for modern .env parsing.
    """

    # Core integrations
    FRED_API_KEY: str | None = None
    NEWSAPI_KEY: str | None = Field(default=None, alias="NEWS_API_KEY")  # 👈 maps NEWS_API_KEY -> NEWSAPI_KEY
    ALPACA_API_KEY: str | None = None
    ALPACA_API_SECRET_KEY: str | None = None
    ALPACA_PAPER: bool | None = True

    # Optional settings
    DATA_DIR: Path = Path("data")
    LOG_LEVEL: str = "INFO"

    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

# Ensure data directory exists
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

# Optional sanity warnings
if not settings.FRED_API_KEY:
    print("⚠️  FRED_API_KEY not set in .env")
if not settings.NEWSAPI_KEY:
    print("⚠️  NEWS_API_KEY not set in .env")
