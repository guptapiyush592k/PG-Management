# API Conventions

REST API conventions for the PG Management backend. Interactive docs are also available at `/docs` (Swagger) and `/redoc`.

## Base URL

```
http://localhost:8000
```

## HTTP methods

| Method | Usage |
|--------|-------|
| GET | List resources or get one by ID |
| POST | Create a new resource |
| PATCH | Partial update (send only changed fields) |
| DELETE | Remove a resource (returns 204, no body) |

PUT is not used. Updates always use PATCH.

## Authentication

| Route group | Headers |
|-------------|---------|
| `/auth/*` | None |
| `/me/*` | `Authorization: Bearer <token>` |
| `/api/v1/*` | `Authorization: Bearer <token>` + `X-Tenant-ID: <uuid>` |

See [AUTHENTICATION.md](AUTHENTICATION.md) and [AUTHORIZATION_EXAMPLES.md](AUTHORIZATION_EXAMPLES.md).

## Pagination

List endpoints accept query parameters:

| Param | Default | Max | Description |
|-------|---------|-----|-------------|
| `page` | 1 | — | Page number (1-based) |
| `page_size` | 20 | 100 | Items per page |

Response shape:

```json
{
  "items": [ ... ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

## Filters

| Resource | Filters |
|----------|---------|
| Flats | `search`, `is_active` |
| Rooms | `search`, `flat_id` |
| Beds | `search`, `room_id`, `status` (`vacant`, `occupied`, `maintenance`) |
| Residents | `search`, `is_active` |

## Error responses

All errors return:

```json
{
  "detail": "Human-readable message",
  "error_code": "machine_readable_code"
}
```

| HTTP status | `error_code` | When |
|-------------|--------------|------|
| 400 | `app_error` | Generic application error |
| 401 | `unauthorized` | Missing or invalid JWT |
| 403 | `forbidden` | No permission or inactive account |
| 404 | `not_found` | Resource does not exist |
| 409 | `conflict` | Duplicate email, phone, room number, etc. |
| 422 | `validation_error` | Business validation failed |
| 422 | `request_validation_error` | Invalid request body or query params |
| 500 | `internal_server_error` | Unexpected server error |

## Endpoint catalog

### Auth (public)

| Method | Path | Body | Response |
|--------|------|------|----------|
| POST | `/auth/signup` | `{ full_name, email, password }` | `TokenResponse` (201) |
| POST | `/auth/login` | `{ email, password }` | `TokenResponse` |
| POST | `/auth/refresh` | `{ refresh_token }` | `TokenResponse` |
| POST | `/auth/logout` | `{ refresh_token }` | `{ message }` |

### Me (JWT only)

| Method | Path | Response |
|--------|------|----------|
| GET | `/me/context` | User, tenant branding, permissions |

### Health (public)

| Method | Path | Response |
|--------|------|----------|
| GET | `/api/v1/health` | App and database status |

### Flats (protected)

| Method | Path | Permission | Notes |
|--------|------|------------|-------|
| POST | `/api/v1/flats` | `manage_flats` | Create |
| GET | `/api/v1/flats` | — | List (paginated) |
| GET | `/api/v1/flats/{flat_id}` | — | Get one |
| PATCH | `/api/v1/flats/{flat_id}` | `manage_flats` | Update |
| DELETE | `/api/v1/flats/{flat_id}` | `manage_flats` | 204 |

### Rooms (protected)

| Method | Path | Permission | Notes |
|--------|------|------------|-------|
| POST | `/api/v1/rooms` | `manage_rooms` | Create |
| GET | `/api/v1/rooms` | — | List; filter by `flat_id` |
| GET | `/api/v1/rooms/{room_id}` | — | Get one |
| PATCH | `/api/v1/rooms/{room_id}` | `manage_rooms` | Update |
| DELETE | `/api/v1/rooms/{room_id}` | `manage_rooms` | 204 |

### Beds (protected)

| Method | Path | Permission | Notes |
|--------|------|------------|-------|
| POST | `/api/v1/beds` | `manage_beds` | Create |
| GET | `/api/v1/beds` | — | List; filter by `room_id`, `status` |
| GET | `/api/v1/beds/{bed_id}` | — | Get one |
| PATCH | `/api/v1/beds/{bed_id}` | `manage_beds` | Update |
| DELETE | `/api/v1/beds/{bed_id}` | `manage_beds` | 204 |

### Residents (protected)

| Method | Path | Permission | Notes |
|--------|------|------------|-------|
| POST | `/api/v1/residents` | `manage_residents` | Create |
| GET | `/api/v1/residents` | — | List (paginated) |
| GET | `/api/v1/residents/{resident_id}` | — | Get one |
| PATCH | `/api/v1/residents/{resident_id}` | `manage_residents` | Update |
| DELETE | `/api/v1/residents/{resident_id}` | `manage_residents` | 204 |

### Examples (protected)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/examples/tenant-scope` | Demo route showing tenant scoping |

### Not implemented

| Resource | Status |
|----------|--------|
| Bookings | Model + migration exist; no API routes |
| Rent payments | Model + migration exist; no API routes |

## UUID identifiers

All resource IDs are UUIDs returned as strings in JSON:

```json
{ "id": "550e8400-e29b-41d4-a716-446655440000" }
```

## Timestamps

All resources include timezone-aware `created_at` and `updated_at` fields in ISO 8601 format.
