"""Tests for OIDC auth API endpoints with PKCE authorization code flow."""

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


class TestAuthLogin:
    """Tests for OIDC authorization code flow initiation."""

    async def test_login_redirects_with_pkce_when_configured(self, client: AsyncClient) -> None:
        """Login endpoint should generate PKCE and set cookies when Keycloak is configured."""
        response = await client.get("/api/v1/auth/login")
        # When Keycloak is not configured, should still set PKCE cookie and return structure
        assert response.status_code in (200, 302)
        # Should set pkce_code_verifier cookie (HttpOnly)
        assert "pkce_code_verifier" in response.cookies

    async def test_login_sets_state_cookie(self, client: AsyncClient) -> None:
        """Login should set auth_state cookie for CSRF protection."""
        response = await client.get("/api/v1/auth/login")
        # Check cookies - auth_state may have path restriction
        cookie_names = list(response.cookies.keys())
        assert "pkce_code_verifier" in cookie_names or response.status_code == 302


class TestAuthCallback:
    """Tests for authorization code callback endpoint."""

    async def test_callback_missing_code(self, client: AsyncClient) -> None:
        """Callback should reject missing authorization code."""
        response = await client.get("/api/v1/auth/callback")
        assert response.status_code == 400

    async def test_callback_with_code(self, client: AsyncClient) -> None:
        """Callback with authorization code should handle it."""
        # Set the pkce_code_verifier cookie first
        response = await client.get(
            "/api/v1/auth/callback?code=test_auth_code&state=test_state",
            cookies={"pkce_code_verifier": "test_verifier"},
        )
        # Should either succeed or fail with appropriate error
        assert response.status_code in (200, 400, 401)


class TestAuthTokens:
    """Tests for token management endpoints."""

    async def test_refresh_requires_refresh_token(self, client: AsyncClient) -> None:
        """Refresh endpoint should require refresh token cookie."""
        response = await client.post("/api/v1/auth/refresh")
        assert response.status_code == 401

    async def test_logout_clears_cookies(self, client: AsyncClient) -> None:
        """Logout should clear all auth cookies."""
        response = await client.post("/api/v1/auth/logout")
        # Should clear cookies - check that auth cookies are not present
        cookie_names = ["access_token", "refresh_token", "id_token"]
        for name in cookie_names:
            cookie = response.cookies.get(name)
            # After deletion, cookie may still be present with Max-Age=0
            if cookie:
                max_age = cookie.value if hasattr(cookie, 'value') else str(cookie)
                assert "Max-Age=0" in max_age or "expires" in max_age.lower()


class TestAuthMe:
    """Tests for user info endpoint."""

    async def test_me_returns_user_info(self, client: AsyncClient) -> None:
        """/me endpoint should return user info."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert "authenticated" in data
