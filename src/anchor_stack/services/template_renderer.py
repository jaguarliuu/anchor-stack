"""
Template Renderer - Render Jinja2 templates.

Responsible for:
- Loading template files
- Rendering templates with context
- Handling template errors gracefully
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateError, select_autoescape

from anchor_stack.core.exceptions import TemplateRenderError
from anchor_stack.core.logger import get_logger

logger = get_logger(__name__)


class TemplateRenderer:
    """
    Renders Jinja2 templates with provided context.

    Supports:
    - File-based templates
    - String templates
    - Custom filters and globals

    Example:
        renderer = TemplateRenderer(templates_dir)
        content = renderer.render("package.json.j2", {"app_name": "my-app"})
    """

    def __init__(self, templates_dir: Path | None = None) -> None:
        """
        Initialize TemplateRenderer.

        Args:
            templates_dir: Base directory for template files
        """
        self._templates_dir = templates_dir

        # Create Jinja2 environment
        loaders = []
        if templates_dir and templates_dir.exists():
            loaders.append(FileSystemLoader(str(templates_dir)))

        self._env = Environment(
            loader=FileSystemLoader(str(templates_dir)) if templates_dir else None,
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        # Register custom filters
        self._register_filters()

        logger.debug(
            "TemplateRenderer initialized",
            extra={"templates_dir": str(templates_dir) if templates_dir else None},
        )

    def _register_filters(self) -> None:
        """Register custom Jinja2 filters."""
        # Convert to snake_case
        self._env.filters["snake_case"] = self._to_snake_case
        # Convert to PascalCase
        self._env.filters["pascal_case"] = self._to_pascal_case
        # Convert to kebab-case
        self._env.filters["kebab_case"] = self._to_kebab_case
        # JSON dumps
        self._env.filters["to_json"] = self._to_json

    @staticmethod
    def _to_snake_case(value: str) -> str:
        """Convert string to snake_case."""
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", value)
        s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
        return s2.lower().replace("-", "_")

    @staticmethod
    def _to_pascal_case(value: str) -> str:
        """Convert string to PascalCase."""
        return "".join(word.capitalize() for word in value.replace("-", "_").split("_"))

    @staticmethod
    def _to_kebab_case(value: str) -> str:
        """Convert string to kebab-case."""
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", value)
        s2 = re.sub("([a-z0-9])([A-Z])", r"\1-\2", s1)
        return s2.lower().replace("_", "-")

    @staticmethod
    def _to_json(value: Any, indent: int = 2) -> str:
        """Convert value to JSON string."""
        import json

        return json.dumps(value, indent=indent, ensure_ascii=False)

    def render(self, template_name: str, context: dict[str, Any]) -> str:
        """
        Render a template file with context.

        Args:
            template_name: Template filename (e.g., "package.json.j2")
            context: Variables to pass to template

        Returns:
            Rendered template content

        Raises:
            TemplateRenderError: If rendering fails
        """
        try:
            template = self._env.get_template(template_name)
            content = template.render(**context)

            logger.debug(
                "Template rendered",
                extra={"template": template_name},
            )

            return content

        except TemplateError as e:
            logger.error(
                "Template render failed",
                extra={"template": template_name, "error": str(e)},
            )
            raise TemplateRenderError(
                f"Failed to render template '{template_name}'",
                template_name=template_name,
                original_error=str(e),
            ) from e

    def render_string(self, template_string: str, context: dict[str, Any]) -> str:
        """
        Render a template from string.

        Args:
            template_string: Template content as string
            context: Variables to pass to template

        Returns:
            Rendered content

        Raises:
            TemplateRenderError: If rendering fails
        """
        try:
            template = self._env.from_string(template_string)
            return template.render(**context)

        except TemplateError as e:
            logger.error(
                "String template render failed",
                extra={"error": str(e)},
            )
            raise TemplateRenderError(
                "Failed to render string template",
                original_error=str(e),
            ) from e

    def render_file(self, template_path: Path, context: dict[str, Any]) -> str:
        """
        Render a template from absolute file path.

        Args:
            template_path: Absolute path to template file
            context: Variables to pass to template

        Returns:
            Rendered content

        Raises:
            TemplateRenderError: If rendering fails
        """
        if not template_path.exists():
            raise TemplateRenderError(
                f"Template file not found: {template_path}",
                template_name=str(template_path),
            )

        try:
            template_content = template_path.read_text(encoding="utf-8")
            return self.render_string(template_content, context)

        except TemplateRenderError:
            raise
        except Exception as e:
            logger.error(
                "File template render failed",
                extra={"template_path": str(template_path), "error": str(e)},
            )
            raise TemplateRenderError(
                f"Failed to render template file '{template_path}'",
                template_name=str(template_path),
                original_error=str(e),
            ) from e

    def set_templates_dir(self, templates_dir: Path) -> None:
        """
        Update the templates directory.

        Args:
            templates_dir: New templates directory
        """
        self._templates_dir = templates_dir
        self._env.loader = FileSystemLoader(str(templates_dir))

        logger.debug(
            "Templates directory updated",
            extra={"templates_dir": str(templates_dir)},
        )
