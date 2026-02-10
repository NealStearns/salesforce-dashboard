#!/usr/bin/env bash
set -euo pipefail
echo "==> Setting up Salesforce Dashboard..."

# ---- Backend ----
echo "==> Installing Python dependencies..."
cd /workspaces/salesforce-dashboard/backend
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# ---- Frontend ----
echo "==> Installing Node dependencies..."
cd /workspaces/salesforce-dashboard/frontend
npm install

# ---- Env file ----
if [ ! -f /workspaces/salesforce-dashboard/.env ]; then
  echo "==> Creating .env from sample (edit with your Salesforce credentials)..."
  cp /workspaces/salesforce-dashboard/.env.sample /workspaces/salesforce-dashboard/.env
fi

echo "==> Setup complete!"
