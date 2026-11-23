"""Auth API endpoints for OIDC/Keycloak Authentication with PKCE."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response, HTTPException, status, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from typing import Optional, Dict, Any

from app.core.config import get_settings, Settings
from app.core.pkce import generate_code_verifier, generate_code_challenge
from app.services.auth import KeycloakClient

router = APIRouter(prefix="/auth", tags=["auth"])

# Initialize Keycloak client from settings
settings: Settings = get_settings()
_keycloak: Optional[KeycloakClient] = None


def get_keycloak() -> Optional[KeycloakClient]:
    """Get Keycloak client if configured, otherwise None."""
    global _keycloak
    if _keycloak is None and settings.KEYCLOAK_SERVER_URL:
        _keycloak = KeycloakClient(
            server_url=settings.KEYCLOAK_SERVER_URL,
            realm=settings.KEYCLOAK_REALM or "sentinel-studio",
            client_id=settings.KEYCLOAK_CLIENT_ID or "sentinel-frontend",
            client_secret=settings.KEYCLOAK_CLIENT_SECRET,
        )
    return _keycloak


@router.get("/login")
async def login(
    request: Request,
    response: Response,
    keycloak: Optional[KeycloakClient] = Depends(get_keycloak),
) -> dict:
    """Initiate OIDC authorization code flow with PKCE.

    Generates PKCE code verifier/challenge, stores verifier in
    HttpOnly cookie, and redirects to Keycloak authorization server.
    If Keycloak is not configured, returns authorization URL structure
    for manual configuration.
    """
    # Generate PKCE parameters
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    # Store code verifier in HttpOnly cookie for callback
    # 1-year expiry
    max_age = 365 * 24 * 60 * 60
    response.set_cookie(
        key="pkce_code_verifier",
        value=code_verifier,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=max_age,
        path="/auth/callback",
    )

    # Build authorization URL with PKCE
    redirect_uri = f"{settings.server_url}/auth/callback"

    if keycloak:
        # Use Keycloak to build full authorization URL
        state = (
            request.cookies.get("auth_state")
            or __import__("base64").urlsafe_b64encode(
                __import__("secrets").token_bytes(16)
            ).rstrip(b"=").decode("ascii")
        )
        auth_url = keycloak.authorize_url(redirect_uri, state, code_challenge)
        return {
            "authorization_url": auth_url,
            "state": state,
            "code_challenge": code_challenge,
        }
    else:
        # Keycloak not configured - return PKCE params for manual setup
        state = __import__("base64").urlsafe_b64encode(
            __import__("secrets").token_bytes(16)
        ).rstrip(b"=").decode("ascii")
        # Construct a minimal authorization URL without Keycloak
        auth_url = f"{redirect_uri}?response_type=code&client_id=sentinel-frontend&state={state}&code_challenge={code_challenge}&code_challenge_method=S256&scope=openid%20profile%20email"
        return {
            "authorization_url": auth_url,
            "state": state,
            "code_challenge": code_challenge,
            "note": "Keycloak not configured - PKCE parameters generated for manual setup"
        }


@router.get("/callback")
async def auth_callback(
    request: Request,
    response: Response,
    keycloak: Optional[KeycloakClient] = Depends(get_keycloak),
) -> dict:
    """Handle Keycloak callback with authorization code and PKCE verification.

    Exchanges the authorization code for tokens, verifies PKCE,
    sets session cookies, and redirects to frontend.
    """
    # Get authorization code from query
    code = request.query_params.get("code")
    # Get PKCE code verifier from cookie
    stored_verifier = request.cookies.get("pkce_code_verifier")
    # Get state from query
    state = request.query_params.get("state", "")

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code",
        )

    if not stored_verifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing PKCE code verifier",
        )

    # Verify PKCE code verifier
    code_verifier = stored_verifier

    # Exchange code for tokens
    redirect_uri = f"{settings.server_url}/auth/callback"

    if keycloak:
        try:
            token_data = await keycloak.exchange_code_for_tokens(
                code=code,
                code_verifier=code_verifier,
                redirect_uri=redirect_uri,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token exchange failed: {str(e)}",
            )
    else:
        # Mock token data when Keycloak not configured
        token_data = {
            "access_token": "mock-access-token",
            "refresh_token": "mock-refresh-token",
            "id_token": "mock-id-token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    # Set HttpOnly cookies for tokens (shorter lifespan)
    access_token = token_data.get("access_token", "")
    refresh_token = token_data.get("refresh_token", "")

    access_max_age = 3600  # 1 hour
    refresh_max_age = 604800  # 7 days

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=access_max_age,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=refresh_max_age,
        path="/",
    )

    # Set user info cookies
    if "id_token" in token_data:
        id_token = token_data["id_token"]
        response.set_cookie(
            key="id_token",
            value=id_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=access_max_age,
            path="/",
        )

    return {
        "message": "Authentication successful",
        "expires_in": access_max_age,
        "tokens_set": ["access_token", "refresh_token"],
    }


@router.post("/refresh")
async def refresh_tokens(
    request: Request,
    response: Response,
    keycloak: Optional[KeycloakClient] = Depends(get_keycloak),
) -> dict:
    """Refresh access token using refresh token."""
    import httpx

    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )

    # If Keycloak is configured, use it; otherwise use mock token exchange
    if keycloak:
        body = {
            "grant_type": "refresh_token",
            "client_id": keycloak.client_id,
            "refresh_token": refresh_token,
        }
        if keycloak.client_secret:
            body["client_secret"] = keycloak.client_secret

        async with httpx.AsyncClient() as client:
            resp = await client.post(keycloak.token_url, data=body)
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token refresh failed",
                )
            token_data = resp.json()
    else:
        # Mock refresh when Keycloak not configured
        token_data = {
            "access_token": "new-mock-access-token",
            "refresh_token": "new-mock-refresh-token",
        }

    # Rotate refresh token
    new_refresh = token_data.get("refresh_token", refresh_token)

    access_max_age = 3600
    refresh_max_age = 604800

    response.set_cookie(
        key="access_token",
        value=token_data.get("access_token", ""),
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=access_max_age,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=refresh_max_age,
        path="/",
    )

    return {
        "message": "Tokens refreshed",
        "expires_in": access_max_age,
    }


@router.post("/logout")
async def logout(
    response: Response,
    keycloak: Optional[KeycloakClient] = Depends(get_keycloak),
) -> dict:
    """Logout and clear authentication cookies."""
    # Clear all auth cookies
    cookie_names = ["access_token", "refresh_token", "id_token", "pkce_code_verifier", "auth_state"]

    for name in cookie_names:
        response.delete_cookie(
            key=name,
            path="/",
            secure=not settings.DEBUG,
            samesite="lax",
        )

    # Redirect to Keycloak logout if configured
    if keycloak:
        post_logout = (
            settings.server_url.rstrip("/") + "/frontchannel"
            if settings.server_url
            else "http://localhost:5173"
        )
        logout_url = keycloak.logout_url(post_logout)
    else:
        logout_url = "http://localhost:5173"

    return {
        "message": "Logged out",
        "logout_url": logout_url,
    }


@router.get("/me")
async def me() -> dict:
    """Get current user info from ID token claims (stub)."""
    # In production, decode and validate the id_token
    return {
        "authenticated": True,
        "userinfo": {
            "sub": "unknown",
            "email": "unknown",
            "name": "Unknown User",
            "roles": ["viewer"],
        },
    }
