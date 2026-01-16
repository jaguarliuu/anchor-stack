"""User endpoints - Example CRUD operations."""

from fastapi import APIRouter, HTTPException

from app.core.logger import logger
from app.schemas.user import User, UserCreate

router = APIRouter()

# In-memory storage for demo
_users: dict[int, User] = {}
_counter = 0


@router.get("", response_model=list[User])
async def list_users() -> list[User]:
    """List all users."""
    logger.info("Listing users", count=len(_users))
    return list(_users.values())


@router.post("", response_model=User, status_code=201)
async def create_user(user_in: UserCreate) -> User:
    """Create a new user."""
    global _counter
    _counter += 1

    user = User(id=_counter, **user_in.model_dump())
    _users[user.id] = user

    logger.info("User created", user_id=user.id, email=user.email)
    return user


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int) -> User:
    """Get a user by ID."""
    user = _users.get(user_id)
    if not user:
        logger.warning("User not found", user_id=user_id)
        raise HTTPException(status_code=404, detail="User not found")

    logger.info("User retrieved", user_id=user_id)
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int) -> None:
    """Delete a user."""
    if user_id not in _users:
        logger.warning("User not found for deletion", user_id=user_id)
        raise HTTPException(status_code=404, detail="User not found")

    del _users[user_id]
    logger.info("User deleted", user_id=user_id)
