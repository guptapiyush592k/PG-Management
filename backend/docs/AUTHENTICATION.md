# Authentication

Authentication uses **JWT access tokens** (via [PyJWT](https://pyjwt.readthedocs.io/)) and **refresh tokens**. Passwords are hashed with [pwdlib](https://frankie567.github.io/pwdlib/) (bcrypt) and never stored in plain text.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/signup` | Register a new user |
| POST | `/auth/login` | Log in with email and password |
| POST | `/auth/refresh` | Get a new token pair using a refresh token |
| POST | `/auth/logout` | Revoke a refresh token |
| POST | `/auth/switch-tenant` | Issue a new token pair for another PG business |

All auth routes are **public** (no `X-Tenant-ID` header). `/auth/switch-tenant` requires a valid Bearer access token.

Auth routes are **rate-limited** per IP (see environment variables below).

## Signup flow

1. Client sends `full_name`, `email`, `password`
2. Server validates password strength (8+ chars, upper, lower, digit)
3. Server checks email is not already registered
4. Server creates the user with a pwdlib-hashed password (bcrypt)
5. Server gets or creates the **demo tenant** (slug from `DEMO_TENANT_SLUG`, default `"demo"`)
6. Server links the user to the demo tenant as **Manager** with `is_primary=true`
7. Server issues access + refresh tokens and returns them

New users always start on the demo PG business. Production tenant onboarding will be added later.

## Login flow

1. Client sends `email`, `password`, and optionally `tenant_id`
2. Server verifies credentials and user is active
3. Server resolves tenant:
   - If `tenant_id` is provided, verifies membership for that tenant
   - Otherwise loads the user's **primary** tenant membership (`is_primary=true`)
4. Server issues a new token pair for the resolved tenant

## Switch tenant flow

1. Client sends `Authorization: Bearer <access_token>` and `{ "tenant_id": "<uuid>" }`
2. Server verifies the user belongs to that tenant
3. Server issues a new token pair scoped to the requested tenant

Use this when a user manages multiple PG businesses and needs a fresh access token after changing `X-Tenant-ID`.

## Token response shape

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "owner@example.com",
    "full_name": "Owner Name"
  },
  "tenant_id": "uuid"
}
```

## Access token (JWT)

| Claim | Meaning |
|-------|---------|
| `sub` | User ID |
| `tenant_id` | Active PG business ID |
| `type` | `"access"` |
| `exp` | Expiry timestamp |
| `iat` | Issued-at timestamp |

Configured via `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60).

## Refresh token

| Claim | Meaning |
|-------|---------|
| `sub` | User ID |
| `jti` | Refresh token row ID (UUID) |
| `type` | `"refresh"` |
| `exp` | Expiry timestamp |

- Stored **hashed** in the `refresh_tokens` table (never plain text in DB)
- Lifetime configured via `REFRESH_TOKEN_EXPIRE_DAYS` (default 7)
- On refresh: old token is revoked, new pair is issued (rotation)
- On logout: refresh token is revoked
- **Reuse detection:** if a revoked refresh token is presented again, all refresh tokens for that user are revoked

## Full auth sequence

```mermaid
sequenceDiagram
    participant Client
    participant Auth as /auth/*
    participant DB as Database

    Client->>Auth: POST /auth/signup
    Auth->>DB: Create user + demo tenant membership
    Auth-->>Client: access_token + refresh_token

    Client->>Auth: POST /auth/login
    Auth->>DB: Verify password + membership
    Auth-->>Client: New token pair

    Client->>Auth: POST /auth/switch-tenant
    Auth->>DB: Verify membership for tenant_id
    Auth-->>Client: New token pair

    Client->>Auth: POST /auth/refresh
    Auth->>DB: Validate + revoke old refresh token
    Auth-->>Client: New token pair

    Client->>Auth: POST /auth/logout
    Auth->>DB: Revoke refresh token
    Auth-->>Client: Success message
```

## Refresh request

```http
POST /auth/refresh
Content-Type: application/json

{ "refresh_token": "eyJ..." }
```

## Logout request

```http
POST /auth/logout
Content-Type: application/json

{ "refresh_token": "eyJ..." }
```

## Switch tenant request

```http
POST /auth/switch-tenant
Authorization: Bearer eyJ...
Content-Type: application/json

{ "tenant_id": "550e8400-e29b-41d4-a716-446655440000" }
```

## Security rules

- Never log passwords or tokens
- Never store plain passwords — use `hash_password()` / `verify_password()` from [`app/core/security.py`](../app/core/security.py)
- Invalid or expired tokens return `401` with `error_code: "unauthorized"`
- Inactive users return `403` with `error_code: "forbidden"`
- Signup passwords must include uppercase, lowercase, and a digit

## Environment variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `JWT_SECRET_KEY` | Yes | — | Signing key (min 32 chars) |
| `JWT_ALGORITHM` | Yes | — | `HS256`, `HS384`, or `HS512` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Yes | — | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | `7` | Refresh token TTL |
| `DEMO_TENANT_SLUG` | No | `demo` | Demo tenant slug for signup |
| `AUTH_RATE_LIMIT_MAX_REQUESTS` | No | `20` | Max auth requests per IP per window |
| `AUTH_RATE_LIMIT_WINDOW_SECONDS` | No | `60` | Auth rate-limit window |

See [AUTHORIZATION_EXAMPLES.md](AUTHORIZATION_EXAMPLES.md) for how to use tokens on protected routes.
