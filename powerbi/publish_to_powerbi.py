"""Push Salesforce dashboard dataset to Power BI Service (app.powerbi.com).

This script:
  1. Authenticates to Power BI via Microsoft device-code flow
  2. Creates a push dataset with pre-defined measures
  3. Uploads all rows from the Excel sample data
  4. Prints the URL to build visuals on the web

Usage:
    python publish_to_powerbi.py
"""

import json
import math
import sys
import time

import pandas as pd
import requests
from msal import PublicClientApplication

# ── Azure AD / Power BI constants ──────────────────────────────
# "Microsoft Power BI" first-party public client
CLIENT_ID = "ea0616ba-638b-4df5-95b9-636659ae5121"
AUTHORITY = "https://login.microsoftonline.com/organizations"
SCOPES = ["https://analysis.windows.net/powerbi/api/.default"]
PBI_BASE = "https://api.powerbi.com/v1.0/myorg"

DATA_FILE = "data/salesforce_opportunity_data.xlsx"


# ── Authentication ─────────────────────────────────────────────
def authenticate() -> str:
    """Authenticate via device-code flow and return an access token."""
    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)

    # Try cached token first
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            print("✓ Authenticated (cached token)")
            return result["access_token"]

    # Device code flow
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        print(f"Error: {flow.get('error_description', 'Unknown error')}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  To sign in, open: {flow['verification_uri']}")
    print(f"  Enter code:       {flow['user_code']}")
    print(f"{'='*60}\n")

    result = app.acquire_token_by_device_flow(flow)
    if "access_token" not in result:
        print(f"Authentication failed: {result.get('error_description')}")
        sys.exit(1)

    print(f"✓ Authenticated as {result.get('id_token_claims', {}).get('preferred_username', 'user')}")
    return result["access_token"]


def pbi_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ── Dataset Definition ─────────────────────────────────────────
def build_dataset_definition() -> dict:
    """Define the push dataset schema with tables and DAX measures."""
    return {
        "name": "Salesforce Opportunity Dashboard",
        "defaultMode": "Push",
        "tables": [
            {
                "name": "Opportunities",
                "columns": [
                    {"name": "Id", "dataType": "String"},
                    {"name": "Name", "dataType": "String"},
                    {"name": "StageName", "dataType": "String"},
                    {"name": "Amount", "dataType": "Double"},
                    {"name": "Probability", "dataType": "Double"},
                    {"name": "CloseDate", "dataType": "DateTime"},
                    {"name": "CreatedDate", "dataType": "DateTime"},
                    {"name": "Type", "dataType": "String"},
                    {"name": "LeadSource", "dataType": "String"},
                    {"name": "ForecastCategory", "dataType": "String"},
                    {"name": "IsWon", "dataType": "Boolean"},
                    {"name": "IsClosed", "dataType": "Boolean"},
                    {"name": "FiscalYear", "dataType": "Int64"},
                    {"name": "FiscalQuarter", "dataType": "Int64"},
                    {"name": "OwnerName", "dataType": "String"},
                    {"name": "AccountName", "dataType": "String"},
                    {"name": "AccountIndustry", "dataType": "String"},
                    {"name": "CampaignName", "dataType": "String"},
                    {"name": "ProductName", "dataType": "String"},
                    {"name": "ProductFamily", "dataType": "String"},
                    {"name": "OpportunityID", "dataType": "String"},
                ],
                "measures": [
                    {
                        "name": "Total Pipeline",
                        "expression": "CALCULATE(SUM(Opportunities[Amount]), Opportunities[IsClosed] = FALSE)",
                        "formatString": "$#,##0",
                    },
                    {
                        "name": "Closed Won Revenue",
                        "expression": "CALCULATE(SUM(Opportunities[Amount]), Opportunities[IsWon] = TRUE)",
                        "formatString": "$#,##0",
                    },
                    {
                        "name": "Closed Lost Amount",
                        "expression": "CALCULATE(SUM(Opportunities[Amount]), Opportunities[IsClosed] = TRUE, Opportunities[IsWon] = FALSE)",
                        "formatString": "$#,##0",
                    },
                    {
                        "name": "Win Rate",
                        "expression": "VAR _won = CALCULATE(COUNTROWS(Opportunities), Opportunities[IsWon] = TRUE) VAR _closed = CALCULATE(COUNTROWS(Opportunities), Opportunities[IsClosed] = TRUE) RETURN IF(_closed > 0, DIVIDE(_won, _closed), BLANK())",
                        "formatString": "0.0%",
                    },
                    {
                        "name": "Avg Deal Size",
                        "expression": "AVERAGE(Opportunities[Amount])",
                        "formatString": "$#,##0",
                    },
                    {
                        "name": "Opportunity Count",
                        "expression": "COUNTROWS(Opportunities)",
                        "formatString": "#,##0",
                    },
                    {
                        "name": "Weighted Pipeline",
                        "expression": "CALCULATE(SUMX(Opportunities, Opportunities[Amount] * Opportunities[Probability] / 100), Opportunities[IsClosed] = FALSE)",
                        "formatString": "$#,##0",
                    },
                    {
                        "name": "Avg Days to Close",
                        "expression": "CALCULATE(AVERAGEX(Opportunities, DATEDIFF(Opportunities[CreatedDate], Opportunities[CloseDate], DAY)), Opportunities[IsClosed] = TRUE)",
                        "formatString": "#,##0",
                    },
                ],
            },
        ],
    }


