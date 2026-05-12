#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
#  scripts/migrate.sh
#  Run Alembic database migrations
# ──────────────────────────────────────────────────────────────
set -euo pipefail

cd "$(dirname "$0")/../backend"

echo "Running database migrations..."
alembic upgrade head

echo "Migrations complete."
