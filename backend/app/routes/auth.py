"""Authentication routes – Salesforce OAuth 2.0 Web Server Flow."""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse

from app.auth.salesforce import get_authorization_url, exchange_code_for_tokens
from app.auth.session import create_session, get_session, delete_session
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/login")
async def login():
    """Redirect the user to Salesforce for authorization."""
    url = get_authorization_url()
    return RedirectResponse(url)


@router.get("/callback")
async def callback(request: Request, code: str | None = None, error: str | None = None):
    """Handle the OAuth callback from Salesforce."""
    if error:
        return RedirectResponse(f"{settings.frontend_url}?error={error}")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    tokens = await exchange_code_for_tokens(code)

    session_id = create_session(
        {
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token"),
            "instance_url": tokens["instance_url"],
        }
    )

    response = RedirectResponse(settings.frontend_url)
    response.set_cookie(
        "session_id",
        session_id,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 8,  # 8 hours
    )
    return response


@router.get("/status")
async def auth_status(request: Request):
    """Check whether the current session is authenticated."""
    session_id = request.cookies.get("session_id")
    session = get_session(session_id) if session_id else None
    return {"authenticated": session is not None}


@router.post("/logout")
async def logout(request: Request):
    """Clear the session and remove the cookie."""
    session_id = request.cookies.get("session_id")
    if session_id:
        delete_session(session_id)
    response = RedirectResponse(settings.frontend_url)
    response.delete_cookie("session_id")
    return response
