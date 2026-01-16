"""Health check endpoints."""

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("")
async def health() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "debug": settings.debug,
    }


@router.get("/ready")
async def readiness() -> dict:
    """Readiness check endpoint."""
    # Add database/service checks here
    return {"status": "ready"}


@router.get("/live")
async def liveness() -> dict:
    """Liveness check endpoint."""
    return {"status": "alive"}
