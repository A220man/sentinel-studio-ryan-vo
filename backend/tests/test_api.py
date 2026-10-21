"""Tests for API endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import create_app


@pytest.fixture
async def client() -> AsyncClient:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    async def test_health_check(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "sentinel-studio"

    async def test_readiness_check(self, client: AsyncClient) -> None:
        response = await client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


class TestCompressionEndpoints:
    """Tests for compression API endpoints."""

    async def test_compress_json(self, client: AsyncClient) -> None:
        payload = {
            "content": '{"items": [{"name": "test"}, {"name": "test"}]}',
            "content_type": "json",
        }
        response = await client.post("/api/v1/compress", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "compressed" in data
        assert "reduction_ratio" in data
        assert data["reduction_ratio"] >= 0.0
        assert data["original_tokens"] > 0
        assert data["compressed_tokens"] > 0

    async def test_compress_text(self, client: AsyncClient) -> None:
        payload = {
            "content": "function foo() {\n  return 42;\n}\n// comment\n",
            "content_type": "text",
        }
        response = await client.post("/api/v1/compress", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["reduction_ratio"] >= 0.0
        assert data["algorithm"].startswith("text")

    async def test_compress_auto_json(self, client: AsyncClient) -> None:
        payload = {"content": '{"auto": "detected"}'}
        response = await client.post("/api/v1/compress", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["algorithm"].startswith("json")

    async def test_compress_auto_text(self, client: AsyncClient) -> None:
        payload = {"content": "plain text"}
        response = await client.post("/api/v1/compress", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["algorithm"].startswith("text")

    async def test_compress_batch(self, client: AsyncClient) -> None:
        payload = [
            {"content": '{"a": 1}', "content_type": "json"},
            {"content": "text content", "content_type": "text"},
        ]
        response = await client.post("/api/v1/compress/batch", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["algorithm"].startswith("json")
        assert data[1]["algorithm"].startswith("text")

    async def test_compress_empty_content_rejected(self, client: AsyncClient) -> None:
        payload = {"content": ""}
        response = await client.post("/api/v1/compress", json=payload)
        assert response.status_code == 422  # Validation error

    async def test_compress_invalid_json_fallback(self, client: AsyncClient) -> None:
        # Invalid JSON with content_type=json should still work (fallback)
        payload = {"content": "not json {", "content_type": "json"}
        response = await client.post("/api/v1/compress", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Falls back to text compression
        assert data["algorithm"] in ("json-fallback", "text-smart")