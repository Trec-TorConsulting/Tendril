# API Reference

The Tendril API is a RESTful JSON API built with FastAPI. Interactive documentation is auto-generated and available at `/v1/docs` (Swagger UI) and `/v1/openapi.json` when the server is running.

This guide covers authentication flows, conventions, and key endpoints beyond what the auto-generated docs show.

## Base URL

```
http://localhost:8000/v1     # Local development
https://your-domain.com/v1   # Production
```

## Authentication

Tendril uses an enterprise RBAC model with three role tiers:

| Tier | Roles | Purpose |
|------|-------|---------|
| **Platform** | `super_admin`, `support`, `readonly_admin`, `user` | SaaS-wide access control |
| **Tenant** | `admin`, `member`, `viewer` | Per-organization permissions |
| **Account** | `owner`, `billing_admin` | Billing and ownership |

Permissions are resolved from the combination of platform role + tenant role. Route guards check permissions (e.g., `grow:create`, `billing:manage`), not roles directly.

### Register

```http
POST /v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecureP@ssword123",
  "display_name": "Jane Doe",
  "tenant_name": "Jane's Garden"
}
```

Creates a new Account → Tenant → User chain. The registering user becomes the Account Owner and Tenant Admin.

### Login

```http
POST /v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecureP@ssword123"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

The access token JWT contains claims: `sub` (user ID), `pr` (platform role), `tid` (tenant ID), `tr` (tenant role), `gs` (grow scope, if restricted), `aid` (account ID).

### Using Tokens

Include the access token in the `Authorization` header:

```http
GET /v1/grows
Authorization: Bearer eyJ...
```

### Refresh Token

Access tokens expire after 15 minutes. Use the refresh token to get a new pair:

```http
POST /v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}
```

Refresh tokens are tenant-agnostic. On refresh, the API resolves the user's most recent tenant context.

### Switch Tenant

Users who belong to multiple tenants can switch their active tenant context:

```http
POST /v1/auth/switch-tenant
Content-Type: application/json
Authorization: Bearer eyJ...

{
  "tenant_id": "uuid-of-target-tenant"
}
```

Returns a new access token scoped to the target tenant. Super Admins can switch to any tenant.

### OAuth2 Login

Google and GitHub OAuth2 are supported when configured. The flow:

1. Frontend redirects user to provider
2. Provider redirects back with authorization code
3. Frontend sends code to `/v1/auth/oauth/{provider}`
4. API exchanges code for user info, creates/links account, returns tokens

## Conventions

### Tenant Isolation

All data endpoints are tenant-scoped. The active tenant is determined from the authenticated user's JWT `tid` claim (set during login or via `switch-tenant`). You never need to pass a tenant ID in requests — it's automatic.

Users can belong to multiple tenants with different roles in each. Use `POST /v1/auth/switch-tenant` to change context.

### Response Format

Successful responses return the resource directly:

```json
{
  "id": "uuid",
  "name": "My Grow",
  "created_at": "2025-01-15T10:30:00Z"
}
```

List endpoints return arrays:

```json
[
  {"id": "uuid1", "name": "Grow 1"},
  {"id": "uuid2", "name": "Grow 2"}
]
```

### Error Responses

```json
{
  "detail": "Not found"
}
```

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad request — invalid input |
| 401 | Unauthorized — missing or expired token |
| 403 | Forbidden — insufficient permissions |
| 404 | Not found |
| 409 | Conflict — duplicate resource |
| 422 | Validation error — Pydantic schema mismatch |
| 429 | Rate limited |
| 500 | Internal server error |

### Dates and Times

All timestamps are UTC in ISO 8601 format: `2025-01-15T10:30:00Z`

## Core Endpoints

### Grow Cycles

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/grows` | List all grow cycles |
| `POST` | `/v1/grows` | Create a new grow cycle |
| `GET` | `/v1/grows/{id}` | Get grow cycle details |
| `PATCH` | `/v1/grows/{id}` | Update a grow cycle |
| `DELETE` | `/v1/grows/{id}` | Delete a grow cycle |

