"""Generate realistic sample data for Power BI dashboard development.

Run this if you don't have Salesforce credentials yet but want to
build and test the Power BI dashboard with realistic data.

Usage:
    pip install pandas openpyxl
    python generate_sample_data.py
"""

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import numpy as np

OUTPUT_DIR = Path("data")
NUM_OPPORTUNITIES = 500
NUM_ACCOUNTS = 80
NUM_USERS = 15

# ── Seed data ────────────────────────────────────────────────────
STAGES = [
    ("Prospecting", 10),
    ("Qualification", 20),
    ("Needs Analysis", 40),
    ("Value Proposition", 50),
    ("Id. Decision Makers", 60),
    ("Perception Analysis", 70),
    ("Proposal/Price Quote", 75),
    ("Negotiation/Review", 90),
    ("Closed Won", 100),
    ("Closed Lost", 0),
]

FORECAST_MAP = {
    "Prospecting": "Pipeline",
    "Qualification": "Pipeline",
    "Needs Analysis": "Best Case",
    "Value Proposition": "Best Case",
    "Id. Decision Makers": "Best Case",
    "Perception Analysis": "Commit",
    "Proposal/Price Quote": "Commit",
    "Negotiation/Review": "Commit",
    "Closed Won": "Closed",
    "Closed Lost": "Omitted",
}

INDUSTRIES = [
    "Technology", "Healthcare", "Financial Services", "Manufacturing",
    "Retail", "Energy", "Telecommunications", "Education",
    "Government", "Media & Entertainment",
]

LEAD_SOURCES = [
    "Web", "Partner Referral", "Phone Inquiry", "Trade Show",
    "Employee Referral", "Purchased List", "Other",
]

TYPES = ["New Customer", "Existing Customer - Upgrade", "Existing Customer - Replacement", "Existing Customer - Downgrade"]

PRODUCTS = {
    "Compute": ["ProLiant DL380", "ProLiant DL360", "Synergy 480", "Edgeline EL8000", "Apollo 6500"],
    "Storage": ["Alletra 9000", "Alletra 6000", "StoreOnce 6600", "MSA 2060", "Nimble HF60"],
    "Networking": ["Aruba CX 8360", "Aruba CX 6300", "Aruba AP-635", "Aruba 2930F", "Aruba SD-WAN"],
    "Software": ["GreenLake Platform", "OneView", "InfoSight", "Zerto", "Data Services Cloud Console"],
    "Services": ["Pointnext Advisory", "Pointnext Operational", "GreenLake Managed", "Financial Services", "Education Services"],
}

