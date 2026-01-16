"""
Utility functions for path manipulation.
"""

from __future__ import annotations

from pathlib import Path


def get_project_root() -> Path:
    """
    Get the root directory of the Anchor Stack package.

    Returns:
        Path to package root directory
    """
    return Path(__file__).parent.parent.parent.parent


def resolve_path(path: str | Path, base: Path | None = None) -> Path:
    """
    Resolve a path to absolute path.

    Args:
        path: Path to resolve (can be relative or absolute)
        base: Base directory for relative paths (defaults to cwd)

    Returns:
        Absolute Path object
    """
    path = Path(path)

    if path.is_absolute():
        return path.resolve()

    if base is None:
        base = Path.cwd()

    return (base / path).resolve()


def ensure_dir(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        The same path (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_inside(child: Path, parent: Path) -> bool:
    """
    Check if a path is inside another path.

    Args:
        child: Potential child path
        parent: Potential parent path

    Returns:
        True if child is inside parent
    """
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False
