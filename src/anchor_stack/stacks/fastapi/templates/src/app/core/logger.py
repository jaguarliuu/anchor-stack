"""
Logging Framework for {{ app_name | pascal_case }}.

IMPORTANT: This is a core module. Do not modify unless you know what you're doing.

Provides standardized logging with:
- Structured logging with context
- JSON output support for production
- Consistent format across the application

Usage:
    from app.core.logger import logger

    logger.info("User logged in", user_id=123)
    logger.error("Request failed", error=str(e))
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class StructuredFormatter(logging.Formatter):
    """Formatter that outputs structured logs."""

    def __init__(self, json_output: bool = False) -> None:
        super().__init__()
        self.json_output = json_output

    def format(self, record: logging.LogRecord) -> str:
        """Format log record."""
        # Base log data
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra context if present
        if hasattr(record, "context"):
            log_data["context"] = record.context

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if self.json_output:
            return json.dumps(log_data, default=str)

        # Human-readable format
        context_str = ""
        if "context" in log_data:
            context_str = " " + " ".join(
                f"{k}={v}" for k, v in log_data["context"].items()
            )

        return (
            f"{log_data['timestamp']} | {log_data['level']:8} | "
            f"{log_data['module']}:{log_data['function']}:{log_data['line']} | "
            f"{log_data['message']}{context_str}"
        )


class ContextLogger(logging.LoggerAdapter):
    """Logger adapter that supports structured context."""

    def process(
        self, msg: str, kwargs: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Process log message with context."""
        # Extract context from kwargs
        context = {k: v for k, v in kwargs.items() if k not in ("exc_info", "extra")}

        # Remove context keys from kwargs
        for key in context:
            kwargs.pop(key, None)

        # Add context to extra
        extra = kwargs.get("extra", {})
        extra["context"] = {**self.extra, **context}
        kwargs["extra"] = extra

        return msg, kwargs


def setup_logging(level: str = "INFO", json_output: bool = False) -> None:
    """
    Set up application logging.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: Whether to output logs as JSON
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredFormatter(json_output=json_output))
    root_logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str = "app", **context: Any) -> ContextLogger:
    """
    Get a logger instance with optional context.

    Args:
        name: Logger name
        **context: Default context to include in all logs

    Returns:
        ContextLogger instance

    Example:
        logger = get_logger("api", request_id="abc123")
        logger.info("Processing request", endpoint="/users")
    """
    base_logger = logging.getLogger(name)
    return ContextLogger(base_logger, context)


# Default logger instance
logger = get_logger("app")
