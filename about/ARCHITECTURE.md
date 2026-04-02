# MemberFlow — Architecture

Multi-tenancy is a first-class design constraint in MemberFlow. Every layer — data model, API, middleware, background tasks, Stripe integration, and deployment — is built around the assumption that the system serves multiple isolated clubs simultaneously from a single deployment.

---

## 1. High-Level Architecture

MemberFlow is a decoupled, API-first system. A Vue.js SPA is served per tenant via subdomain. All requests pass through a tenant resolution layer before reaching any business logic. The backend exposes a REST API where every response is scoped to the current tenant. Stripe Connect handles payments independently per club. Background tasks carry tenant context through Celery.

```
  springfield-cc.memberflow.com          barton-fc.memberflow.com
         │                                        │
         └──────────────┬─────────────────────────┘
                        │ Wildcard DNS → Load Balancer
                        ▼
            ┌───────────────────────┐
            │  Nginx (reverse proxy)│
            │  Wildcard TLS cert    │
            └───────────┬───────────┘
                        │
            ┌───────────▼───────────┐
            │   TenantMiddleware    │  ← resolves Organization from subdomain
            │   Django REST API     │     attaches request.tenant to all views
            │                       │
            │  ┌─────────────────┐  │
            │  │  organizations  │  │
            │  │  users          │  │
            │  │  memberships    │  │
            │  │  payments       │  │
            │  │  admin_portal   │  │
            │  │  webhooks       │  │
            │  └─────────────────┘  │
            └──────┬────────────────┘
                   │
      ┌────────────┼────────────────┐
      ▼            ▼                ▼
┌──────────┐ ┌──────────┐   ┌─────────────────┐
│PostgreSQL│ │  Redis   │   │  Celery Workers │
│(shared,  │ │ (broker) │   │  (tenant-aware) │
│ row-level│ └──────────┘   └────────┬────────┘
│ isolation│                         │
└──────────┘              ┌──────────▼──────────┐
                          │  Stripe Connect API  │
                          │  (per-tenant account)│
                          └─────────────────────┘
```

**Core architectural constraints:**
- Every database query is filtered by `organization_id` — no query runs without a tenant in scope
- `request.tenant` is set by middleware before any view executes; views never resolve the tenant themselves
- Stripe Connect means each club's payments go into their own Stripe account; MemberFlow never commingles funds
- Celery tasks receive `organization_id` as an explicit argument — they never infer tenant from global state
- The frontend bootstraps tenant context on load by calling a public `/api/v1/config/` endpoint

---

## 2. Backend Architecture

### Technology Stack

| Layer | Technology |
|---|---|
| Framework | Django 4.x + Django REST Framework |
| Database | PostgreSQL 15 |
| Auth | djangorestframework-simplejwt |
| Payments | Stripe Python SDK + Stripe Connect |
| Task Queue | Celery 5.x + Redis |
| Web Server | Gunicorn behind Nginx |
| Containerisation | Docker + Docker Compose |

### Django Project Structure

```
memberflow/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── organizations/         # Tenant model, config, feature flags
│   ├── users/                 # Registration, auth, profiles (tenant-scoped)
│   ├── memberships/           # Tiers, membership records, status (tenant-scoped)
│   ├── payments/              # Stripe Connect integration, payment records
│   ├── admin_portal/          # Org-admin and platform-admin views
│   └── webhooks/              # Per-tenant Stripe webhook receiver
├── core/
│   ├── models.py              # TenantAwareModel base class
│   ├── middleware.py          # TenantMiddleware
│   ├── managers.py            # TenantManager base queryset
│   ├── mixins.py              # TenantScopedViewMixin for DRF views
│   └── permissions.py        # IsOrgAdmin, IsOrgStaff, IsPlatformAdmin
├── tasks/                     # Celery task definitions (all tenant-aware)
└── manage.py
```

### Tenant Resolution Middleware

The `TenantMiddleware` runs before every request. It resolves the `Organization` from the subdomain and attaches it to the request. Any request that cannot be resolved to a known, active tenant is rejected before reaching any view.

```python
# core/middleware.py
class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]          # strip port
        subdomain = host.split('.')[0]                   # "springfield-cc"

        try:
            request.tenant = Organization.objects.get(
                slug=subdomain,
                is_active=True
            )
        except Organization.DoesNotExist:
            return JsonResponse({'error': 'Organisation not found'}, status=404)

        return self.get_response(request)
```

### Tenant-Scoped Base Model and Manager

All tenant-owned models inherit from `TenantAwareModel`. This enforces `organization` as a required FK and provides a scoped manager:

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

# core/managers.py
class TenantManager(models.Manager):
    def for_tenant(self, organization):
        return self.get_queryset().filter(organization=organization)
