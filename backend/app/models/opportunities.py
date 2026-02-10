"""Pydantic models for Opportunity-related data."""

from datetime import date
from typing import Optional

from pydantic import BaseModel


class OpportunityRecord(BaseModel):
    id: str
    name: str
    stage_name: str
    amount: Optional[float] = None
    close_date: Optional[date] = None
    probability: Optional[float] = None
    owner_name: Optional[str] = None
    account_name: Optional[str] = None
    type: Optional[str] = None


class OpportunityListResponse(BaseModel):
    records: list[OpportunityRecord]
    total: int
    limit: int
    offset: int


class KPIMetric(BaseModel):
    count: int
    total: float


class KPISummaryWithAvg(KPIMetric):
    average: float = 0


class KPISummary(BaseModel):
    open_pipeline: KPISummaryWithAvg
    won_this_quarter: KPIMetric
    lost_this_quarter: KPIMetric


class StageBreakdown(BaseModel):
    stage_name: str
    count: int
    total_amount: float


class PipelineDataPoint(BaseModel):
    month: int
    year: int
    total: float
    count: int
