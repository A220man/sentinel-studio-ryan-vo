"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CompressRequest(BaseModel):
    """Request payload for compression."""

    content: str = Field(..., description="Content to compress", min_length=1)
    content_type: str | None = Field(
        default=None,
        description="Content type: 'json', 'text', or 'auto' (default)",
    )
    aggressive: bool = Field(default=True, description="Enable aggressive JSON deduplication")


class CompressResponse(BaseModel):
    """Response payload for compression."""

    compressed: str
    original_tokens: int
    compressed_tokens: int
    reduction_ratio: float
    algorithm: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str


class ErrorResponse(BaseModel):
    """Error response."""

    detail: str