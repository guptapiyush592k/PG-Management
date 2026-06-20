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
| `/me/*` | `Authorization: Bearer <token>`; optional `X-Tenant-ID` on `/me/context` |
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
| Payments | `search`, `resident_id`, `status` (`paid`, `pending`, `partial`, `overdue`) |
| Bookings | `search`, `resident_id`, `bed_id`, `status` (`active`, `completed`, `cancelled`) |
| Files | `search`, `status` (`pending`, `uploaded`) |

## Error responses

All errors return:

```json
{
  "detail": "Human-readable message",
  "error_code": "machine_readable_code",
  "errors": [ ... ]
}
```

The `errors` array is included for `422 request_validation_error` responses and contains Pydantic field-level details.

| HTTP status | `error_code` | When |
|-------------|--------------|------|
| 400 | `app_error` | Generic application error |
| 401 | `unauthorized` | Missing or invalid JWT |
| 403 | `forbidden` | No permission or inactive account |
| 404 | `not_found` | Resource does not exist |
| 409 | `conflict` | Duplicate email, phone, room number, etc. |
| 422 | `validation_error` | Business validation failed |
| 422 | `request_validation_error` | Invalid request body or query params |
| 429 | `rate_limit_exceeded` | Too many auth requests from one IP |
| 500 | `internal_server_error` | Unexpected server error |

## Endpoint catalog

### Auth (public)

| Method | Path | Body | Response |
|--------|------|------|----------|
| POST | `/auth/signup` | `{ full_name, email, password }` | `TokenResponse` (201) |
| POST | `/auth/login` | `{ email, password, tenant_id? }` | `TokenResponse` |
| POST | `/auth/refresh` | `{ refresh_token }` | `TokenResponse` |
| POST | `/auth/logout` | `{ refresh_token }` | `{ message }` |
| POST | `/auth/switch-tenant` | `{ tenant_id }` + Bearer token | `TokenResponse` |

Password rules on signup: minimum 8 characters with at least one uppercase letter, one lowercase letter, and one digit.

### Me (JWT only)

| Method | Path | Headers | Response |
|--------|------|---------|----------|
| GET | `/me/context` | Bearer token; optional `X-Tenant-ID` | User, tenant branding, permissions |

When `X-Tenant-ID` is sent, membership is verified and that tenant is used instead of the JWT `tenant_id` claim.

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
| DELETE | `/api/v1/flats/{flat_id}` | `manage_flats` | 204; rejected if rooms still exist |

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
| DELETE | `/api/v1/beds/{bed_id}` | `manage_beds` | 204; rejected if bed is occupied or has an active booking |

### Residents (protected)

| Method | Path | Permission | Notes |
|--------|------|------------|-------|
| POST | `/api/v1/residents` | `manage_residents` | Create |
| GET | `/api/v1/residents` | — | List (paginated) |
| GET | `/api/v1/residents/{resident_id}` | — | Get one (`aadhaar` masked in response) |
| PATCH | `/api/v1/residents/{resident_id}` | `manage_residents` | Update |
| DELETE | `/api/v1/residents/{resident_id}` | `manage_residents` | 204 |

### Payments (protected)

| Method | Path | Permission | Notes |
|--------|------|------------|-------|
| POST | `/api/v1/payments` | `manage_payments` | Create rent payment record |
| GET | `/api/v1/payments` | — | List (paginated); filter by `resident_id`, `status` |
| GET | `/api/v1/payments/{payment_id}` | — | Get one |
| PATCH | `/api/v1/payments/{payment_id}` | `manage_payments` | Partial update |
| GET | `/api/v1/payments/summary` | — | Aggregated totals by status |

Pending payments with `due_date` before today are automatically marked `overdue` when listing, fetching, or summarizing.

Payment summary response:

```json
{
  "total_collected": "19000.00",
  "pending_amount": "14500.00",
  "overdue_amount": "3000.00",
  "counts": {
    "paid": 2,
    "pending": 1,
    "partial": 1,
    "overdue": 1
  }
}
```

`pending_amount` includes both `pending` and `partial` statuses.

### Bookings (protected)

| Method | Path | Permission | Notes |
|--------|------|------------|-------|
| POST | `/api/v1/bookings` | `manage_beds` | Assign resident to a vacant bed |
| GET | `/api/v1/bookings` | — | List (paginated); filter by `resident_id`, `bed_id`, `status` |
| GET | `/api/v1/bookings/{booking_id}` | — | Get one |
| POST | `/api/v1/bookings/{booking_id}/checkout` | `manage_beds` | Complete stay and free the bed |

Create booking body:

```json
{
  "resident_id": "550e8400-e29b-41d4-a716-446655440000",
  "bed_id": "660e8400-e29b-41d4-a716-446655440001",
  "start_date": "2026-06-01"
}
```

Checkout body (`end_date` optional, defaults to today):

```json
{
  "end_date": "2026-06-30"
}
```

On create, the bed status is set to `occupied`. On checkout, the booking status becomes `completed` and the bed returns to `vacant`. Only one `active` booking is allowed per bed (enforced in the service layer and by a partial unique index).

### Files (protected)

| Method | Path | Permission | Notes |
|--------|------|------------|-------|
| POST | `/api/v1/files/upload-url` | `manage_files` | Presigned upload URL (201) |
| POST | `/api/v1/files/{file_id}/confirm` | `manage_files` | Mark S3 upload complete |
| GET | `/api/v1/files` | — | List (paginated); filter by `status` |
| GET | `/api/v1/files/{file_id}` | — | Get one |
| PUT | `/api/v1/files/{file_id}/content` | Signed URL or JWT | Local storage — upload via presigned URL |
| GET | `/api/v1/files/{file_id}/content` | Signed URL or JWT | Local storage — download via presigned URL |

Create upload URL body:

```json
{
  "filename": "aadhaar.pdf",
  "content_type": "application/pdf"
}
```

Upload URL response:

```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "upload_url": "https://...",
  "method": "PUT",
  "headers": { "Content-Type": "application/pdf" },
  "storage_key": "tenant-uuid/file-uuid/aadhaar.pdf",
  "expires_at": "2026-06-20T12:00:00Z"
}
```

See [STORAGE.md](STORAGE.md) for provider configuration and upload flow.

### Examples (protected)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/examples/tenant-scope` | Demo route showing tenant scoping |

## UUID identifiers

All resource IDs are UUIDs returned as strings in JSON:

```json
{ "id": "550e8400-e29b-41d4-a716-446655440000" }
```

## Timestamps

All resources include timezone-aware `created_at` and `updated_at` fields in ISO 8601 format.
