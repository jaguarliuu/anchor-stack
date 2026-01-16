"""
Rules Generator - Generate AI Rules files for different tools.

Responsible for:
- Generating rules files for Cursor, Claude Code, Windsurf, etc.
- Using Stack-specific rules templates
- Creating standardized project documentation
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from anchor_stack.core.logger import get_logger
from anchor_stack.models.pack import Pack
from anchor_stack.models.stack import Stack
from anchor_stack.models.stack_spec import StackSpec
from anchor_stack.services.file_writer import FileWriter
from anchor_stack.services.template_renderer import TemplateRenderer

logger = get_logger(__name__)


# Rules file output paths and their corresponding template names
RULES_CONFIG = {
    "cursor": {
        "output_path": ".cursor/rules/anchor-stack.mdc",
        "template_name": "cursor.mdc.j2",
    },
    "claude": {
        "output_path": "CLAUDE.md",
        "template_name": "claude.md.j2",
    },
    "windsurf": {
        "output_path": ".windsurfrules",
        "template_name": "windsurf.md.j2",
    },
}


class RulesGenerator:
    """
    Generates AI Rules files for a project.

    Creates rules files for multiple AI coding tools,
    using Stack-specific templates for proper content.

    Example:
        generator = RulesGenerator()
        files = generator.generate(stack, spec, packs, file_writer)
    """

    def __init__(self) -> None:
        """Initialize RulesGenerator."""
        self._renderer = TemplateRenderer()
        logger.debug("RulesGenerator initialized")

    def generate(
        self,
        stack: Stack,
        spec: StackSpec,
        packs: list[Pack],
        file_writer: FileWriter,
    ) -> dict[str, str]:
        """
        Generate all AI Rules files for a project.

        Args:
            stack: Stack being used
            spec: Project specification
            packs: List of installed Packs
            file_writer: FileWriter instance for output

        Returns:
            Dict mapping tool name to rules file path
        """
        # Build context for templates
        context = self._build_context(stack, spec, packs)

        # Get rules directory from stack
        rules_dir = stack.get_rules_path()

        rules_files = {}

        for tool_name, config in RULES_CONFIG.items():
            output_path = config["output_path"]
            template_path = None

            if rules_dir:
                template_path = rules_dir / config["template_name"]

            if template_path and template_path.exists():
                # Use stack-specific template
                content = self._renderer.render_file(template_path, context)
                logger.debug(
                    "Using stack rules template",
                    extra={"tool": tool_name, "template": str(template_path)},
                )
            else:
                # Fallback to generic content
                logger.warning(
                    "Rules template not found, using fallback",
                    extra={"tool": tool_name, "template": str(template_path)},
                )
                content = self._generate_fallback_content(context, tool_name)

            # Write file
            file_writer.write_file(output_path, content)
            rules_files[tool_name] = output_path

            logger.debug(
                "Rules file generated",
                extra={"tool": tool_name, "path": output_path},
            )

        logger.info(
            "AI Rules generated",
            extra={"tools": list(rules_files.keys())},
        )

        return rules_files

    def append_pack_rules(
        self,
        pack: Pack,
        stack_type: str,
        file_writer: FileWriter,
    ) -> bool:
        """
        Append Pack-specific rules to existing rules files.

        Args:
            pack: Pack being added
            stack_type: Stack type for the project
            file_writer: FileWriter instance

        Returns:
            True if rules were updated
        """
        if not pack.rules_content:
            logger.debug(
                "Pack has no rules content",
                extra={"pack": pack.name},
            )
            return False

        # Append to each rules file
        for tool_name, config in RULES_CONFIG.items():
            file_path = config["output_path"]
            full_path = file_writer.base_dir / file_path
            if full_path.exists():
                existing_content = full_path.read_text(encoding="utf-8")
                pack_section = self._format_pack_rules(pack, tool_name)
                new_content = existing_content + "\n" + pack_section
                file_writer.write_file(file_path, new_content)

        logger.info(
            "Pack rules appended",
            extra={"pack": pack.name},
        )

        return True

    def _build_context(
        self,
        stack: Stack,
        spec: StackSpec,
        packs: list[Pack],
    ) -> dict[str, Any]:
        """Build template context from Stack, Spec, and Packs."""
        return {
            "app_name": spec.app_name,
            "app_description": spec.description or f"A {stack.display_name} project",
            "stack_name": stack.name,
            "stack_version": stack.version,
            "stack_display_name": stack.display_name,
            "stack_id": stack.stack_id,
            "dependencies": stack.dependencies,
            "dev_dependencies": stack.dev_dependencies,
            "packs": [p.name for p in packs],
            "packs_display": [p.display_name for p in packs],
            "directory_structure": stack.directory_structure,
            "has_logging": stack.builtin_features.logging,
            "has_config": stack.builtin_features.config_management,
        }

    def _generate_fallback_content(
        self, context: dict[str, Any], tool_name: str
    ) -> str:
        """Generate fallback rules content when no template exists."""
        app_name = context["app_name"]
        stack_id = context["stack_id"]

        content = f"""# {app_name} - Project Rules

## Overview
- **Project**: {app_name}
- **Stack**: {stack_id}

## Conventions

### Logging
Use the built-in logger module instead of print/console.log.

### Configuration
Use the config module for all configuration values.

### Protected Files
Do not modify files in the `core/` directory.

## Generated by Anchor Stack
"""

        if tool_name == "cursor":
            header = """---
description: Project rules for AI assistance
globs: ["**/*"]
---

"""
            return header + content

        return content

    def _format_pack_rules(self, pack: Pack, tool_name: str) -> str:
        """Format Pack-specific rules section."""
        return f"""
---

## {pack.display_name} ({pack.name})

{pack.rules_content}
"""