# ── Push Data ──────────────────────────────────────────────────
def push_rows(token: str, dataset_id: str, table_name: str, df: pd.DataFrame):
    """Push DataFrame rows to a Power BI push dataset (max 10K rows per call)."""
    url = f"{PBI_BASE}/datasets/{dataset_id}/tables/{table_name}/rows"
    batch_size = 10_000
    total = len(df)

    for start in range(0, total, batch_size):
        batch = df.iloc[start : start + batch_size]
        rows = json.loads(batch.to_json(orient="records", date_format="iso"))
        resp = requests.post(url, headers=pbi_headers(token), json={"rows": rows})
        if resp.status_code not in (200, 201):
            print(f"  ✗ Error pushing rows {start}-{start+len(batch)}: {resp.status_code} {resp.text}")
            return False
        print(f"  ✓ Pushed rows {start+1}-{start+len(batch)} of {total}")
        time.sleep(0.5)  # Rate limit courtesy

    return True


def main():
    # 1. Authenticate
    print("Step 1: Authenticating to Power BI...\n")
    token = authenticate()

    # 2. Read sample data
    print("\nStep 2: Reading sample data...")
    df = pd.read_excel(DATA_FILE, sheet_name="Opportunities")

    # Flatten column names (Owner.Name → OwnerName, etc.)
    rename_map = {
        "Owner.Name": "OwnerName",
        "Owner.Id": "OwnerId",
        "Account.Name": "AccountName",
        "Account.Id": "AccountId",
        "Account.Industry": "AccountIndustry",
        "Campaign.Name": "CampaignName",
    }
    df = df.rename(columns=rename_map)

    # Drop columns not in our schema before selecting
    drop_cols = ["LastModifiedDate", "ForecastCategoryName", "OwnerId", "AccountId"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")

    # Keep only columns in our schema
    keep_cols = [
        "Id", "Name", "StageName", "Amount", "Probability",
        "CloseDate", "CreatedDate", "Type", "LeadSource",
        "ForecastCategory", "IsWon", "IsClosed",
        "FiscalYear", "FiscalQuarter",
        "OwnerName", "AccountName", "AccountIndustry", "CampaignName",
        "ProductName", "ProductFamily", "OpportunityID",
    ]
    df = df[[c for c in keep_cols if c in df.columns]]

    # Clean NaN values for JSON serialization
    df = df.fillna({"CampaignName": "", "AccountIndustry": "", "Type": "", "LeadSource": "", "ProductName": "", "ProductFamily": "", "OpportunityID": ""})
    # Replace remaining NaN/NaT with None for clean JSON
    df = df.where(df.notna(), None)

    print(f"  {len(df)} opportunities ready to push")

    # 3. Create push dataset
    print("\nStep 3: Creating dataset on Power BI Service...")
    dataset_def = build_dataset_definition()
    resp = requests.post(
        f"{PBI_BASE}/datasets",
        headers=pbi_headers(token),
        json=dataset_def,
    )
    if resp.status_code not in (200, 201, 202):
        print(f"  ✗ Failed to create dataset: {resp.status_code} {resp.text}")
        sys.exit(1)

    dataset_id = resp.json()["id"]
    print(f"  ✓ Dataset created: {dataset_id}")

    # 4. Push data rows
    print("\nStep 4: Pushing opportunity data...")
    success = push_rows(token, dataset_id, "Opportunities", df)

    if success:
        report_url = f"https://app.powerbi.com/groups/me/datasets/{dataset_id}"
        print(f"\n{'='*60}")
        print(f"  ✓ DONE! Dataset is live on Power BI Service")
        print(f"")
        print(f"  Dataset: {report_url}")
        print(f"")
        print(f"  Next steps:")
        print(f"  1. Go to: https://app.powerbi.com")
        print(f"  2. Find 'Salesforce Opportunity Dashboard' in My Workspace")
        print(f"  3. Click '+ Create a report' → 'From scratch'")
        print(f"  4. All measures (Total Pipeline, Win Rate, etc.) are pre-loaded!")
        print(f"  5. Just drag fields onto the canvas to build visuals")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
