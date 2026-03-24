# PRD: Project Foundation

**Branch:** `ralph/project-foundation`

## Overview

No runnable codebase exists for MemberFlow. This PRD scaffolds a full-stack skeleton — Django backend and Vue.js frontend running in Docker, connected to PostgreSQL and Redis, with multi-tenant infrastructure in place — so every future feature spec has somewhere to land.

## Source Spec

`simpsons-no-jony/lisa/features/project-foundation/spec.md`

**⚠️ READ THE SPEC — it contains implementation patterns with exact code for TenantMiddleware, entrypoint, Axios client, and health check view.**

## Goals

- `docker compose up` starts all four services (api, db, redis, frontend) cleanly
- `GET /api/v1/health/` returns `{"status": "ok", "tenant": "test-club"}`
- Vue home view renders `"Connected to tenant: test-club"` without errors
- All backend tests pass (`pytest`)
- CI pipeline is green on push to `main`

## Testing Requirements (Applies to ALL Work Items)

**⚠️ MANDATORY GATES — every WI acceptance criteria MUST include both:**

1. ✅ **Backend check:** `docker compose exec api pytest` exits 0 (or `pytest` from `backend/`)
2. ✅ **Frontend check:** `cd frontend && npm run check` exits 0

**If ANY check fails:** Fix before marking WI complete. Do NOT skip.

## Architecture Decision: Vite Proxy (resolves Marge Warning 2)

