"""
doctor tool - Check project health status.

This tool analyzes an Anchor Stack project and reports issues.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from anchor_stack.core.exceptions import AnchorStackError, ProjectValidationError
from anchor_stack.core.logger import get_logger
from anchor_stack.models.project import DoctorResult, ProjectConfig
from anchor_stack.services.stack_manager import StackManager

logger = get_logger(__name__)


async def doctor(project_dir: str) -> dict[str, Any]:
    """
    Check project health status.

    Analyzes the project for:
    - Configuration validity
    - Version drift from Stack definition
    - Missing or modified core files
    - Rules file integrity

    Args:
        project_dir: Path to project directory

    Returns:
        DoctorResult as dictionary

    Example:
        result = await doctor("/path/to/project")
        if not result["healthy"]:
            for issue in result["issues"]:
                print(issue["message"])
    """
    logger.info(
        "Starting doctor check",
        extra={"project_dir": project_dir},
    )

    issues: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    try:
        project_path = Path(project_dir).resolve()

        # Check 1: Is this an Anchor Stack project?
        project_config = ProjectConfig.load(project_path)
        if project_config is None:
            raise ProjectValidationError(
                "This is not an Anchor Stack project",
                field="project_dir",
                reason="anchor.config.json not found",
            )

        logger.debug(
            "Project config loaded",
            extra={"stack": project_config.stack_id},
        )

        # Check 2: Load Stack definition and compare
        try:
            stack_manager = StackManager()
            stack = stack_manager.load(
                project_config.stack_type,
                project_config.stack_version,
            )

            # Check version drift in package.json / pyproject.toml
            version_issues = _check_version_drift(project_path, stack, project_config)
            issues.extend(version_issues)

        except AnchorStackError as e:
            warnings.append(
                {
                    "type": "stack_load",
                    "message": f"Could not load Stack definition: {e}",
                }
            )

        # Check 3: Verify directory structure
        structure_warnings = _check_directory_structure(project_path, project_config)
        warnings.extend(structure_warnings)

        # Check 4: Check rules files
        rules_warnings = _check_rules_files(project_path)
        warnings.extend(rules_warnings)

        # Check 5: Check for common issues
        common_issues = _check_common_issues(project_path, project_config)
        issues.extend(common_issues)

        # Build summary
        is_healthy = len(issues) == 0
        summary = _build_summary(issues, warnings)

        result = DoctorResult(
            success=True,
            healthy=is_healthy,
            issues=issues,
            warnings=warnings,
            summary=summary,
        )

        logger.info(
            "Doctor check completed",
            extra={
                "healthy": is_healthy,
                "issues_count": len(issues),
                "warnings_count": len(warnings),
            },
        )

        return result.model_dump()

    except AnchorStackError as e:
        logger.error(
            "Doctor check failed",
            extra={"error": str(e)},
        )
        return DoctorResult(
            success=False,
            healthy=False,
            error=str(e),
        ).model_dump()

    except Exception as e:
        logger.error(
            "Doctor check unexpected error",
            extra={"error": str(e)},
        )
        return DoctorResult(
            success=False,
            healthy=False,
            error=f"Unexpected error: {e}",
        ).model_dump()


def _check_version_drift(
    project_path: Path,
    stack: Any,
    config: ProjectConfig,
) -> list[dict[str, str]]:
    """Check for dependency version drift from Stack definition."""
    issues = []

    if config.stack_type in ["nextjs", "vue"]:
        package_json_path = project_path / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, encoding="utf-8") as f:
                    package_data = json.load(f)

                current_deps = package_data.get("dependencies", {})
                expected_deps = stack.dependencies

                for dep_name, expected_version in expected_deps.items():
                    current_version = current_deps.get(dep_name)
                    if current_version and current_version != expected_version:
                        # Only report if it's a different major/minor version
                        if not _versions_compatible(expected_version, current_version):
                            issues.append(
                                {
                                    "type": "version_drift",
                                    "message": (
                                        f"Dependency '{dep_name}' version drift: "
                                        f"expected {expected_version}, found {current_version}"
                                    ),
                                }
                            )

            except (json.JSONDecodeError, OSError) as e:
                issues.append(
                    {
                        "type": "file_read_error",
                        "message": f"Could not read package.json: {e}",
                    }
                )

    return issues


def _versions_compatible(expected: str, actual: str) -> bool:
    """Check if two versions are compatible (same major.minor)."""
    try:
        # Remove common prefixes like ^, ~, >=
        expected_clean = expected.lstrip("^~>=<")
        actual_clean = actual.lstrip("^~>=<")

        expected_parts = expected_clean.split(".")
        actual_parts = actual_clean.split(".")

        # Compare major.minor
        if len(expected_parts) >= 2 and len(actual_parts) >= 2:
            return (
                expected_parts[0] == actual_parts[0]
                and expected_parts[1] == actual_parts[1]
            )

        return expected_clean == actual_clean

    except Exception:
        return False


def _check_directory_structure(
    project_path: Path,
    config: ProjectConfig,
) -> list[dict[str, str]]:
    """Check for non-standard directories."""
    warnings = []

    # Check for common non-standard directories
    non_standard_dirs = {
        "utils": "src/lib/",
        "helpers": "src/lib/",
        "common": "src/lib/",
    }

    src_path = project_path / "src"
    if src_path.exists():
        for item in src_path.iterdir():
            if item.is_dir() and item.name in non_standard_dirs:
                suggestion = non_standard_dirs[item.name]
                warnings.append(
                    {
                        "type": "structure",
                        "message": (
                            f"Found non-standard directory 'src/{item.name}/', "
                            f"consider using '{suggestion}' instead"
                        ),
                    }
                )

    return warnings


def _check_rules_files(project_path: Path) -> list[dict[str, str]]:
    """Check if AI Rules files exist."""
    warnings = []

    rules_files = {
        "CLAUDE.md": "Claude Code",
        ".cursor/rules/anchor-stack.mdc": "Cursor",
        ".windsurfrules": "Windsurf",
    }

    for file_path, tool_name in rules_files.items():
        full_path = project_path / file_path
        if not full_path.exists():
            warnings.append(
                {
                    "type": "rules_missing",
                    "message": f"Rules file for {tool_name} not found: {file_path}",
                }
            )

    return warnings


def _check_common_issues(
    project_path: Path,
    config: ProjectConfig,
) -> list[dict[str, str]]:
    """Check for common issues in the project."""
    issues = []

    # Check for .env file without .env.example
    env_path = project_path / ".env"
    env_example_path = project_path / ".env.example"

    if env_path.exists() and not env_example_path.exists():
        issues.append(
            {
                "type": "missing_example",
                "message": (
                    ".env file exists but .env.example is missing. "
                    "Create .env.example for documentation."
                ),
            }
        )

    # Check if anchor.config.json is in .gitignore (it shouldn't be)
    gitignore_path = project_path / ".gitignore"
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text(encoding="utf-8")
        if "anchor.config.json" in gitignore_content:
            issues.append(
                {
                    "type": "config_ignored",
                    "message": (
                        "anchor.config.json should NOT be in .gitignore. "
                        "It's needed for project tracking."
                    ),
                }
            )

    return issues


def _build_summary(
    issues: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> str:
    """Build human-readable summary."""
    if not issues and not warnings:
        return "Project is healthy. No issues found."

    parts = []
    if issues:
        parts.append(f"{len(issues)} issue(s) found")
    if warnings:
        parts.append(f"{len(warnings)} warning(s)")

    return ", ".join(parts) + ". Run with --verbose for details."
