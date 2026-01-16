"""
Pack Manager - Load and manage Pack definitions.

Responsible for:
- Loading Pack definitions from YAML files
- Validating Pack configurations
- Checking Pack compatibility with Stacks
"""

from __future__ import annotations

from pathlib import Path

import yaml

from anchor_stack.core.config import get_settings
from anchor_stack.core.exceptions import PackCompatibilityError, PackNotFoundError
from anchor_stack.core.logger import get_logger
from anchor_stack.models.pack import Pack

logger = get_logger(__name__)


class PackManager:
    """
    Manages Pack definitions.

    Loads Pack configurations from the packs directory
    and provides lookup and compatibility checking.

    Example:
        manager = PackManager()
        pack = manager.load("database-postgres")
        if pack.is_compatible_with("nextjs"):
            adapter = pack.get_adapter("nextjs")
    """

    def __init__(self, packs_dir: Path | None = None) -> None:
        """
        Initialize PackManager.

        Args:
            packs_dir: Override default packs directory
        """
        settings = get_settings()
        self._packs_dir = packs_dir or settings.get_packs_path()
        self._cache: dict[str, Pack] = {}

        logger.debug(
            "PackManager initialized",
            extra={"packs_dir": str(self._packs_dir)},
        )

    def load(self, pack_name: str) -> Pack:
        """
        Load a Pack by name.

        Args:
            pack_name: Pack identifier (e.g., "database-postgres")

        Returns:
            Pack instance

        Raises:
            PackNotFoundError: If Pack not found
        """
        # Normalize name
        pack_name = pack_name.lower().strip()

        # Check cache first
        if pack_name in self._cache:
            logger.debug("Pack loaded from cache", extra={"pack_name": pack_name})
            return self._cache[pack_name]

        # Find pack directory
        pack_dir = self._packs_dir / pack_name
        if not pack_dir.exists():
            logger.error(
                "Pack not found",
                extra={"pack_name": pack_name, "packs_dir": str(self._packs_dir)},
            )
            raise PackNotFoundError(
                f"Pack '{pack_name}' not found",
                pack_name=pack_name,
            )

        # Load pack.yaml
        pack_file = pack_dir / "pack.yaml"
        if not pack_file.exists():
            logger.error(
                "pack.yaml not found",
                extra={"pack_dir": str(pack_dir)},
            )
            raise PackNotFoundError(
                f"Pack definition not found for '{pack_name}'",
                pack_name=pack_name,
            )

        # Parse YAML
        try:
            with open(pack_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(
                "Failed to parse pack.yaml",
                extra={"pack_file": str(pack_file), "error": str(e)},
            )
            raise PackNotFoundError(
                f"Failed to parse Pack definition: {e}",
                pack_name=pack_name,
            ) from e

        # Create Pack instance
        pack = Pack.from_yaml(data, source_path=pack_file)

        # Cache it
        self._cache[pack_name] = pack

        logger.info(
            "Pack loaded successfully",
            extra={"pack_name": pack_name, "display_name": pack.display_name},
        )

        return pack

    def load_for_stack(self, pack_name: str, stack_type: str) -> Pack:
        """
        Load a Pack and verify compatibility with a Stack.

        Args:
            pack_name: Pack identifier
            stack_type: Stack type to check compatibility

        Returns:
            Pack instance

        Raises:
            PackNotFoundError: If Pack not found
            PackCompatibilityError: If Pack not compatible with Stack
        """
        pack = self.load(pack_name)

        if not pack.is_compatible_with(stack_type):
            logger.error(
                "Pack not compatible with Stack",
                extra={"pack_name": pack_name, "stack_type": stack_type},
            )
            raise PackCompatibilityError(
                f"Pack '{pack_name}' is not compatible with Stack '{stack_type}'",
                pack_name=pack_name,
                stack_type=stack_type,
            )

        return pack

    def list_available(self) -> list[dict[str, str | list[str]]]:
        """
        List all available Packs.

        Returns:
            List of pack info dicts with name, display_name, compatible_stacks
        """
        packs = []

        if not self._packs_dir.exists():
            logger.warning(
                "Packs directory not found",
                extra={"packs_dir": str(self._packs_dir)},
            )
            return packs

        for pack_dir in self._packs_dir.iterdir():
            if not pack_dir.is_dir():
                continue

            pack_file = pack_dir / "pack.yaml"
            if not pack_file.exists():
                continue

            try:
                with open(pack_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                packs.append(
                    {
                        "name": data.get("name", pack_dir.name),
                        "display_name": data.get("display_name", pack_dir.name),
                        "compatible_stacks": data.get("compatible_stacks", []),
                    }
                )
            except Exception as e:
                logger.warning(
                    "Failed to read pack",
                    extra={"pack_dir": str(pack_dir), "error": str(e)},
                )

        return packs

    def list_compatible(self, stack_type: str) -> list[dict[str, str]]:
        """
        List Packs compatible with a specific Stack.

        Args:
            stack_type: Stack type to filter by

        Returns:
            List of compatible pack info dicts
        """
        all_packs = self.list_available()
        compatible = []

        for pack_info in all_packs:
            compatible_stacks = pack_info.get("compatible_stacks", [])
            if isinstance(compatible_stacks, list):
                if stack_type.lower() in [s.lower() for s in compatible_stacks]:
                    compatible.append(
                        {
                            "name": str(pack_info["name"]),
                            "display_name": str(pack_info["display_name"]),
                        }
                    )

        return compatible

    def clear_cache(self) -> None:
        """Clear the Pack cache."""
        self._cache.clear()
        logger.debug("Pack cache cleared")
