"""Auth service for OIDC/Keycloak PKCE authorization code flow."""

from __future__ import annotations

import base64
import secrets
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

from app.core.pkce import (
    generate_code_verifier,
    generate_code_challenge,
    verifier_from_url,
    code_verifier_valid,
)


class KeycloakClient:
    """Minimal Keycloak OIDC client supporting PKCE authorization code flow."""

    def __init__(
        self,
        server_url: str,
        realm: str,
        client_id: str,
        client_secret: Optional[str] = None,
    ):
        self.server_url = server_url.rstrip("/")
        self.realm = realm
        self.client_id = client_id
        self.client_secret = client_secret

        self.auth_url = f"{self.server_url}/realms/{self.realm}/protocol/openid/authorize"
        self.token_url = f"{self.server_url}/realms/{self.realm}/protocol/openid/token"
        self.introspection_url = f"{self.server_url}/realms/{self.realm}/protocol/openid/introspect"
        self.logout_url = f"{self.server_url}/realms/{self.realm}/protocol/openid/logout"

    def auth_url_params(
        self,
        redirect_uri: str,
        state: str,
        code_challenge: str,
        code_challenge_method: str = "S256",
    ) -> dict:
        """Build authorization request parameters."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": "openid profile email",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method,
        }
        return params

    def authorize_url(self, redirect_uri: str, state: str, code_challenge: str) -> str:
        """Build full Keycloak authorization URL."""
        params = self.auth_url_params(redirect_uri, state, code_challenge)
        query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        return f"{self.auth_url}?{query}"

    async def exchange_code_for_tokens(
        self,
        code: str,
        code_verifier: str,
        redirect_uri: str,
    ) -> Dict[str, Any]:
        """Exchange authorization code for tokens (PKCE flow)."""
        body = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        }
        if self.client_secret:
            body["client_secret"] = self.client_secret

        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.token_url, data=body)
            resp.raise_for_status()
            return resp.json()

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify introspect a token."""
        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.introspection_url,
                data={
                    "token": token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            if resp.status_code == 200:
                return resp.json()
            return None

    def logout_url(self, post_logout_redirect_uri: str, state: Optional[str] = None) -> str:
        """Build Keycloak logout URL."""
        params = {"post_logout_redirect_uri": post_logout_redirect_uri}
        if state:
            params["state"] = state
        query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        return f"{self.logout_url}?{query}"
