"""
Validation utilities for user input.
"""

from __future__ import annotations

import re

from anchor_stack.core.exceptions import ProjectValidationError


def validate_app_name(name: str) -> str:
    """
    Validate and normalize an application name.

    Rules:
    - Must start with a lowercase letter
    - Can contain lowercase letters, numbers, and hyphens
    - Cannot contain consecutive hyphens
    - Cannot end with a hyphen
    - Length: 1-100 characters

    Args:
        name: Application name to validate

    Returns:
        Normalized application name

    Raises:
        ProjectValidationError: If validation fails
    """
    name = name.lower().strip()

    if not name:
        raise ProjectValidationError(
            "Application name cannot be empty",
            field="app_name",
            reason="Empty value",
        )

    if len(name) > 100:
        raise ProjectValidationError(
            "Application name too long (max 100 characters)",
            field="app_name",
            reason="Exceeds maximum length",
        )

    if not re.match(r"^[a-z]", name):
        raise ProjectValidationError(
            "Application name must start with a lowercase letter",
            field="app_name",
            reason="Invalid start character",
        )

    if not re.match(r"^[a-z][a-z0-9-]*[a-z0-9]$|^[a-z]$", name):
        raise ProjectValidationError(
            "Application name can only contain lowercase letters, numbers, and hyphens",
            field="app_name",
            reason="Invalid characters",
        )

    if "--" in name:
        raise ProjectValidationError(
            "Application name cannot contain consecutive hyphens",
            field="app_name",
            reason="Consecutive hyphens",
        )

    return name


def validate_pack_name(name: str) -> str:
    """
    Validate and normalize a pack name.

    Rules:
    - Must start with a lowercase letter
    - Can contain lowercase letters, numbers, and hyphens
    - Length: 1-50 characters

    Args:
        name: Pack name to validate

    Returns:
        Normalized pack name

    Raises:
        ProjectValidationError: If validation fails
    """
    name = name.lower().strip()

    if not name:
        raise ProjectValidationError(
            "Pack name cannot be empty",
            field="pack_name",
            reason="Empty value",
        )

    if len(name) > 50:
        raise ProjectValidationError(
            "Pack name too long (max 50 characters)",
            field="pack_name",
            reason="Exceeds maximum length",
        )

    if not re.match(r"^[a-z][a-z0-9-]*$", name):
        raise ProjectValidationError(
            "Pack name must start with a letter and contain only "
            "lowercase letters, numbers, and hyphens",
            field="pack_name",
            reason="Invalid format",
        )

    return name


def validate_stack_type(stack_type: str, available: list[str]) -> str:
    """
    Validate that a stack type is available.

    Args:
        stack_type: Stack type to validate
        available: List of available stack types

    Returns:
        Normalized stack type

    Raises:
        ProjectValidationError: If stack type not available
    """
    stack_type = stack_type.lower().strip()

    available_lower = [s.lower() for s in available]

    if stack_type not in available_lower:
        raise ProjectValidationError(
            f"Stack type '{stack_type}' is not available. "
            f"Available: {', '.join(available)}",
            field="app_type",
            reason="Unknown stack type",
        )

    return stack_type