```

### Tenant-Scoped View Mixin

All DRF views that handle tenant data inherit from `TenantScopedViewMixin`. This is the enforcement point that prevents cross-tenant data access:

```python
# core/mixins.py
class TenantScopedViewMixin:
    """
    Forces all queryset access to be filtered by request.tenant.
    Must be the left-most parent in any view that touches tenant data.
    """
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.for_tenant(self.request.tenant)
```

Every view that accesses tenant data uses this mixin — failure to do so results in a global queryset, which is caught in code review and test coverage.

### App Responsibilities

**`organizations`**
- `Organization` model: the tenant entity
- `OrganizationConfig` model: per-tenant settings and feature flags
- Endpoint: `GET /api/v1/config/` — public, returns the current tenant's config for frontend bootstrapping
- Platform admin endpoints for creating and managing organisations

**`users`**
- `User` model: scoped to an `Organization` via `TenantAwareModel`
- Email uniqueness is enforced **per organisation**, not globally (same person can be a member of two clubs)
- `UserOrganizationRole` model: replaces a flat role field; one user can have different roles in different orgs
- `UserInvitation` model: time-limited (7-day) invite token; scoped to org; tracks `invited_by`, `is_used`, `expires_at`
- `PasswordResetToken` model: single-use 24-hour reset token; linked to `User` (not tenant-scoped directly — User FK provides org link)
- `BlacklistedRefreshToken` model: lightweight custom blacklist keyed by JWT JTI (avoids dependency on simplejwt's `OutstandingToken` which requires Django's `auth.User`)
- Registration, login, invite, and password reset endpoints; JWT payload includes `organization_id` and `role`

**JWT token issuance pattern (`apps/users/tokens.py`):**
```python
# Our User model is not Django's auth.User, so we cannot use simplejwt's for_user().
# Tokens are built manually to include org/role claims:
def make_tokens_for_user(user):
    refresh = RefreshToken()
    refresh[USER_ID_CLAIM] = str(user.pk)
    refresh['organization_id'] = str(user.organization_id)
    refresh['role'] = role  # from UserOrganizationRole
    access = refresh.access_token
    # access token inherits the same claims
    return access, refresh
```
Token payload: `{ user_id, organization_id, role, exp, jti }`

**`memberships`**
- `MembershipTier`: per-organisation tier catalogue
- `Membership`: per-organisation membership instance for a user
- All queries filtered through `TenantScopedViewMixin`
- Status transitions (pending → active → expired/cancelled) are unchanged in logic, scoped by tenant

**`payments`**
- Stripe Connect: each `Organization` stores a `stripe_account_id` (their connected account)
- Checkout sessions are created on behalf of the connected account
- `Payment` and `Subscription` models inherit from `TenantAwareModel`

**`admin_portal`**
- Org admin views: member list (`GET /api/v1/admin/members/`), member detail (`GET /api/v1/admin/members/{id}/`), member CSV export (`GET /api/v1/admin/members/export/`) — all scoped to `request.tenant`
- Platform admin views: cross-tenant member read and edit (`GET/PATCH /api/v1/platform/members/{id}/`) — no tenant filter, for support use only
- `IsOrgStaff` permission (admins + staff) gates list and detail; `IsOrgAdmin` gates export; `IsPlatformAdmin` gates platform endpoints
- Separated permission classes prevent org admins from accessing platform admin endpoints

**`webhooks`**
- Per-tenant webhook endpoint: `POST /api/v1/webhooks/stripe/{org_slug}/`
- Each organisation has its own `stripe_webhook_secret` stored on `OrganizationConfig`
- The org slug in the URL path is used to resolve the tenant before signature validation

---

## 3. Frontend Architecture

### Technology Stack

| Layer | Technology |
|---|---|
| Framework | Vue.js 3 (Composition API) |
| Routing | Vue Router 4 |
| HTTP Client | Axios |
| State | Pinia |
| Build Tool | Vite |
| Styling | Bulma v1.x + SCSS |
| Hosting | DigitalOcean Spaces (static) or Nginx |

### Directory Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.js          # Axios instance; JWT attachment + silent refresh interceptor
│   │   ├── auth.js
│   │   ├── contact.js         # POST /api/v1/contact/ — platform contact form
│   │   ├── memberships.js
│   │   └── payments.js
│   ├── components/
│   │   ├── platform/          # Platform marketing page components (memberflow.com)
│   │   │   ├── PlatformNavbar.vue      # Fixed navbar; transparent → white on scroll
│   │   │   ├── PlatformHero.vue        # Full-viewport navy→teal gradient hero
│   │   │   ├── PlatformFeatures.vue    # 6 feature cards with Heroicons + AOS
│   │   │   ├── PlatformPricing.vue     # 3-tier pricing; Pro highlighted
│   │   │   ├── PlatformCarousel.vue    # CSS marquee: "Trusted by clubs"
│   │   │   ├── PlatformContactForm.vue # #contact section; POST /api/v1/contact/
│   │   │   └── PlatformFooter.vue      # 4-column footer
│   │   └── club/              # Club subdomain homepage components
│   │       ├── ClubNavbar.vue          # Club logo + name, Log in + Join Now
│   │       └── ClubHero.vue            # Branded hero with initials fallback
│   ├── composables/
│   │   └── useScrollPosition.js       # window.scrollY reactive ref
│   ├── views/
│   │   ├── PlatformHomePage.vue   # / when no tenant — assembles platform sections
│   │   ├── ClubHomePage.vue       # / when tenant present — assembles club sections
│   │   ├── LoginView.vue          # /login — email/password; inline error; Forgot password link
│   │   ├── RegisterView.vue       # /register — gated by allow_self_registration
│   │   ├── ForgotPasswordView.vue # /forgot-password — no-enumeration confirmation
│   │   ├── SetPasswordView.vue    # /auth/set-password?token=&mode=invite|reset
│   │   └── DashboardView.vue      # /dashboard — protected; placeholder
│   ├── stores/
│   │   ├── auth.js            # Access token (memory), user, isAuthenticated, isOrgAdmin
│   │   ├── tenant.js          # OrganizationConfig, feature flags, branding, hasTenant
│   │   └── membership.js      # Current user's membership state
│   ├── styles/
│   │   ├── main.scss          # Entry point — imports Bulma + all SCSS partials
│   │   ├── _variables.scss    # SCSS variables for layout/spacing (not brand colours)
│   │   ├── base/
│   │   │   └── _root.scss     # :root custom property defaults, html, reduced-motion
│   │   ├── views/             # One partial per view (dashboard, profile, etc.)
│   │   └── components/        # Mirrors src/components/ — one partial per component
│   ├── router/
│   │   └── index.js           # / → PlatformHomePage or ClubHomePage; auth routes + guards
│   └── main.js                # Bootstraps tenant; initialises AOS; mounts app
├── tests/
│   ├── unit/
│   │   └── api/
│   │       └── client.test.js # Vitest: interceptor silent refresh + force-logout paths
│   └── e2e/
│       ├── homepage/          # Platform + club homepage smoke tests
│       └── auth/              # Auth regression tests (login page reachable)
├── public/
├── vitest.e2e.config.ts       # Vitest config for e2e smoke tests (jsdom)
└── vite.config.js
```

