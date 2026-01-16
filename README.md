<div align="center">

# Anchor Stack

<img src="https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"/>
<img src="https://img.shields.io/badge/MCP-1.25+-green?style=for-the-badge&logo=anthropic&logoColor=white" alt="MCP 1.25+"/>
<img src="https://img.shields.io/badge/license-MIT-orange?style=for-the-badge" alt="MIT License"/>
<img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=for-the-badge" alt="PRs Welcome"/>

**AI-Friendly Engineering Foundation**

*Stable versions, unified logging, and pluggable capability packs*

[English](./README.md) | [中文](./README_CN.md)

---

</div>

## Why Anchor Stack?

Have you ever experienced this?

> *"AI helped me write the code, but debugging took longer than writing it myself..."*

The problem isn't the AI - it's that **your project wasn't designed for AI collaboration**.

Anchor Stack solves this by creating projects that are:

| Problem | Solution |
|---------|----------|
| Inconsistent logging | Standardized `logger` module - AI knows exactly how to add logs |
| Environment chaos | Type-safe `config` module - no more `process.env` everywhere |
| Version conflicts | Curated dependency versions - tested and stable |
| AI confusion | Rules files that teach AI your project conventions |

## Features

- **Stable Stacks** - Curated technology stacks with version-locked dependencies
- **Unified Logging** - Standardized logging framework that AI understands
- **AI Rules** - Auto-generated rules for Claude, Cursor, Windsurf, and more
- **Pluggable Packs** - Add database, AI, auth capabilities on demand
- **MCP Native** - Works seamlessly with MCP-compatible AI tools

## Quick Start

### Installation

```bash
# Using pip
pip install anchor-stack

# Using uv (recommended)
uv pip install anchor-stack
```

### Configure Your AI Tool

<details>
<summary><b>Claude Desktop</b></summary>

Edit `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

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

</details>

<details>
<summary><b>Cursor</b></summary>

Edit `~/.cursor/mcp.json`:

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

</details>

<details>
<summary><b>VS Code (Copilot)</b></summary>

Edit `.vscode/settings.json`:

```json
{
  "mcp": {
    "servers": {
      "anchor-stack": {
        "command": "anchor-stack",
        "args": ["serve"]
      }
    }
  }
}
```

</details>

### Create Your First Project

Simply ask your AI assistant:

```
Create a Next.js project called "my-app" using Anchor Stack
```

The AI will use `scaffold_project` to create:

```
my-app/
├── src/
│   ├── app/              # Next.js App Router
│   ├── components/       # React components
│   ├── lib/
│   │   ├── core/         # Logger & Config (DO NOT MODIFY)
│   │   └── utils/        # Utility functions
│   └── services/         # Business logic
├── CLAUDE.md             # Rules for Claude
├── .cursor/rules/        # Rules for Cursor
├── .windsurfrules        # Rules for Windsurf
└── anchor.config.json    # Project metadata
```

## Available Tools

### `scaffold_project`

Create a new project from a Stack template.

```typescript
scaffold_project({
  stack_name: "nextjs",        // Stack type
  project_name: "my-app",      // Project name
  target_dir: "/path/to/dir"   // Target directory
})
```

### `add_pack`

Add a capability pack to an existing project.

```typescript
add_pack({
  project_dir: "/path/to/project",
  pack_name: "database-postgres"
})
```

### `doctor`

Check project health and configuration.

```typescript
doctor({
  project_dir: "/path/to/project"
})
```

## Available Stacks

| Stack | Version | Description |
|-------|---------|-------------|
| `nextjs` | 2026.1 | Next.js 16 + React 19 + TypeScript 5.9 + Tailwind CSS |
| `fastapi` | 2026.1 | FastAPI 0.128 + SQLAlchemy 2.0 + Pydantic v2 |

## Available Packs

| Pack | Description |
|------|-------------|
| `database-postgres` | PostgreSQL with Drizzle ORM (JS) or SQLAlchemy (Python) |
| `ai-langgraph` | LangChain + LangGraph for AI applications |

## How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   AI Assistant  │────▶│   Anchor Stack   │────▶│  Your Project   │
│  (Claude, etc.) │     │   (MCP Server)   │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
              ┌──────────┐         ┌──────────┐
              │  Stacks  │         │  Packs   │
              │ (nextjs) │         │ (db,ai)  │
              └──────────┘         └──────────┘
```

1. **You ask** your AI to create a project
2. **AI calls** Anchor Stack's MCP tools
3. **Anchor Stack generates** files with proper structure
4. **AI Rules** help future AI interactions understand your project

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

| Variable | Default | Description |
|----------|---------|-------------|
| `ANCHOR_STACK_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `ANCHOR_STACK_LOG_JSON` | `false` | Output logs in JSON format |
| `ANCHOR_STACK_STACKS_DIR` | `stacks` | Custom stacks directory |
| `ANCHOR_STACK_PACKS_DIR` | `packs` | Custom packs directory |

## Development

```bash
# Clone the repository
git clone https://github.com/anthropics/anchor-stack.git
cd anchor-stack

# Install dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Run linting
uv run ruff check src/

# Start dev server
uv run anchor-stack serve
```

## Roadmap

- [x] Core MCP Server implementation
- [x] Next.js Stack template
- [x] FastAPI Stack template
- [ ] Database Pack (PostgreSQL)
- [ ] AI Pack (LangGraph)
- [ ] Auth Pack (NextAuth/OAuth)
- [ ] Web UI for template management

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](./LICENSE) for details.

---

<div align="center">

**Built with Anchor Stack - Making AI-assisted development reliable**

[Report Bug](https://github.com/anthropics/anchor-stack/issues) · [Request Feature](https://github.com/anthropics/anchor-stack/issues)

</div>
