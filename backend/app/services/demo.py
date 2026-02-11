"""Demo data service — serves sample data when no Salesforce credentials are configured.

Reads from backend/demo_data.xlsx and returns the same response shapes
as SalesforceClient, so the frontend works identically.
"""

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

_DATA_FILE = Path(__file__).resolve().parent.parent.parent / "demo_data.xlsx"

# Cache the DataFrame in memory on first load
_df: pd.DataFrame | None = None


def _load() -> pd.DataFrame:
    global _df
    if _df is None:
        _df = pd.read_excel(_DATA_FILE, sheet_name="Opportunities")
        # Normalize column names (flatten dot notation from sample generator)
        rename = {
            "Owner.Name": "OwnerName",
            "Owner.Id": "OwnerId",
            "Account.Name": "AccountName",
            "Account.Id": "AccountId",
            "Account.Industry": "AccountIndustry",
            "Campaign.Name": "CampaignName",
        }
        _df = _df.rename(columns={k: v for k, v in rename.items() if k in _df.columns})
        _df["CloseDate"] = pd.to_datetime(_df["CloseDate"])
        _df["CreatedDate"] = pd.to_datetime(_df["CreatedDate"])
    return _df


class DemoClient:
    """Drop-in replacement for SalesforceClient that serves sample data."""

    async def get_kpi_summary(self) -> dict:
        df = _load()
        open_df = df[df["IsClosed"] == False]  # noqa: E712
        now = datetime.now()
        q_start = datetime(now.year, (now.month - 1) // 3 * 3 + 1, 1)
        q_end = q_start + timedelta(days=92)
        won_df = df[(df["IsWon"] == True) & (df["CloseDate"] >= q_start) & (df["CloseDate"] < q_end)]  # noqa: E712
        lost_df = df[
            (df["IsClosed"] == True) & (df["IsWon"] == False)  # noqa: E712
            & (df["CloseDate"] >= q_start) & (df["CloseDate"] < q_end)
        ]

        return {
            "open_pipeline": {
                "count": int(len(open_df)),
                "total": float(open_df["Amount"].sum()),
                "average": float(open_df["Amount"].mean()) if len(open_df) else 0,
            },
            "won_this_quarter": {
                "count": int(len(won_df)),
                "total": float(won_df["Amount"].sum()),
            },
            "lost_this_quarter": {
                "count": int(len(lost_df)),
                "total": float(lost_df["Amount"].sum()),
            },
        }

    async def get_opportunity_stages(self) -> list[dict]:
        df = _load()
        open_df = df[df["IsClosed"] == False]  # noqa: E712
        grouped = open_df.groupby("StageName").agg(
            cnt=("Id", "count"),
            total_amount=("Amount", "sum"),
        ).reset_index()
        grouped = grouped.sort_values("StageName")
        return [
            {"StageName": row["StageName"], "cnt": int(row["cnt"]), "total_amount": float(row["total_amount"])}
            for _, row in grouped.iterrows()
        ]

    async def get_pipeline_over_time(self, months: int = 12) -> list[dict]:
        df = _load()
        cutoff = datetime.now() - timedelta(days=months * 30)
        recent = df[df["CloseDate"] >= cutoff].copy()
        recent["month"] = recent["CloseDate"].dt.month
        recent["year"] = recent["CloseDate"].dt.year
        grouped = recent.groupby(["year", "month"]).agg(
            total=("Amount", "sum"),
            cnt=("Id", "count"),
        ).reset_index().sort_values(["year", "month"])
        return [
            {"month": int(row["month"]), "year": int(row["year"]),
             "total": float(row["total"]), "cnt": int(row["cnt"])}
            for _, row in grouped.iterrows()
        ]

    async def get_opportunities(
        self,
        limit: int = 50,
        offset: int = 0,
        stage: str | None = None,
        owner_id: str | None = None,
        min_amount: float | None = None,
        sort_by: str = "CloseDate",
        sort_dir: str = "DESC",
    ) -> dict:
        df = _load()
        filtered = df[df["Amount"].notna()].copy()

        if stage:
            filtered = filtered[filtered["StageName"] == stage]
        if owner_id:
            col = "OwnerId" if "OwnerId" in filtered.columns else "Owner.Id"
            filtered = filtered[filtered[col] == owner_id]
        if min_amount is not None:
            filtered = filtered[filtered["Amount"] >= min_amount]

        # Map frontend sort column names to DataFrame columns
        col_map = {
            "CloseDate": "CloseDate",
            "Amount": "Amount",
            "Name": "Name",
            "StageName": "StageName",
            "Owner.Name": "OwnerName",
            "Account.Name": "AccountName",
        }
        sort_col = col_map.get(sort_by, sort_by)
        if sort_col in filtered.columns:
            filtered = filtered.sort_values(sort_col, ascending=(sort_dir.upper() == "ASC"))

        total = len(filtered)
        page = filtered.iloc[offset: offset + limit]

        records = []
        for _, row in page.iterrows():
            records.append({
                "Id": row.get("Id", ""),
                "Name": row.get("Name", ""),
                "StageName": row.get("StageName", ""),
                "Amount": float(row["Amount"]) if pd.notna(row["Amount"]) else 0,
                "CloseDate": row["CloseDate"].isoformat() if pd.notna(row["CloseDate"]) else "",
                "Probability": float(row.get("Probability", 0)),
                "Owner": {"Name": row.get("OwnerName", "")},
                "Account": {"Name": row.get("AccountName", "")},
                "Type": row.get("Type", ""),
                "CreatedDate": row["CreatedDate"].isoformat() if pd.notna(row.get("CreatedDate")) else "",
                "ProductName": row.get("ProductName", ""),
                "ProductFamily": row.get("ProductFamily", ""),
                "OpportunityID": row.get("OpportunityID", ""),
            })

        return {
            "records": records,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