### Tenant Bootstrap on App Load

The frontend does not hardcode any tenant details. On `main.js` init, before mounting the app, it fetches the current tenant's config from the API. The backend resolves the tenant from the subdomain server-side; the frontend simply uses whatever subdomain it's running on.

```js
// main.js
const tenantStore = useTenantStore()
await tenantStore.bootstrap()   // GET /api/v1/config/ — sets branding + feature flags
app.mount('#app')
```

```js
// stores/tenant.js
export const useTenantStore = defineStore('tenant', {
  state: () => ({ config: null }),
  getters: {
    hasTenant: (state) => state.config !== null,         // true on club subdomains
    isFeatureEnabled: (state) => (flag) => state.config?.features?.[flag] ?? false,
    brandName: (state) => state.config?.name ?? 'MemberFlow',
  },
  actions: {
    async bootstrap() {
      try {
        const { data } = await client.get('/api/v1/config/')
        this.config = data
        this._applyBranding(data.branding)
      } catch {
        this.config = null   // root domain (memberflow.com) → platform page
      }
    }
  }
})
```

### Platform vs Club Homepage Routing

The router at `/` serves two different experiences based on whether a tenant is present:

```js
// router/index.js
{
  path: '/',
  component: () => import('./views/PlatformHomePage.vue'),
  beforeEnter: async () => {
    const tenantStore = useTenantStore()
    if (tenantStore.hasTenant) return '/club'
  }
},
{
  path: '/club',
  component: () => import('./views/ClubHomePage.vue'),
  beforeEnter: async () => {
    const tenantStore = useTenantStore()
    if (!tenantStore.hasTenant) return '/'
  }
}
```

- `memberflow.com` (no tenant) → `config = null` → `hasTenant = false` → `PlatformHomePage` (marketing page)
- `springfield-cc.memberflow.com` (tenant present) → `config = {...}` → `hasTenant = true` → `ClubHomePage`

The `TenantMiddleware` was updated to pass through with `request.tenant = None` when no subdomain is detected, rather than returning 404. This allows `memberflow.com` to reach the contact endpoint and serve the SPA.

### Platform Contact Form

`apps/contact/` is a standalone Django app (no tenant scope) that receives enquiries from the platform marketing page:

- `POST /api/v1/contact/` — public endpoint, no JWT required
- Validates: name (min 2 chars, letters), email (RFC + MX record check via `dnspython`), message (min 20 chars)
- Hidden honeypot field (`website`): if filled, returns 200 silently with no email queued
- Rate limiting: 3 submissions per IP per hour (Django cache-based); 4th returns 429
- On success: queues `tasks.contact.send_contact_email` Celery task to deliver email to configured recipient
- Frontend shows success message replacing the form; errors are shown inline below each field (no toasts)

Feature flags gate entire routes and components:

```js
// router/index.js — guard for a feature-flagged route
{
  path: '/waitlist',
  component: WaitlistView,
  beforeEnter: () => {
    const tenant = useTenantStore()
    if (!tenant.isFeatureEnabled('waitlist')) return '/dashboard'
  }
}
```

### Authentication Flow (Frontend)

