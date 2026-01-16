"""
Anchor Stack - AI-friendly engineering foundation.

A MCP Server that provides stable versions, unified logging,
and pluggable capability packs for AI-assisted development.
"""

from anchor_stack.core.logger import get_logger, setup_logging

__version__ = "0.1.2"
__all__ = ["__version__", "get_logger", "setup_logging"]
