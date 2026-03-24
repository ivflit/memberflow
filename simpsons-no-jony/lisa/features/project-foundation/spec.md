# Feature: Project Foundation

**Spec author:** Lisa
**Date:** 2026-03-24
**Status:** Draft — pending Marge review

---

## Problem Statement

MemberFlow has no code. The architecture is defined in `about/ARCHITECTURE.md` but nothing is scaffolded. Before any feature can be built, the project needs a working full-stack skeleton: a Django backend and Vue.js frontend running together in Docker, connected to PostgreSQL and Redis, with the multi-tenant infrastructure in place. Without this foundation, every future feature spec has nowhere to land.

---

## Scope

**In:**
- Django project structure with settings split (`base`, `development`, `production`)
- Docker Compose with `api`, `db`, `redis`, `frontend` services
- `core` Django app: `TenantAwareModel`, `TenantManager`, `TenantMiddleware`
- `organizations` Django app: `Organization` model + migration
- `GET /api/v1/health/` endpoint — returns status and resolved tenant slug
- Vue 3 + Vite frontend: Vue Router (basic), one Pinia store stub, Axios client
- Axios client hits `GET /api/v1/health/` and renders response on the home view
- `manage.py seed_dev` management command — creates a test `Organization(slug="test-club")`
- Seed command runs automatically on `docker compose up` via entrypoint script
- GitHub Actions CI pipeline: `pytest` (backend) + `npm run check` (frontend) on push to `main`
- Python 3.12, Node 20 LTS pinned in Dockerfiles
- Python packages: `django`, `djangorestframework`, `psycopg2-binary`, `django-cors-headers`, `python-decouple`
- Dev-only tenant resolution via `X-Tenant-Slug` request header (when `DEBUG=True`)
- Production tenant resolution via subdomain (always)

**Out:**
- `users`, `memberships`, `payments`, `admin_portal`, `webhooks` apps
- `OrganizationConfig` model (comes with auth/config feature)
- Permission classes (`IsOrgAdmin`, `IsPlatformAdmin`) — come with auth feature
- Celery worker and Beat scheduler services
- Nginx reverse proxy service
- JWT authentication
- Stripe integration
- CI/CD deploy job
- Any business logic

---

## Requirements

### FR-1: Django project scaffolded and running

**Input:** `docker compose up`
**Output:** Django development server running at `http://localhost:8000`, connected to PostgreSQL
**Errors:** Container fails to start if `DATABASE_URL` env var is missing

The project follows the structure defined in `about/ARCHITECTURE.md`:

```
memberflow/
├── config/
│   ├── settings/
│   │   ├── base.py          # shared: INSTALLED_APPS, MIDDLEWARE, DRF defaults
│   │   ├── development.py   # DEBUG=True, reads env vars via python-decouple
│   │   └── production.py    # DEBUG=False, placeholder for prod secrets
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/
│   └── organizations/
├── manage.py
└── requirements.txt
```

`DJANGO_SETTINGS_MODULE` is set via environment variable, defaulting to `config.settings.development`.

---

### FR-2: Multi-tenant middleware

**Input:** Every inbound HTTP request
**Output:** `request.tenant` is set to an `Organization` instance before any view executes
**Errors:**
- `404 {"error": "Organisation not found"}` if slug resolves to no active org
- `400 {"error": "Tenant not specified"}` if no slug can be determined at all

**Resolution logic:**

```python
# Production (DEBUG=False): always use subdomain
host = request.get_host().split(':')[0]   # "springfield-cc.memberflow.com"
slug = host.split('.')[0]                 # "springfield-cc"

# Development (DEBUG=True): prefer X-Tenant-Slug header, fall back to subdomain
if settings.DEBUG:
    slug = request.headers.get('X-Tenant-Slug') or host.split('.')[0]
```

`TenantMiddleware` is registered in `MIDDLEWARE` after `SecurityMiddleware` and before `AuthenticationMiddleware`.

---

### FR-3: TenantAwareModel base class

**Input:** Any model that inherits `TenantAwareModel`
**Output:** That model automatically has `organization` (FK), `created_at`, `updated_at` fields and uses `TenantManager`
**Errors:** N/A — abstract model, enforced at definition time

```python
# core/models.py
class TenantAwareModel(models.Model):
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantManager()

    class Meta:
        abstract = True
```

---

### FR-4: TenantManager

**Input:** `SomeModel.objects.for_tenant(org)`
**Output:** Queryset filtered to `organization=org`
**Errors:** N/A

