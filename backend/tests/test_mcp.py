"""Tests for MCP server."""

from __future__ import annotations

import json

import pytest

from app.mcp.server import mcp_server


def _is_error(result) -> bool:
    """Check if call_tool result indicates an error."""
    if isinstance(result, tuple):
        content_list, structured = result
        if isinstance(structured, dict) and structured.get('isError'):
            return True
        for item in content_list:
            if hasattr(item, 'text') and 'Error' in item.text:
                return True
    return False


class TestMCPServerTools:
    """Tests for MCP server tool listing."""

    @pytest.mark.asyncio
    async def test_list_tools(self) -> None:
        tools = await mcp_server.list_tools()
        tool_names = [tool.name for tool in tools]

        expected = [
            "compress_json",
            "compress_text",
            "compress_auto",
            "decompress_json",
            "compress_batch",
        ]
        for name in expected:
            assert name in tool_names

        for tool in tools:
            assert tool.name
            assert tool.description
            assert tool.inputSchema
            assert tool.inputSchema.get("type") == "object"


class TestMCPServerCompressJSON:
    """Tests for compress_json tool."""

    @pytest.mark.asyncio
    async def test_compress_json_basic(self) -> None:
        payload = {"content": '{"items": [{"id": 1, "name": "test"}, {"id": 2, "name": "test"}]}'}
        result = await mcp_server.call_tool("compress_json", payload)

        assert not _is_error(result)
        content_list, _ = result
        data = json.loads(content_list[0].text)
        assert "compressed" in data
        assert "original_tokens" in data
        assert "compressed_tokens" in data
        assert "reduction_ratio" in data
        assert "algorithm" in data
        assert data["algorithm"].startswith("json")

    @pytest.mark.asyncio
    async def test_compress_json_aggressive_false(self) -> None:
        payload = {"content": '{"a": "repeat", "b": "repeat"}', "aggressive": False}
        result = await mcp_server.call_tool("compress_json", payload)

        assert not _is_error(result)
        content_list, _ = result
        data = json.loads(content_list[0].text)
        assert data["algorithm"].startswith("json")

    @pytest.mark.asyncio
    async def test_compress_json_missing_content(self) -> None:
        try:
            result = await mcp_server.call_tool("compress_json", {})
            assert _is_error(result)
        except Exception:
            pass


class TestMCPServerCompressText:
    """Tests for compress_text tool."""

    @pytest.mark.asyncio
    async def test_compress_text_basic(self) -> None:
        payload = {"content": "function test() {\n    // comment\n    return 42;\n}"}
        result = await mcp_server.call_tool("compress_text", payload)

        assert not _is_error(result)
        content_list, _ = result
        data = json.loads(content_list[0].text)
        assert "compressed" in data
        assert data["algorithm"].startswith("text")

    @pytest.mark.asyncio
    async def test_compress_text_algorithm_option(self) -> None:
        payload = {"content": "test code", "algorithm": "text-basic"}
        result = await mcp_server.call_tool("compress_text", payload)

        assert not _is_error(result)
        content_list, _ = result
        data = json.loads(content_list[0].text)
        assert data["algorithm"] in ("text-basic", "text-smart")


class TestMCPServerCompressAuto:
    """Tests for compress_auto tool."""

    @pytest.mark.asyncio
    async def test_compress_auto_detects_json(self) -> None:
        payload = {"content": '{"auto": "detected"}'}
        result = await mcp_server.call_tool("compress_auto", payload)

        assert not _is_error(result)
        content_list, _ = result
        data = json.loads(content_list[0].text)
        assert data["algorithm"].startswith("json")

    @pytest.mark.asyncio
    async def test_compress_auto_detects_text(self) -> None:
        payload = {"content": "plain text content"}
        result = await mcp_server.call_tool("compress_auto", payload)

        assert not _is_error(result)
        content_list, _ = result
        data = json.loads(content_list[0].text)
        assert data["algorithm"].startswith("text")


class TestMCPServerDecompressJSON:
    """Tests for decompress_json tool."""

    @pytest.mark.asyncio
    async def test_decompress_json(self) -> None:
        compress_result = await mcp_server.call_tool("compress_json", {"content": '{"test": "value"}'})
        assert not _is_error(compress_result)
        compress_content, _ = compress_result
        compressed_data = json.loads(compress_content[0].text)
        compressed = compressed_data["compressed"]

        result = await mcp_server.call_tool("decompress_json", {"compressed": compressed})

        assert not _is_error(result)
        content_list, _ = result
        assert "test" in content_list[0].text
        assert "value" in content_list[0].text


class TestMCPServerCompressBatch:
    """Tests for compress_batch tool."""

    @pytest.mark.asyncio
    async def test_compress_batch(self) -> None:
        payload = {
            "items": [
                {"content": '{"a": 1}', "content_type": "json", "aggressive": True},
                {"content": "plain text", "content_type": "text", "aggressive": True},
            ]
        }
        result = await mcp_server.call_tool("compress_batch", payload)

        assert not _is_error(result)
        content_list, _ = result
        data = json.loads(content_list[0].text)
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["algorithm"].startswith("json")
        assert data[1]["algorithm"].startswith("text")


class TestMCPServerErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_unknown_tool(self) -> None:
        try:
            result = await mcp_server.call_tool("unknown_tool", {})
            assert _is_error(result)
        except Exception as e:
            assert "Unknown tool" in str(e)


class TestMCPServerRun:
    """Tests for server entry point."""

    def test_server_has_run(self) -> None:
        assert callable(mcp_server.run)
