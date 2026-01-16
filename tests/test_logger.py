"""
Tests for logger module.
"""

import logging

from anchor_stack.core.logger import get_logger, setup_logging


class TestLogger:
    """Tests for logging functionality."""

    def test_get_logger_returns_logger(self) -> None:
        """Test get_logger returns a Logger instance."""
        logger = get_logger(__name__)
        assert isinstance(logger, logging.Logger)

    def test_get_logger_namespaced(self) -> None:
        """Test logger is namespaced under anchor_stack."""
        logger = get_logger("test_module")
        assert logger.name.startswith("anchor_stack")

    def test_setup_logging_configures_level(self) -> None:
        """Test setup_logging sets correct log level."""
        setup_logging(level="DEBUG", force=True)
        logger = get_logger(__name__)

        # The anchor_stack root logger should be at DEBUG
        root = logging.getLogger("anchor_stack")
        assert root.level == logging.DEBUG

    def test_logger_extra_fields(self) -> None:
        """Test logger handles extra fields without error."""
        logger = get_logger(__name__)

        # Should not raise
        logger.info("Test message", extra={"key": "value", "count": 42})
