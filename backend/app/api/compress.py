"""Compression API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import CompressRequest, CompressResponse
from app.services.compression import compression_service


router = APIRouter(prefix="/compress", tags=["compression"])


@router.post("", response_model=CompressResponse)
async def compress_endpoint(request: CompressRequest) -> CompressResponse:
    """
    Compress content for LLM token efficiency.

    - **json**: 60-95% token reduction via deduplication and minification
    - **text/code**: ~20% token reduction via whitespace/comment cleanup
    - **auto**: Detects JSON vs text automatically
    """
    try:
        result = compression_service.compress(
            request.content,
            request.content_type,
            request.aggressive,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Compression failed: {e}") from e

    return CompressResponse(
        compressed=result.compressed,
        original_tokens=result.original_tokens,
        compressed_tokens=result.compressed_tokens,
        reduction_ratio=result.ratio,
        algorithm=result.algorithm,
    )


@router.post("/batch", response_model=list[CompressResponse])
async def compress_batch(requests: list[CompressRequest]) -> list[CompressResponse]:
    """Compress multiple items in one request."""
    items = [(req.content, req.content_type, req.aggressive) for req in requests]
    results = compression_service.compress_batch(items)

    return [
        CompressResponse(
            compressed=r.compressed,
            original_tokens=r.original_tokens,
            compressed_tokens=r.compressed_tokens,
            reduction_ratio=r.ratio,
            algorithm=r.algorithm,
        )
        for r in results
    ]