FIRST_NAMES = ["Sarah", "James", "Maria", "David", "Jennifer", "Michael", "Lisa", "Robert", "Emily", "William", "Jessica", "Daniel", "Ashley", "Chris", "Amanda"]
LAST_NAMES = ["Johnson", "Smith", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore"]

COMPANY_PREFIXES = ["Acme", "Global", "Summit", "Atlas", "Nexus", "Pinnacle", "Vertex", "Horizon", "Catalyst", "Quantum"]
COMPANY_SUFFIXES = ["Corp", "Inc", "Systems", "Solutions", "Group", "Technologies", "Enterprises", "Partners", "Industries", "Labs"]

STATES = ["CA", "TX", "NY", "FL", "IL", "PA", "OH", "GA", "NC", "MI", "WA", "CO", "MA", "VA", "AZ"]
DEPARTMENTS = ["Sales", "Sales", "Sales", "Business Development", "Account Management"]
ROLES = ["Sales Rep", "Sr. Sales Rep", "Account Executive", "Sr. Account Executive", "Sales Manager"]

random.seed(42)
np.random.seed(42)


def generate_users() -> pd.DataFrame:
    users = []
    for i in range(NUM_USERS):
        users.append({
            "Id": f"005{i:012d}",
            "Name": f"{FIRST_NAMES[i]} {LAST_NAMES[i]}",
            "Email": f"{FIRST_NAMES[i].lower()}.{LAST_NAMES[i].lower()}@example.com",
            "Title": random.choice(ROLES),
            "Department": random.choice(DEPARTMENTS),
            "UserRole.Name": random.choice(ROLES),
        })
    return pd.DataFrame(users)


def generate_accounts() -> pd.DataFrame:
    accounts = []
    used_names = set()
    for i in range(NUM_ACCOUNTS):
        while True:
            name = f"{random.choice(COMPANY_PREFIXES)} {random.choice(COMPANY_SUFFIXES)}"
            if name not in used_names:
                used_names.add(name)
                break
        accounts.append({
            "Id": f"001{i:012d}",
            "Name": name,
            "Industry": random.choice(INDUSTRIES),
            "Type": random.choice(["Customer", "Prospect", "Partner"]),
            "BillingState": random.choice(STATES),
            "BillingCountry": "United States",
            "AnnualRevenue": round(random.uniform(1_000_000, 500_000_000), -3),
            "NumberOfEmployees": random.choice([50, 100, 250, 500, 1000, 2500, 5000, 10000]),
            "OwnerId": f"005{random.randint(0, NUM_USERS - 1):012d}",
        })
    return pd.DataFrame(accounts)


def generate_opportunities(df_accounts: pd.DataFrame, df_users: pd.DataFrame) -> pd.DataFrame:
    opps = []
    now = datetime.now()
    account_ids = df_accounts["Id"].tolist()
    account_names = dict(zip(df_accounts["Id"], df_accounts["Name"]))
    account_industries = dict(zip(df_accounts["Id"], df_accounts["Industry"]))
    user_ids = df_users["Id"].tolist()
    user_names = dict(zip(df_users["Id"], df_users["Name"]))

    for i in range(NUM_OPPORTUNITIES):
        stage_name, probability = random.choice(STAGES)
        is_closed = stage_name in ("Closed Won", "Closed Lost")
        is_won = stage_name == "Closed Won"

        # Dates: spread over last 18 months
        created = now - timedelta(days=random.randint(30, 540))
        if is_closed:
            close_date = created + timedelta(days=random.randint(14, 180))
        else:
            close_date = now + timedelta(days=random.randint(-30, 180))

        # Amount: log-normal distribution centered around $50K
        amount = round(np.random.lognormal(mean=10.8, sigma=1.2), -2)
        amount = max(1000, min(amount, 5_000_000))  # Clip extremes

        account_id = random.choice(account_ids)
        owner_id = random.choice(user_ids)
        fiscal_quarter = (close_date.month - 1) // 3 + 1

        opp_name_prefix = random.choice(["Expansion", "Renewal", "New Deal", "Upgrade", "Implementation", "Migration", "Platform"])
        opp_name = f"{account_names[account_id]} - {opp_name_prefix}"

        # Product assignment
        product_family = random.choice(list(PRODUCTS.keys()))
        product_name = random.choice(PRODUCTS[product_family])

        # Custom Opportunity ID (auto-number style)
        opportunity_id = f"OPP-{i + 1:05d}"

        opps.append({
            "Id": f"006{i:012d}",
            "Name": opp_name,
            "StageName": stage_name,
            "Amount": amount,
            "Probability": probability,
            "CloseDate": close_date.strftime("%Y-%m-%d"),
            "CreatedDate": created.strftime("%Y-%m-%d"),
            "LastModifiedDate": (created + timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            "Type": random.choice(TYPES),
            "LeadSource": random.choice(LEAD_SOURCES),
            "ForecastCategory": FORECAST_MAP[stage_name],
            "ForecastCategoryName": FORECAST_MAP[stage_name],
            "IsWon": is_won,
            "IsClosed": is_closed,
            "FiscalYear": close_date.year,
            "FiscalQuarter": fiscal_quarter,
            "Owner.Id": owner_id,
            "Owner.Name": user_names[owner_id],
            "Account.Id": account_id,
            "Account.Name": account_names[account_id],
            "Account.Industry": account_industries[account_id],
            "Campaign.Name": random.choice([None, "Q1 Campaign", "Partner Push", "Webinar Series", "Trade Show 2025", "Digital Ads"]),
            "ProductName": product_name,
            "ProductFamily": product_family,
            "OpportunityID": opportunity_id,
        })

    df = pd.DataFrame(opps)
    df["CloseDate"] = pd.to_datetime(df["CloseDate"])
    df["CreatedDate"] = pd.to_datetime(df["CreatedDate"])
    df["LastModifiedDate"] = pd.to_datetime(df["LastModifiedDate"])
    return df


def create_date_table(df_opp: pd.DataFrame) -> pd.DataFrame:
    min_date = df_opp["CloseDate"].min()
    max_date = max(df_opp["CloseDate"].max(), pd.Timestamp.now())
    dates = pd.date_range(
        start=min_date - pd.offsets.YearBegin(),
        end=max_date + pd.offsets.YearEnd(),
        freq="D",
    )
    now = datetime.now()
    date_df = pd.DataFrame({"Date": dates})
    date_df["Year"] = date_df["Date"].dt.year
    date_df["Quarter"] = date_df["Date"].dt.quarter
    date_df["QuarterLabel"] = "Q" + date_df["Quarter"].astype(str) + " " + date_df["Year"].astype(str)
    date_df["Month"] = date_df["Date"].dt.month
    date_df["MonthName"] = date_df["Date"].dt.strftime("%b")
    date_df["MonthYear"] = date_df["Date"].dt.strftime("%b %Y")
    date_df["MonthYearSort"] = date_df["Date"].dt.strftime("%Y%m").astype(int)
    date_df["IsCurrentQuarter"] = (
        (date_df["Year"] == now.year) & (date_df["Quarter"] == (now.month - 1) // 3 + 1)
    )
    return date_df


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating sample data...")
    df_users = generate_users()
    df_accounts = generate_accounts()
    df_opps = generate_opportunities(df_accounts, df_users)
    df_dates = create_date_table(df_opps)

    print(f"  Opportunities: {len(df_opps)}")
    print(f"  Accounts: {len(df_accounts)}")
    print(f"  Users: {len(df_users)}")
    print(f"  Date table: {len(df_dates)} rows")

    output_file = OUTPUT_DIR / "salesforce_opportunity_data.xlsx"
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df_opps.to_excel(writer, sheet_name="Opportunities", index=False)
        df_accounts.to_excel(writer, sheet_name="Accounts", index=False)
        df_users.to_excel(writer, sheet_name="Users", index=False)
        df_dates.to_excel(writer, sheet_name="DateTable", index=False)

    print(f"\n✓ Saved to {output_file}")
    print("\nNext steps:")
    print("  1. Open Power BI Desktop")
    print("  2. Get Data → Excel Workbook")
    print(f"  3. Browse to: {output_file.resolve()}")
    print("  4. Select all 4 sheets and click Load")
    print("  5. See powerbi/dax_measures.txt for KPI formulas")


if __name__ == "__main__":
    main()
