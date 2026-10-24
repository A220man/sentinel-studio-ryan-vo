"""History API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.models.schemas import (
    AnalyticsSummary,
    HistoryQuery,
    HistoryResponse,
)
from app.services.history import history_service


router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=HistoryResponse)
async def get_history(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    content_type: str | None = Query(None),
    algorithm: str | None = Query(None),
    min_ratio: float | None = Query(None, ge=0.0, le=1.0),
    since: str | None = Query(None),
    until: str | None = Query(None),
) -> HistoryResponse:
    """Get compression history with optional filtering and pagination."""
    from datetime import datetime

    query = HistoryQuery(
        limit=limit,
        offset=offset,
        content_type=content_type,
        algorithm=algorithm,
        min_ratio=min_ratio,
        since=datetime.fromisoformat(since) if since else None,
        until=datetime.fromisoformat(until) if until else None,
    )
    return history_service.get_history(query)


@router.get("/analytics", response_model=AnalyticsSummary)
async def get_analytics() -> AnalyticsSummary:
    """Get aggregated compression analytics."""
    return history_service.get_analytics()


@router.delete("")
async def clear_history() -> dict[str, int]:
    """Clear all compression history."""
    count = history_service.clear_history()
    return {"deleted": count}