1. User submits credentials at `springfield-cc.memberflow.com/login`
2. Backend returns `access` + `refresh` JWT tokens; the `access` token payload contains `organization_id` and `role`
3. `access` token stored in Pinia `auth` store (memory only — never persisted); `refresh` token in `localStorage('mf_refresh_token')`
4. Axios request interceptor attaches `Authorization: Bearer <access>` on every request
5. On 401, interceptor calls `POST /api/v1/auth/token/refresh/`, rotates tokens via `authStore.setTokens()`, retries the original request exactly once
6. If refresh also returns 401: clears auth store state, removes `mf_refresh_token` from localStorage, redirects to `/login`
7. The refresh endpoint itself never triggers a second refresh attempt (infinite loop prevention)
8. Role from the JWT payload (`member`, `org_staff`, `org_admin`, `platform_admin`) drives route guards and UI visibility

**Token storage:**
| Token | Storage | Lifetime |
|---|---|---|
| `access` | Pinia store (memory) | 15 minutes |
| `refresh` | `localStorage('mf_refresh_token')` | 7 days |

**Pinia `auth` store (`src/stores/auth.js`):**
- `state.accessToken` — null until login
- `state.user` — `{ id, email, first_name, last_name, role }`
- `getters.isAuthenticated` — `!!accessToken`
- `getters.isOrgAdmin` — role is `org_admin` or `org_staff`
- `actions.login(email, password)` — calls API, stores tokens
- `actions.register(payload)` — calls API, stores tokens
- `actions.logout()` — calls API to blacklist refresh token, clears state
- `actions.setTokens({ access, refresh, user })` — called by Axios interceptor on silent refresh

### Routing and Guards

```js
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  const tenant = useTenantStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) return next('/login')
  if (to.meta.requiresOrgAdmin && !auth.isOrgAdmin) return next('/dashboard')
  if (to.meta.requiresPlatformAdmin && !auth.isPlatformAdmin) return next('/dashboard')
  if (to.meta.feature && !tenant.isFeatureEnabled(to.meta.feature)) return next('/dashboard')

  next()
})
```

### Per-Tenant Runtime Theming

MemberFlow uses **Bulma v1.x + SCSS** for styling. Bulma v1.x is built entirely on CSS custom properties, which makes per-tenant colour theming possible at runtime — there is no per-tenant build step and no per-tenant stylesheet. A single compiled CSS bundle serves all tenants.

**How it works:**

1. `OrganizationConfig.branding` stores tenant colours as a JSONField:
   ```json
   { "primary_color": "#1a472a", "secondary_color": "#f4d03f", "logo_url": "https://..." }
   ```

2. During tenant bootstrap (`main.js`, before app mount), the branding values are applied to the document root as CSS custom properties:
   ```js
   // stores/tenant.js — called during bootstrap()
   function applyBranding(branding) {
     const root = document.documentElement
     if (branding.primary_color) {
       root.style.setProperty('--bulma-primary', branding.primary_color)
     }
     if (branding.secondary_color) {
       root.style.setProperty('--bulma-secondary', branding.secondary_color)
     }
   }
   ```

3. Bulma v1.x reads `--bulma-primary`, `--bulma-secondary`, etc. for all component colours. Overriding these properties at the root level is all that is required — no SCSS recompilation.

**SCSS structure:**

All styles live in `src/styles/` — **Vue SFCs have no `<style>` blocks**. The structure mirrors the component tree:

```
src/styles/
├── main.scss                   # Entry: @use Bulma + every partial
├── _variables.scss             # SCSS layout/spacing vars (not brand colours)
├── base/_root.scss             # :root defaults, html, prefers-reduced-motion
├── views/                      # _dashboard.scss, _profile.scss, etc.
└── components/
    ├── club/                   # _club-hero.scss, _dashboard-navbar.scss, etc.
    │   └── dashboard/          # _db-card.scss, _membership-status-card.scss, etc.
    └── platform/               # _platform-navbar.scss, _platform-hero.scss, etc.
```

`_variables.scss` contains SCSS variables for layout/spacing only. Tenant-specific colours always come through CSS custom properties at runtime, never through SCSS variables.

**Adding styles for a new component:**
1. Create `src/styles/components/<group>/_my-component.scss`
2. Add `@use 'components/<group>/my-component';` in `main.scss`
3. Write styles in the partial — no `<style>` block in the Vue file

**Rules:**
- **No `<style>` blocks in Vue SFCs** — all styles live in `src/styles/` partials
- Never hardcode brand colours — use Bulma utility classes or `var(--bulma-*)` properties
- Custom components reference CSS custom properties, not SCSS variables
- When overriding Bulma class names (e.g. `.input`) inside a component partial, scope them to a parent class to prevent global leakage
- One static build serves all tenants; per-tenant builds are explicitly out of scope

---

## 4. Data Model Design

### Core Entities

