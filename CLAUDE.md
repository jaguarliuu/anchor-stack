# CLAUDE.md - Anchor Stack Project Instructions

This file contains instructions for Claude Code when working on this project.

## Project Overview

- **Project Name**: Anchor Stack
- **Type**: MCP Server (Model Context Protocol)
- **Language**: Python 3.10+
- **Purpose**: AI-friendly engineering foundation with stable versions, unified logging, and pluggable capability packs

## Directory Structure

### Modifiable Directories
- `src/anchor_stack/tools/` - MCP tool implementations
- `src/anchor_stack/services/` - Core business logic
- `src/anchor_stack/models/` - Pydantic data models
- `stacks/` - Stack template definitions
- `packs/` - Pack template definitions
- `tests/` - Test files

### Protected Directories (Do Not Modify Without Understanding)
- `src/anchor_stack/core/` - Framework essentials (logger, config, exceptions)

## Code Standards

### Logging
Always use the built-in logger, NOT print():

```python
from anchor_stack.core.logger import get_logger

logger = get_logger(__name__)

# Correct usage
logger.info("Operation completed", extra={"task_id": 123, "status": "success"})
logger.error("Operation failed", extra={"error": str(e), "context": ctx})
logger.debug("Debug info", extra={"data": data})

# INCORRECT - Never use
print("Operation completed")  # ❌
```

### Configuration
All configuration should use pydantic-settings:

```python
from anchor_stack.core.config import get_settings

settings = get_settings()
# Access settings.log_level, settings.stacks_dir, etc.

# INCORRECT - Never hardcode
LOG_LEVEL = "DEBUG"  # ❌
```

### Exceptions
Use custom exceptions from core.exceptions:

```python
from anchor_stack.core.exceptions import (
    StackNotFoundError,
    PackNotFoundError,
    TemplateRenderError,
)

# Raise with context
raise StackNotFoundError(
    "Stack not found",
    stack_type="nextjs",
    version="2025.1"
)
```

### Type Hints
All functions must have type hints:

```python
# Correct
def process_data(items: list[str], count: int = 10) -> dict[str, Any]:
    ...

# INCORRECT
def process_data(items, count=10):  # ❌
    ...
```

### Async Functions
MCP tools must be async:

```python
async def scaffold_project(...) -> dict[str, Any]:
    ...
```

## Adding New Features

### Adding a New MCP Tool
1. Create file in `src/anchor_stack/tools/`
2. Implement async function with proper type hints
3. Register in `server.py` using `@mcp.tool()` decorator
4. Add logging at entry and exit points
5. Export in `tools/__init__.py`

### Adding a New Stack
1. Create directory in `stacks/<stack-name>/`
2. Create `stack.yaml` with metadata
3. Add templates in `templates/` subdirectory
4. Add rules templates in `rules/` subdirectory

### Adding a New Pack
1. Create directory in `packs/<pack-name>/`
2. Create `pack.yaml` with metadata and adapters
3. Add stack-specific templates in `<stack-name>/templates/`

## Testing

Run tests with:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=anchor_stack --cov-report=html
```

## Code Quality

Run linting:
```bash
ruff check src/
```

Run type checking:
```bash
mypy src/
```

Format code:
```bash
ruff format src/
```

## Prohibited Actions

- ❌ Do NOT use print() for logging
- ❌ Do NOT hardcode configuration values
- ❌ Do NOT skip type hints
- ❌ Do NOT modify core/ files without discussion
- ❌ Do NOT add dependencies without updating pyproject.toml
- ❌ Do NOT skip error handling in tools

## Key Files

| File | Purpose |
|------|---------|
| `src/anchor_stack/server.py` | MCP Server entry point |
| `src/anchor_stack/cli.py` | CLI entry point |
| `src/anchor_stack/core/logger.py` | Logging infrastructure |
| `src/anchor_stack/core/config.py` | Configuration management |
| `pyproject.toml` | Project dependencies and metadata |
