"""
Stack Spec model - User input specification for project creation.

This is the primary input from users when creating a new project.
It declares what they want, not how to build it.
"""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class StackSpec(BaseModel):
    """
    User-provided specification for creating a new project.

    This is the "what" - users declare their requirements,
    and Anchor Stack figures out the "how".

    Example:
        spec = StackSpec(
            app_name="my-awesome-app",
            app_type="nextjs",
            stack_version="2025.1",
            capabilities=["database-postgres", "ai-langgraph"]
        )
    """

    app_name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="Project name (lowercase, alphanumeric, hyphens allowed)",
            examples=["my-app", "awesome-project"],
        ),
    ]

    app_type: Annotated[
        str,
        Field(
            description="Stack type identifier",
            examples=["nextjs", "python-api", "vue"],
        ),
    ]

    stack_version: Annotated[
        str,
        Field(
            default="2025.1",
            description="Stack version to use",
            examples=["2025.1", "2025.2"],
        ),
    ]

    capabilities: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="List of Pack names to include",
            examples=[["database-postgres", "ai-langgraph"]],
        ),
    ]

    description: Annotated[
        str | None,
        Field(
            default=None,
            max_length=500,
            description="Optional project description",
        ),
    ]

    author: Annotated[
        str | None,
        Field(
            default=None,
            max_length=100,
            description="Optional author name",
        ),
    ]

    @field_validator("app_name")
    @classmethod
    def validate_app_name(cls, v: str) -> str:
        """
        Validate app_name follows naming conventions.

        Rules:
        - Lowercase letters, numbers, hyphens only
        - Must start with a letter
        - No consecutive hyphens
        - No trailing hyphens
        """
        v = v.lower().strip()

        if not re.match(r"^[a-z][a-z0-9-]*[a-z0-9]$|^[a-z]$", v):
            raise ValueError(
                "app_name must start with a letter, contain only lowercase letters, "
                "numbers, and hyphens, and not end with a hyphen"
            )

        if "--" in v:
            raise ValueError("app_name cannot contain consecutive hyphens")

        return v

    @field_validator("app_type")
    @classmethod
    def validate_app_type(cls, v: str) -> str:
        """Normalize app_type to lowercase."""
        return v.lower().strip()

    @field_validator("capabilities")
    @classmethod
    def validate_capabilities(cls, v: list[str]) -> list[str]:
        """Normalize and deduplicate capabilities."""
        # Normalize to lowercase and remove duplicates while preserving order
        seen: set[str] = set()
        result: list[str] = []
        for cap in v:
            cap_lower = cap.lower().strip()
            if cap_lower and cap_lower not in seen:
                seen.add(cap_lower)
                result.append(cap_lower)
        return result

    @property
    def stack_id(self) -> str:
        """Get full stack identifier (type@version)."""
        return f"{self.app_type}@{self.stack_version}"
