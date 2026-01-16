"""
Standardized logging module for Anchor Stack.

This module provides a consistent logging interface that:
- Uses structured logging with context
- Supports JSON output for production
- Provides human-readable output for development
- Allows log level configuration via environment

Usage:
    from anchor_stack.core import get_logger

    logger = get_logger(__name__)
    logger.info("Operation completed", extra={"user_id": 123, "action": "create"})

Log Levels:
    - DEBUG: Detailed information for debugging
    - INFO: Normal operational messages
    - WARNING: Something unexpected but not critical
    - ERROR: Error that needs attention
    - CRITICAL: System failure

IMPORTANT: Do not use print() or logging.basicConfig() directly.
           Always use get_logger() from this module.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

# Module-level state
_logging_configured = False
_log_level = logging.INFO
_json_output = False


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured log messages.

    In JSON mode, outputs machine-parseable JSON lines.
    In text mode, outputs human-readable formatted messages.
    """

    def __init__(self, json_output: bool = False) -> None:
        super().__init__()
        self._json_output = json_output

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured output."""
        # Build base log entry
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add location info for errors
        if record.levelno >= logging.ERROR:
            log_entry["location"] = {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields (excluding standard LogRecord attributes)
        standard_attrs = {
            "name",
            "msg",
            "args",
            "created",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "exc_info",
            "exc_text",
            "thread",
            "threadName",
            "taskName",
            "message",
        }

        extra_fields = {
            key: value
            for key, value in record.__dict__.items()
            if key not in standard_attrs and not key.startswith("_")
        }

        if extra_fields:
            log_entry["context"] = extra_fields

        if self._json_output:
            return json.dumps(log_entry, ensure_ascii=False, default=str)

        # Human-readable format
        return self._format_text(log_entry)

    def _format_text(self, log_entry: dict[str, Any]) -> str:
        """Format log entry as human-readable text."""
        timestamp = log_entry["timestamp"][:19].replace("T", " ")
        level = log_entry["level"]
        logger_name = log_entry["logger"]
        message = log_entry["message"]

        # Color codes for different levels (works in most terminals)
        level_colors = {
            "DEBUG": "\033[36m",  # Cyan
            "INFO": "\033[32m",  # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",  # Red
            "CRITICAL": "\033[35m",  # Magenta
        }
        reset = "\033[0m"
        color = level_colors.get(level, "")

        # Base message
        output = f"{timestamp} {color}{level:8}{reset} [{logger_name}] {message}"

        # Add context if present
        if "context" in log_entry:
            context_str = " ".join(f"{k}={v}" for k, v in log_entry["context"].items())
            output += f" | {context_str}"

        # Add exception if present
        if "exception" in log_entry:
            output += f"\n{log_entry['exception']}"

        return output


def setup_logging(
    level: int | str = logging.INFO,
    json_output: bool = False,
    force: bool = False,
) -> None:
    """
    Configure the logging system for Anchor Stack.

    This should be called once at application startup.
    Subsequent calls are ignored unless force=True.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: If True, output JSON format (for production)
        force: If True, reconfigure even if already configured

    Example:
        # Development
        setup_logging(level="DEBUG", json_output=False)

        # Production
        setup_logging(level="INFO", json_output=True)
    """
    global _logging_configured, _log_level, _json_output

    if _logging_configured and not force:
        return

    # Convert string level to int
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    _log_level = level
    _json_output = json_output

    # Get root logger for anchor_stack
    root_logger = logging.getLogger("anchor_stack")
    root_logger.setLevel(level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    handler.setFormatter(StructuredFormatter(json_output=json_output))

    root_logger.addHandler(handler)

    # Prevent propagation to root logger
    root_logger.propagate = False

    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    The logger is automatically namespaced under 'anchor_stack'.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured Logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("Starting process", extra={"task_id": 42})
    """
    # Ensure logging is configured
    if not _logging_configured:
        setup_logging()

    # Ensure name is under anchor_stack namespace
    if not name.startswith("anchor_stack"):
        name = f"anchor_stack.{name}"

    return logging.getLogger(name)


class LogContext:
    """
    Context manager for adding consistent context to log messages.

    Usage:
        with LogContext(logger, request_id="abc123", user_id=42):
            logger.info("Processing request")  # Includes request_id and user_id
    """

    def __init__(self, logger: logging.Logger, **context: Any) -> None:
        self._logger = logger
        self._context = context
        self._old_factory: Any = None

    def __enter__(self) -> LogContext:
        """Enter context and add fields to all log records."""
        old_factory = logging.getLogRecordFactory()
        context = self._context

        def record_factory(
            *args: Any, **kwargs: Any
        ) -> logging.LogRecord:
            record = old_factory(*args, **kwargs)
            for key, value in context.items():
                setattr(record, key, value)
            return record

        self._old_factory = old_factory
        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context and restore original factory."""
        if self._old_factory is not None:
            logging.setLogRecordFactory(self._old_factory)
