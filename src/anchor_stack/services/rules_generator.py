"""
Rules Generator - Generate AI Rules files for different tools.

Responsible for:
- Generating rules files for Cursor, Claude Code, Windsurf, etc.
- Merging Stack and Pack rules
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


# Rules file paths for different AI tools
RULES_PATHS = {
    "cursor": ".cursor/rules/anchor-stack.mdc",
    "claude": "CLAUDE.md",
    "windsurf": ".windsurfrules",
    "copilot": ".github/copilot-instructions.md",
    "common": "docs/PROJECT_RULES.md",
}


class RulesGenerator:
    """
    Generates AI Rules files for a project.

    Creates rules files for multiple AI coding tools,
    ensuring consistent project documentation across all tools.

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

        # Generate rules content
        rules_content = self._generate_rules_content(context)

        # Write rules files
        rules_files = {}
        for tool_name, file_path in RULES_PATHS.items():
            # Customize content for each tool
            tool_content = self._customize_for_tool(rules_content, tool_name)

            # Write file
            file_writer.write_file(file_path, tool_content)
            rules_files[tool_name] = file_path

            logger.debug(
                "Rules file generated",
                extra={"tool": tool_name, "path": file_path},
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
        for tool_name, file_path in RULES_PATHS.items():
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
            "packs": [p.name for p in packs],
            "packs_display": [p.display_name for p in packs],
            "directory_structure": stack.directory_structure,
            "has_logging": stack.builtin_features.logging,
            "has_config": stack.builtin_features.config_management,
        }

    def _generate_rules_content(self, context: dict[str, Any]) -> str:
        """Generate the main rules content."""
        app_name = context["app_name"]
        stack_id = context["stack_id"]
        packs = context["packs"]
        directory_structure = context["directory_structure"]

        # Build modifiable and protected directories
        modifiable_dirs = []
        protected_dirs = []
        for dir_path in directory_structure:
            if "lib/core" in dir_path or "lib/db" in dir_path:
                protected_dirs.append(dir_path)
            else:
                modifiable_dirs.append(dir_path)

        content = f"""# Project Rules - {app_name}

## Project Overview
- **Project Name**: {app_name}
- **Stack**: {stack_id}
- **Installed Packs**: {', '.join(packs) if packs else 'None'}

## Directory Structure

### Modifiable Directories
These directories can be freely modified:
{self._format_dir_list(modifiable_dirs)}

### Protected Directories
These directories contain framework code. Do not modify directly:
{self._format_dir_list(protected_dirs) if protected_dirs else '- None'}

## Logging Standards

### How to Add Logs
Use the built-in logger, NOT console.log or print():

```typescript
// TypeScript/JavaScript
import {{ logger }} from '@/lib/logger';

// Correct usage
logger.info('User logged in', {{ userId: user.id }});
logger.error('Payment failed', {{ orderId, error: error.message }});
logger.debug('Cache hit', {{ key, ttl }});

// INCORRECT - Do not use
console.log('User logged in');  // ❌
```

```python
# Python
from app.core.logger import get_logger

logger = get_logger(__name__)

# Correct usage
logger.info("User logged in", extra={{"user_id": user.id}})
logger.error("Payment failed", extra={{"order_id": order_id, "error": str(e)}})

# INCORRECT - Do not use
print("User logged in")  # ❌
```

### Log Levels
- `DEBUG`: Development debugging info
- `INFO`: Normal business operations
- `WARNING`: Unexpected but non-critical issues
- `ERROR`: Errors requiring attention

### Where to Add Logs
1. **API endpoints**: Log request start and completion
2. **Database operations**: Log queries and errors
3. **External service calls**: Log requests and responses
4. **Authentication**: Log login/logout events
5. **Critical business logic**: Log state changes

## Adding New Features

### Adding a New Page/Route
1. Create file in the appropriate route directory
2. Follow existing naming conventions
3. Use shared components from `src/components/`
4. Add appropriate logging

### Adding a New API Endpoint
1. Create route handler in the API directory
2. Use the standard API handler wrapper
3. Add request/response logging
4. Handle errors with standard error types

### Adding a New Component
1. Create in `src/components/`
2. Use TypeScript types
3. Follow existing component patterns

## Debug Guide

When encountering issues, provide:
1. **Full error logs** (from logger output, not console)
2. **Request parameters** that triggered the error
3. **Environment** (development/production)
4. **Recent code changes** related to the error

## Prohibited Actions
- ❌ Do NOT delete or modify `anchor.config.json`
- ❌ Do NOT modify files in `src/lib/core/`
- ❌ Do NOT use console.log/print instead of logger
- ❌ Do NOT write database queries directly in components
- ❌ Do NOT hardcode configuration values
- ❌ Do NOT skip error handling in API endpoints

## Configuration Management

All configuration should go through the config system:
- Environment variables in `.env` / `.env.local`
- Do NOT hardcode secrets or URLs
- Use typed config objects

"""
        return content

    def _format_dir_list(self, directories: list[str]) -> str:
        """Format a list of directories as markdown."""
        if not directories:
            return "- (none)"
        return "\n".join(f"- `{d}`" for d in directories)

    def _customize_for_tool(self, content: str, tool_name: str) -> str:
        """Customize rules content for a specific tool."""
        if tool_name == "cursor":
            # Cursor uses MDC format
            header = """---
description: Project rules and conventions for AI assistance
globs: ["**/*"]
---

"""
            return header + content

        elif tool_name == "claude":
            # Claude Code format
            header = """# CLAUDE.md - Project Instructions

This file contains instructions for Claude Code when working on this project.

"""
            return header + content

        elif tool_name == "windsurf":
            # Windsurf format (similar to standard markdown)
            return content

        elif tool_name == "copilot":
            # GitHub Copilot format
            header = """# GitHub Copilot Instructions

These instructions guide GitHub Copilot when generating code for this project.

"""
            return header + content

        else:
            # Common/default format
            return content

    def _format_pack_rules(self, pack: Pack, tool_name: str) -> str:
        """Format Pack-specific rules section."""
        return f"""
---

## {pack.display_name} ({pack.name})

{pack.rules_content}
"""
