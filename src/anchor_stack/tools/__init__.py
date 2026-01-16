"""
MCP Tools module.

This module contains MCP tool implementations:
- scaffold_project: Create a new project from Stack and Packs
- add_pack: Add a capability pack to existing project
- doctor: Check project health status
"""

from anchor_stack.tools.doctor import doctor
from anchor_stack.tools.pack import add_pack
from anchor_stack.tools.scaffold import scaffold_project

__all__ = [
    "scaffold_project",
    "add_pack",
    "doctor",
]
