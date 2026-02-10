"""Salesforce → Excel data extractor for Power BI.

Pulls Opportunity data from Salesforce via OAuth and exports
to Excel files that Power BI can consume directly.

Usage:
    1. Set environment variables (or .env file):
       SF_CLIENT_ID, SF_CLIENT_SECRET, SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN
    2. pip install -r requirements.txt
    3. python extract_salesforce_data.py
    4. Open the generated .xlsx files in Power BI Desktop
"""

import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from simple_salesforce import Salesforce
    import pandas as pd
    from dotenv import load_dotenv
except ImportError:
    print("Missing dependencies. Run:")
    print("  pip install simple-salesforce pandas openpyxl python-dotenv")
    sys.exit(1)

load_dotenv()

# ── Configuration ────────────────────────────────────────────────
OUTPUT_DIR = Path("powerbi/data")


def connect_to_salesforce() -> Salesforce:
    """Authenticate to Salesforce using username/password flow."""
    sf = Salesforce(
        username=os.environ["SF_USERNAME"],
        password=os.environ["SF_PASSWORD"],
        security_token=os.environ.get("SF_SECURITY_TOKEN", ""),
        client_id=os.environ.get("SF_CLIENT_ID", "PowerBI-Dashboard"),
        domain="login",  # Use 'test' for sandboxes
    )
    print(f"✓ Connected to Salesforce ({sf.sf_instance})")
    return sf


def query_to_dataframe(sf: Salesforce, soql: str) -> pd.DataFrame:
    """Execute SOQL and return as a clean DataFrame."""
    result = sf.query_all(soql)
    records = result["records"]
    # Flatten the Salesforce response
    rows = []
    for rec in records:
        row = {}
        for key, val in rec.items():
            if key == "attributes":
                continue
            if isinstance(val, dict):
                # Flatten nested lookups like Owner.Name, Account.Name
                for sub_key, sub_val in val.items():
                    if sub_key != "attributes":
                        row[f"{key}.{sub_key}"] = sub_val
            else:
                row[key] = val
        rows.append(row)
    return pd.DataFrame(rows)


def extract_opportunities(sf: Salesforce) -> pd.DataFrame:
    """Pull all opportunity records with key fields."""
    soql = """
    SELECT
        Id, Name, StageName, Amount, Probability,
        CloseDate, CreatedDate, LastModifiedDate,
        Type, LeadSource, ForecastCategory, ForecastCategoryName,
        IsWon, IsClosed, FiscalYear, FiscalQuarter,
        Owner.Name, Owner.Id,
        Account.Name, Account.Id, Account.Industry,
        Campaign.Name
    FROM Opportunity
    WHERE Amount != null
    ORDER BY CloseDate DESC
    """
    df = query_to_dataframe(sf, soql)

    # Type conversions
    if "CloseDate" in df.columns:
        df["CloseDate"] = pd.to_datetime(df["CloseDate"])
    if "CreatedDate" in df.columns:
        df["CreatedDate"] = pd.to_datetime(df["CreatedDate"])
    if "LastModifiedDate" in df.columns:
        df["LastModifiedDate"] = pd.to_datetime(df["LastModifiedDate"])
    if "Amount" in df.columns:
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    if "Probability" in df.columns:
        df["Probability"] = pd.to_numeric(df["Probability"], errors="coerce")

    print(f"  Opportunities: {len(df)} records")
    return df


def extract_accounts(sf: Salesforce) -> pd.DataFrame:
    """Pull account dimension table."""
    soql = """
    SELECT
        Id, Name, Industry, Type, BillingState, BillingCountry,
        AnnualRevenue, NumberOfEmployees, OwnerId
    FROM Account
    WHERE Id IN (SELECT AccountId FROM Opportunity WHERE Amount != null)
    """
    df = query_to_dataframe(sf, soql)
    print(f"  Accounts: {len(df)} records")
    return df


def extract_users(sf: Salesforce) -> pd.DataFrame:
    """Pull user/owner dimension table."""
    soql = """
    SELECT
        Id, Name, Email, Title, Department, UserRole.Name
    FROM User
    WHERE Id IN (SELECT OwnerId FROM Opportunity WHERE Amount != null)
    """
    df = query_to_dataframe(sf, soql)
    print(f"  Users: {len(df)} records")
    return df


def create_date_table(df_opp: pd.DataFrame) -> pd.DataFrame:
    """Generate a date dimension table from opportunity date range."""
    if df_opp.empty or "CloseDate" not in df_opp.columns:
        return pd.DataFrame()

    min_date = df_opp["CloseDate"].min()
    max_date = max(df_opp["CloseDate"].max(), pd.Timestamp.now())

    dates = pd.date_range(start=min_date - pd.offsets.YearBegin(), end=max_date + pd.offsets.YearEnd(), freq="D")
    date_df = pd.DataFrame({"Date": dates})
    date_df["Year"] = date_df["Date"].dt.year
    date_df["Quarter"] = date_df["Date"].dt.quarter
    date_df["QuarterLabel"] = "Q" + date_df["Quarter"].astype(str) + " " + date_df["Year"].astype(str)
    date_df["Month"] = date_df["Date"].dt.month
    date_df["MonthName"] = date_df["Date"].dt.strftime("%b")
    date_df["MonthYear"] = date_df["Date"].dt.strftime("%b %Y")
    date_df["WeekOfYear"] = date_df["Date"].dt.isocalendar().week.astype(int)
    date_df["DayOfWeek"] = date_df["Date"].dt.day_name()
    date_df["IsCurrentQuarter"] = (
        (date_df["Year"] == datetime.now().year) & (date_df["Quarter"] == (datetime.now().month - 1) // 3 + 1)
    )
    print(f"  Date table: {len(date_df)} rows ({date_df['Year'].min()}-{date_df['Year'].max()})")
    return date_df


def main():
    """Extract all data and write to Excel."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Connecting to Salesforce...")
    sf = connect_to_salesforce()

    print("\nExtracting data...")
    df_opp = extract_opportunities(sf)
    df_accounts = extract_accounts(sf)
    df_users = extract_users(sf)
    df_dates = create_date_table(df_opp)

    # Write to Excel
    output_file = OUTPUT_DIR / "salesforce_opportunity_data.xlsx"
    print(f"\nWriting to {output_file}...")
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df_opp.to_excel(writer, sheet_name="Opportunities", index=False)
        df_accounts.to_excel(writer, sheet_name="Accounts", index=False)
        df_users.to_excel(writer, sheet_name="Users", index=False)
        df_dates.to_excel(writer, sheet_name="DateTable", index=False)

    print(f"\n✓ Done! Open '{output_file}' in Power BI Desktop.")
    print("  → Get Data → Excel Workbook → select all 4 sheets")


if __name__ == "__main__":
    main()
