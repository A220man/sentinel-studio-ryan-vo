"""PKCE (Proof Key for Code Exchange) utilities for OIDC authentication."""

from __future__ import annotations

import secrets
import base64
import urllib.parse
from typing import Tuple


def generate_code_verifier() -> str:
    """Generate a PKCE code verifier (43-128 characters, URL-safe)."""
    # 32 bytes -> base64url encoded = ~44 chars, within 43-128 range
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode("ascii")
    return verifier


def generate_code_challenge(verifier: str) -> str:
    """Generate a PKCE code challenge from the verifier using S256 method."""
    challenge = base64.urlsafe_b64encode(
        __import__("hashlib").sha256(verifier.encode("utf-8")).digest()
    ).rstrip(b"=").decode("ascii")
    return challenge


def verifier_from_url(encoded_params: dict) -> str | None:
    """Extract code_verifier from URL query parameters (for callback)."""
    return urllib.parse.parse_qs(encoded_params.get("query", "")).get("code_verifier", [None])[0]


def code_verifier_valid(stored: str, supplied: str) -> bool:
    """Constant-time comparison of code verifiers."""
    return secrets.compare_digest(stored, supplied)
