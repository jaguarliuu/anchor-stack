"""
MCP Server entry point.

This module creates and configures the MCP Server using FastMCP.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from anchor_stack import __version__
from anchor_stack.core.config import get_settings
from anchor_stack.core.logger import get_logger, setup_logging
from anchor_stack.tools.doctor import doctor
from anchor_stack.tools.pack import add_pack
from anchor_stack.tools.scaffold import scaffold_project

# Initialize logging
settings = get_settings()
setup_logging(level=settings.log_level, json_output=settings.log_json)

logger = get_logger(__name__)

# Create MCP Server
mcp = FastMCP(settings.server_name)


@mcp.tool()
async def scaffold_project_tool(
    app_name: str,
    stack_name: str,
    target_dir: str,
    stack_version: str = "2026.1",
    capabilities: list[str] | None = None,
    description: str | None = None,
) -> dict:
    """
    Create a new Anchor Stack project.

    Creates a complete project structure with:
    - Standardized directory layout
    - Curated dependency versions
    - Built-in logging framework
    - AI Rules for multiple tools (Cursor, Claude Code, etc.)

    Args:
        app_name: Project name (lowercase, alphanumeric, hyphens allowed)
        stack_name: Technology stack to use. MUST be one of:
                   - "nextjs" - Next.js 16 + React 19 + TypeScript + Tailwind
                   - "fastapi" - FastAPI + SQLAlchemy + Pydantic
        target_dir: Absolute path where project will be created
        stack_version: Stack version (default: "2026.1")
        capabilities: Optional list of capability packs to include.
                     Available: "database-postgres", "ai-langgraph"
        description: Optional project description

    Returns:
        Dictionary containing:
        - success: Whether creation succeeded
        - project_path: Path to created project
        - files_created: List of created files
        - rules_generated: Map of AI tool to rules file path
        - next_steps: Suggested commands to run

    Example:
        scaffold_project_tool(
            app_name="my-saas-app",
            stack_name="nextjs",
            target_dir="/home/user/projects/my-saas-app",
            capabilities=["database-postgres"]
        )
    """
    logger.info(
        "MCP tool called: scaffold_project",
        extra={"app_name": app_name, "stack_name": stack_name},
    )

    return await scaffold_project(
        app_name=app_name,
        app_type=stack_name,
        target_dir=target_dir,
        stack_version=stack_version,
        capabilities=capabilities,
        description=description,
    )


@mcp.tool()
async def add_pack_tool(
    project_dir: str,
    pack_name: str,
) -> dict:
    """
    Add a capability pack to an existing Anchor Stack project.

    Capability packs provide pre-configured, production-ready
    integrations for common functionality.

    Args:
        project_dir: Absolute path to existing Anchor Stack project
        pack_name: Name of pack to add.
                   Available: "database-postgres", "ai-langgraph"

    Returns:
        Dictionary containing:
        - success: Whether addition succeeded
        - pack: Name of added pack
        - files_created: List of new files
        - dependencies_added: New dependencies to install
        - next_steps: Setup instructions

    Example:
        add_pack_tool(
            project_dir="/home/user/projects/my-app",
            pack_name="database-postgres"
        )
    """
    logger.info(
        "MCP tool called: add_pack",
        extra={"project_dir": project_dir, "pack_name": pack_name},
    )

    return await add_pack(
        project_dir=project_dir,
        pack_name=pack_name,
    )


@mcp.tool()
async def doctor_tool(project_dir: str) -> dict:
    """
    Check health status of an Anchor Stack project.

    Analyzes the project for:
    - Configuration validity
    - Dependency version drift
    - Missing AI rules files
    - Common structural issues

    Args:
        project_dir: Absolute path to Anchor Stack project

    Returns:
        Dictionary containing:
        - success: Whether check completed
        - healthy: Whether project has no issues
        - issues: List of problems requiring attention
        - warnings: List of non-critical warnings
        - summary: Human-readable summary

    Example:
        doctor_tool(project_dir="/home/user/projects/my-app")
    """
    logger.info(
        "MCP tool called: doctor",
        extra={"project_dir": project_dir},
    )

    return await doctor(project_dir=project_dir)


def create_server() -> FastMCP:
    """
    Create and return the MCP server instance.

    This function is the entry point for running the server.

    Returns:
        Configured FastMCP server instance
    """
    logger.info(
        "MCP Server created",
        extra={"name": settings.server_name, "version": __version__},
    )
    return mcp


def run_server(transport: str = "stdio") -> None:
    """
    Run the MCP server.

    Args:
        transport: Transport type ("stdio" or "streamable-http")
    """
    logger.info(
        "Starting MCP Server",
        extra={"transport": transport},
    )
    mcp.run(transport=transport)


# Allow direct execution
if __name__ == "__main__":
    run_server()
