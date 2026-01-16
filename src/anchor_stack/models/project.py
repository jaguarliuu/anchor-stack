"""
Project model - Generated project metadata.

These models represent the state of a generated project,
including configuration and manifest information.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    """
    Project configuration stored in anchor.config.json.

    This file is generated in every Anchor Stack project
    and tracks the project's Stack and Pack configuration.
    """

    # Anchor Stack metadata
    anchor_version: Annotated[
        str,
        Field(description="Anchor Stack version used to create project"),
    ]

    created_at: Annotated[
        datetime,
        Field(
            default_factory=lambda: datetime.now(timezone.utc),
            description="Project creation timestamp",
        ),
    ]

    # Stack info
    stack_type: Annotated[
        str,
        Field(description="Stack type (e.g., 'nextjs')"),
    ]

    stack_version: Annotated[
        str,
        Field(description="Stack version (e.g., '2025.1')"),
    ]

    # Project info
    app_name: Annotated[
        str,
        Field(description="Project name"),
    ]

    description: Annotated[
        str,
        Field(default="", description="Project description"),
    ]

    # Installed packs
    packs: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="List of installed Pack names",
        ),
    ]

    @property
    def stack_id(self) -> str:
        """Get full stack identifier."""
        return f"{self.stack_type}@{self.stack_version}"

    def add_pack(self, pack_name: str) -> None:
        """Add a pack to the installed list."""
        if pack_name not in self.packs:
            self.packs.append(pack_name)

    def has_pack(self, pack_name: str) -> bool:
        """Check if a pack is installed."""
        return pack_name in self.packs

    @classmethod
    def load(cls, project_dir: Path) -> ProjectConfig | None:
        """
        Load project config from a directory.

        Args:
            project_dir: Path to project root

        Returns:
            ProjectConfig or None if not found
        """
        import json

        config_path = project_dir / "anchor.config.json"
        if not config_path.exists():
            return None

        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)

        return cls(**data)

    def save(self, project_dir: Path) -> None:
        """
        Save project config to a directory.

        Args:
            project_dir: Path to project root
        """
        import json

        config_path = project_dir / "anchor.config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(
                self.model_dump(mode="json"),
                f,
                indent=2,
                ensure_ascii=False,
                default=str,
            )


class ProjectManifest(BaseModel):
    """
    Result of scaffold_project operation.

    Contains all information about the generated project.
    """

    success: Annotated[
        bool,
        Field(description="Whether the operation succeeded"),
    ]

    project_path: Annotated[
        str,
        Field(description="Absolute path to generated project"),
    ]

    app_name: Annotated[
        str,
        Field(description="Project name"),
    ]

    stack: Annotated[
        str,
        Field(description="Stack identifier (type@version)"),
    ]

    packs_installed: Annotated[
        list[str],
        Field(default_factory=list, description="List of installed Packs"),
    ]

    files_created: Annotated[
        list[str],
        Field(default_factory=list, description="List of created file paths"),
    ]

    rules_generated: Annotated[
        dict[str, str],
        Field(
            default_factory=dict,
            description="Map of tool name to rules file path",
        ),
    ]

    next_steps: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Suggested next steps for user",
        ),
    ]

    error: Annotated[
        str | None,
        Field(default=None, description="Error message if failed"),
    ]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump(exclude_none=True)


class DoctorResult(BaseModel):
    """
    Result of doctor health check.

    Contains issues and warnings found in the project.
    """

    success: Annotated[
        bool,
        Field(description="Whether the check completed successfully"),
    ]

    healthy: Annotated[
        bool,
        Field(description="Whether the project is healthy (no issues)"),
    ]

    issues: Annotated[
        list[dict[str, str]],
        Field(
            default_factory=list,
            description="List of issues that need attention",
        ),
    ]

    warnings: Annotated[
        list[dict[str, str]],
        Field(
            default_factory=list,
            description="List of warnings (non-critical)",
        ),
    ]

    summary: Annotated[
        str,
        Field(default="", description="Human-readable summary"),
    ]

    error: Annotated[
        str | None,
        Field(default=None, description="Error message if check failed"),
    ]
