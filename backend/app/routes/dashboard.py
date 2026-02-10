"""Dashboard aggregate data endpoints."""

from fastapi import APIRouter, Depends

from app.dependencies import get_sf_client
from app.services.salesforce import SalesforceClient

router = APIRouter()


@router.get("/kpis")
async def get_kpis(sf: SalesforceClient = Depends(get_sf_client)):
    """Return KPI summary: open pipeline, won/lost this quarter."""
    return await sf.get_kpi_summary()


@router.get("/stages")
async def get_stages(sf: SalesforceClient = Depends(get_sf_client)):
    """Return opportunity counts and amounts grouped by stage."""
    stages = await sf.get_opportunity_stages()
    return {"stages": stages}


@router.get("/pipeline")
async def get_pipeline(
    months: int = 12, sf: SalesforceClient = Depends(get_sf_client)
):
    """Return monthly pipeline totals for the last N months."""
    data = await sf.get_pipeline_over_time(months)
    return {"pipeline": data}