```
Organization  (the tenant)
├── id (UUID)
├── name                           # "Springfield Cricket Club"
├── slug (unique)                  # "springfield-cc" — used for subdomain routing
├── is_active
├── created_at

OrganizationConfig  (OneToOne → Organization)
├── stripe_account_id              # Stripe Connect connected account ID
├── stripe_webhook_secret          # Per-tenant webhook signing secret
├── default_currency               # "gbp", "aud", etc.
├── allow_self_registration        # bool
├── require_membership_approval    # bool
├── reminder_days_before_expiry    # int (e.g. 7)
├── features                       # JSONField: {"waitlist": true, "family_memberships": false}
├── branding                       # JSONField: {"logo_url": "...", "primary_color": "#1a1a2e"}

User  (inherits TenantAwareModel → scoped to Organization)
├── id (UUID)
├── organization → Organization (FK)
├── email                          # unique per organization, not globally
├── first_name, last_name
├── is_active
├── created_at

UserOrganizationRole  (replaces flat role field on User)
├── user → User (FK)
├── organization → Organization (FK)
├── role (member | org_staff | org_admin | platform_admin)
│   Unique together: (user, organization)

UserInvitation  (inherits TenantAwareModel)
├── email
├── token (UUID, unique)
├── invited_by → User (FK, SET_NULL)
├── is_used (default=False)
├── expires_at (timezone.now() + 7 days on creation)

PasswordResetToken
├── id (UUID, PK)
├── user → User (FK, CASCADE)
├── token (UUID, unique)
├── is_used (default=False)
├── expires_at (timezone.now() + 24 hours on creation)
├── created_at

BlacklistedRefreshToken
├── jti (unique string — JWT ID claim)
├── blacklisted_at

MembershipTier  (inherits TenantAwareModel)
├── id
├── organization → Organization (FK)
├── name                           # "Full Member", "Junior", "Social"
├── price (Decimal)
├── billing_period (monthly | annual | one_time)
├── stripe_price_id                # Price ID on the connected Stripe account
├── is_active

Membership  (inherits TenantAwareModel)
├── id
├── organization → Organization (FK)
├── user → User (FK)
├── tier → MembershipTier (FK)
├── status (pending | active | expired | cancelled | suspended)
├── start_date
├── expiry_date
├── stripe_subscription_id (nullable)
├── created_at, updated_at
│   Unique together: (organization, user) — one membership per user per org

Subscription  (inherits TenantAwareModel)
├── id
├── organization → Organization (FK)
├── user → User (FK)
├── stripe_subscription_id (unique)
├── stripe_customer_id
├── status (active | past_due | cancelled | unpaid)
├── current_period_start
├── current_period_end
├── created_at, updated_at

Payment  (inherits TenantAwareModel — append-only)
├── id
├── organization → Organization (FK)
├── user → User (FK)
├── membership → Membership (FK)
├── stripe_payment_intent_id (unique)
├── amount (Decimal)
├── currency
├── status (pending | succeeded | failed | refunded)
├── payment_method_type
├── created_at
```

### Key Relationships

- `User.email` is unique **per organisation** (`UniqueConstraint(fields=['organization', 'email'])`)
- `Membership` is unique per `(organization, user)` — one active membership per user per club
- `MembershipTier` is defined per organisation; there is no global tier catalogue
- `OrganizationConfig` is OneToOne with `Organization` and always created alongside it
- `UserOrganizationRole` replaces a flat role field — the same physical user account can have different roles across different organisations (future use case: a person who is an org admin of one club and a regular member of another)
- All `Payment` records are append-only; mutations to payment state use status field updates only

### Database Indexes

```python
# Applied at model level for query performance
class Membership(TenantAwareModel):
    class Meta:
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'expiry_date']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['organization', 'user'], name='unique_membership_per_org')
        ]
```

---

## 5. API Design

### Principles

- All endpoints (except `/auth/` and `/config/`) operate in the context of `request.tenant`
- No endpoint accepts a tenant identifier in the request body or URL — tenant is always derived from the subdomain
- JWT payload contains `organization_id`; this is cross-checked against `request.tenant` on protected endpoints
- Consistent error response shape: `{ "error": "...", "detail": "..." }`
- Pagination on all list endpoints (cursor-based)

### Key Endpoints

#### Tenant Config (public — no auth)
```
GET    /api/v1/config/                  Returns OrganizationConfig for the current tenant
                                        (branding, feature flags, currency, registration settings)
```

#### Authentication
```
POST   /api/v1/auth/register/              Self-register within current tenant (gated by allow_self_registration)
POST   /api/v1/auth/login/                 Obtain JWT tokens (tenant-scoped; same error for wrong email/password)
POST   /api/v1/auth/token/refresh/         Rotate access + refresh tokens
POST   /api/v1/auth/logout/                Blacklist refresh token (custom BlacklistedRefreshToken model)
POST   /api/v1/auth/invite/                Org admin sends invitation email (org_admin or org_staff only)
POST   /api/v1/auth/invite/accept/         Invitee completes registration via token (7-day, single-use)
POST   /api/v1/auth/password/reset/        Request password reset email (no enumeration — always 200)
POST   /api/v1/auth/password/reset/confirm/ Complete reset; auto-logs user in on success
GET    /api/v1/profile/                    Current user profile + role within this org
PATCH  /api/v1/profile/                    Update profile (supports DOB + address fields)
```

#### Org Admin (IsOrgAdmin / IsOrgStaff)
```
GET    /api/v1/admin/members/             Member list with calculated age (IsOrgStaff)
GET    /api/v1/admin/members/{id}/        Member detail with DOB + address (IsOrgStaff)
GET    /api/v1/admin/members/export/      CSV export of all members (IsOrgAdmin only)
```

