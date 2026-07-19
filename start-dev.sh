#!/usr/bin/env bash
# Starts the backend (uvicorn) and frontend (vite) dev servers together
# and stops both on Ctrl+C. Assumes dependencies are already installed
# (see README.md) — this script only launches, it doesn't install.

set -e

cleanup() {
  echo ""
  echo "Stopping servers..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
  wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
  exit 0
}
trap cleanup INT TERM

echo "Starting backend on http://127.0.0.1:8000 ..."
(
  cd backend
  if [ -d venv ]; then source venv/bin/activate; fi
  uvicorn app.main:app --reload
) &
BACKEND_PID=$!

echo "Starting frontend on http://localhost:5173 ..."
(
  cd frontend
  npm run dev
) &
FRONTEND_PID=$!

echo ""
echo "Both servers starting. Press Ctrl+C to stop both."
wait
