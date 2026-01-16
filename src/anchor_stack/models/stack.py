"""
Stack model - Technology stack definition.

A Stack represents a curated, versioned combination of:
- Runtime version (Node.js, Python, etc.)
- Framework versions
- Directory structure conventions
- Built-in logging and configuration
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel, Field


class StackDependencies(BaseModel):
    """Dependencies configuration for a Stack."""

    runtime: Annotated[
        dict[str, str],
        Field(
            default_factory=dict,
            description="Runtime requirements (e.g., node: '20.x')",
        ),
    ]

    dependencies: Annotated[
        dict[str, str],
        Field(
            default_factory=dict,
            description="Production dependencies with versions",
        ),
    ]

    dev_dependencies: Annotated[
        dict[str, str],
        Field(
            default_factory=dict,
            description="Development dependencies with versions",
        ),
    ]


class StackBuiltinFeatures(BaseModel):
    """Built-in features provided by the Stack."""

    logging: Annotated[
        bool,
        Field(default=True, description="Include standardized logging"),
    ]

    config_management: Annotated[
        bool,
        Field(default=True, description="Include configuration management"),
    ]

    error_boundary: Annotated[
        bool,
        Field(default=False, description="Include error boundary (frontend)"),
    ]


class Stack(BaseModel):
    """
    Technology stack definition.

    A Stack is a versioned, curated combination of technologies
    that work well together. It provides:
    - Stable dependency versions
    - Standard directory structure
    - Built-in logging and config

    Example stack.yaml:
        name: nextjs
        version: "2025.1"
        display_name: "Next.js Full-Stack"
        dependencies:
          next: "15.1.0"
          react: "19.0.0"
    """

    name: Annotated[
        str,
        Field(description="Stack identifier (e.g., 'nextjs', 'python-api')"),
    ]

    version: Annotated[
        str,
        Field(description="Stack version (e.g., '2025.1')"),
    ]

    display_name: Annotated[
        str,
        Field(description="Human-readable name"),
    ]

    description: Annotated[
        str,
        Field(default="", description="Stack description"),
    ]

    # Dependencies
    runtime: Annotated[
        dict[str, str],
        Field(
            default_factory=dict,
            description="Runtime version requirements",
            examples=[{"node": "20.x", "npm": "10.x"}],
        ),
    ]

    dependencies: Annotated[
        dict[str, str],
        Field(
            default_factory=dict,
            description="Production dependencies",
        ),
    ]

    dev_dependencies: Annotated[
        dict[str, str],
        Field(
            default_factory=dict,
            description="Development dependencies",
        ),
    ]

    # Structure
    directory_structure: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="List of directories to create",
            examples=[["src/", "src/app/", "src/components/", "src/lib/"]],
        ),
    ]

    # Features
    builtin_features: Annotated[
        StackBuiltinFeatures,
        Field(
            default_factory=StackBuiltinFeatures,
            description="Built-in features configuration",
        ),
    ]

    # Metadata
    templates_dir: Annotated[
        str,
        Field(
            default="templates",
            description="Relative path to templates directory",
        ),
    ]

    rules_dir: Annotated[
        str,
        Field(
            default="rules",
            description="Relative path to rules templates directory",
        ),
    ]

    # Internal: path to stack definition file
    _source_path: Path | None = None

    @property
    def stack_id(self) -> str:
        """Get full stack identifier."""
        return f"{self.name}@{self.version}"

    def get_templates_path(self) -> Path | None:
        """Get absolute path to templates directory."""
        if self._source_path is None:
            return None
        return self._source_path.parent / self.templates_dir

    def get_rules_path(self) -> Path | None:
        """Get absolute path to rules directory."""
        if self._source_path is None:
            return None
        return self._source_path.parent / self.rules_dir

    def set_source_path(self, path: Path) -> None:
        """Set the source path for this Stack definition."""
        object.__setattr__(self, "_source_path", path)

    def get_all_dependencies(self) -> dict[str, str]:
        """Get merged dependencies dict."""
        return {**self.dependencies}

    def get_all_dev_dependencies(self) -> dict[str, str]:
        """Get merged dev dependencies dict."""
        return {**self.dev_dependencies}

    @classmethod
    def from_yaml(cls, data: dict[str, Any], source_path: Path | None = None) -> Stack:
        """
        Create Stack from parsed YAML data.

        Args:
            data: Parsed YAML dictionary
            source_path: Path to the YAML file

        Returns:
            Stack instance
        """
        # Handle nested builtin_features
        if "builtin_features" in data and isinstance(data["builtin_features"], dict):
            data["builtin_features"] = StackBuiltinFeatures(**data["builtin_features"])

        stack = cls(**data)
        if source_path:
            stack.set_source_path(source_path)
        return stack
