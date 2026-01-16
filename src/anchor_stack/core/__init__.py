"""
Core module - Framework essentials that should not be modified.

This module contains:
- Logger: Standardized logging infrastructure
- Config: Configuration management
- Exceptions: Custom exception hierarchy
- Constants: Project-wide constants
"""

from anchor_stack.core.config import Settings, get_settings
from anchor_stack.core.exceptions import (
    AnchorStackError,
    PackCompatibilityError,
    PackNotFoundError,
    ProjectValidationError,
    StackNotFoundError,
    TemplateRenderError,
)
from anchor_stack.core.logger import get_logger, setup_logging

__all__ = [
    # Logger
    "get_logger",
    "setup_logging",
    # Config
    "Settings",
    "get_settings",
    # Exceptions
    "AnchorStackError",
    "StackNotFoundError",
    "PackNotFoundError",
    "PackCompatibilityError",
    "TemplateRenderError",
    "ProjectValidationError",
]
