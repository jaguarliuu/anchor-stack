"""
CLI entry point for Anchor Stack.

Provides command-line interface for:
- Running the MCP server
- Listing available stacks and packs
- Version information
"""

from __future__ import annotations

import click

from anchor_stack import __version__
from anchor_stack.core.config import get_settings
from anchor_stack.core.logger import get_logger, setup_logging


@click.group()
@click.version_option(version=__version__, prog_name="anchor-stack")
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default=None,
    help="Set log level (overrides ANCHOR_STACK_LOG_LEVEL)",
)
@click.option(
    "--log-json",
    is_flag=True,
    default=False,
    help="Output logs in JSON format",
)
@click.pass_context
def cli(ctx: click.Context, log_level: str | None, log_json: bool) -> None:
    """
    Anchor Stack - AI-friendly engineering foundation.

    A MCP Server providing stable versions, unified logging,
    and pluggable capability packs for AI-assisted development.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Configure logging
    settings = get_settings()
    effective_log_level = log_level or settings.log_level
    effective_log_json = log_json or settings.log_json

    setup_logging(level=effective_log_level, json_output=effective_log_json, force=True)

    ctx.obj["logger"] = get_logger(__name__)


@cli.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "streamable-http"]),
    default="stdio",
    help="Transport type for MCP communication",
)
@click.pass_context
def serve(ctx: click.Context, transport: str) -> None:
    """
    Start the MCP server.

    Run this command to start Anchor Stack as an MCP server
    that can be connected to by AI coding tools.

    Examples:

        # Start with stdio transport (default, for Claude Desktop/Cursor)
        anchor-stack serve

        # Start with HTTP transport
        anchor-stack serve --transport streamable-http
    """
    logger = ctx.obj["logger"]
    logger.info("Starting Anchor Stack MCP Server", extra={"transport": transport})

    from anchor_stack.server import run_server

    run_server(transport=transport)


@cli.command()
@click.pass_context
def list_stacks(ctx: click.Context) -> None:
    """
    List available technology stacks.

    Shows all Stack definitions that can be used with scaffold_project.
    """
    logger = ctx.obj["logger"]
    logger.debug("Listing available stacks")

    from anchor_stack.services.stack_manager import StackManager

    manager = StackManager()
    stacks = manager.list_available()

    if not stacks:
        click.echo("No stacks available.")
        click.echo("Stacks should be placed in the 'stacks/' directory.")
        return

    click.echo("Available Stacks:\n")
    for stack in stacks:
        click.echo(f"  {stack['type']}@{stack['version']}")
        click.echo(f"    {stack['display_name']}")
        click.echo()


@cli.command()
@click.option(
    "--stack",
    "-s",
    default=None,
    help="Filter packs compatible with a specific stack",
)
@click.pass_context
def list_packs(ctx: click.Context, stack: str | None) -> None:
    """
    List available capability packs.

    Shows all Pack definitions that can be added to projects.

    Examples:

        # List all packs
        anchor-stack list-packs

        # List packs compatible with nextjs
        anchor-stack list-packs --stack nextjs
    """
    logger = ctx.obj["logger"]
    logger.debug("Listing available packs", extra={"stack_filter": stack})

    from anchor_stack.services.pack_manager import PackManager

    manager = PackManager()

    if stack:
        packs = manager.list_compatible(stack)
        click.echo(f"Packs compatible with '{stack}':\n")
    else:
        packs = manager.list_available()
        click.echo("Available Packs:\n")

    if not packs:
        click.echo("No packs available.")
        click.echo("Packs should be placed in the 'packs/' directory.")
        return

    for pack in packs:
        click.echo(f"  {pack['name']}")
        click.echo(f"    {pack['display_name']}")
        if "compatible_stacks" in pack:
            stacks_str = ", ".join(pack["compatible_stacks"])  # type: ignore
            click.echo(f"    Compatible: {stacks_str}")
        click.echo()


@cli.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    """
    Show Anchor Stack information.

    Displays version, configuration, and paths.
    """
    settings = get_settings()

    click.echo(f"Anchor Stack v{__version__}")
    click.echo()
    click.echo("Configuration:")
    click.echo(f"  Log Level:      {settings.log_level}")
    click.echo(f"  Log JSON:       {settings.log_json}")
    click.echo(f"  Stacks Dir:     {settings.get_stacks_path()}")
    click.echo(f"  Packs Dir:      {settings.get_packs_path()}")
    click.echo(f"  Default Stack:  {settings.default_stack_version}")
    click.echo()
    click.echo("MCP Server:")
    click.echo(f"  Name:           {settings.server_name}")
    click.echo(f"  Version:        {settings.server_version}")


def main() -> None:
    """Main entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
