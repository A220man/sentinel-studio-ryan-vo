"""Tests for history API and service."""

from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.services.history import history_service
from app.models.schemas import HistoryQuery


@pytest.fixture
async def client() -> AsyncClient:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
async def clear_history():
    """Clear history before and after each test."""
    history_service.clear_history()
    yield
    history_service.clear_history()


class TestHistoryService:
    """Tests for HistoryService."""

    def test_record_and_retrieve(self) -> None:
        """Test recording and retrieving a compression record."""
        record = history_service.record_compression(
            content_type="json",
            algorithm="json-dedup",
            original_tokens=100,
            compressed_tokens=30,
            reduction_ratio=0.7,
            aggressive=True,
            content_preview='{"test": "data"}',
        )
        assert record.id is not None
        assert record.content_type == "json"
        assert record.algorithm == "json-dedup"
        assert record.original_tokens == 100
        assert record.compressed_tokens == 30
        assert record.reduction_ratio == 0.7

        # Retrieve
        query = HistoryQuery(limit=10)
        response = history_service.get_history(query)
        assert response.total == 1
        assert len(response.items) == 1
        assert response.items[0].id == record.id

    def test_filter_by_content_type(self) -> None:
        """Test filtering history by content type."""
        history_service.record_compression(
            content_type="json", algorithm="json-dedup", original_tokens=100,
            compressed_tokens=30, reduction_ratio=0.7, aggressive=True, content_preview="test"
        )
        history_service.record_compression(
            content_type="text", algorithm="text-smart", original_tokens=100,
            compressed_tokens=80, reduction_ratio=0.2, aggressive=True, content_preview="test"
        )

        query = HistoryQuery(content_type="json")
        response = history_service.get_history(query)
        assert response.total == 1
        assert response.items[0].content_type == "json"

    def test_filter_by_algorithm(self) -> None:
        """Test filtering history by algorithm."""
        history_service.record_compression(
            content_type="json", algorithm="json-dedup", original_tokens=100,
            compressed_tokens=30, reduction_ratio=0.7, aggressive=True, content_preview="test"
        )
        history_service.record_compression(
            content_type="json", algorithm="json-fallback", original_tokens=100,
            compressed_tokens=90, reduction_ratio=0.1, aggressive=True, content_preview="test"
        )

        query = HistoryQuery(algorithm="json-dedup")
        response = history_service.get_history(query)
        assert response.total == 1
        assert response.items[0].algorithm == "json-dedup"

    def test_pagination(self) -> None:
        """Test history pagination."""
        for i in range(5):
            history_service.record_compression(
                content_type="json", algorithm="json-dedup", original_tokens=100,
                compressed_tokens=30, reduction_ratio=0.7, aggressive=True, content_preview=f"test{i}"
            )

        query = HistoryQuery(limit=2, offset=0)
        response = history_service.get_history(query)
        assert response.total == 5
        assert len(response.items) == 2

        query = HistoryQuery(limit=2, offset=2)
        response = history_service.get_history(query)
        assert len(response.items) == 2

    def test_analytics(self) -> None:
        """Test analytics summary."""
        history_service.record_compression(
            content_type="json", algorithm="json-dedup", original_tokens=100,
            compressed_tokens=30, reduction_ratio=0.7, aggressive=True, content_preview="test"
        )
        history_service.record_compression(
            content_type="text", algorithm="text-smart", original_tokens=100,
            compressed_tokens=80, reduction_ratio=0.2, aggressive=True, content_preview="test"
        )

        analytics = history_service.get_analytics()
        assert analytics.total_compressions == 2
        assert analytics.total_original_tokens == 200
        assert analytics.total_compressed_tokens == 110
        assert analytics.by_content_type == {"json": 1, "text": 1}
        assert analytics.by_algorithm == {"json-dedup": 1, "text-smart": 1}

    def test_clear_history(self) -> None:
        """Test clearing history."""
        history_service.record_compression(
            content_type="json", algorithm="json-dedup", original_tokens=100,
            compressed_tokens=30, reduction_ratio=0.7, aggressive=True, content_preview="test"
        )
        assert history_service.clear_history() == 1

        query = HistoryQuery(limit=10)
        response = history_service.get_history(query)
        assert response.total == 0


class TestHistoryAPI:
    """Tests for history API endpoints."""

    async def test_get_history_empty(self, client: AsyncClient) -> None:
        """Test getting empty history."""
        response = await client.get("/api/v1/history")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_get_history_with_records(self, client: AsyncClient) -> None:
        """Test getting history with records."""
        # Create records via compression API
        await client.post("/api/v1/compress", json={
            "content": '{"test": "data"}',
            "content_type": "json",
        })
        await client.post("/api/v1/compress", json={
            "content": "plain text",
            "content_type": "text",
        })

        response = await client.get("/api/v1/history")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    async def test_get_history_filter_content_type(self, client: AsyncClient) -> None:
        """Test filtering history by content type."""
        await client.post("/api/v1/compress", json={
            "content": '{"test": "data"}',
            "content_type": "json",
        })
        await client.post("/api/v1/compress", json={
            "content": "plain text",
            "content_type": "text",
        })

        response = await client.get("/api/v1/history?content_type=json")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["content_type"] == "json"

    async def test_get_analytics(self, client: AsyncClient) -> None:
        """Test analytics endpoint."""
        await client.post("/api/v1/compress", json={
            "content": '{"test": "data"}',
            "content_type": "json",
        })
        await client.post("/api/v1/compress", json={
            "content": "plain text",
            "content_type": "text",
        })

        response = await client.get("/api/v1/history/analytics")
        assert response.status_code == 200
        data = response.json()
        assert data["total_compressions"] == 2
        assert "by_content_type" in data
        assert "by_algorithm" in data

    async def test_clear_history(self, client: AsyncClient) -> None:
        """Test clearing history via API."""
        await client.post("/api/v1/compress", json={
            "content": '{"test": "data"}',
            "content_type": "json",
        })

        response = await client.delete("/api/v1/history")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] == 1

        response = await client.get("/api/v1/history")
        assert response.json()["total"] == 0