#### Platform Admin (IsPlatformAdmin — cross-tenant)
```
GET    /api/v1/platform/members/{id}/     Read any member across any tenant
PATCH  /api/v1/platform/members/{id}/     Edit member DOB + address for support
```

#### Memberships (authenticated member)
```
GET    /api/v1/memberships/tiers/       List this org's active membership tiers
GET    /api/v1/memberships/me/          Current user's membership within this org
POST   /api/v1/memberships/join/        Initiate membership application
```

#### Payments (authenticated member)
```
POST   /api/v1/payments/checkout/       Create Stripe Checkout session (on org's connected account)
GET    /api/v1/payments/history/        Current user's payment history within this org
POST   /api/v1/payments/cancel/         Cancel active subscription
```

#### Webhooks (no auth — Stripe signature validated per tenant)
```
POST   /api/v1/webhooks/stripe/{org_slug}/    Stripe event receiver for a specific org
```

The `org_slug` in the URL path is how Stripe knows which club the webhook belongs to. Each org registers this URL in its own Stripe connected account dashboard. The `stripe_webhook_secret` on `OrganizationConfig` is used for signature validation — it is unique per org.

#### Org Admin (org_admin or org_staff role required)
```
GET    /api/v1/admin/members/                  List this org's members
GET    /api/v1/admin/members/{id}/             Member detail + payment history
PATCH  /api/v1/admin/members/{id}/             Update membership status / tier
GET    /api/v1/admin/tiers/                    List/manage this org's membership tiers
POST   /api/v1/admin/tiers/                    Create a new tier
PATCH  /api/v1/admin/tiers/{id}/               Update a tier
GET    /api/v1/admin/stats/                    Aggregate stats for this org
GET    /api/v1/admin/payments/                 Full payment ledger for this org
```

#### Platform Admin (platform_admin role required)
```
GET    /api/v1/platform/organizations/         List all organisations
POST   /api/v1/platform/organizations/         Create a new organisation (onboard a club)
GET    /api/v1/platform/organizations/{id}/    Organisation detail + config
PATCH  /api/v1/platform/organizations/{id}/    Update config, toggle features, activate/deactivate
GET    /api/v1/platform/stats/                 Cross-tenant aggregate stats (member count, revenue)
```

### Permission Model

| Endpoint group | Required |
|---|---|
| `/config/` | None (public) |
| `/auth/register/`, `/auth/login/` | None |
| `/auth/me/`, `/memberships/*`, `/payments/*` | Authenticated + valid tenant membership |
| `/admin/*` | `org_admin` or `org_staff` role in this org |
| `/platform/*` | `platform_admin` role |
| `/webhooks/stripe/{org_slug}/` | None (Stripe signature validation only) |

---

## 6. Payment Flow

### Stripe Connect Setup

Each `Organization` is a Stripe Connect **Standard** or **Express** connected account. MemberFlow is the Stripe platform account. When a club is onboarded:

1. Platform admin initiates a Stripe Connect OAuth flow for the club
2. Club owner completes Stripe onboarding
3. Stripe returns a `stripe_account_id` which is stored on `OrganizationConfig`
4. Club creates their `MembershipTier` prices in MemberFlow; these are created as `Price` objects on the connected account via the Stripe API

This means **all payments go directly to the club's Stripe account**. MemberFlow can optionally take a platform fee via `application_fee_amount` on the Checkout Session.

### Checkout Flow

```
1. Member selects a MembershipTier on the frontend
2. Frontend calls POST /api/v1/payments/checkout/ with { tier_id }
3. Backend:
   a. Reads org's stripe_account_id from OrganizationConfig
   b. Retrieves or creates a Stripe Customer on the connected account
   c. Creates a Checkout Session on the connected account:
      stripe.checkout.Session.create(
          ...,
          stripe_account=org.config.stripe_account_id
      )
   d. Returns { checkout_url }
4. Frontend redirects to the Stripe-hosted Checkout page
5. Member completes payment
6. Stripe redirects to success_url; frontend shows confirmation
7. Stripe fires webhook to /api/v1/webhooks/stripe/{org_slug}/
```

### Webhook Processing (Per-Tenant)

```
1. Stripe sends event to /api/v1/webhooks/stripe/springfield-cc/
2. Django resolves Organization from org_slug in URL
3. Retrieves stripe_webhook_secret from OrganizationConfig
4. Validates Stripe-Signature header (rejects with 400 if invalid)
5. Queues Celery task: process_stripe_event.delay(event_id, organization_id)
6. Returns HTTP 200 immediately
7. Celery worker:
   - checkout.session.completed      → activate Membership, create Payment
   - invoice.payment_succeeded       → extend expiry, create Payment
   - invoice.payment_failed          → suspend Membership, queue failure email
   - customer.subscription.deleted   → cancel Membership
```

The `organization_id` is passed explicitly to every Celery task. Workers never infer tenant from global or thread-local state.

### Membership State Transitions