The frontend uses Vite's dev server proxy to forward `/api/*` requests to the Django backend. This means:
- Browser calls `/api/v1/health/` on `localhost:5173`
- Vite forwards the request to `http://api:8000` (Docker internal network)
- Django sees the request and processes it normally
- **No CORS configuration needed in development** (same-origin from browser's perspective)
- Axios baseURL is `''` (empty) — all API calls use relative paths like `/api/v1/health/`
- `VITE_API_TARGET` env var controls proxy destination: `http://api:8000` in Docker, `http://localhost:8000` outside Docker

---

## Work Items

### WI-001: Docker Compose + Dockerfiles

**Priority:** 1
**Effort:** M
**Status:** ❌ Not started

**Description:** Create the Docker Compose file and Dockerfiles for all four services. This is the container skeleton everything else runs inside. No application code yet — just infrastructure wiring.

**Acceptance Criteria:**
- [ ] `docker-compose.yml` defines `api`, `db`, `redis`, `frontend` services
- [ ] `api` service: builds from `backend/Dockerfile`, mounts `./backend` as volume, exposes port 8000, depends on `db` and `redis`
- [ ] `db` service: `postgres:15`, env vars `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, named volume for persistence
- [ ] `redis` service: `redis:7-alpine`
- [ ] `frontend` service: builds from `frontend/Dockerfile`, mounts `./frontend/src` as volume, exposes port 5173
- [ ] `backend/Dockerfile`: `FROM python:3.12-slim`, installs requirements, copies app, sets `PYTHONUNBUFFERED=1`
- [ ] `frontend/Dockerfile`: `FROM node:20-alpine`, runs `npm ci`, starts `npm run dev -- --host`
- [ ] `.env.example` lists all required env vars with placeholder values
- [ ] `backend/entrypoint.sh` exists (skeleton: just `exec "$@"` for now — seed logic added in WI-007)
- [ ] `docker compose up` starts without error (Django not yet installed — verify containers start, db accepts connections)
- [ ] `cd frontend && npm run check` exits 0 (no frontend code yet — verify npm scripts exist)

**Notes:**
- **Pattern:** Standard Django + Vite Docker Compose setup; no special patterns in spec for this WI
- **Reference:** This is the first file — no existing file to extend
- **Hook point:** `docker-compose.yml` at repo root; `backend/Dockerfile`, `frontend/Dockerfile` in respective dirs
- **Decision:** `api` service does NOT expose port 8000 to host — all browser traffic goes through Vite proxy on port 5173. Port 8000 is only accessible inside the Docker network.

---

### WI-002: Django project structure + settings + requirements

**Priority:** 2
**Effort:** M
**Status:** ❌ Not started

**Description:** Scaffold the Django project skeleton: settings split across three files, URL config, WSGI, manage.py, and requirements.txt. Resolves Marge Warnings 3 and 4 — CORS and SECRET_KEY are explicitly configured here.

**Acceptance Criteria:**
- [ ] `backend/requirements.txt` contains: `django`, `djangorestframework`, `psycopg2-binary`, `django-cors-headers`, `python-decouple`
- [ ] `backend/config/settings/base.py` contains: `INSTALLED_APPS` (django built-ins + `rest_framework` + `corsheaders` + `apps.core` + `apps.organizations`), `MIDDLEWARE` (SecurityMiddleware first, corsheaders, placeholder for TenantMiddleware), `REST_FRAMEWORK` defaults
- [ ] `backend/config/settings/development.py` contains: `DEBUG = True`, `SECRET_KEY = config('SECRET_KEY', default='dev-insecure-key-change-in-prod')`, `ALLOWED_HOSTS = ['*']`, `DATABASES` from `DATABASE_URL` env via `python-decouple`, `CORS_ALLOWED_ORIGINS = ['http://localhost:5173']`
- [ ] `backend/config/settings/production.py` is a stub: imports base, `DEBUG = False`, comments for `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASES` to be filled later
- [ ] `backend/config/urls.py` has `urlpatterns = [path('admin/', admin.site.urls)]` (API routes added per feature)
- [ ] `backend/config/wsgi.py` exists
- [ ] `backend/manage.py` exists and references `config.settings.development` as default
- [ ] `DJANGO_SETTINGS_MODULE` env var in `docker-compose.yml` api service set to `config.settings.development`
- [ ] `docker compose exec api python manage.py check` exits 0
- [ ] `docker compose exec api pytest` exits 0 (no tests yet — verify pytest is importable)

**Notes:**
- **Pattern:** `python-decouple` reads from `.env` file and environment variables; `config('KEY')` syntax
- **Reference:** No existing file — first Django setup
- **Hook point:** `MIDDLEWARE` list in `base.py` — TenantMiddleware will be inserted here in WI-005
- **Marge Warning 3 resolved:** `CORS_ALLOWED_ORIGINS = ['http://localhost:5173']` in `development.py` (not needed with Vite proxy but present as fallback for direct API calls e.g. from tests)
- **Marge Warning 4 resolved:** `SECRET_KEY` via `python-decouple` with insecure dev default; `ALLOWED_HOSTS = ['*']` in development

---

### 🚦 INTEGRATION GATE: Django Project Starts

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Run: `docker compose up api db`
2. [ ] Run: `docker compose exec api python manage.py check`
3. [ ] Expected: `System check identified no issues (0 silenced).`
4. [ ] Evidence: Write `VERIFIED: manage.py check passes @ [timestamp]` in `learnings.md`

**If gate fails:** Check `INSTALLED_APPS`, `DATABASES` config, and that `psycopg2-binary` is installed.

---

### WI-003: core app — TenantAwareModel + TenantManager

**Priority:** 3
**Effort:** M
**Status:** ❌ Not started

**Description:** Create the `core` Django app with the two base classes every future tenant-owned model will inherit. No migrations — `TenantAwareModel` is abstract.

**Acceptance Criteria:**
- [ ] `backend/apps/core/__init__.py` exists
- [ ] `backend/apps/core/apps.py` defines `CoreConfig` with `name = 'apps.core'`
- [ ] `backend/apps/core/managers.py` defines `TenantManager(models.Manager)` with `for_tenant(self, organization)` method returning filtered queryset
- [ ] `backend/apps/core/models.py` defines `TenantAwareModel(models.Model)` as abstract, with `organization` FK to `'organizations.Organization'` (`db_index=True`, `on_delete=CASCADE`), `created_at` (`auto_now_add`), `updated_at` (`auto_now`), `objects = TenantManager()`
- [ ] `apps.core` is in `INSTALLED_APPS` (already added in WI-002)
- [ ] `docker compose exec api python manage.py check` still exits 0
- [ ] `docker compose exec api pytest` exits 0

**Notes:**
- **Pattern:** See spec "Implementation Patterns → TenantAwareModel base class" for exact code
- **Reference:** `backend/config/settings/base.py:INSTALLED_APPS` — `apps.core` already listed
- **Hook point:** `backend/apps/core/models.py` — all future models import and inherit from here

---

### WI-004: organizations app — Organization model + migration

**Priority:** 4
**Effort:** S
**Status:** ❌ Not started

**Description:** Create the `organizations` Django app with the `Organization` model (the tenant entity) and run its initial migration. This creates the table everything else pivots around.

**Acceptance Criteria:**
- [ ] `backend/apps/organizations/__init__.py`, `apps.py`, `models.py` exist
- [ ] `Organization` model has: `id` (UUIDField, PK, `default=uuid.uuid4`), `name` (CharField 255), `slug` (SlugField, unique), `is_active` (BooleanField, `default=True`), `created_at` (DateTimeField, `auto_now_add`)
- [ ] `Organization.__str__` returns `self.name`
- [ ] `Organization` does NOT inherit `TenantAwareModel` (it IS the tenant)
- [ ] `apps.organizations` in `INSTALLED_APPS`
- [ ] `docker compose exec api python manage.py makemigrations organizations` produces `0001_initial.py`
- [ ] `docker compose exec api python manage.py migrate` exits 0
- [ ] `docker compose exec api pytest` exits 0

**Notes:**
- **Pattern:** See spec "FR-5: Organization model" for exact field definitions
- **Reference:** `backend/apps/core/models.py` — do NOT inherit from here
- **Hook point:** `backend/apps/organizations/models.py` — `TenantMiddleware` (WI-005) imports this model

---

### 🚦 INTEGRATION GATE: Database Foundation

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Run: `docker compose exec api python manage.py migrate`
2. [ ] Run: `docker compose exec api python manage.py shell -c "from apps.organizations.models import Organization; print(Organization._meta.db_table)"`
3. [ ] Expected: `organizations_organization`
4. [ ] Evidence: Write `VERIFIED: Organization table exists @ [timestamp]` in `learnings.md`

**If gate fails:** Check `INSTALLED_APPS` includes `apps.organizations`, migration file was generated.

---

### WI-005: TenantMiddleware

**Priority:** 5
**Effort:** M
**Status:** ❌ Not started

**Description:** Implement `TenantMiddleware` in `core` — the gatekeeper for every request. Resolves tenant from `X-Tenant-Slug` header (dev) or subdomain (production) and attaches `request.tenant`. Rejects unknown or inactive tenants before any view runs.

**Acceptance Criteria:**
- [ ] `backend/apps/core/middleware.py` implements `TenantMiddleware` with `__init__` and `__call__`
- [ ] `_resolve_slug` method: in `DEBUG=True` mode, checks `X-Tenant-Slug` header first, falls back to subdomain; in `DEBUG=False` mode, subdomain only
- [ ] Returns `JsonResponse({'error': 'Tenant not specified'}, status=400)` if no slug resolved
- [ ] Returns `JsonResponse({'error': 'Organisation not found'}, status=404)` if slug doesn't match an active org
- [ ] Sets `request.tenant = Organization.objects.get(slug=slug, is_active=True)` on success
- [ ] Registered in `base.py` `MIDDLEWARE` after `SecurityMiddleware`, before `AuthenticationMiddleware`
- [ ] `docker compose exec api python manage.py check` exits 0
- [ ] `docker compose exec api pytest` exits 0

**Notes:**
- **Pattern:** See spec "Implementation Patterns → TenantMiddleware structure" for complete code
- **Reference:** `backend/apps/core/middleware.py` (new file), `backend/config/settings/base.py:MIDDLEWARE` (edit)
- **Hook point:** `MIDDLEWARE` list in `base.py` — insert as `'apps.core.middleware.TenantMiddleware'`

---

### WI-006: Health check endpoint

**Priority:** 6
**Effort:** S
**Status:** ❌ Not started

**Description:** Add `GET /api/v1/health/` — a single view that returns the resolved tenant slug. Proves middleware is working and the request cycle is complete. No auth required.

**Acceptance Criteria:**
- [ ] `backend/apps/organizations/views.py` defines `health_check` using `@api_view(['GET'])`
- [ ] View returns `Response({'status': 'ok', 'tenant': request.tenant.slug})` with status 200
- [ ] `backend/apps/organizations/urls.py` maps `GET ''` to `health_check`
- [ ] `backend/config/urls.py` includes `apps.organizations.urls` under `api/v1/health/`
- [ ] `curl -H "X-Tenant-Slug: test-club" http://localhost:8000/api/v1/health/` returns `{"status": "ok", "tenant": "test-club"}`
- [ ] `curl http://localhost:8000/api/v1/health/` (no header, no subdomain) returns 400 or 404
- [ ] `docker compose exec api pytest` exits 0

**Notes:**
- **Pattern:** See spec "Implementation Patterns → Health check view" for exact code
- **Reference:** `backend/apps/organizations/views.py` (new), `backend/config/urls.py` (edit)
- **Hook point:** `backend/config/urls.py:urlpatterns` — add `path('api/v1/health/', include('apps.organizations.urls'))`

---

### 🚦 INTEGRATION GATE: API Layer

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Run: `docker compose up api db`
2. [ ] Run: `curl -s -H "X-Tenant-Slug: test-club" http://localhost:8000/api/v1/health/`
3. [ ] Expected: `{"status": "ok", "tenant": "test-club"}`
4. [ ] Run: `curl -s http://localhost:8000/api/v1/health/` (no header)
5. [ ] Expected: 400 or 404 response
6. [ ] Evidence: Write `VERIFIED: health check responds correctly @ [timestamp]` in `learnings.md`

**If gate fails:** Check TenantMiddleware is registered in MIDDLEWARE, seed org doesn't exist yet (expected — 404 is correct at this point).

---

### WI-007: seed_dev management command + entrypoint

**Priority:** 7
**Effort:** M
**Status:** ❌ Not started

**Description:** Create the `seed_dev` management command that creates the test organisation, and wire the entrypoint script to run `migrate` + `seed_dev` automatically on container start with a DB readiness retry loop.

**Acceptance Criteria:**
- [ ] `backend/apps/organizations/management/__init__.py` and `commands/__init__.py` exist
- [ ] `backend/apps/organizations/management/commands/seed_dev.py` defines `Command(BaseCommand)`
- [ ] `handle()` calls `Organization.objects.get_or_create(slug='test-club', defaults={'name': 'Test Club', 'is_active': True})`
- [ ] Prints `[seed_dev] Organisation "test-club" ready.` to stdout regardless of create/get
- [ ] Running `seed_dev` twice does not raise an error or create a duplicate
- [ ] `backend/entrypoint.sh` updated: retry loop (up to 15 attempts, 2s sleep) runs `python manage.py migrate`, then `python manage.py seed_dev`, then `exec "$@"`
- [ ] `docker-compose.yml` api service uses `entrypoint: ["/app/entrypoint.sh"]` and `command: python manage.py runserver 0.0.0.0:8000`
- [ ] After `docker compose up`, `curl -s -H "X-Tenant-Slug: test-club" http://localhost:8000/api/v1/health/` returns `{"status":"ok","tenant":"test-club"}`
- [ ] `docker compose exec api pytest` exits 0

**Notes:**
- **Pattern:** See spec "Implementation Patterns → Docker entrypoint with retry" for entrypoint.sh shell script
- **Reference:** `backend/entrypoint.sh` (update from WI-001 skeleton), `backend/apps/organizations/management/` (new)
- **Hook point:** `docker-compose.yml:services.api.entrypoint` + `command`

---

### 🚦 INTEGRATION GATE: Full Backend Working

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Run: `docker compose up` (all services)
2. [ ] Wait for `[seed_dev] Organisation "test-club" ready.` in api logs
3. [ ] Run: `curl -s -H "X-Tenant-Slug: test-club" http://localhost:8000/api/v1/health/`
4. [ ] Expected: `{"status": "ok", "tenant": "test-club"}`
5. [ ] Evidence: Write `VERIFIED: full backend working, test-club org seeded @ [timestamp]` in `learnings.md`

**If gate fails:** Check entrypoint.sh is executable (`chmod +x`), retry loop logic, seed_dev command path.

---

### WI-008: Unit tests — TenantMiddleware

**Priority:** 8
**Effort:** M
**Status:** ❌ Not started

**Description:** Write unit tests for all TenantMiddleware resolution paths. Five test scenarios covering the full decision tree. Written immediately after the middleware is working — not at the end.

**Acceptance Criteria:**
- [ ] `backend/apps/core/tests/__init__.py` exists
- [ ] `backend/apps/core/tests/test_middleware.py` exists with `pytest.ini` or `setup.cfg` configuring `DJANGO_SETTINGS_MODULE`
- [ ] Test: header `X-Tenant-Slug: test-club` with `DEBUG=True` → `request.tenant.slug == 'test-club'`
- [ ] Test: no header, subdomain `test-club.localhost` with `DEBUG=True` → `request.tenant.slug == 'test-club'`
- [ ] Test: unknown slug → response status 404, body `{"error": "Organisation not found"}`
- [ ] Test: `is_active=False` org slug → response status 404
- [ ] Test: `DEBUG=False`, `X-Tenant-Slug` header present → header is ignored, subdomain used instead
- [ ] All 5 tests pass: `docker compose exec api pytest apps/core/tests/test_middleware.py -v`
- [ ] `docker compose exec api pytest` exits 0

**Notes:**
- **Pattern:** Use `pytest-django` with `@pytest.mark.django_db` and `RequestFactory` or `APIRequestFactory` to build requests without a running server
- **Reference:** `backend/apps/core/middleware.py` — tests exercise `TenantMiddleware.__call__` directly
- **Hook point:** `backend/apps/core/tests/test_middleware.py` — new file, no existing test to extend

---

### WI-009: Tests — Organization model, health endpoint, seed_dev

**Priority:** 9
**Effort:** M
**Status:** ❌ Not started

**Description:** Write tests for the Organization model, health check view, and seed_dev command idempotency. Covers all remaining test scenarios from the spec's test strategy.

**Acceptance Criteria:**
- [ ] `backend/apps/organizations/tests/__init__.py` exists
- [ ] `backend/apps/organizations/tests/test_models.py`: test `Organization` creates with UUID PK, `slug` is unique (duplicate raises `IntegrityError`), `__str__` returns name
- [ ] `backend/apps/organizations/tests/test_views.py`: test health check returns 200 + correct JSON when valid tenant in request; test returns 404 when middleware blocks (unknown org)
- [ ] `backend/apps/organizations/tests/test_commands.py`: test `seed_dev` creates org on first run; test `seed_dev` twice does not raise and does not create duplicate
- [ ] `backend/pytest.ini` (or `setup.cfg`) exists, sets `DJANGO_SETTINGS_MODULE = config.settings.development` and `python_files = tests/test_*.py`
- [ ] All tests pass: `docker compose exec api pytest -v`
- [ ] `docker compose exec api pytest` exits 0

**Notes:**
- **Pattern:** Use `pytest-django`, `@pytest.mark.django_db`, `APIClient` from DRF test utils for view tests
- **Reference:** `backend/apps/core/tests/test_middleware.py` (WI-008) — follow same test structure
- **Hook point:** `backend/apps/organizations/tests/` — new directory

---

### 🚦 INTEGRATION GATE: All Backend Tests Pass

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Run: `docker compose exec api pytest -v`
2. [ ] Expected: all tests pass, 0 failures, 0 errors
3. [ ] Count: should be at least 10 test scenarios across middleware, model, views, commands
4. [ ] Evidence: Write `VERIFIED: pytest passes, X tests in Ys @ [timestamp]` in `learnings.md`

**If gate fails:** Fix failing tests before touching frontend. Do NOT skip.

---

### WI-010: Vue.js frontend scaffold

**Priority:** 10
**Effort:** M
**Status:** ❌ Not started

**Description:** Scaffold the Vue.js frontend: package.json, Vite config with proxy (resolving Marge Warning 2), Vue Router, Pinia store stub, and main.js. No views yet — just the skeleton with npm scripts working.

**Acceptance Criteria:**
- [ ] `frontend/package.json` has dependencies: `vue@^3`, `vue-router@^4`, `pinia`, `axios`; devDependencies: `vite`, `@vitejs/plugin-vue`, `eslint`, `eslint-plugin-vue`
- [ ] `frontend/package.json` scripts: `dev` (`vite`), `build` (`vite build`), `check` (`eslint src/`)
- [ ] `frontend/vite.config.js` configures `@vitejs/plugin-vue` and proxy: `/api` → `process.env.VITE_API_TARGET || 'http://localhost:8000'` with `changeOrigin: true`
- [ ] `frontend/.env.development` sets `VITE_API_TARGET=http://api:8000` (Docker internal hostname)
- [ ] `frontend/src/main.js` creates Vue app, uses router and pinia, mounts to `#app`
- [ ] `frontend/src/App.vue` contains `<router-view />`
- [ ] `frontend/src/router/index.js` creates router with `createWebHistory`, single route `'/'` → `HomeView` (lazy-loaded)
- [ ] `frontend/src/stores/app.js` exports a stub Pinia store (`defineStore('app', { state: () => ({}) })`)
- [ ] `frontend/src/views/HomeView.vue` exists (stub — just renders `<div>Loading...</div>` for now)
- [ ] `cd frontend && npm run check` exits 0
- [ ] `docker compose exec api pytest` exits 0

**Notes:**
- **Pattern:** Vite proxy config: `server.proxy['/api'] = { target: process.env.VITE_API_TARGET, changeOrigin: true }`
- **Reference:** No existing frontend — new scaffold
- **Hook point:** `frontend/vite.config.js:server.proxy` — this is the key decision from Marge Warning 2
- **VITE_API_TARGET in Docker:** `http://api:8000` uses Docker service name; outside Docker `http://localhost:8000` is the default

---

### WI-011: Axios client + HomeView with health check

**Priority:** 11
**Effort:** M
**Status:** ❌ Not started

**Description:** Wire up the Axios client and implement `HomeView` to call the health check endpoint and render the response. This is the end-to-end proof that frontend → Vite proxy → Django → TenantMiddleware → response → Vue render all work together.

**Acceptance Criteria:**
- [ ] `frontend/src/api/client.js` creates Axios instance with `baseURL: ''` (empty — all calls are relative, Vite proxy handles routing), `Content-Type: application/json` header, and `X-Tenant-Slug: test-club` header hardcoded for development
- [ ] `frontend/src/views/HomeView.vue` on `onMounted`: calls `GET /api/v1/health/` via Axios client
- [ ] On success: renders `"Connected to tenant: [slug]"` (e.g. `"Connected to tenant: test-club"`)
- [ ] On network error: renders `"API unreachable"`
- [ ] `cd frontend && npm run check` exits 0
- [ ] `docker compose exec api pytest` exits 0

**Notes:**
- **Pattern:** See spec "Implementation Patterns → Axios client" — adapt to use empty baseURL since proxy handles routing
- **Reference:** `frontend/src/api/client.js` (new), `frontend/src/views/HomeView.vue` (update stub from WI-010)
- **Hook point:** `HomeView.vue:onMounted` — import and call `client.get('/api/v1/health/')`
- **X-Tenant-Slug header:** Hardcoded to `test-club` via `import.meta.env.VITE_TENANT_SLUG` (set in `.env.development`) — this will be replaced by subdomain-based resolution in production

---

### 🚦 INTEGRATION GATE: Full Stack Wiring

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Run: `docker compose up` (all four services)
2. [ ] Open browser: `http://localhost:5173`
3. [ ] Expected: page renders `"Connected to tenant: test-club"`
4. [ ] Open browser DevTools → Network tab → confirm `/api/v1/health/` returns 200
5. [ ] Stop the `api` service: `docker compose stop api`
6. [ ] Reload browser
7. [ ] Expected: page renders `"API unreachable"`
8. [ ] Evidence: Write `VERIFIED: full stack wiring works, frontend renders tenant @ [timestamp]` in `learnings.md`

**If gate fails:** Check Vite proxy config, `VITE_API_TARGET` env var, `X-Tenant-Slug` header in Axios client.

---

### WI-012: GitHub Actions CI pipeline

**Priority:** 12
**Effort:** M
**Status:** ❌ Not started

**Description:** Add the GitHub Actions workflow that runs backend tests and frontend checks in parallel on every push to `main`. Failing tests block merges from day one.

**Acceptance Criteria:**
- [ ] `.github/workflows/ci.yml` exists
- [ ] Triggers on `push` and `pull_request` to `main`
- [ ] `test-backend` job: `runs-on: ubuntu-latest`, sets up Python 3.12, `pip install -r backend/requirements.txt`, sets `DJANGO_SETTINGS_MODULE=config.settings.development` and `DATABASE_URL=sqlite:///test.db` env vars, runs `cd backend && pytest --tb=short`
- [ ] `test-frontend` job: `runs-on: ubuntu-latest`, sets up Node 20, runs `cd frontend && npm ci && npm run check`
- [ ] Both jobs run in parallel (no `needs:` dependency between them)
- [ ] Pushing to `main` triggers the workflow and both jobs pass
- [ ] `cd frontend && npm run check` exits 0
- [ ] `docker compose exec api pytest` exits 0

**Notes:**
- **Pattern:** Standard GitHub Actions matrix — two independent jobs in one workflow file
- **Reference:** No existing CI — new file
- **Hook point:** `.github/workflows/ci.yml` — new file at repo root level
- **SQLite for CI:** Backend tests use `DATABASE_URL=sqlite:///test.db` in CI to avoid spinning up PostgreSQL. `python-decouple` reads this from the env var.

---

### 🚦 INTEGRATION GATE: CI Passes

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Push branch `ralph/project-foundation` to GitHub
2. [ ] Open GitHub Actions tab → confirm workflow triggered
3. [ ] Both `test-backend` and `test-frontend` jobs show green ✅
4. [ ] Evidence: Write `VERIFIED: CI green on first push, both jobs pass @ [timestamp]` in `learnings.md`

**If gate fails:** Check workflow YAML indentation, env var names, working directory in `run:` steps.

---

## Functional Requirements Summary

- FR-1: Django project scaffolded and running in Docker
- FR-2: TenantMiddleware resolves org from header (dev) or subdomain (prod)
- FR-3: TenantAwareModel — abstract base for all tenant-owned models
- FR-4: TenantManager — `.for_tenant(org)` queryset filtering
- FR-5: Organization model — UUID PK, slug, is_active, migration
- FR-6: `GET /api/v1/health/` returns `{"status": "ok", "tenant": "<slug>"}`
- FR-7: `manage.py seed_dev` — idempotent, auto-runs on container start
- FR-8: Vue 3 + Vite, Vite proxy to Django, HomeView renders health response
- FR-9: GitHub Actions CI — pytest + npm run check, parallel jobs

## Non-Goals

- Users, memberships, payments, webhooks — future features
- JWT authentication — future feature
- Nginx reverse proxy — future feature
- Celery workers and Beat — future feature
- Stripe — future feature
- CI deploy job — future feature
- Any business logic whatsoever

## Success Metrics

`docker compose up` starts all four services cleanly, `GET /api/v1/health/` returns `{"status": "ok", "tenant": "test-club"}`, and the Vue home view at `http://localhost:5173` renders `"Connected to tenant: test-club"` without errors.
