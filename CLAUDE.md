# CLAUDE.md — MemberFlow

This file is the primary reference for Claude Code working in this repository. Read it fully before touching any code. When in doubt, re-read the relevant section rather than guessing.

---

## Project Overview

MemberFlow is a **multi-tenant** membership and payments SaaS platform for small sports clubs and community organisations. Each club (tenant) gets a fully isolated environment — their own members, tiers, payments, config, and Stripe account.

Full product context: [`about/PURPOSE.md`](about/PURPOSE.md)
Full technical design: [`about/ARCHITECTURE.md`](about/ARCHITECTURE.md)

**These two documents are the source of truth.** If this CLAUDE.md contradicts them, the `about/` docs win. If you make architectural changes, update `about/ARCHITECTURE.md` as part of that work.

---

## Repository Structure

```
memberflow/
├── about/
│   ├── PURPOSE.md              # Product overview — what it is and why
│   └── ARCHITECTURE.md         # Full technical architecture (read this)
├── simpsons-no-jony/           # Agent workflow system (see section below)
│   ├── lisa/                   # Feature spec interviewer
│   ├── marge/                  # Spec QA reviewer
│   ├── bart/                   # PRD generator
│   ├── chief/                  # PRD quality control
│   └── ralph/                  # Autonomous executor
│       ├── todo/               # PRDs queued for execution
│       ├── inprogress/         # PRDs currently being executed
│       ├── completed/          # Finished PRDs
│       └── analysis/           # Research and analysis outputs
├── CLAUDE.md                   # This file
└── [backend/ and frontend/ once scaffolded]
```

---

## Tech Stack (Quick Reference)

| Layer | Technology |
|---|---|
| Backend framework | Django 4.x + Django REST Framework |
| Database | PostgreSQL 15 |
| Auth | djangorestframework-simplejwt |
| Payments | Stripe Python SDK + Stripe Connect |
| Task queue | Celery 5.x + Redis |
| Web server | Gunicorn behind Nginx |
| Frontend | Vue.js 3 (Composition API) + Vite |
| Frontend state | Pinia |
| HTTP client | Axios |
| Containerisation | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Hosting | DigitalOcean (Managed PostgreSQL, Managed Redis, Spaces CDN) |

---

## The Most Important Rule: Multi-Tenancy

**Multi-tenancy is a non-negotiable constraint at every layer.** Every piece of code you write must be tenant-scoped. There are no exceptions.

### The five rules of tenant safety

**1. Every tenant-owned model inherits `TenantAwareModel`**

```python
# CORRECT
class Membership(TenantAwareModel):
    ...

# WRONG — will create a global table with no tenant scoping
class Membership(models.Model):
    ...
```

**2. Every DRF view that touches tenant data uses `TenantScopedViewMixin`**

```python
# CORRECT
class MembershipListView(TenantScopedViewMixin, generics.ListAPIView):
    queryset = Membership.objects.all()      # mixin filters this automatically

# WRONG — returns data for ALL tenants
class MembershipListView(generics.ListAPIView):
    queryset = Membership.objects.all()
```

**3. Never resolve the tenant in a view — it comes from `request.tenant`**

```python
# CORRECT — TenantMiddleware set this before the view ran
org = self.request.tenant

# WRONG — view is doing work the middleware already did
org = Organization.objects.get(slug=self.request.headers.get('X-Org'))
```

**4. Celery tasks always receive `organization_id` explicitly**

```python
# CORRECT
@app.task
def send_expiry_reminder(membership_id: int, organization_id: str):
    org = Organization.objects.get(id=organization_id)
    membership = Membership.objects.for_tenant(org).get(id=membership_id)
    ...

# WRONG — no tenant context; task could process the wrong data
@app.task
def send_expiry_reminder(membership_id: int):
    membership = Membership.objects.get(id=membership_id)
    ...
```

**5. `User.email` is unique per organisation, not globally**

```python
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=['organization', 'email'],
            name='unique_email_per_org'
        )
    ]
```

### What a cross-tenant data leak looks like

A cross-tenant data leak is when one club can read or modify another club's data. This is the most serious class of bug in this codebase. It is caused by:

- A view that queries without `for_tenant()` filtering
- A task that looks up records by ID without scoping to the org
- A queryset that uses `.get(id=...)` instead of `.for_tenant(org).get(id=...)`
- An admin endpoint that doesn't check `IsOrgAdmin` permission

When writing a new view or task, ask yourself: "if I call this with a valid ID from a different org, does it return data?" If yes, it is broken.

---

## Backend Conventions

### Django App Structure

