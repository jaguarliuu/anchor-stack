"""
scaffold_project tool - Create a new project from Stack and Packs.

This is the main tool for creating new Anchor Stack projects.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from anchor_stack import __version__
from anchor_stack.core.exceptions import AnchorStackError
from anchor_stack.core.logger import get_logger
from anchor_stack.models.pack import Pack
from anchor_stack.models.project import ProjectConfig, ProjectManifest
from anchor_stack.models.stack import Stack
from anchor_stack.models.stack_spec import StackSpec
from anchor_stack.services.file_writer import FileWriter
from anchor_stack.services.pack_manager import PackManager
from anchor_stack.services.rules_generator import RulesGenerator
from anchor_stack.services.stack_manager import StackManager
from anchor_stack.services.template_renderer import TemplateRenderer

logger = get_logger(__name__)


async def scaffold_project(
    app_name: str,
    app_type: str,
    target_dir: str,
    stack_version: str = "2025.1",
    capabilities: list[str] | None = None,
    description: str | None = None,
    author: str | None = None,
) -> dict[str, Any]:
    """
    Create a new Anchor Stack project.

    Args:
        app_name: Project name (lowercase, alphanumeric, hyphens)
        app_type: Stack type (nextjs, python-api, etc.)
        target_dir: Target directory path
        stack_version: Stack version to use
        capabilities: List of Pack names to include
        description: Optional project description
        author: Optional author name

    Returns:
        ProjectManifest as dictionary

    Example:
        result = await scaffold_project(
            app_name="my-app",
            app_type="nextjs",
            target_dir="/path/to/project",
            capabilities=["database-postgres"]
        )
    """
    logger.info(
        "Starting scaffold_project",
        extra={
            "app_name": app_name,
            "app_type": app_type,
            "target_dir": target_dir,
            "stack_version": stack_version,
            "capabilities": capabilities,
        },
    )

    try:
        # Validate and create StackSpec
        spec = StackSpec(
            app_name=app_name,
            app_type=app_type,
            stack_version=stack_version,
            capabilities=capabilities or [],
            description=description,
            author=author,
        )

        # Initialize managers
        stack_manager = StackManager()
        pack_manager = PackManager()

        # Load Stack
        stack = stack_manager.load(spec.app_type, spec.stack_version)

        # Load and validate Packs
        packs: list[Pack] = []
        for pack_name in spec.capabilities:
            pack = pack_manager.load_for_stack(pack_name, spec.app_type)
            packs.append(pack)

        # Initialize FileWriter
        target_path = Path(target_dir).resolve()
        file_writer = FileWriter(target_path)

        # Create project directory
        file_writer.ensure_dir()

        # Create directory structure
        file_writer.create_directories(stack.directory_structure)

        # Render and write Stack templates
        _write_stack_templates(stack, spec, file_writer)

        # Write Pack files
        for pack in packs:
            _write_pack_templates(pack, stack, spec, file_writer)

        # Generate AI Rules
        rules_generator = RulesGenerator()
        rules_files = rules_generator.generate(stack, spec, packs, file_writer)

        # Create anchor.config.json
        project_config = ProjectConfig(
            anchor_version=__version__,
            stack_type=spec.app_type,
            stack_version=spec.stack_version,
            app_name=spec.app_name,
            description=spec.description or "",
            packs=[p.name for p in packs],
        )
        project_config.save(target_path)
        file_writer._files_created.append("anchor.config.json")

        # Build result
        manifest = ProjectManifest(
            success=True,
            project_path=str(target_path),
            app_name=spec.app_name,
            stack=stack.stack_id,
            packs_installed=[p.name for p in packs],
            files_created=file_writer.files_created,
            rules_generated=rules_files,
            next_steps=_get_next_steps(spec.app_type),
        )

        logger.info(
            "scaffold_project completed",
            extra={
                "project_path": str(target_path),
                "files_count": len(file_writer.files_created),
            },
        )

        return manifest.to_dict()

    except AnchorStackError as e:
        logger.error(
            "scaffold_project failed",
            extra={"error": str(e), "code": e.code},
        )
        return ProjectManifest(
            success=False,
            project_path=str(target_dir),
            app_name=app_name,
            stack=f"{app_type}@{stack_version}",
            error=str(e),
        ).to_dict()

    except Exception as e:
        logger.error(
            "scaffold_project unexpected error",
            extra={"error": str(e)},
        )
        return ProjectManifest(
            success=False,
            project_path=str(target_dir),
            app_name=app_name,
            stack=f"{app_type}@{stack_version}",
            error=f"Unexpected error: {e}",
        ).to_dict()


def _write_stack_templates(
    stack: Stack,
    spec: StackSpec,
    file_writer: FileWriter,
) -> None:
    """Write Stack template files to project."""
    templates_path = stack.get_templates_path()
    if templates_path is None or not templates_path.exists():
        logger.warning(
            "Stack templates directory not found",
            extra={"stack": stack.name},
        )
        return

    # Build template context
    context = {
        "app_name": spec.app_name,
        "app_description": spec.description or f"A {stack.display_name} project",
        "author": spec.author or "",
        "stack_name": stack.name,
        "stack_version": stack.version,
        "dependencies": stack.get_all_dependencies(),
        "dev_dependencies": stack.get_all_dev_dependencies(),
        "runtime": stack.runtime,
    }

    renderer = TemplateRenderer(templates_path)

    # Walk through template files
    for template_file in templates_path.rglob("*"):
        if template_file.is_dir():
            continue

        # Get relative path within templates
        rel_path = template_file.relative_to(templates_path)
        rel_path_str = str(rel_path).replace("\\", "/")

        # Determine output path (remove .j2 extension if present)
        if rel_path_str.endswith(".j2"):
            output_path = rel_path_str[:-3]
            # Render template
            content = renderer.render(rel_path_str, context)
        else:
            output_path = rel_path_str
            # Copy as-is
            content = template_file.read_text(encoding="utf-8")

        file_writer.write_file(output_path, content)


def _write_pack_templates(
    pack: Pack,
    stack: Stack,
    spec: StackSpec,
    file_writer: FileWriter,
) -> None:
    """Write Pack template files to project."""
    adapter = pack.get_adapter(stack.name)
    if adapter is None:
        logger.warning(
            "Pack adapter not found",
            extra={"pack": pack.name, "stack": stack.name},
        )
        return

    templates_path = pack.get_templates_path(stack.name)
    if templates_path is None or not templates_path.exists():
        logger.warning(
            "Pack templates directory not found",
            extra={"pack": pack.name, "stack": stack.name},
        )
        return

    # Build template context
    context = {
        "app_name": spec.app_name,
        "pack_name": pack.name,
        "env_vars": adapter.env_vars,
    }

    renderer = TemplateRenderer(templates_path)

    # Walk through template files
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


def _get_next_steps(app_type: str) -> list[str]:
    """Get next steps for a given app type."""
    steps_map = {
        "nextjs": [
            "cd <project_dir>",
            "npm install",
            "cp .env.example .env.local",
            "npm run dev",
        ],
        "python-api": [
            "cd <project_dir>",
            "python -m venv .venv",
            "source .venv/bin/activate  # Windows: .venv\\Scripts\\activate",
            "pip install -e .",
            "cp .env.example .env",
            "python -m src.main",
        ],
        "vue": [
            "cd <project_dir>",
            "npm install",
            "cp .env.example .env.local",
            "npm run dev",
        ],
    }

    return steps_map.get(app_type, ["cd <project_dir>", "Follow README.md for setup"])
