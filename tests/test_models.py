"""
Tests for StackSpec model.
"""

import pytest
from pydantic import ValidationError

from anchor_stack.models.stack_spec import StackSpec


class TestStackSpec:
    """Tests for StackSpec model validation."""

    def test_valid_spec(self) -> None:
        """Test creating a valid StackSpec."""
        spec = StackSpec(
            app_name="my-app",
            app_type="nextjs",
            stack_version="2025.1",
            capabilities=["database-postgres"],
        )

        assert spec.app_name == "my-app"
        assert spec.app_type == "nextjs"
        assert spec.stack_version == "2025.1"
        assert spec.capabilities == ["database-postgres"]
        assert spec.stack_id == "nextjs@2025.1"

    def test_app_name_normalization(self) -> None:
        """Test app_name is normalized to lowercase."""
        spec = StackSpec(
            app_name="My-App",
            app_type="NEXTJS",
        )

        assert spec.app_name == "my-app"
        assert spec.app_type == "nextjs"

    def test_app_name_validation_start_letter(self) -> None:
        """Test app_name must start with a letter."""
        with pytest.raises(ValidationError):
            StackSpec(app_name="123-app", app_type="nextjs")

    def test_app_name_validation_no_consecutive_hyphens(self) -> None:
        """Test app_name cannot have consecutive hyphens."""
        with pytest.raises(ValidationError):
            StackSpec(app_name="my--app", app_type="nextjs")

    def test_app_name_validation_no_trailing_hyphen(self) -> None:
        """Test app_name cannot end with a hyphen."""
        with pytest.raises(ValidationError):
            StackSpec(app_name="my-app-", app_type="nextjs")

    def test_capabilities_deduplication(self) -> None:
        """Test capabilities are deduplicated."""
        spec = StackSpec(
            app_name="my-app",
            app_type="nextjs",
            capabilities=["database-postgres", "Database-Postgres", "ai-langgraph"],
        )

        assert spec.capabilities == ["database-postgres", "ai-langgraph"]

    def test_default_values(self) -> None:
        """Test default values are applied."""
        spec = StackSpec(
            app_name="my-app",
            app_type="nextjs",
        )

        assert spec.stack_version == "2025.1"
        assert spec.capabilities == []
        assert spec.description is None
        assert spec.author is None

    def test_single_letter_app_name(self) -> None:
        """Test single letter app name is valid."""
        spec = StackSpec(app_name="a", app_type="nextjs")
        assert spec.app_name == "a"
