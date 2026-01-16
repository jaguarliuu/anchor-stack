"""
add_pack tool - Add a capability pack to an existing project.

This tool allows adding new capabilities to existing Anchor Stack projects.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from anchor_stack.core.exceptions import AnchorStackError, ProjectValidationError
from anchor_stack.core.logger import get_logger
from anchor_stack.models.project import ProjectConfig
from anchor_stack.services.file_writer import FileWriter
from anchor_stack.services.pack_manager import PackManager
from anchor_stack.services.rules_generator import RulesGenerator
from anchor_stack.services.template_renderer import TemplateRenderer

logger = get_logger(__name__)


async def add_pack(
    project_dir: str,
    pack_name: str,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Add a capability pack to an existing project.

    Args:
        project_dir: Path to existing project
        pack_name: Name of Pack to add
        options: Optional Pack configuration

    Returns:
        Result dictionary with added files and next steps

    Example:
        result = await add_pack(
            project_dir="/path/to/project",
            pack_name="database-postgres"
        )
    """
    logger.info(
        "Starting add_pack",
        extra={"project_dir": project_dir, "pack_name": pack_name},
    )

    try:
        project_path = Path(project_dir).resolve()

        # Load project config
        project_config = ProjectConfig.load(project_path)
        if project_config is None:
            raise ProjectValidationError(
                f"Not an Anchor Stack project: {project_dir}",
                field="project_dir",
                reason="anchor.config.json not found",
            )

        # Check if pack already installed
        if project_config.has_pack(pack_name):
            logger.warning(
                "Pack already installed",
                extra={"pack_name": pack_name},
            )
            return {
                "success": True,
                "pack": pack_name,
                "message": f"Pack '{pack_name}' is already installed",
                "files_created": [],
                "next_steps": [],
            }

        # Load Pack
        pack_manager = PackManager()
        pack = pack_manager.load_for_stack(pack_name, project_config.stack_type)

        # Get adapter for this stack
        adapter = pack.get_adapter(project_config.stack_type)
        if adapter is None:
            raise ProjectValidationError(
                f"Pack '{pack_name}' has no adapter for '{project_config.stack_type}'",
                field="pack_name",
                reason="No adapter available",
            )

        # Initialize FileWriter
        file_writer = FileWriter(project_path)

        # Write Pack templates
        templates_path = pack.get_templates_path(project_config.stack_type)
        if templates_path and templates_path.exists():
            context = {
                "app_name": project_config.app_name,
                "pack_name": pack.name,
                "env_vars": adapter.env_vars,
                **(options or {}),
            }

            renderer = TemplateRenderer(templates_path)

            for template_file in templates_path.rglob("*"):
                if template_file.is_dir():
                    continue

                rel_path = template_file.relative_to(templates_path)
                rel_path_str = str(rel_path).replace("\\", "/")

                if rel_path_str.endswith(".j2"):
                    output_path = rel_path_str[:-3]
                    content = renderer.render(rel_path_str, context)
                else:
                    output_path = rel_path_str
                    content = template_file.read_text(encoding="utf-8")

                file_writer.write_file(output_path, content)

        # Update package.json or requirements.txt with dependencies
        deps_updated = _update_dependencies(
            project_path,
            project_config.stack_type,
            adapter.dependencies,
            adapter.dev_dependencies,
            file_writer,
        )

        # Append Pack rules
        rules_generator = RulesGenerator()
        rules_generator.append_pack_rules(pack, project_config.stack_type, file_writer)

        # Update project config
        project_config.add_pack(pack_name)
        project_config.save(project_path)

        # Build result
        result = {
            "success": True,
            "pack": pack_name,
            "files_created": file_writer.files_created,
            "dependencies_added": adapter.dependencies,
            "dev_dependencies_added": adapter.dev_dependencies,
            "env_vars_required": adapter.env_vars,
            "rules_updated": True,
            "next_steps": adapter.setup_instructions or _get_default_next_steps(pack_name),
        }

        logger.info(
            "add_pack completed",
            extra={"pack": pack_name, "files_count": len(file_writer.files_created)},
        )

        return result

    except AnchorStackError as e:
        logger.error(
            "add_pack failed",
            extra={"error": str(e), "code": e.code},
        )
        return {
            "success": False,
            "pack": pack_name,
            "error": str(e),
        }

    except Exception as e:
        logger.error(
            "add_pack unexpected error",
            extra={"error": str(e)},
        )
        return {
            "success": False,
            "pack": pack_name,
            "error": f"Unexpected error: {e}",
        }


def _update_dependencies(
    project_path: Path,
    stack_type: str,
    dependencies: dict[str, str],
    dev_dependencies: dict[str, str],
    file_writer: FileWriter,
) -> dict[str, str]:
    """Update project dependencies based on stack type."""
    if stack_type in ["nextjs", "vue"]:
        # Update package.json
        package_json_path = project_path / "package.json"
        if package_json_path.exists():
            updates: dict[str, Any] = {}
            if dependencies:
                updates["dependencies"] = dependencies
            if dev_dependencies:
                updates["devDependencies"] = dev_dependencies

            if updates:
                file_writer.merge_json("package.json", updates)

    elif stack_type == "python-api":
        # Update pyproject.toml or requirements.txt
        # For simplicity, append to requirements.txt
        requirements_path = project_path / "requirements.txt"
        if requirements_path.exists():
            existing = requirements_path.read_text(encoding="utf-8")
            new_deps = []
            for name, version in dependencies.items():
                dep_line = f"{name}>={version}"
                if dep_line not in existing:
                    new_deps.append(dep_line)

            if new_deps:
                new_content = existing.rstrip() + "\n" + "\n".join(new_deps) + "\n"
                file_writer.write_file("requirements.txt", new_content)

    return dependencies


def _get_default_next_steps(pack_name: str) -> list[str]:
    """Get default next steps for a pack."""
    steps_map = {
        "database-postgres": [
            "Run package installer (npm install / pip install)",
            "Set DATABASE_URL in your .env file",
            "Run database migrations if applicable",
        ],
        "ai-langgraph": [
            "Run package installer (npm install / pip install)",
            "Set OPENAI_API_KEY or other LLM API keys in .env",
            "Review AI agent configuration in src/lib/ai/",
        ],
    }

    return steps_map.get(pack_name, ["Run package installer to install new dependencies"])
