"""Salesforce REST API client with SOQL helpers for Opportunity data."""

from typing import Any

import httpx


class SalesforceClient:
    """Thin async wrapper around the Salesforce REST API."""

    API_VERSION = "v59.0"

    def __init__(self, instance_url: str, access_token: str):
        self.instance_url = instance_url
        self.access_token = access_token
        self.base_url = f"{instance_url}/services/data/{self.API_VERSION}"

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def query(self, soql: str) -> dict[str, Any]:
        """Execute a single SOQL query."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/query",
                params={"q": soql},
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    async def query_all(self, soql: str) -> list[dict]:
        """Execute a SOQL query and follow nextRecordsUrl for full results."""
        result = await self.query(soql)
        records = result.get("records", [])

        while not result.get("done", True):
            next_url = result["nextRecordsUrl"]
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.instance_url}{next_url}",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                result = resp.json()
                records.extend(result.get("records", []))

        return records

    # ------------------------------------------------------------------
    # Dashboard-specific queries
    # ------------------------------------------------------------------

    async def get_opportunity_stages(self) -> list[dict]:
        """Aggregate open opportunities by stage."""
        soql = (
            "SELECT StageName, COUNT(Id) cnt, SUM(Amount) total_amount "
            "FROM Opportunity "
            "WHERE IsClosed = false "
            "GROUP BY StageName "
            "ORDER BY StageName"
        )
        result = await self.query(soql)
        return result.get("records", [])

    async def get_pipeline_over_time(self, months: int = 12) -> list[dict]:
        """Monthly pipeline totals for the last N months."""
        soql = (
            "SELECT CALENDAR_MONTH(CloseDate) month, "
            "CALENDAR_YEAR(CloseDate) year, "
            "SUM(Amount) total, COUNT(Id) cnt "
            "FROM Opportunity "
            f"WHERE CloseDate = LAST_N_MONTHS:{months} "
            "GROUP BY CALENDAR_MONTH(CloseDate), CALENDAR_YEAR(CloseDate) "
            "ORDER BY CALENDAR_YEAR(CloseDate), CALENDAR_MONTH(CloseDate)"
        )
        result = await self.query(soql)
        return result.get("records", [])

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
        """Paginated, filterable opportunity list."""
        conditions = ["Amount != null"]
        if stage:
            conditions.append(f"StageName = '{stage}'")
        if owner_id:
            conditions.append(f"OwnerId = '{owner_id}'")
        if min_amount is not None:
            conditions.append(f"Amount >= {min_amount}")

        where = " AND ".join(conditions)

        # Total count
        count_result = await self.query(
            f"SELECT COUNT() FROM Opportunity WHERE {where}"
        )
        total = count_result.get("totalSize", 0)

        # Page of records
        soql = (
            "SELECT Id, Name, StageName, Amount, CloseDate, "
            "Probability, Owner.Name, Account.Name, Type, "
            "CreatedDate, LastModifiedDate "
            f"FROM Opportunity WHERE {where} "
            f"ORDER BY {sort_by} {sort_dir} "
            f"LIMIT {limit} OFFSET {offset}"
        )
        result = await self.query(soql)

        return {
            "records": result.get("records", []),
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    async def get_kpi_summary(self) -> dict:
        """Key metrics: open pipeline, won this quarter, lost this quarter."""
        soql_open = (
            "SELECT COUNT(Id) cnt, SUM(Amount) total, AVG(Amount) avg_amount "
            "FROM Opportunity "
            "WHERE IsClosed = false AND Amount != null"
        )
        soql_won = (
            "SELECT COUNT(Id) cnt, SUM(Amount) total "
            "FROM Opportunity "
            "WHERE IsWon = true AND Amount != null "
            "AND CloseDate = THIS_FISCAL_QUARTER"
        )
        soql_lost = (
            "SELECT COUNT(Id) cnt, SUM(Amount) total "
            "FROM Opportunity "
            "WHERE IsWon = false AND IsClosed = true AND Amount != null "
            "AND CloseDate = THIS_FISCAL_QUARTER"
        )

        open_result = await self.query(soql_open)
        won_result = await self.query(soql_won)
        lost_result = await self.query(soql_lost)

        def _extract(result: dict) -> dict:
            rec = result["records"][0] if result.get("records") else {}
            return rec

        open_rec = _extract(open_result)
        won_rec = _extract(won_result)
        lost_rec = _extract(lost_result)

        return {
            "open_pipeline": {
                "count": open_rec.get("cnt", 0),
                "total": open_rec.get("total", 0),
                "average": open_rec.get("avg_amount", 0),
            },
            "won_this_quarter": {
                "count": won_rec.get("cnt", 0),
                "total": won_rec.get("total", 0),
            },
            "lost_this_quarter": {
                "count": lost_rec.get("cnt", 0),
                "total": lost_rec.get("total", 0),
            },
        }
