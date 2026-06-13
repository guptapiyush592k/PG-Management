# PG Management Backend

Production-ready FastAPI backend for the PG Management SaaS platform.

## Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0 (async)
- Alembic
- Pydantic v2
- JWT authentication infrastructure
- Multi-tenant architecture (shared schema with `tenant_id`)

## Prerequisites

- Python 3.12
- PostgreSQL 14+

## Setup

### 1. Create virtual environment

**Windows (PowerShell):**

```powershell
cd "PG Management Backend"
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
cd "PG Management Backend"
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure environment

```powershell
copy .env.example .env
```

Edit `.env` and set at minimum:

- `DATABASE_URL` — async connection string (`postgresql+asyncpg://...`)
- `DATABASE_URL_SYNC` — sync connection string for Alembic (`postgresql+psycopg://...`)
- `JWT_SECRET_KEY` — long random secret (min 32 characters)

### 3. Create database

```sql
CREATE DATABASE pg_management;
```

### 4. Run migrations

```powershell
alembic upgrade head
```

### 5. Start the server

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

## Health Check

```http
GET /api/v1/health
```

Example response:

```json
{
  "status": "ok",
  "app_name": "PG Management API",
  "environment": "development",
  "database": "ok"
}
```

## Running Tests

```powershell
pytest
```

## Project Structure

```
app/
├── api/           # REST API routers
├── core/          # Config, security, exceptions, dependencies
├── db/            # Database engine and base models
├── middleware/    # Request logging, tenant context
├── models/        # SQLAlchemy ORM models
├── repositories/  # Data access layer
├── schemas/       # Pydantic request/response schemas
├── services/      # Business logic (future)
└── utils/         # Shared utilities
alembic/           # Database migrations
tests/             # Test suite
```

## Multi-Tenancy

This backend uses a **shared PostgreSQL schema** with row-level isolation via `tenant_id`.

- JWT tokens include a `tenant_id` claim
- `X-Tenant-ID` header is supported for local development
- `BaseRepository` auto-filters tenant-scoped queries
- New tenant-scoped records auto-receive `tenant_id` on flush

## Alembic Commands

```powershell
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Notes

- Auth routes (`/auth/login`, `/auth/register`) are not implemented yet — only JWT infrastructure is in place.
- Business domain APIs (properties, residents, payments) will be added in future phases.
