"""
Configuration management for Anchor Stack.

Uses pydantic-settings for type-safe configuration with:
- Environment variable support
- .env file loading
- Validation and defaults

Configuration Priority (highest to lowest):
1. Environment variables
2. .env file
3. Default values

IMPORTANT: Do not hardcode configuration values in code.
           Always use get_settings() to access configuration.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables
    with the ANCHOR_STACK_ prefix.

    Example:
        ANCHOR_STACK_LOG_LEVEL=DEBUG
        ANCHOR_STACK_LOG_JSON=true
    """

    model_config = SettingsConfigDict(
        env_prefix="ANCHOR_STACK_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Logging configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level for the application",
    )
    log_json: bool = Field(
        default=False,
        description="Output logs in JSON format (recommended for production)",
    )

    # Paths configuration
    stacks_dir: Path = Field(
        default=Path("stacks"),
        description="Directory containing Stack definitions",
    )
    packs_dir: Path = Field(
        default=Path("packs"),
        description="Directory containing Pack definitions",
    )

    # Server configuration
    server_name: str = Field(
        default="Anchor Stack",
        description="MCP Server display name",
    )
    server_version: str = Field(
        default="0.1.0",
        description="MCP Server version",
    )

    # Default stack version
    default_stack_version: str = Field(
        default="2026.1",
        description="Default Stack version when not specified",
    )

    @field_validator("stacks_dir", "packs_dir", mode="before")
    @classmethod
    def resolve_path(cls, v: str | Path) -> Path:
        """Convert string to Path and resolve relative to package root."""
        if isinstance(v, str):
            v = Path(v)
        return v

    def get_stacks_path(self) -> Path:
        """Get absolute path to stacks directory."""
        if self.stacks_dir.is_absolute():
            return self.stacks_dir
        # Resolve relative to package installation
        return self._get_package_root() / self.stacks_dir

    def get_packs_path(self) -> Path:
        """Get absolute path to packs directory."""
        if self.packs_dir.is_absolute():
            return self.packs_dir
        return self._get_package_root() / self.packs_dir

    @staticmethod
    def _get_package_root() -> Path:
        """Get the root directory of the installed package."""
        # config.py is at anchor_stack/core/config.py
        # package root is anchor_stack/
        return Path(__file__).parent.parent


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Settings are loaded once and cached for performance.
    Use this function instead of creating Settings() directly.

    Returns:
        Cached Settings instance

    Example:
        settings = get_settings()
        print(settings.log_level)
    """
    return Settings()


def clear_settings_cache() -> None:
    """
    Clear the settings cache.

    Use this when you need to reload settings,
    typically only in tests.
    """
    get_settings.cache_clear()
