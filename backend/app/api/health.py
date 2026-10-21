"""Health check endpoints."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "sentinel-studio"}


@router.get("/health/ready")
async def readiness_check() -> dict[str, str]:
    """Readiness check for Kubernetes."""
    return {"status": "ready", "service": "sentinel-studio"}