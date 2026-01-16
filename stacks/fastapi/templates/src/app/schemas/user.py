"""User schemas."""

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=100, description="User name")


class UserCreate(UserBase):
    """Schema for creating a user."""

    pass


class User(UserBase):
    """User schema with ID."""

    id: int = Field(..., description="User ID")

    model_config = {"from_attributes": True}