### Tents / Grow Rooms

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/tents` | List all tents |
| `POST` | `/v1/tents` | Create a tent |
| `GET` | `/v1/tents/{id}` | Get tent details (includes equipment) |
| `PATCH` | `/v1/tents/{id}` | Update tent |
| `DELETE` | `/v1/tents/{id}` | Delete tent |

### Buckets (Plants / Containers)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/buckets` | List buckets for a grow |
| `POST` | `/v1/buckets` | Create a bucket |
| `GET` | `/v1/buckets/{id}` | Get bucket details |
| `PATCH` | `/v1/buckets/{id}` | Update bucket |
| `DELETE` | `/v1/buckets/{id}` | Delete bucket |

### Sensors

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/sensors` | Query bucket sensor readings |
| `GET` | `/v1/tent-sensors` | Query tent ambient readings |

Query parameters for sensor endpoints:

| Parameter | Type | Description |
|-----------|------|-------------|
| `bucket_id` or `tent_id` | UUID | Filter by container/tent |
| `start` | ISO datetime | Start of time range |
| `end` | ISO datetime | End of time range |
| `limit` | int | Max readings to return |

### Journal

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/journal` | List journal entries |
| `POST` | `/v1/journal` | Create a journal entry |
| `PATCH` | `/v1/journal/{id}` | Update entry |
| `DELETE` | `/v1/journal/{id}` | Delete entry |

### Photos

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/photos` | Upload a photo (multipart/form-data) |
| `GET` | `/v1/photos/{key}` | Download a photo |
| `DELETE` | `/v1/photos/{key}` | Delete a photo |

Photo uploads accept `image/jpeg`, `image/png`, and `image/webp` up to 10 MB.

### Feeding Logs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/feeding` | List feeding records |
| `POST` | `/v1/feeding` | Log a feeding |
| `PATCH` | `/v1/feeding/{id}` | Update feeding record |
| `DELETE` | `/v1/feeding/{id}` | Delete feeding record |

### Strains

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/strains` | List strains |
| `POST` | `/v1/strains` | Create a strain |
| `GET` | `/v1/strains/{id}` | Get strain details |
| `PATCH` | `/v1/strains/{id}` | Update strain |

### Devices

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/devices` | List registered devices |
| `POST` | `/v1/devices` | Register a new device |
| `GET` | `/v1/devices/{id}` | Get device details |
| `PATCH` | `/v1/devices/{id}` | Update device (assign to bucket/tent) |
| `DELETE` | `/v1/devices/{id}` | Unregister a device |

### Grow Types

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/grow-types` | List built-in grow types (DWC, Kratky, Soil, etc.) |

### Yields

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/yields` | List harvest yields |
| `POST` | `/v1/yields` | Record a harvest yield |

## AI Endpoints

### Chat (WebSocket)

```
WebSocket /v1/ai/chat?grow_id={uuid}
```

Send messages as JSON:
```json
{"message": "How are my plants doing?"}
```

Receive streamed responses:
```json
{"type": "chunk", "content": "Based on your sensor data..."}
{"type": "done"}
```

The AI assistant has access to:
- Current grow cycle data
- Recent sensor readings and trends
- Journal entries and feeding history
- Tent equipment and configuration
- Previous health evaluations

### Health Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/ai/reports/{grow_id}` | Get latest AI health report |
| `POST` | `/v1/ai/reports/{grow_id}` | Generate a new health report |

## Automation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/automation` | List automation rules |
| `POST` | `/v1/automation` | Create an automation rule |
| `PATCH` | `/v1/automation/{id}` | Update rule |
| `DELETE` | `/v1/automation/{id}` | Delete rule |