```
         ┌──────────┐
         │ pending  │ ← created on join
         └────┬─────┘
              │ checkout.session.completed
              ▼
         ┌──────────┐
    ┌───▶│  active  │◀─────────────────────┐
    │    └────┬─────┘                      │
    │         │ invoice.payment_succeeded  │
    │         │                     invoice.payment_succeeded
    │    ┌────▼──────────┐                 │
    │    │ (renewal loop)│─────────────────┘
    │    └────┬──────────┘
    │         │ invoice.payment_failed
    │         ▼
    │    ┌─────────────┐
    │    │  suspended  │ (grace period — Stripe retries)
    │    └────┬────────┘
    │         │ payment recovered
    └──────────┘
              │ subscription deleted / not recovered
              ▼
         ┌──────────┐
         │cancelled │
         └──────────┘

    expiry_date < today (Celery Beat daily check)
              ▼
         ┌──────────┐
         │ expired  │ (one-time payments only)
         └──────────┘
```

---

## 7. Async Processing

### Celery Configuration

- **Broker**: Redis
- **Result backend**: Redis
- **Workers**: separate Docker container(s), scalable independently of the API
- **Queues**: `default`, `webhooks`, `emails`
- **Beat**: Celery Beat for periodic tasks (separate process)

### Tenant Context in Tasks

All tasks receive `organization_id` as an explicit argument. No task uses thread-local state or infers the tenant from the environment.

```python
@app.task(queue='webhooks', bind=True, max_retries=5)
def process_stripe_event(self, event_id: str, organization_id: str):
    try:
        org = Organization.objects.get(id=organization_id)
        # all subsequent DB queries scoped to org
        ...
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### Task Inventory

**Webhook Processing**
```python
process_stripe_event(event_id, organization_id)
# Retries up to 5 times with exponential backoff. Idempotent by event_id.
```

**Email Notifications**
```python
send_payment_confirmation(user_id, payment_id, organization_id)
send_membership_expiry_reminder(membership_id, organization_id)
send_payment_failed_notice(user_id, organization_id)
```

**Periodic Tasks (Celery Beat — run across all active tenants)**
```python
# Daily 08:00 UTC
def expire_overdue_memberships():
    """
    Iterates all active Organizations.
    For each, finds Memberships past expiry_date with status=active.
    Transitions to expired. Scoped per org — no cross-tenant mutation.
    """

# Daily 09:00 UTC
def send_expiry_reminders():
    """
    Per org: finds memberships expiring in reminder_days_before_expiry (from OrganizationConfig).
    Queues send_membership_expiry_reminder task per membership.
    """
```

Periodic tasks iterate tenants explicitly rather than querying all memberships globally. This preserves tenant isolation in background processing and makes per-tenant task failures observable in isolation.

---

## 8. Deployment Architecture

### Docker Setup

```yaml
services:
  api:          # Django + Gunicorn (tenant-aware)
  worker:       # Celery worker
  beat:         # Celery Beat scheduler
  nginx:        # Reverse proxy + wildcard subdomain routing + TLS termination
  db:           # PostgreSQL (dev only — managed DB in production)
  redis:        # Redis broker (dev only — managed Redis in production)
  frontend:     # Nginx serving built Vue.js static files
```

### Subdomain Routing

Nginx is configured to accept all subdomains of `memberflow.com` and forward them to the Django API. The subdomain is preserved in the `Host` header so `TenantMiddleware` can resolve it.

```nginx
server {
    listen 443 ssl;
    server_name *.memberflow.com;

    ssl_certificate     /etc/ssl/memberflow/fullchain.pem;   # wildcard cert
    ssl_certificate_key /etc/ssl/memberflow/privkey.pem;

    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;                         # preserves subdomain
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /usr/share/nginx/html;                          # built Vue.js SPA
        try_files $uri $uri/ /index.html;
    }
}
```

The wildcard TLS certificate covers `*.memberflow.com` — obtained via Let's Encrypt DNS challenge (Certbot + DigitalOcean DNS plugin), renewed automatically.

### Production Topology (DigitalOcean)

```
        Wildcard DNS: *.memberflow.com → Load Balancer IP

                  ┌──────────────────────┐
                  │  DigitalOcean        │
                  │  Load Balancer       │
                  │  (TLS termination)   │
                  └──────────┬───────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                                 ▼
┌──────────────────────┐         ┌──────────────────────┐
│  App Droplet         │         │  App Droplet         │
│  Nginx + Gunicorn    │         │  Nginx + Gunicorn    │
│  Celery Worker       │         │  Celery Worker       │
└──────────┬───────────┘         └──────────┬───────────┘
           │                                │
           └──────────────┬─────────────────┘
                          │
           ┌──────────────┼──────────────┐
           ▼              ▼              ▼
  ┌──────────────┐ ┌────────────┐ ┌──────────────────┐
  │  Managed     │ │  Managed   │ │  Spaces + CDN    │
  │  PostgreSQL  │ │  Redis     │ │  (static assets) │
  └──────────────┘ └────────────┘ └──────────────────┘