```python
# core/managers.py
class TenantManager(models.Manager):
    def for_tenant(self, organization):
        return self.get_queryset().filter(organization=organization)
```

---

### FR-5: Organization model

**Input:** N/A (data model)
**Output:** `Organization` table in PostgreSQL with initial migration

```python
# apps/organizations/models.py
class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)      # used for subdomain + header resolution
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
```

No `TenantAwareModel` inheritance — `Organization` IS the tenant, not owned by one.

---

### FR-6: Health check endpoint

**Input:** `GET /api/v1/health/`
**Output:**
```json
{
  "status": "ok",
  "tenant": "test-club"
}
```
**Errors:**
- If `TenantMiddleware` rejects the request: `404 {"error": "Organisation not found"}`
- This endpoint requires a valid tenant to be resolved — it is not public in the sense of bypassing middleware

**Auth:** None — no JWT required. Used to verify Docker networking and tenant resolution only.

---

### FR-7: Seed management command

**Input:** `python manage.py seed_dev`
**Output:**
- Creates `Organization(name="Test Club", slug="test-club", is_active=True)` if it does not already exist
- Prints `[seed_dev] Organisation "test-club" ready.` to stdout
- Is idempotent — running twice does not create duplicates or raise errors

**Errors:** Should not raise. Uses `get_or_create`.

**Auto-run:** The Docker `api` container entrypoint script runs `manage.py migrate` then `manage.py seed_dev` before starting Gunicorn/Django dev server.

---

### FR-8: Vue.js frontend scaffold

**Input:** `docker compose up` (frontend service) or `npm run dev` (local)
**Output:** Vue app running at `http://localhost:5173`

Structure:
```
frontend/
├── src/
│   ├── api/
│   │   └── client.js        # Axios instance, base URL from env var
│   ├── stores/
│   │   └── app.js           # Stub Pinia store (placeholder)
│   ├── router/
│   │   └── index.js         # Vue Router with single route: "/" → HomeView
│   ├── views/
│   │   └── HomeView.vue     # Calls GET /api/v1/health/, renders response
│   ├── App.vue
│   └── main.js
├── .env.development         # VITE_API_BASE_URL=http://localhost:8000
├── package.json
└── vite.config.js
```

`HomeView.vue` on mount calls `GET /api/v1/health/` using the Axios client and renders:
- `"Connected to tenant: test-club"` on success
- `"API unreachable"` on network error

This is the only UI in the foundation. It proves end-to-end Docker wiring.

---

### FR-9: GitHub Actions CI pipeline

**Input:** Push or PR to `main` branch
**Output:** Two jobs run in parallel — `test-backend` and `test-frontend`

**`test-backend` job:**
```
- Checkout code
- Set up Python 3.12
- Install requirements.txt
- Run: pytest (with --tb=short)
```

**`test-frontend` job:**
```
- Checkout code
- Set up Node 20
- npm ci
- npm run check   (lint + type check)
```

Both jobs must pass. If either fails, the pipeline is red. No deploy job.

---

## Data Model

| Model | Table | Key fields |
|---|---|---|
| `Organization` | `organizations_organization` | `id` (UUID PK), `name`, `slug` (unique), `is_active`, `created_at` |

No other models in scope for foundation. All future tenant-owned models will inherit `TenantAwareModel` and gain `organization_id`, `created_at`, `updated_at` automatically.

---

## API

### GET /api/v1/health/

**Auth:** None
**Tenant required:** Yes — request must resolve to an active org via middleware

**Request:** No body

**Response 200:**
```json
{
  "status": "ok",
  "tenant": "test-club"
}
```

**Response 404:**
```json
{
  "error": "Organisation not found"
}
```

**Response 400:**
```json
{
  "error": "Tenant not specified"
}
```

---

## UX Flow

1. Developer runs `docker compose up`
2. `api` container: runs `migrate` → `seed_dev` → starts Django dev server on port 8000
3. `frontend` container: runs `npm run dev` → Vite dev server on port 5173
4. Developer opens `http://localhost:5173`
5. `HomeView` mounts → calls `GET http://localhost:8000/api/v1/health/` with header `X-Tenant-Slug: test-club`
6. Django resolves slug → returns `{"status": "ok", "tenant": "test-club"}`
7. `HomeView` renders: `"Connected to tenant: test-club"`

This is the entire UX of the foundation. It is a developer-facing smoke test, not end-user UI.

---

## Edge Cases

