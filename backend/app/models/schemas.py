"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

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


class CompressionRecord(BaseModel):
    """Stored compression history record."""

    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    content_type: str
    algorithm: str
    original_tokens: int
    compressed_tokens: int
    reduction_ratio: float
    aggressive: bool
    content_preview: str = Field(default="", max_length=200)


class HistoryQuery(BaseModel):
    """Query parameters for history retrieval."""

    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
    content_type: Optional[str] = None
    algorithm: Optional[str] = None
    min_ratio: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    since: Optional[datetime] = None
    until: Optional[datetime] = None


class HistoryResponse(BaseModel):
    """Paginated history response."""

    items: list[CompressionRecord]
    total: int
    limit: int
    offset: int


class AnalyticsSummary(BaseModel):
    """Aggregated compression analytics."""

    total_compressions: int
    total_original_tokens: int
    total_compressed_tokens: int
    average_reduction_ratio: float
    by_content_type: dict[str, int]
    by_algorithm: dict[str, int]


class ErrorResponse(BaseModel):
    """Error response."""

    detail: str

