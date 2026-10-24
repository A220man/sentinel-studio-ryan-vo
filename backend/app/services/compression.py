"""Service layer for compression operations."""

from __future__ import annotations

from app.core.compression import (
    compress_auto,
    compress_json,
    compress_text,
    decompress_json,
    CompressionResult,
)
from app.services.history import history_service


class CompressionService:
    """Service for handling compression operations."""

    def compress(self, content: str, content_type: str | None = None, aggressive: bool = True) -> CompressionResult:
        """Compress content with automatic type detection."""
        ctype = (content_type or "auto").lower()
        if ctype == "json":
            result = compress_json(content, aggressive=aggressive)
        elif ctype == "text":
            result = compress_text(content)
        else:
            result = compress_auto(content, aggressive=aggressive)

        # Record in history
        history_service.record_compression(
            content_type=result.algorithm.replace("-", "_").split("_")[0],
            algorithm=result.algorithm,
            original_tokens=result.original_tokens,
            compressed_tokens=result.compressed_tokens,
            reduction_ratio=result.ratio,
            aggressive=aggressive,
            content_preview=content[:200],
        )

        return result

    def compress_batch(self, items: list[tuple[str, str | None, bool]]) -> list[CompressionResult]:
        """Compress multiple items."""
        results = []
        for content, content_type, aggressive in items:
            results.append(self.compress(content, content_type, aggressive))
        return results

    def decompress(self, compressed: str) -> str:
        """Decompress JSON content."""
        return decompress_json(compressed)


# Singleton instance
compression_service = CompressionService()

