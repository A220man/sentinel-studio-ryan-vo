"""Auth API endpoints for OIDC/Keycloak integration."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(request: Request) -> dict:
    """Exchange authorization code and verifier for tokens (stub)."""
    data = await request.json()
    # Stub implementation: ignore code and code_verifier, just return success
    return {"message": "stub"}
