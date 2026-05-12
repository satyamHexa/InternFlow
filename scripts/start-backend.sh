#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
#  scripts/start-backend.sh
#  Start FastAPI development server
# ──────────────────────────────────────────────────────────────
set -euo pipefail

cd "$(dirname "$0")/../backend"

uvicorn app.main:app \
  --reload \
  --host 0.0.0.0 \
  --port 8000 \
  --log-level info
