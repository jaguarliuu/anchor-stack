"""
Configuration Management for {{ app_name | pascal_case }}.

IMPORTANT: This is a core module. Do not modify unless you know what you're doing.

Uses pydantic-settings for type-safe configuration with:
- Environment variable support
- .env file loading
- Validation and defaults

Usage:
    from app.core.config import settings

    database_url = settings.database_url
    debug_mode = settings.debug
"""

from functools import lru_cache
from typing import List, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(
        default="{{ app_name }}",
        description="Application name",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    # Server
    host: str = Field(
        default="0.0.0.0",
        description="Server host",
    )
    port: int = Field(
        default=8000,
        description="Server port",
    )

    # Database
    database_url: str = Field(
        default="sqlite:///./app.db",
        description="Database connection URL",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )
    log_json: bool = Field(
        default=False,
        description="Output logs in JSON format",
    )

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.debug


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Returns:
        Cached Settings instance
    """
    return Settings()


# Singleton instance for easy import
settings = get_settings()
