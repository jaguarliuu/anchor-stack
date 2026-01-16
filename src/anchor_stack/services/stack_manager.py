"""
Stack Manager - Load and manage Stack definitions.

Responsible for:
- Loading Stack definitions from YAML files
- Validating Stack configurations
- Providing Stack lookup by type and version
"""

from __future__ import annotations

from pathlib import Path

import yaml

from anchor_stack.core.config import get_settings
from anchor_stack.core.exceptions import StackNotFoundError
from anchor_stack.core.logger import get_logger
from anchor_stack.models.stack import Stack

logger = get_logger(__name__)


class StackManager:
    """
    Manages Stack definitions.

    Loads Stack configurations from the stacks directory
    and provides lookup functionality.

    Example:
        manager = StackManager()
        stack = manager.load("nextjs", "2025.1")
    """

    def __init__(self, stacks_dir: Path | None = None) -> None:
        """
        Initialize StackManager.

        Args:
            stacks_dir: Override default stacks directory
        """
        settings = get_settings()
        self._stacks_dir = stacks_dir or settings.get_stacks_path()
        self._cache: dict[str, Stack] = {}

        logger.debug(
            "StackManager initialized",
            extra={"stacks_dir": str(self._stacks_dir)},
        )

    def load(self, stack_type: str, version: str) -> Stack:
        """
        Load a Stack by type and version.

        Args:
            stack_type: Stack type identifier (e.g., "nextjs")
            version: Stack version (e.g., "2025.1")

        Returns:
            Stack instance

        Raises:
            StackNotFoundError: If Stack not found
        """
        cache_key = f"{stack_type}@{version}"

        # Check cache first
        if cache_key in self._cache:
            logger.debug("Stack loaded from cache", extra={"stack_id": cache_key})
            return self._cache[cache_key]

        # Find stack directory
        stack_dir = self._stacks_dir / stack_type
        if not stack_dir.exists():
            logger.error(
                "Stack type not found",
                extra={"stack_type": stack_type, "stacks_dir": str(self._stacks_dir)},
            )
            raise StackNotFoundError(
                f"Stack type '{stack_type}' not found",
                stack_type=stack_type,
                version=version,
            )

        # Load stack.yaml
        stack_file = stack_dir / "stack.yaml"
        if not stack_file.exists():
            logger.error(
                "stack.yaml not found",
                extra={"stack_dir": str(stack_dir)},
            )
            raise StackNotFoundError(
                f"Stack definition not found for '{stack_type}'",
                stack_type=stack_type,
                version=version,
            )

        # Parse YAML
        try:
            with open(stack_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(
                "Failed to parse stack.yaml",
                extra={"stack_file": str(stack_file), "error": str(e)},
            )
            raise StackNotFoundError(
                f"Failed to parse Stack definition: {e}",
                stack_type=stack_type,
                version=version,
            ) from e

        # Validate version matches
        if data.get("version") != version:
            available_version = data.get("version", "unknown")
            logger.warning(
                "Stack version mismatch",
                extra={
                    "requested": version,
                    "available": available_version,
                },
            )
            # For now, use whatever version is available
            # In the future, support multiple versions per stack type

        # Create Stack instance
        stack = Stack.from_yaml(data, source_path=stack_file)

        # Cache it
        self._cache[cache_key] = stack

        logger.info(
            "Stack loaded successfully",
            extra={"stack_id": cache_key, "display_name": stack.display_name},
        )

        return stack

    def list_available(self) -> list[dict[str, str]]:
        """
        List all available Stacks.

        Returns:
            List of stack info dicts with type, version, display_name
        """
        stacks = []

        if not self._stacks_dir.exists():
            logger.warning(
                "Stacks directory not found",
                extra={"stacks_dir": str(self._stacks_dir)},
            )
            return stacks

        for stack_dir in self._stacks_dir.iterdir():
            if not stack_dir.is_dir():
                continue

            stack_file = stack_dir / "stack.yaml"
            if not stack_file.exists():
                continue

            try:
                with open(stack_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                stacks.append(
                    {
                        "type": data.get("name", stack_dir.name),
                        "version": data.get("version", "unknown"),
                        "display_name": data.get("display_name", stack_dir.name),
                    }
                )
            except Exception as e:
                logger.warning(
                    "Failed to read stack",
                    extra={"stack_dir": str(stack_dir), "error": str(e)},
                )

        return stacks

    def clear_cache(self) -> None:
        """Clear the Stack cache."""
        self._cache.clear()
        logger.debug("Stack cache cleared")
