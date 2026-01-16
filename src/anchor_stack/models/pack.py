"""
Pack model - Capability pack definition.

A Pack is a pluggable capability that can be added to any compatible Stack.
Each Pack provides:
- Unified interface (Facade pattern)
- Default logging and observability
- Secure-by-default configuration
- AI-readable documentation
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel, Field


class PackAdapter(BaseModel):
    """
    Stack-specific adapter for a Pack.

    Each Pack can be adapted to different Stacks.
    The adapter defines what files, dependencies, and
    configuration are needed for that specific Stack.
    """

    dependencies: Annotated[
        dict[str, str],
        Field(
            default_factory=dict,
            description="Dependencies to add for this Stack",
        ),
    ]

    dev_dependencies: Annotated[
        dict[str, str],
        Field(
            default_factory=dict,
            description="Dev dependencies to add for this Stack",
        ),
    ]

    files: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Files to generate for this Stack",
            examples=[["src/lib/db/index.ts", "src/lib/db/schema.ts"]],
        ),
    ]

    env_vars: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Environment variables required",
            examples=[["DATABASE_URL", "DATABASE_POOL_SIZE"]],
        ),
    ]

    templates_dir: Annotated[
        str,
        Field(
            default="templates",
            description="Relative path to templates for this adapter",
        ),
    ]

    setup_instructions: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Post-installation setup steps",
        ),
    ]


class Pack(BaseModel):
    """
    Capability pack definition.

    A Pack provides a specific capability (database, AI, auth, etc.)
    that can be plugged into compatible Stacks.

    Example pack.yaml:
        name: database-postgres
        version: "1.0.0"
        display_name: "PostgreSQL Database"
        compatible_stacks:
          - nextjs
          - python-api
        adapters:
          nextjs:
            dependencies:
              drizzle-orm: "0.38.0"
            files:
              - src/lib/db/index.ts
    """

    name: Annotated[
        str,
        Field(description="Pack identifier (e.g., 'database-postgres')"),
    ]

    version: Annotated[
        str,
        Field(description="Pack version"),
    ]

    display_name: Annotated[
        str,
        Field(description="Human-readable name"),
    ]

    description: Annotated[
        str,
        Field(default="", description="Pack description"),
    ]

    compatible_stacks: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="List of compatible Stack types",
            examples=[["nextjs", "python-api"]],
        ),
    ]

    adapters: Annotated[
        dict[str, PackAdapter],
        Field(
            default_factory=dict,
            description="Stack-specific adapters",
        ),
    ]

    # AI Rules content for this Pack
    rules_content: Annotated[
        str,
        Field(
            default="",
            description="AI Rules content to append to project rules",
        ),
    ]

    # Internal: path to pack definition file
    _source_path: Path | None = None

    def is_compatible_with(self, stack_type: str) -> bool:
        """Check if this Pack is compatible with a Stack type."""
        return stack_type.lower() in [s.lower() for s in self.compatible_stacks]

    def get_adapter(self, stack_type: str) -> PackAdapter | None:
        """Get the adapter for a specific Stack type."""
        stack_type_lower = stack_type.lower()
        for key, adapter in self.adapters.items():
            if key.lower() == stack_type_lower:
                return adapter
        return None

    def get_templates_path(self, stack_type: str) -> Path | None:
        """Get absolute path to templates for a specific Stack."""
        if self._source_path is None:
            return None
        adapter = self.get_adapter(stack_type)
        if adapter is None:
            return None
        return self._source_path.parent / stack_type / adapter.templates_dir

    def set_source_path(self, path: Path) -> None:
        """Set the source path for this Pack definition."""
        object.__setattr__(self, "_source_path", path)

    @classmethod
    def from_yaml(cls, data: dict[str, Any], source_path: Path | None = None) -> Pack:
        """
        Create Pack from parsed YAML data.

        Args:
            data: Parsed YAML dictionary
            source_path: Path to the YAML file

        Returns:
            Pack instance
        """
        # Convert adapter dicts to PackAdapter instances
        if "adapters" in data:
            adapters = {}
            for stack_type, adapter_data in data["adapters"].items():
                if isinstance(adapter_data, dict):
                    adapters[stack_type] = PackAdapter(**adapter_data)
                else:
                    adapters[stack_type] = adapter_data
            data["adapters"] = adapters

        pack = cls(**data)
        if source_path:
            pack.set_source_path(source_path)
        return pack
