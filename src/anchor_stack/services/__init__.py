"""
Services module - Core business logic.

This module contains:
- StackManager: Load and manage Stack definitions
- PackManager: Load and manage Pack definitions
- TemplateRenderer: Render Jinja2 templates
- FileWriter: Write files to filesystem
- RulesGenerator: Generate AI Rules files
"""

from anchor_stack.services.file_writer import FileWriter
from anchor_stack.services.pack_manager import PackManager
from anchor_stack.services.rules_generator import RulesGenerator
from anchor_stack.services.stack_manager import StackManager
from anchor_stack.services.template_renderer import TemplateRenderer

__all__ = [
    "StackManager",
    "PackManager",
    "TemplateRenderer",
    "FileWriter",
    "RulesGenerator",
]
