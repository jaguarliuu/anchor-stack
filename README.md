# Anchor Stack

> AI-friendly engineering foundation with stable versions, unified logging, and pluggable capability packs.

## What is Anchor Stack?

Anchor Stack is an MCP (Model Context Protocol) Server that helps you create well-structured projects that AI coding tools can understand and maintain. It solves the problem of projects dying in the Debug phase by providing:

- **Stable Versions**: Curated dependency combinations that work well together
- **Unified Logging**: Standardized logging framework that AI can use to add meaningful logs
- **AI Rules**: Documentation that tells AI tools how to work with your project
- **Pluggable Packs**: Pre-configured capabilities (database, AI, auth) that can be added on demand

## Installation

```bash
pip install anchor-stack
```

Or with uv:

```bash
uv pip install anchor-stack
```

## Quick Start

### 1. Configure Your AI Tool

Add to your MCP configuration:

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "anchor-stack": {
      "command": "anchor-stack",
      "args": ["serve"]
    }
  }
}
```

**Cursor** (MCP settings):
```json
{
  "anchor-stack": {
    "command": "anchor-stack",
    "args": ["serve"]
  }
}
```

### 2. Create a Project

Ask your AI assistant:
> "Use anchor-stack to create a new Next.js project called my-app with PostgreSQL database support"

The AI will use the `scaffold_project` tool to create your project with:
- Proper directory structure
- Locked dependency versions
- Built-in logging
- AI rules files for Cursor, Claude Code, etc.

### 3. Add Capabilities

Ask your AI assistant:
> "Add the database-postgres pack to my project"

## Available Tools

### scaffold_project

Create a new project from a Stack template.

Parameters:
- `app_name`: Project name (lowercase, alphanumeric, hyphens)
- `app_type`: Stack type (`nextjs`, `python-api`)
- `target_dir`: Where to create the project
- `capabilities`: List of Packs to include

### add_pack

Add a capability pack to an existing project.

Parameters:
- `project_dir`: Path to project
- `pack_name`: Pack to add (`database-postgres`, `ai-langgraph`)

### doctor

Check project health and report issues.

Parameters:
- `project_dir`: Path to project

## Available Stacks

| Stack | Description |
|-------|-------------|
| `nextjs` | Next.js 15 + React 19 + TypeScript |
| `python-api` | FastAPI + SQLAlchemy + Pydantic |

## Available Packs

| Pack | Description |
|------|-------------|
| `database-postgres` | PostgreSQL with Drizzle ORM (JS) or SQLAlchemy (Python) |
| `ai-langgraph` | LangChain + LangGraph for AI applications |

## CLI Commands

```bash
# Start MCP server
anchor-stack serve

# List available stacks
anchor-stack list-stacks

# List available packs
anchor-stack list-packs

# Show configuration
anchor-stack info
```

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `ANCHOR_STACK_LOG_LEVEL` | `INFO` | Log level |
| `ANCHOR_STACK_LOG_JSON` | `false` | JSON log output |
| `ANCHOR_STACK_STACKS_DIR` | `stacks` | Stacks directory |
| `ANCHOR_STACK_PACKS_DIR` | `packs` | Packs directory |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
ruff check src/

# Run type checking
mypy src/
```

## License

MIT License

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.
