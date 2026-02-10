from fastapi import Request, HTTPException

from app.auth.session import get_session
from app.services.salesforce import SalesforceClient


async def get_sf_client(request: Request) -> SalesforceClient:
    """FastAPI dependency that extracts the Salesforce client from the session."""
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated – please log in")

    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Session expired – please log in again")

    return SalesforceClient(
        instance_url=session["instance_url"],
        access_token=session["access_token"],
    )
