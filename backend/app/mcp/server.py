"""MCP Server for Sentinel Studio compression tools.

Exposes compression functionality via the Model Context Protocol.
Compatible with Claude Desktop and other MCP clients.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from app.core.compression import (
    compress_json as core_compress_json,
    compress_text as core_compress_text,
    compress_auto as core_compress_auto,
    decompress_json as core_decompress_json,
    CompressionResult,
)
from app.services.compression import compression_service


# Create the MCP server using FastMCP (high-level API)
mcp_server = FastMCP("sentinel-studio-compression")


def _format_result(result: CompressionResult) -> str:
    """Format compression result as JSON string."""
    return json.dumps(
        {
            "compressed": result.compressed,
            "original_tokens": result.original_tokens,
            "compressed_tokens": result.compressed_tokens,
            "reduction_ratio": round(result.ratio, 4),
            "algorithm": result.algorithm,
        },
        indent=2,
    )


@mcp_server.tool()
def compress_json(content: str, aggressive: bool = True) -> str:
    """Compress JSON content using dictionary deduplication and minification.
    
    Achieves 60-95% token reduction for repetitive JSON.
    
    Args:
        content: JSON content to compress
        aggressive: Enable aggressive deduplication (default: true)
    
    Returns:
        JSON string with compressed content and metadata
    """
    result = core_compress_json(content, aggressive=aggressive)
    return _format_result(result)


@mcp_server.tool()
def compress_text(content: str, algorithm: str = "text-smart") -> str:
    """Compress plain text or code by removing redundant whitespace, trailing spaces, and full-line comments.
    
    Achieves ~20% token reduction.
    
    Args:
        content: Text or code content to compress
        algorithm: Compression algorithm: 'text-smart' (default) or 'text-basic'
    
    Returns:
        JSON string with compressed content and metadata
    """
    result = core_compress_text(content, algorithm=algorithm)
    return _format_result(result)


@mcp_server.tool()
def compress_auto(content: str, aggressive: bool = True) -> str:
    """Automatically detect content type (JSON vs text) and apply optimal compression strategy.
    
    Args:
        content: Content to compress (JSON or text)
        aggressive: Enable aggressive JSON deduplication (default: true)
    
    Returns:
        JSON string with compressed content and metadata
    """
    result = core_compress_auto(content, aggressive=aggressive)
    return _format_result(result)


@mcp_server.tool()
def decompress_json(compressed: str) -> str:
    """Decompress JSON that was compressed with compress_json.
    
    Restores dictionary references.
    
    Args:
        compressed: Compressed JSON content to decompress
    
    Returns:
        Decompressed JSON string
    """
    return core_decompress_json(compressed)


@mcp_server.tool()
def compress_batch(items: list[dict[str, Any]]) -> str:
    """Compress multiple items in one request.
    
    Useful for compressing multiple log entries or API responses.
    
    Args:
        items: Array of items to compress, each with content, content_type, and aggressive options
    
    Returns:
        JSON array of compression results
    """
    service_items = []
    for item in items:
        content = item.get("content", "")
        content_type = item.get("content_type")
        aggressive = item.get("aggressive", True)
        service_items.append((content, content_type, aggressive))

    results = compression_service.compress_batch(service_items)
    formatted = [_format_result(r) for r in results]
    return "[\n  " + ",\n  ".join(formatted) + "\n]"


if __name__ == "__main__":
    mcp_server.run()