```
apps/
├── organizations/     # Organization, OrganizationConfig — the tenant layer
├── users/             # User, UserOrganizationRole — scoped to org
├── memberships/       # MembershipTier, Membership — scoped to org
├── payments/          # Payment, Subscription — scoped to org
├── admin_portal/      # Org-admin and platform-admin endpoints
└── webhooks/          # Stripe webhook receiver (per-tenant)

core/
├── models.py          # TenantAwareModel — base for all tenant-owned models
├── middleware.py      # TenantMiddleware — resolves org from subdomain
├── managers.py        # TenantManager — provides .for_tenant(org) on querysets
├── mixins.py          # TenantScopedViewMixin — enforces scoping in DRF views
└── permissions.py     # IsOrgAdmin, IsPlatformAdmin, IsOwnerOrOrgAdmin
```

### Models

- All tenant-owned models inherit `TenantAwareModel` (provides `organization`, `created_at`, `updated_at`)
- Use UUIDs for primary keys on `Organization` and `User`; integer PKs are fine for other models
- `Payment` records are **append-only** — never update or delete payment records, only change `status`
- Add `db_index=True` on fields used in frequent filters: `status`, `expiry_date`, `stripe_subscription_id`
- Always add `Meta.indexes` for composite query patterns: `(organization_id, status)`, `(organization_id, expiry_date)`

### Serializers

- Never expose `organization` or `organization_id` in response bodies to members — tenant context is implicit
- Admin serializers are separate from member-facing serializers; never reuse them across permission levels
- Always validate that FKs in request bodies belong to the current tenant (e.g. `tier_id` must belong to `request.tenant`)

### Views

- Use class-based views (DRF generics or `APIView`)
- `TenantScopedViewMixin` goes on the **left** of the inheritance list
- Separate views for org-admin and platform-admin; never use conditional logic on role inside a view to decide what data to return

### URL patterns

```
/api/v1/config/                        # Public — returns OrganizationConfig
/api/v1/auth/                          # Auth endpoints
/api/v1/memberships/                   # Member-facing
/api/v1/payments/                      # Member-facing
/api/v1/admin/                         # Org admin (IsOrgAdmin permission)
/api/v1/platform/                      # Platform admin (IsPlatformAdmin permission)
/api/v1/webhooks/stripe/<org_slug>/    # Stripe webhooks — no JWT, Stripe sig validation
```

### Stripe

- All Stripe API calls specify `stripe_account=org.config.stripe_account_id` (Connect)
- Never make a Stripe call without the connected account — all money belongs to the club, not the platform
- Webhook handler resolves org from `org_slug` in the URL, then validates signature using `org.config.stripe_webhook_secret`
- Queue the Celery task immediately and return 200 to Stripe — do not process inside the webhook view

### Celery Tasks

- All tasks in `tasks/` module, organised by domain: `tasks/membership.py`, `tasks/email.py`, `tasks/webhooks.py`
- Tasks are **idempotent** — safe to retry. Use `event_id` or similar to prevent double-processing
- Use `bind=True` and `self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))` for retries with exponential backoff
- Periodic tasks (Celery Beat) iterate over `Organization.objects.filter(is_active=True)` and fan out per-tenant sub-tasks — never query globally across all tenants in a single task

### Settings

- Never hardcode secrets — use environment variables
- Settings split: `config/settings/base.py`, `development.py`, `production.py`
- `INSTALLED_APPS` order: Django built-ins → third-party → local apps
- `MIDDLEWARE` order: SecurityMiddleware → TenantMiddleware → AuthenticationMiddleware → ...

---

## Frontend Conventions

### Tenant Bootstrap

The app bootstraps tenant config **before mounting**. This is non-negotiable — feature flags and branding must be available before any component renders.

```js
// main.js
const tenantStore = useTenantStore()
await tenantStore.bootstrap()   // blocks until GET /api/v1/config/ resolves
app.mount('#app')
```

### API Layer

- All HTTP calls go through `src/api/` service modules — never call Axios directly from a component or store
- One service file per domain: `auth.js`, `memberships.js`, `payments.js`
- The shared `src/api/client.js` Axios instance handles: base URL, JWT attachment, 401 → token refresh → retry

### Stores (Pinia)

- `auth` store: user identity, role, token lifecycle
- `tenant` store: `OrganizationConfig`, feature flags (`isFeatureEnabled(flag)`), branding
- `membership` store: current user's membership state

### Feature Flags

Gate routes and components through the tenant store, not hardcoded conditions:

```js
// In router
beforeEnter: () => {
    if (!useTenantStore().isFeatureEnabled('waitlist')) return '/dashboard'
}

// In component
<template>
  <WaitlistPanel v-if="tenant.isFeatureEnabled('waitlist')" />
</template>
```

### JWT Handling

