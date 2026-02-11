# Salesforce Dashboard

A modern dashboard for visualizing Salesforce Opportunity data. Built with **FastAPI** (Python) and **React + TypeScript** (Vite).

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/NealStearns/salesforce-dashboard?quickstart=1)

> **One-click demo:** Click the button above to launch a fully configured dev environment in your browser. The backend (FastAPI) and frontend (React) start automatically — no local setup required. The Codespace will auto-stop after 30 minutes of inactivity.

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   React SPA  │───▶│  FastAPI API  │───▶│  Salesforce   │
│  (Vite + TS) │     │  (Python)    │     │  REST API     │
└──────────────┘     └──────────────┘     └──────────────┘
    :5173                :8000            login.salesforce.com
```

### Features

- **OAuth 2.0** authentication with Salesforce
- **KPI cards** – open pipeline, average deal size, won/lost this quarter
- **Pipeline chart** – opportunity amounts over time (bar chart)
- **Stage breakdown** – pie chart of opportunities by stage
- **Opportunity table** – sortable, filterable, paginated list
- Responsive layout with Tailwind CSS

## Prerequisites

- **Python 3.12+**
- **Node.js 20+**
- **Salesforce Connected App** with OAuth enabled

### Setting Up Salesforce Connected App

1. In Salesforce Setup, navigate to **App Manager** → **New Connected App**
2. Enable **OAuth Settings**
3. Set Callback URL to `http://localhost:8000/auth/callback`
4. Select OAuth Scopes: `Access and manage your data (api)`, `Perform requests at any time (refresh_token)`
5. Save and copy the **Consumer Key** and **Consumer Secret**

## Quick Start

### 1. Clone & configure

```bash
git clone https://github.com/NealStearns/salesforce-dashboard.git
cd salesforce-dashboard
cp .env.sample .env
# Edit .env with your Salesforce Connected App credentials
```

### 2. Run with Docker Compose

```bash
docker compose up --build
```

### 3. Or run manually

**Backend:**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

### 4. Open the app

Visit **http://localhost:5173** and click "Connect to Salesforce" to authenticate.

## API Endpoints

| Method | Path                              | Description                   |
|--------|-----------------------------------|-------------------------------|
| `GET`  | `/auth/login`                     | Redirect to Salesforce OAuth  |
| `GET`  | `/auth/callback`                  | OAuth callback handler        |
| `GET`  | `/auth/status`                    | Check authentication status   |
| `POST` | `/auth/logout`                    | Clear session                 |
| `GET`  | `/api/dashboard/kpis`             | KPI summary metrics           |
| `GET`  | `/api/dashboard/stages`           | Opportunities grouped by stage|
| `GET`  | `/api/dashboard/pipeline?months=12` | Pipeline over time          |
| `GET`  | `/api/opportunities`              | Paginated opportunity list    |
| `GET`  | `/health`                         | Health check                  |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Environment settings
│   │   ├── dependencies.py      # Request dependency injection
│   │   ├── auth/
│   │   │   ├── salesforce.py    # OAuth flow helpers
│   │   │   └── session.py       # Server-side session store
│   │   ├── services/
│   │   │   └── salesforce.py    # Salesforce API client + SOQL
│   │   ├── routes/
│   │   │   ├── auth.py          # Auth endpoints
│   │   │   ├── dashboard.py     # Dashboard data endpoints
│   │   │   └── opportunities.py # Opportunity list endpoint
│   │   └── models/
│   │       └── opportunities.py # Pydantic models
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Root component + auth check
│   │   ├── components/          # React UI components
│   │   ├── services/api.ts      # Axios API client
│   │   ├── hooks/useApi.ts      # Data fetching hook
│   │   └── types/index.ts       # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.sample
└── README.md
```

## Tech Stack

| Layer    | Technology                                               |
|----------|----------------------------------------------------------|
| Backend  | Python 3.12, FastAPI, httpx, Pydantic                    |
| Frontend | React 18, TypeScript, Vite 5, Tailwind CSS 3, Recharts  |
| Auth     | Salesforce OAuth 2.0 (Web Server Flow)                   |
| DevOps   | Docker, Docker Compose                                   |
