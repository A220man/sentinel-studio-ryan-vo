"""Tests for auth API endpoints."""

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


class TestAuthEndpoints:
    """Tests for OIDC auth endpoints."""

    async def test_login_stub(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/auth/login", json={"code": "c", "code_verifier": "v"})
        assert response.status_code == 200
        assert response.json()["message"] == "stub"
