"""
File Writer - Write files to filesystem.

Responsible for:
- Creating directories
- Writing files with proper encoding
- Updating existing files (e.g., package.json)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from anchor_stack.core.exceptions import FileWriteError
from anchor_stack.core.logger import get_logger

logger = get_logger(__name__)


class FileWriter:
    """
    Writes files to the filesystem.

    Handles:
    - Directory creation
    - File writing with encoding
    - JSON file merging
    - Tracking created files

    Example:
        writer = FileWriter("/path/to/project")
        writer.write_file("src/index.ts", content)
        print(writer.files_created)
    """

    def __init__(self, base_dir: str | Path) -> None:
        """
        Initialize FileWriter.

        Args:
            base_dir: Base directory for all file operations
        """
        self._base_dir = Path(base_dir).resolve()
        self._files_created: list[str] = []

        logger.debug(
            "FileWriter initialized",
            extra={"base_dir": str(self._base_dir)},
        )

    @property
    def base_dir(self) -> Path:
        """Get the base directory."""
        return self._base_dir

    @property
    def files_created(self) -> list[str]:
        """Get list of created file paths (relative to base_dir)."""
        return self._files_created.copy()

    def ensure_dir(self, relative_path: str | Path = "") -> Path:
        """
        Ensure a directory exists.

        Args:
            relative_path: Path relative to base_dir

        Returns:
            Absolute path to directory
        """
        if relative_path:
            dir_path = self._base_dir / relative_path
        else:
            dir_path = self._base_dir

        dir_path.mkdir(parents=True, exist_ok=True)

        logger.debug(
            "Directory ensured",
            extra={"path": str(dir_path)},
        )

        return dir_path

    def write_file(
        self,
        relative_path: str | Path,
        content: str,
        *,
        overwrite: bool = True,
    ) -> Path:
        """
        Write content to a file.

        Args:
            relative_path: Path relative to base_dir
            content: File content
            overwrite: Whether to overwrite existing files

        Returns:
            Absolute path to written file

        Raises:
            FileWriteError: If writing fails
        """
        file_path = self._base_dir / relative_path

        # Check if file exists and overwrite is disabled
        if file_path.exists() and not overwrite:
            logger.debug(
                "File exists, skipping",
                extra={"path": str(relative_path)},
            )
            return file_path

        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            file_path.write_text(content, encoding="utf-8")

            # Track created file
            rel_path_str = str(relative_path).replace("\\", "/")
            if rel_path_str not in self._files_created:
                self._files_created.append(rel_path_str)

            logger.debug(
                "File written",
                extra={"path": str(relative_path)},
            )

            return file_path

        except OSError as e:
            logger.error(
                "Failed to write file",
                extra={"path": str(relative_path), "error": str(e)},
            )
            raise FileWriteError(
                f"Failed to write file '{relative_path}'",
                file_path=str(file_path),
                original_error=str(e),
            ) from e

    def write_json(
        self,
        relative_path: str | Path,
        data: dict[str, Any],
        *,
        indent: int = 2,
    ) -> Path:
        """
        Write JSON data to a file.

        Args:
            relative_path: Path relative to base_dir
            data: JSON-serializable data
            indent: JSON indentation

        Returns:
            Absolute path to written file
        """
        content = json.dumps(data, indent=indent, ensure_ascii=False) + "\n"
        return self.write_file(relative_path, content)

    def merge_json(
        self,
        relative_path: str | Path,
        updates: dict[str, Any],
        *,
        indent: int = 2,
    ) -> Path:
        """
        Merge updates into an existing JSON file.

        Args:
            relative_path: Path relative to base_dir
            updates: Data to merge
            indent: JSON indentation

        Returns:
            Absolute path to updated file

        Raises:
            FileWriteError: If file doesn't exist or merge fails
        """
        file_path = self._base_dir / relative_path

        if not file_path.exists():
            # If file doesn't exist, just write the updates
            return self.write_json(relative_path, updates, indent=indent)

        try:
            # Read existing data
            existing_data = json.loads(file_path.read_text(encoding="utf-8"))

            # Deep merge
            merged_data = self._deep_merge(existing_data, updates)

            # Write back
            return self.write_json(relative_path, merged_data, indent=indent)

        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse JSON file",
                extra={"path": str(relative_path), "error": str(e)},
            )
            raise FileWriteError(
                f"Failed to parse JSON file '{relative_path}'",
                file_path=str(file_path),
                original_error=str(e),
            ) from e

    def _deep_merge(
        self,
        base: dict[str, Any],
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Deep merge two dictionaries.

        Args:
            base: Base dictionary
            updates: Updates to apply

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in updates.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def copy_file(
        self,
        source: Path,
        relative_dest: str | Path,
    ) -> Path:
        """
        Copy a file to the project.

        Args:
            source: Absolute source path
            relative_dest: Destination relative to base_dir

        Returns:
            Absolute path to copied file
        """
        content = source.read_text(encoding="utf-8")
        return self.write_file(relative_dest, content)

    def create_directories(self, directories: list[str]) -> None:
        """
        Create multiple directories.

        Args:
            directories: List of relative directory paths
        """
        for dir_path in directories:
            self.ensure_dir(dir_path)

        logger.debug(
            "Directories created",
            extra={"count": len(directories)},
        )

    def reset_tracking(self) -> None:
        """Reset the list of created files."""
        self._files_created.clear()
