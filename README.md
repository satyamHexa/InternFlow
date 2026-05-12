# Intern Flow

AI-assisted internship referral and onboarding automation platform.

## Tech Stack

| Layer      | Technology                                     |
|------------|------------------------------------------------|
| Frontend   | React 18 + TypeScript + Vite + Tailwind CSS    |
| Backend    | FastAPI + SQLAlchemy (async) + Alembic         |
| AI         | Azure OpenAI GPT-4o + Azure Document Intelligence |
| Database   | PostgreSQL 15                                   |
| Queue      | Redis 7 + Celery                               |
| Storage    | Azure Blob Storage                             |
| Infra      | Docker + Nginx + Terraform + GitHub Actions    |

## Monorepo Structure

```
internflow/
├── frontend/           React SPA (HR portal + employee portal)
├── backend/            FastAPI application
├── ai-services/        AI parsing and generation modules
├── infrastructure/     Nginx, Terraform, GitHub Actions
├── scripts/            Dev and ops helper scripts
├── docker-compose.yml  Local development stack
└── .env.example        Environment variable template
```

## Quick Start

```bash
# 1. Clone and setup
git clone <repo>
cd internflow
bash scripts/setup-dev.sh

# 2. Configure secrets
cp .env.example .env
# Edit .env with your Azure and database credentials

# 3. Start all services
docker-compose up

# 4. Run database migrations
bash scripts/migrate.sh

# 5. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Core Modules

- **Auth** — JWT + RBAC (6 roles)
- **Referral** — Multi-step form + resume upload
- **AI Engine** — Resume parsing, email generation, duplicate detection
- **Workflow Engine** — 12-stage onboarding pipeline with SLA tracking
- **NDA Module** — PDF generation + e-signature + Blob archival
- **Dashboard** — HR metrics, SLA heatmap, department charts
- **Notifications** — Email + Teams + in-app
- **Audit Logging** — Immutable append-only compliance trail
- **Certificates** — Auto-generated completion certificates

## Development

```bash
# Backend tests
cd backend && pytest tests/ -v --cov=app

# Frontend type check + lint
cd frontend && npm run type-check && npm run lint

# Build frontend
cd frontend && npm run build
```

## API Documentation

Interactive API docs available at `/docs` (Swagger UI) and `/redoc` when running locally.
