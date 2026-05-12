#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
#  scripts/setup-dev.sh
#  One-time local development environment setup
# ──────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Setting up Intern Flow development environment"

# Copy env template
if [ ! -f "$ROOT/.env" ]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "  Created .env from .env.example — fill in your secrets"
fi

# Backend Python setup
echo "==> Setting up backend Python environment"
cd "$ROOT/backend"
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "  Backend dependencies installed"

# Frontend Node setup
echo "==> Setting up frontend Node environment"
cd "$ROOT/frontend"
npm ci
echo "  Frontend dependencies installed"

# AI services Python setup
echo "==> Setting up AI services Python environment"
cd "$ROOT/ai-services"
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "  AI service dependencies installed"

echo ""
echo "==> Setup complete!"
echo "    Run: docker-compose up  (to start all services)"
echo "    Or:  cd backend && uvicorn app.main:app --reload"
