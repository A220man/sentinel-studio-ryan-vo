"""Service layer for compression operations."""

from __future__ import annotations

from app.core.compression import (
    compress_auto,
    compress_json,
    compress_text,
    decompress_json,
    CompressionResult,
)


class CompressionService:
    """Service for handling compression operations."""

    def compress(self, content: str, content_type: str | None = None, aggressive: bool = True) -> CompressionResult:
        """Compress content with automatic type detection."""
        ctype = (content_type or "auto").lower()
        if ctype == "json":
            return compress_json(content, aggressive=aggressive)
        elif ctype == "text":
            return compress_text(content)
        else:
            return compress_auto(content, aggressive=aggressive)

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