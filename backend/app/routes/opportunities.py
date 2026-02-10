"""Opportunity list endpoint with filtering, sorting and pagination."""

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_sf_client
from app.services.salesforce import SalesforceClient

router = APIRouter()


@router.get("")
async def list_opportunities(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    stage: str | None = None,
    owner_id: str | None = None,
    min_amount: float | None = None,
    sort_by: str = "CloseDate",
    sort_dir: str = "DESC",
    sf: SalesforceClient = Depends(get_sf_client),
):
    """Return a paginated, filterable list of opportunities."""
    return await sf.get_opportunities(
        limit=limit,
        offset=offset,
        stage=stage,
        owner_id=owner_id,
        min_amount=min_amount,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
