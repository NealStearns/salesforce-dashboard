"""Salesforce OAuth 2.0 Web Server Flow helpers."""

import httpx
from urllib.parse import urlencode

from app.config import get_settings

settings = get_settings()

AUTHORIZE_URL = f"{settings.sf_login_url}/services/oauth2/authorize"
TOKEN_URL = f"{settings.sf_login_url}/services/oauth2/token"


def get_authorization_url(state: str = "") -> str:
    """Build the Salesforce OAuth authorization URL."""
    params = {
        "response_type": "code",
        "client_id": settings.sf_client_id,
        "redirect_uri": settings.sf_redirect_uri,
        "scope": "api refresh_token",
        "state": state,
    }
    return f"{AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_code_for_tokens(code: str) -> dict:
    """Exchange an authorization code for access + refresh tokens."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": settings.sf_client_id,
                "client_secret": settings.sf_client_secret,
                "redirect_uri": settings.sf_redirect_uri,
                "code": code,
            },
        )
        resp.raise_for_status()
        return resp.json()


async def refresh_access_token(refresh_token: str) -> dict:
    """Use a refresh token to obtain a new access token."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "client_id": settings.sf_client_id,
                "client_secret": settings.sf_client_secret,
                "refresh_token": refresh_token,
            },
        )
        resp.raise_for_status()
        return resp.json()
