# PG Management Backend

Production-ready FastAPI backend for the PG Management SaaS platform.

**Documentation:** See [`docs/README.md`](docs/README.md) for the full reference — architecture, auth, tenancy, API conventions, and database schema.

## Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0 (async)
- Alembic
- Pydantic v2
- JWT authentication (access + refresh tokens)
- Multi-tenant architecture (shared schema with `tenant_id`)

## Prerequisites

- Python 3.12
- PostgreSQL 14+

## Setup

### 1. Create virtual environment

**Windows (PowerShell):**

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure environment

```powershell
copy .env.example .env
```

Edit `.env` and set all **required** variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Async PostgreSQL URL (`postgresql+asyncpg://...`) |
| `JWT_SECRET_KEY` | Yes | Secret key for JWT signing (min 32 characters) |
| `JWT_ALGORITHM` | Yes | JWT algorithm (`HS256`, `HS384`, or `HS512`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Yes | Access token lifetime in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | Refresh token lifetime (default `7`) |
| `DEMO_TENANT_SLUG` | No | Demo tenant slug for signup (default `demo`) |
| `CORS_ORIGINS` | No | Comma-separated allowed origins |
| `LOG_LEVEL` | No | Logging level (default `INFO`) |
| `STORAGE_PROVIDER` | No | `local` (default) or `s3` — see [docs/STORAGE.md](docs/STORAGE.md) |

Optional: `DATABASE_URL_SYNC` for Alembic (auto-derived from `DATABASE_URL` if omitted).

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

## Implemented APIs

| Group | Routes |
|-------|--------|
| Auth | `POST /auth/signup`, `/login`, `/refresh`, `/logout` |
| Me | `GET /me/context` |
| Health | `GET /api/v1/health` |
| Flats | CRUD at `/api/v1/flats` |
| Rooms | CRUD at `/api/v1/rooms` |
| Beds | CRUD at `/api/v1/beds` |
| Residents | CRUD at `/api/v1/residents` |
| Payments | Create, list, update, summary at `/api/v1/payments` |
| Bookings | Create, list, checkout at `/api/v1/bookings` |
| Files | Upload URL, list at `/api/v1/files` |

See [docs/API_CONVENTIONS.md](docs/API_CONVENTIONS.md) for the full endpoint catalog and [docs/STORAGE.md](docs/STORAGE.md) for file storage configuration.

## Project Structure

```
app/
├── api/           # REST API routers
├── core/          # Config, security, exceptions, dependencies
├── db/            # Database engine and base models
├── middleware/    # Request logging, tenant authorization
├── models/        # SQLAlchemy ORM models
├── repositories/  # Data access layer
├── schemas/       # Pydantic request/response schemas
├── services/      # Business logic and permission checks
├── storage/       # Cloud-agnostic file storage providers
└── utils/         # Shared utilities
alembic/           # Database migrations
docs/              # Documentation (source of truth)
tests/             # Test suite
```

## Multi-Tenancy

This backend uses a **shared PostgreSQL schema** with row-level isolation via `tenant_id`.

- Protected routes require `Authorization: Bearer <token>` and `X-Tenant-ID` header
- `BaseRepository` auto-filters tenant-scoped queries
- New tenant-scoped records auto-receive `tenant_id` on flush
- See [docs/TENANCY.md](docs/TENANCY.md) for details

## Alembic Commands

```powershell
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```