| Case | Behaviour |
|---|---|
| `seed_dev` run twice | `get_or_create` — no duplicate, no error |
| `X-Tenant-Slug` header missing in `DEBUG=True` | Falls back to subdomain parsing |
| Subdomain is not a known org slug | `TenantMiddleware` returns 404 |
| `db` container not yet ready when `api` starts | Entrypoint script retries `migrate` with a wait loop (max 30s) |
| Frontend `VITE_API_BASE_URL` not set | Axios calls fail; `HomeView` renders `"API unreachable"` |
| `is_active=False` org slug used | `TenantMiddleware` returns 404 (filters on `is_active=True`) |

---

## Implementation Patterns

These patterns are referenced by Bart when writing work item Notes.

### Pattern: TenantMiddleware structure

```python
# apps/core/middleware.py
import json
from django.conf import settings
from django.http import JsonResponse
from apps.organizations.models import Organization

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        slug = self._resolve_slug(request)
        if not slug:
            return JsonResponse({'error': 'Tenant not specified'}, status=400)
        try:
            request.tenant = Organization.objects.get(slug=slug, is_active=True)
        except Organization.DoesNotExist:
            return JsonResponse({'error': 'Organisation not found'}, status=404)
        return self.get_response(request)

    def _resolve_slug(self, request):
        if settings.DEBUG:
            header_slug = request.headers.get('X-Tenant-Slug')
            if header_slug:
                return header_slug
        host = request.get_host().split(':')[0]
        parts = host.split('.')
        return parts[0] if len(parts) > 1 else None
```

### Pattern: Docker entrypoint with retry

```bash
#!/bin/sh
# entrypoint.sh
set -e

echo "Waiting for database..."
until python manage.py migrate 2>&1; do
  echo "DB not ready — retrying in 2s"
  sleep 2
done

python manage.py seed_dev
exec "$@"
```

### Pattern: Axios client with env-based base URL

```js
// src/api/client.js
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

export default api
```

### Pattern: Health check view

```python
# apps/organizations/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def health_check(request):
    return Response({
        'status': 'ok',
        'tenant': request.tenant.slug,
    })
```

---

## Test Strategy

### Philosophy: E2E Smoke First

```
🔥 E2E Smoke Tests — PREFERRED: Prove the foundation wires together
📦 Unit Tests     — FOR: TenantMiddleware resolution logic (many edge cases)
```

⚠️ **INTERLEAVING RULE:** Tests are written immediately after the work items they cover — not at the end.

### Test Type by Requirement

| FR | Test Type | Justification |
|---|---|---|
| FR-1: Django scaffold runs | E2E smoke | Prove it starts |
| FR-2: TenantMiddleware | Unit | 6+ resolution edge cases |
| FR-3/4: TenantAwareModel + Manager | Unit | Pure logic, no HTTP |
| FR-5: Organization model | Unit | Model + migration |
| FR-6: Health check endpoint | E2E smoke | Full request cycle |
| FR-7: seed_dev command | Unit | Idempotency check |
| FR-8: Frontend renders health | E2E smoke | End-to-end Docker wiring |
| FR-9: CI pipeline | Manual | Verify on first push |

### Test Phases

| Phase | Test type | File | When |
|---|---|---|---|
| Phase 1: Core infrastructure | Unit | `apps/core/tests/test_middleware.py` | After middleware WIs |
| Phase 2: Organization model | Unit | `apps/organizations/tests/test_models.py` | After model WI |
| Phase 3: Health endpoint | E2E smoke | `apps/organizations/tests/test_views.py` | After health WI |
| Phase 4: Frontend wiring | E2E smoke | Manual browser verification | After frontend WI |

### Regression Tests

None — this is the first code.

### New Tests Required

| Scenario | Type | File |
|---|---|---|
| Middleware resolves slug from `X-Tenant-Slug` header | Unit | `test_middleware.py` |
| Middleware resolves slug from subdomain | Unit | `test_middleware.py` |
| Middleware returns 404 for unknown slug | Unit | `test_middleware.py` |
| Middleware returns 404 for inactive org | Unit | `test_middleware.py` |
| Middleware ignores header in production (`DEBUG=False`) | Unit | `test_middleware.py` |
| `seed_dev` is idempotent | Unit | `test_commands.py` |
| Health check returns 200 with tenant slug | Integration | `test_views.py` |
| Health check returns 404 for unknown org | Integration | `test_views.py` |

### Test Data Requirements

- `seed_dev` command creates `Organization(slug="test-club")` — available for all tests via management command or factory

---

## Open Questions

None — all resolved during interview.
