#!/usr/bin/env bash
set -euo pipefail

# Determine the Codespace public URL for the backend
# CODESPACE_NAME is auto-set by GitHub Codespaces
if [ -n "${CODESPACE_NAME:-}" ]; then
  BACKEND_URL="https://${CODESPACE_NAME}-8000.app.github.dev"
  FRONTEND_URL="https://${CODESPACE_NAME}-5173.app.github.dev"

  # Patch .env so OAuth callback and CORS point to the Codespace URLs
  sed -i "s|SF_REDIRECT_URI=.*|SF_REDIRECT_URI=${BACKEND_URL}/auth/callback|" /workspaces/salesforce-dashboard/.env
  sed -i "s|FRONTEND_URL=.*|FRONTEND_URL=${FRONTEND_URL}|" /workspaces/salesforce-dashboard/.env

  echo "==> Codespace detected"
  echo "    Backend:  ${BACKEND_URL}"
  echo "    Frontend: ${FRONTEND_URL}"
  echo "    Remember to update your Salesforce Connected App callback URL to:"
  echo "    ${BACKEND_URL}/auth/callback"
fi

# ---- Start Backend ----
echo "==> Starting FastAPI backend on :8000..."
cd /workspaces/salesforce-dashboard/backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# ---- Start Frontend ----
echo "==> Starting Vite dev server on :5173..."
cd /workspaces/salesforce-dashboard/frontend
VITE_API_URL="${BACKEND_URL:-http://localhost:8000}" npm run dev &

echo ""
echo "============================================"
echo "  Salesforce Dashboard is running!"
echo "  Frontend: ${FRONTEND_URL:-http://localhost:5173}"
echo "  Backend:  ${BACKEND_URL:-http://localhost:8000}"
echo "  API Docs: ${BACKEND_URL:-http://localhost:8000}/docs"
echo "============================================"

# Keep the script alive so Codespaces doesn't kill the processes
wait