- `access` token: stored in Pinia (memory only — not localStorage, not sessionStorage)
- `refresh` token: stored in `localStorage`
- JWT payload contains `organization_id` — the Axios interceptor cross-checks this matches the current subdomain on sensitive operations

### Router Guards

Four guard levels, checked in order:

1. `requiresAuth` — must be authenticated
2. `requiresOrgAdmin` — must have org_admin or org_staff role in this org
3. `requiresPlatformAdmin` — must have platform_admin role
4. `feature` — feature flag must be enabled for this tenant

---

## Testing

### Philosophy

Prefer **E2E smoke tests** over unit tests. A test that proves a feature works end-to-end for a real user is more valuable than isolated unit tests. Unit tests are for complex algorithmic logic only.

| Scenario | Test type |
|---|---|
| New feature works | E2E smoke |
| CRUD operations | E2E smoke |
| Form submission flow | E2E smoke |
| Membership state transitions (complex) | Unit |
| Stripe webhook event routing | Unit |
| Price calculation with many edge cases | Unit |
| Pure utility functions | Unit |

### Tenant Isolation Tests (MANDATORY)

Every new endpoint must have a test that verifies cross-tenant access is blocked:

```python
def test_cannot_access_other_org_membership(self):
    """A member of org A cannot retrieve org B's membership data."""
    response = self.client_org_a.get(f'/api/v1/memberships/{self.membership_org_b.id}/')
    self.assertEqual(response.status_code, 404)
```

This test pattern is required for every resource endpoint. A missing tenant isolation test is a missing test, not an optional test.

### Backend Tests

- Use `pytest` + `pytest-django`
- Test files mirror app structure: `apps/memberships/tests/test_views.py`
- Use factory classes (factory_boy) for test data — never raw `Model.objects.create()` in multiple test methods
- Each test class sets up its own `Organization` — never share tenant state between test classes

### Frontend Tests

- Use `Vitest` for unit tests
- E2E tests use the agent-browser framework with Page Object Model pattern (see `simpsons-no-jony/ralph/SKILL.md`)
- E2E tests live in `frontend/tests/e2e/[feature]/[name].test.ts`

---

## The Agent Workflow (simpsons-no-jony)

This repository uses a structured agent pipeline for feature development. **Never bypass this pipeline for non-trivial features.**

### The Pipeline

```
Lisa  → Interviews user, produces spec.md
  ↓
Marge → Reviews spec for completeness (90+ points to pass)
  ↓
Bart  → Converts spec to granular work items in prd.md
  ↓
Chief → Reviews PRD for quality (85+ points to pass)
  ↓
Ralph → Executes PRDs autonomously, work item by work item
```

### Agent Roles

| Agent | Role | Output location |
|---|---|---|
| **Lisa** | Feature specification via interview. One question at a time. Never generates spec until interview is complete. | `simpsons-no-jony/lisa/features/[feature-name]/spec.md` |
| **Marge** | QA review of Lisa's spec. Flags vagueness, gaps, missing edge cases. Does NOT fix — flags and returns to Lisa. | `simpsons-no-jony/marge/reviews/[feature-name]/review.md` |
| **Bart** | Converts approved spec to granular PRD. Only S/M effort items allowed — L/XL are banned. Integration gates every 3–5 items. | `simpsons-no-jony/ralph/todo/[feature-name]/prd.md` |
| **Chief** | Validates Bart's PRD: sizing, E2E test placement, gates, Notes quality. Does NOT fix — scores and returns to Bart. | `simpsons-no-jony/chief/reviews/[feature-name]/review.md` |
| **Ralph** | Executes PRDs. Picks up from `ralph/todo/`, moves to `inprogress/`, then `completed/`. Records learnings throughout. | Executes in-place; `learnings.md` alongside `prd.md` |

### How to trigger agents

Use the skill system in chat:

```
@lisa spec out [feature name]
@marge review spec simpsons-no-jony/lisa/features/[feature-name]/spec.md
@bart create prd simpsons-no-jony/lisa/features/[feature-name]/spec.md
@chief review prd simpsons-no-jony/ralph/todo/[feature-name]/prd.md
@ralph            (picks up next PRD from todo/)
```

### Key rules for the pipeline

- **Lisa reads PURPOSE.md and ARCHITECTURE.md at the start of every interview.** Questions must align with the existing system — never spec something that contradicts the architecture.
- **Marge requires 90+ to pass.** If she scores below 90, Lisa re-interviews the user to fill the gaps.
- **Chief requires 85+ to pass.** If below 85, Bart fixes and Chief re-reviews. Never send a rejected PRD to Ralph.
- **Ralph's work items must be vertically sliced (tracer bullets)** — each WI touches all affected layers (model + API + view) for one unit of functionality, not one layer across all functionality.
- **E2E tests are interleaved, not bunched at the end.** A test work item follows immediately after the feature phase it covers.
- **Every PRD work item includes a Notes section** with: Pattern reference, existing file to extend, and hook point (file:function).
- **If a feature changes the architecture, Bart adds a work item to update `about/ARCHITECTURE.md`.**

