"""
Custom exceptions for Anchor Stack.

Exception hierarchy:
    AnchorStackError (base)
    ├── StackNotFoundError
    ├── PackNotFoundError
    ├── PackCompatibilityError
    ├── TemplateRenderError
    └── ProjectValidationError

IMPORTANT: Always raise specific exceptions, not generic Exception.
           This enables better error handling and debugging.
"""

from __future__ import annotations

from typing import Any


class AnchorStackError(Exception):
    """
    Base exception for all Anchor Stack errors.

    All custom exceptions should inherit from this class.
    Provides structured error information for debugging.
    """

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize exception with structured information.

        Args:
            message: Human-readable error message
            code: Machine-readable error code (e.g., "STACK_NOT_FOUND")
            details: Additional context for debugging
        """
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__.upper()
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for JSON serialization."""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }

    def __str__(self) -> str:
        """Return formatted error message."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class StackNotFoundError(AnchorStackError):
    """
    Raised when a requested Stack cannot be found.

    Example:
        raise StackNotFoundError(
            "Stack 'nextjs@2025.1' not found",
            details={"stack_type": "nextjs", "version": "2025.1"}
        )
    """

    def __init__(
        self,
        message: str,
        *,
        stack_type: str | None = None,
        version: str | None = None,
    ) -> None:
        details = {}
        if stack_type:
            details["stack_type"] = stack_type
        if version:
            details["version"] = version
        super().__init__(message, code="STACK_NOT_FOUND", details=details)


class PackNotFoundError(AnchorStackError):
    """
    Raised when a requested Pack cannot be found.

    Example:
        raise PackNotFoundError(
            "Pack 'database-postgres' not found",
            details={"pack_name": "database-postgres"}
        )
    """

    def __init__(
        self,
        message: str,
        *,
        pack_name: str | None = None,
    ) -> None:
        details = {}
        if pack_name:
            details["pack_name"] = pack_name
        super().__init__(message, code="PACK_NOT_FOUND", details=details)


class PackCompatibilityError(AnchorStackError):
    """
    Raised when a Pack is not compatible with the target Stack.

    Example:
        raise PackCompatibilityError(
            "Pack 'ai-langgraph' is not compatible with Stack 'vue'",
            pack_name="ai-langgraph",
            stack_type="vue"
        )
    """

    def __init__(
        self,
        message: str,
        *,
        pack_name: str | None = None,
        stack_type: str | None = None,
    ) -> None:
        details = {}
        if pack_name:
            details["pack_name"] = pack_name
        if stack_type:
            details["stack_type"] = stack_type
        super().__init__(message, code="PACK_INCOMPATIBLE", details=details)


class TemplateRenderError(AnchorStackError):
    """
    Raised when template rendering fails.

    Example:
        raise TemplateRenderError(
            "Failed to render package.json template",
            template_name="package.json.j2",
            original_error=str(e)
        )
    """

    def __init__(
        self,
        message: str,
        *,
        template_name: str | None = None,
        original_error: str | None = None,
    ) -> None:
        details = {}
        if template_name:
            details["template_name"] = template_name
        if original_error:
            details["original_error"] = original_error
        super().__init__(message, code="TEMPLATE_RENDER_ERROR", details=details)


class ProjectValidationError(AnchorStackError):
    """
    Raised when project validation fails.

    Example:
        raise ProjectValidationError(
            "Invalid project configuration",
            field="app_name",
            reason="Must be lowercase alphanumeric"
        )
    """

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        reason: str | None = None,
    ) -> None:
        details = {}
        if field:
            details["field"] = field
        if reason:
            details["reason"] = reason
        super().__init__(message, code="PROJECT_VALIDATION_ERROR", details=details)


class FileWriteError(AnchorStackError):
    """
    Raised when file writing fails.

    Example:
        raise FileWriteError(
            "Failed to write file",
            file_path="/path/to/file",
            original_error=str(e)
        )
    """

    def __init__(
        self,
        message: str,
        *,
        file_path: str | None = None,
        original_error: str | None = None,
    ) -> None:
        details = {}
        if file_path:
            details["file_path"] = file_path
        if original_error:
            details["original_error"] = original_error
        super().__init__(message, code="FILE_WRITE_ERROR", details=details)
