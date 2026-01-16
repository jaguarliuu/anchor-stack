"""Response schemas."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""

    success: bool = Field(default=True, description="Whether the request succeeded")
    data: T | None = Field(default=None, description="Response data")
    message: str | None = Field(default=None, description="Optional message")


class ErrorResponse(BaseModel):
    """Error response schema."""

    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    detail: Any | None = Field(default=None, description="Error details")
