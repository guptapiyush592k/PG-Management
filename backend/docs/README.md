# Backend Documentation

This folder is the **single source of truth** for the PG Management backend. Read these docs before changing code. When you change behavior, update the matching doc in the same change.

## Documents

| Document | What it covers |
|----------|----------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Layers, folders, middleware, request lifecycle |
| [AUTHENTICATION.md](AUTHENTICATION.md) | Signup, login, refresh, logout, JWT tokens |
| [AUTHORIZATION_EXAMPLES.md](AUTHORIZATION_EXAMPLES.md) | Protected routes, headers, RBAC, examples |
| [TENANCY.md](TENANCY.md) | Multi-tenant isolation, `tenant_id`, repositories |
| [DATABASE_ERD.md](DATABASE_ERD.md) | Tables, relationships, migrations |
| [API_CONVENTIONS.md](API_CONVENTIONS.md) | REST patterns, pagination, errors, endpoint list |
| [STORAGE.md](STORAGE.md) | File upload module, storage providers, configuration |

## Quick links

| Task | Command / URL |
|------|----------------|
| Local setup | See [backend README](../README.md) |
| Interactive API docs | http://localhost:8000/docs |
| Run tests | `pytest` (from `backend/`) |
| Apply migrations | `alembic upgrade head` |

## Keeping docs in sync

1. Change code and docs together — never leave them out of date.
2. If code and docs disagree, fix whichever is wrong and note the conflict.
3. New features need updates to the relevant doc(s) and the endpoint catalog in [API_CONVENTIONS.md](API_CONVENTIONS.md).

## What is not implemented yet

- **Platform-level Super Admin** — role exists in DB; assign manually until platform admin APIs are built