## Outdoor Grows

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/grows/{id}/plots` | List outdoor plots |
| `POST` | `/v1/grows/{id}/plots` | Create a plot |
| `GET` | `/v1/grows/{id}/soil-tests` | List soil test results |
| `POST` | `/v1/grows/{id}/soil-tests` | Log a soil test |
| `GET` | `/v1/grows/{id}/pests` | List pest observations |
| `POST` | `/v1/grows/{id}/pests` | Log a pest observation |
| `GET` | `/v1/companion-plants` | Get companion planting suggestions |
| `GET` | `/v1/grows/{id}/runoff` | List runoff readings |
| `POST` | `/v1/grows/{id}/runoff` | Log a runoff reading |
| `GET` | `/v1/outdoor/intelligence` | Get outdoor grow recommendations |

## Integrations

Third-party device and service connectors. Built-in connectors: Pulse Grow, OpenWeather, Ecowitt.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/integrations` | List all integrations for tenant |
| `POST` | `/v1/integrations` | Create integration config |
| `GET` | `/v1/integrations/{id}` | Get single integration |
| `PATCH` | `/v1/integrations/{id}` | Update integration config |
| `DELETE` | `/v1/integrations/{id}` | Delete integration + mappings |
| `POST` | `/v1/integrations/{id}/devices` | Create device mapping |
| `GET` | `/v1/integrations/{id}/devices` | List device mappings |
| `PATCH` | `/v1/integrations/{id}/devices/{device_id}` | Update device mapping |
| `DELETE` | `/v1/integrations/{id}/devices/{device_id}` | Remove device mapping |
| `POST` | `/v1/integrations/webhook/{integration_id}` | Inbound webhook receiver |
| `GET` | `/v1/integrations/{id}/logs` | Sync history |
| `POST` | `/v1/integrations/{id}/sync` | Trigger manual sync |
| `POST` | `/v1/integrations/{id}/discover` | Discover available external devices |

### Integration Types

| Type | Mode | Config Fields |
|------|------|---------------|
| `pulse` | Polling | `api_key` (required), `base_url` (optional) |
| `openweather` | Polling | `api_key` (required), `use_onecall_30` (optional flag), `base_url` (optional) |
| `ecowitt` | Webhook + Polling | `mode` (`webhook`/`cloud`), `application_key`, `api_key`, `mac`, `base_url` |

Credentials are encrypted at rest via Fernet and redacted in API responses.

## Billing

Stripe billing fields (customer ID, subscription ID) are stored on the **Account** model, not the Tenant. One Account can own multiple Tenants.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/billing/status` | Get billing status and plan for current tenant's account |
| `POST` | `/v1/billing/checkout` | Create a Stripe checkout session (Account Owner only) |
| `POST` | `/v1/billing/portal` | Create a Stripe billing portal session (Account Owner only) |
| `POST` | `/v1/billing/webhook` | Stripe webhook handler (called by Stripe) |

## Admin

Platform administration endpoints. Access varies by platform role.

| Method | Endpoint | Required Role | Description |
|--------|----------|---------------|-------------|
| `GET` | `/v1/admin/tenants` | `super_admin`, `support`, `readonly_admin` | List all tenants with member counts |
| `GET` | `/v1/admin/tenants/{id}/users` | `super_admin`, `support`, `readonly_admin` | List users in a specific tenant |
| `GET` | `/v1/admin/users` | `super_admin`, `support`, `readonly_admin` | List all users platform-wide |
| `PATCH` | `/v1/admin/users/{id}/flags` | `super_admin` only | Update a user's platform role |
| `GET` | `/v1/admin/stats` | `super_admin`, `support`, `readonly_admin` | Platform statistics |

### Platform Roles

| Role | Capabilities |
|------|--------------|
| `super_admin` | Full platform access. Can manage all tenants, users, and settings. Can switch to any tenant. |
| `support` | Read-only platform access + can manage user accounts (reset, unlock). Cannot make platform config changes. |
| `readonly_admin` | Read-only access to all platform data. Cannot modify anything. |
| `user` | Standard user. No platform-level permissions. |

## Commercial

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/api-keys` | List API keys |
| `POST` | `/v1/api-keys` | Create an API key |
| `DELETE` | `/v1/api-keys/{id}` | Revoke an API key |
| `GET` | `/v1/audit` | List audit log entries |
| `GET` | `/v1/tasks` | List scheduled/generated tasks |

## Health Check

```http
GET /health
```

Returns `{"status": "ok"}` — no authentication required. Use for load balancer health probes.

## Rate Limiting

The API includes rate limiting middleware. Default limits apply per IP. Authenticated requests may have higher limits. When rate limited, the API returns `429 Too Many Requests`.

## OpenAPI Specification

The full machine-readable API specification is available at:

```
GET /v1/openapi.json
```

Import this into Postman, Insomnia, or any OpenAPI-compatible tool for a complete endpoint reference with request/response schemas.