```

- **Frontend** is a single static build deployed to DigitalOcean Spaces. The SPA detects its own subdomain at runtime; there is no per-tenant build.
- **Celery Beat** runs as a single instance (one Droplet) to avoid duplicate periodic task execution.
- **Database and Redis** are DigitalOcean Managed services, accessible only within the private VPC.

### CI/CD Pipeline (GitHub Actions)

```
on: push to main

jobs:
  test:
    - pytest (Django test suite, including tenant isolation tests)
    - Vitest (Vue.js unit tests)
    - flake8 + eslint

  build:
    - Build Docker image (backend)
    - Build Vue.js static files (frontend)
    - Push Docker image to DigitalOcean Container Registry

  deploy:
    - SSH → pull latest image
    - manage.py migrate
    - Restart Gunicorn + Celery
    - Upload frontend build to DigitalOcean Spaces
    - Purge CDN cache
```

---

## 9. Scalability Considerations

### API Layer

- Stateless design — no request carries session state; all context comes from JWT + subdomain
- Horizontal scaling behind the load balancer with no session affinity
- `TenantMiddleware` adds one DB lookup per request; this is cached in Redis with a short TTL (e.g. 60s) keyed by `slug`

### Database

- All high-traffic tables (`Membership`, `Payment`) carry a composite index on `(organization_id, status)` and `(organization_id, expiry_date)`
- Tenant isolation means queries are always filtered by `organization_id` — full-table scans are structurally prevented
- At very high tenant count, PostgreSQL row-level security (RLS) can be added as a defence-in-depth layer without application changes
- Read replicas for admin/reporting queries are introduced without touching the write path

### Celery Workers

- Workers are independently scalable per queue (`webhooks`, `emails`, `default`)
- Periodic tasks iterate tenants in batches to avoid long-running single tasks that hold locks

### Frontend

- Single static build serves all tenants — no per-tenant build pipeline
- DigitalOcean Spaces CDN caches assets globally; cache busting via content-hashed filenames (Vite default)
- The tenant bootstrap call (`GET /api/v1/config/`) is the only blocking request before mount; it is fast and can be cached client-side with a short TTL

### Potential Bottlenecks

| Area | Risk | Mitigation |
|---|---|---|
| Tenant resolution DB lookup | Adds latency per request | Redis cache on `Organization` by slug |
| Stripe webhook burst (many tenants) | Worker queue saturation | Monitor queue depth; scale workers horizontally |
| Periodic tasks across many tenants | Beat task duration grows | Batch tenants; fan out per-tenant tasks to workers |
| Email delivery at scale | Transactional throughput | Delegate to SendGrid or Postmark via SMTP/API |

---

## 10. Security Considerations

### Tenant Isolation

Tenant isolation is the highest-priority security concern. Mechanisms in place:

- **Middleware layer**: every request is rejected or scoped before reaching a view
- **`TenantScopedViewMixin`**: all views that touch tenant data must inherit this; enforced in code review
- **JWT cross-check**: the `organization_id` in the JWT is validated against `request.tenant.id` on every authenticated request — a token from one club cannot be replayed against another club's subdomain
- **Test coverage**: tenant isolation is tested explicitly with a suite that verifies one tenant cannot retrieve another's data through any endpoint

### Authentication

- JWT access tokens expire after 15 minutes; refresh tokens after 7 days
- Refresh tokens are rotated on use (`ROTATE_REFRESH_TOKENS = True`) and blacklisted after use
- JWT payload includes `organization_id` — tokens are implicitly scoped to a tenant
- Tokens are never logged or included in error responses

### Password Handling

- PBKDF2-SHA256 with high iteration count (Django default)
- Password reset tokens are time-limited (1 hour) and single-use
- Minimum complexity enforced via Django validators

### Stripe Webhook Validation

- Each tenant has its own `stripe_webhook_secret` (stored on `OrganizationConfig`, never in source code)
- Signature validation uses the org-specific secret — a webhook delivered to the wrong org endpoint is rejected
- Replay protection: Stripe includes a timestamp in the signature; events older than 5 minutes are rejected

### API Protection

- All non-public endpoints require a valid JWT
- Role checks use `UserOrganizationRole` — a user's role in org A gives no permissions in org B
- Rate limiting: Nginx limits at 60 req/min per IP; DRF throttles auth endpoints independently
- CORS: each tenant's frontend origin (`https://{slug}.memberflow.com`) is dynamically added to `CORS_ALLOWED_ORIGINS` via the `Organization` record — no wildcard CORS

### Infrastructure

- All secrets per-tenant (Stripe keys, webhook secrets) stored in the database (encrypted at rest via DigitalOcean Managed DB)
- Platform-level secrets (JWT secret, DB credentials) stored as environment variables, excluded from version control
- HTTPS enforced end-to-end; TLS 1.2+ only
- DigitalOcean Firewall: ports 80/443 only; DB and Redis accessible within private VPC only
- Docker image vulnerability scanning in CI pipeline

### Data

- PII limited to name, email, and payment status
- Stripe handles all card data — MemberFlow never processes or stores raw card information
- `Payment` records are append-only; no soft-delete on financial records
- All tenant data is logically isolated; physical separation (separate DB schemas or databases) is an upgrade path if compliance requirements demand it