### PRD work item format

```markdown
### WI-001: [Title]

**Priority:** 1
**Effort:** S | M
**Status:** ❌ Not started

**Description:** [What and why — one short paragraph]

**Acceptance Criteria:**
- [ ] [Specific verifiable criterion]
- [ ] Tenant isolation test: verify org B cannot access org A's data through this endpoint
- [ ] `pytest` passes (backend) or `npm run check` passes (frontend)

**Notes:**
- **Pattern:** See spec "Implementation Patterns → [Pattern Name]"
- **Reference:** Extend from `apps/memberships/views.py:MembershipListView`
- **Hook point:** Register in `config/urls.py` under `/api/v1/memberships/`
```

### Integration Gates

Every 3–5 work items, a gate halts Ralph until verified:

```markdown
### 🚦 INTEGRATION GATE: [Milestone Name]

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Start dev server: `docker compose up`
2. [ ] Perform: [specific action to test]
3. [ ] Expected: [specific observable outcome]
4. [ ] Evidence: Write "VERIFIED: [observation] @ [timestamp]" in learnings.md

**If gate fails:** Fix before proceeding. Do NOT skip.
```

---

## Marge's `about/` Audit

Marge can audit the `about/` docs to check they reflect reality:

```
@marge audit about memberflow
```

Output: `simpsons-no-jony/marge/audits/memberflow/about-audit.md`

Run this when: a significant feature ships, the architecture changes, or the docs feel stale.

---

## What I Should Always Do

- Read `about/ARCHITECTURE.md` before writing any backend or frontend code for a new feature
- Add `TenantAwareModel` to every new tenant-owned model, without exception
- Add `TenantScopedViewMixin` to every new DRF view that queries tenant data
- Write a cross-tenant access test for every new resource endpoint
- Pass `organization_id` explicitly to every new Celery task
- Update `about/ARCHITECTURE.md` when making structural changes to the system
- Check that Stripe API calls include `stripe_account=org.config.stripe_account_id`
- Scope email subjects and content to the organisation (`org.name`)

## What I Should Never Do

- Write a model that doesn't inherit `TenantAwareModel` for tenant data
- Write a view that queries tenant data without `TenantScopedViewMixin`
- Resolve the tenant inside a view — it comes from `request.tenant`
- Write a Celery task that infers tenant from global or thread-local state
- Use a single global Stripe API key — every Stripe call is on a connected account
- Make a Stripe API call synchronously inside a webhook view
- Use `User.email` as a globally unique field
- Skip the agent pipeline for non-trivial features
- Allow a PRD to reach Ralph without a Chief review score of 85+
- Bundle all E2E tests at the end of a PRD
- Write L or XL effort work items in a PRD
- Commit secrets, stripe keys, or `.env` files

---

## Environment Setup (Local Development)

```bash
# Start all services
docker compose up

# Apply migrations
docker compose exec api python manage.py migrate

# Create a test organisation (tenant)
docker compose exec api python manage.py shell
>>> from apps.organizations.models import Organization, OrganizationConfig
>>> org = Organization.objects.create(name="Test Club", slug="test-club")
>>> OrganizationConfig.objects.create(organization=org)

# Access the API at:
# http://test-club.localhost/api/v1/  (requires /etc/hosts entry or local DNS)

# Run backend tests
docker compose exec api pytest

# Run frontend dev server
cd frontend && npm run dev

# Run frontend checks
npm run check    # lint + type check
npm run fix      # auto-fix lint issues
```

---

## Key Files to Know

| File | Purpose |
|---|---|
| `core/middleware.py` | `TenantMiddleware` — resolves org from subdomain |
| `core/models.py` | `TenantAwareModel` — base for all tenant-owned models |
| `core/managers.py` | `TenantManager` — provides `.for_tenant(org)` |
| `core/mixins.py` | `TenantScopedViewMixin` — enforces tenant scoping in views |
| `core/permissions.py` | `IsOrgAdmin`, `IsPlatformAdmin`, `IsOwnerOrOrgAdmin` |
| `apps/organizations/models.py` | `Organization`, `OrganizationConfig` |
| `apps/webhooks/views.py` | Stripe webhook receiver — per-tenant sig validation |
| `tasks/webhooks.py` | Stripe event processing tasks |
| `frontend/src/api/client.js` | Axios instance with JWT + refresh interceptors |
| `frontend/src/stores/tenant.js` | Tenant config + feature flags |
| `frontend/src/main.js` | Tenant bootstrap before app mount |
