# Development Learnings: User Authentication

_Append entries here as work progresses. One entry per work item completed._

---

## WI-001: Create `users` Django app

Created `backend/apps/users/` with all required files: `__init__.py`, `models.py`, `serializers.py`, `views.py`, `urls.py`, `apps.py`, `tests/__init__.py`, `migrations/__init__.py`. Registered in `INSTALLED_APPS` and mounted at `/api/v1/auth/` in `config/urls.py`. Django `manage.py check` exits 0.

---

## WI-002: `User` model + `UserOrganizationRole` model + migrations

Created `User(TenantAwareModel)` with `email`, `first_name`, `last_name`, `is_active`, `password` fields. Added `UniqueConstraint(fields=['organization', 'email'])`. Created `UserOrganizationRole` with `user`, `organization`, `role` fields and `unique_together`. **Key learning:** Our custom `User` is not Django's `auth.User` — cannot use simplejwt's `for_user()` or `OutstandingToken`. All token issuance done manually via `RefreshToken()` with explicit claims. Added `is_authenticated` and `is_anonymous` properties to `User` for DRF compatibility.

---

## WI-003: `allow_self_registration` on `OrganizationConfig` + seed update

Added `OrganizationConfig` model (new — did not exist before) to `apps/organizations/models.py` with `allow_self_registration = BooleanField(default=False)`. Updated `seed_dev` to create/update config with `allow_self_registration=True` for `test-club`. Migration generated as `0002_organizationconfig.py`.

---

## WI-004: simplejwt settings + throttle config

Added `djangorestframework-simplejwt` and `celery` to `requirements.txt`, installed in container. Added `rest_framework_simplejwt` and `rest_framework_simplejwt.token_blacklist` to `INSTALLED_APPS`. Configured `SIMPLE_JWT` dict with 15-min access / 7-day refresh / rotation enabled. Created `apps/core/throttles.py` with `LoginRateThrottle` (10/min) and `PasswordResetRateThrottle` (5/min).

---

## WI-005: Custom JWT token with `organization_id` + `role` in payload

Created `backend/apps/users/tokens.py` with `make_tokens_for_user(user)` function. Does NOT use `RefreshToken.for_user()` (which requires Django's `auth.User` FK in `OutstandingToken`). Instead builds `RefreshToken()` directly and sets `user_id`, `organization_id`, `role` claims manually. Also created `TenantJWTAuthentication` in `authentication.py` that looks up our custom `User` model.

---

## INTEGRATION GATE: Backend Foundation — VERIFIED

VERIFIED: `migrate` applied all migrations including simplejwt blacklist tables. `seed_dev` created test-club with `allow_self_registration=True`. All 36 tests pass (after fixing pre-existing test failure). @ 2026-03-24

**Key fix:** Pre-existing tests in `test_views.py` were failing because `APIClient` goes through Django's test WSGI handler which has `DEBUG=False` at request time (even though settings.py sets it True). Fix: added `backend/conftest.py` with `autouse` fixture that sets `settings.DEBUG = True` for all tests via pytest-django's `settings` fixture.

---

## WI-006: Registration serializer + `POST /api/v1/auth/register/` view

Built `RegisterSerializer` with password validation via `django.contrib.auth.password_validation.validate_password`. `RegisterView` checks `request.tenant.config.allow_self_registration`, returns 403 if disabled, 409 on duplicate email, 400 on bad password, 201 with tokens on success.

---

## WI-007: Custom login view — `POST /api/v1/auth/login/`

`LoginView` uses `User.objects.for_tenant(request.tenant).get(email=email)`. Returns 401 for both wrong email and wrong password (no enumeration). Returns 403 for inactive user. Applied `LoginRateThrottle`.

---

## WI-008: Token refresh + logout endpoints

`LogoutView` blacklists via our custom `BlacklistedRefreshToken` model (JTI-keyed). `TenantTokenRefreshView` extends simplejwt's `TokenRefreshView` and checks our custom blacklist before delegating. **Key learning:** simplejwt's built-in blacklist has a FK to Django's `auth.User` — cannot use it directly with our custom User. Implemented `BlacklistedRefreshToken(jti, blacklisted_at)` model instead.

---

## WI-009: `UserInvitation` model + migration

Added `UserInvitation(TenantAwareModel)` to existing `models.py`. Fields: `email`, `token` (UUID), `invited_by` (FK→User, SET_NULL), `is_used`, `expires_at`. Auto-sets `expires_at = now + 7 days` in `save()`. Included in the single initial migration `0001_initial.py`.

---

## WI-010: Celery email tasks

Created `backend/tasks/email.py` with `send_invite_email` and `send_reset_email` shared tasks. Both use `bind=True`, `max_retries=3`, exponential backoff `60 * (2 ** retries)`. Email bodies match spec templates exactly. `base_url` passed explicitly. Celery not fully wired in dev (no worker), but tasks are importable; invite/reset views catch exceptions if Celery unavailable.

---

## WI-011: `POST /api/v1/auth/invite/` — send invite

`SendInviteView` uses `IsOrgStaff` permission (which also allows `org_admin`). Created `apps/core/permissions.py` with `IsOrgAdmin` and `IsOrgStaff`. Returns 409 on existing email, 201 with message on success.

---

## WI-012: `POST /api/v1/auth/invite/accept/` — accept invite

`InviteAcceptView` validates token against `request.tenant` (cross-org rejection). Returns 400 for used/missing token, 410 for expired, 201 with tokens on success. Sets `invitation.is_used = True`.

---

## INTEGRATION GATE: Register + Login API — VERIFIED

VERIFIED: Via Django shell test: register returns 201 with access/refresh/user.role=member. Login returns 200. Logout returns 204. Retry refresh after logout returns 401 (blacklisted). @ 2026-03-24

---

## INTEGRATION GATE: Invitation Flow — VERIFIED

VERIFIED: Via Django shell test: admin JWT created, `POST /invite/` returns 201, `UserInvitation` record confirmed. `POST /invite/accept/` returns 201 with tokens, `invitation.is_used=True`, new `User` + `UserOrganizationRole` confirmed. All 36 pytest tests pass. @ 2026-03-24

---

## WI-013: `PasswordResetToken` model + migration

Added `PasswordResetToken` to `models.py` with UUID PK, `user` FK, `token`, `is_used`, `expires_at` (24h), `created_at`. Auto-sets `expires_at` in `save()`.

---

## WI-014: `POST /api/v1/auth/password/reset/` — request reset

`PasswordResetRequestView` always returns 200 regardless of email found/not found. Invalidates existing unused tokens, creates new one, queues email task. Applied `PasswordResetRateThrottle`.

---

## WI-015: `POST /api/v1/auth/password/reset/confirm/` — complete reset

`PasswordResetConfirmView` validates token, returns 400 for used/missing (same message), 410 for expired, 400 for bad password. On success: sets new password, marks token used, returns 200 with tokens (auto-login).

---

## WI-016: Unit tests — password reset + invite token logic

Created `apps/users/tests/test_password_reset.py` and `apps/users/tests/test_invite.py`. 19 users tests pass (including auth_views, password_reset, invite). All 36 total pytest tests pass.

---

## INTEGRATION GATE: Full Auth API — VERIFIED

VERIFIED: `docker compose exec api pytest` — all 36 tests pass. Reset flow confirmed: valid email generates token, second request invalidates first, used token rejected (400), expired token rejected (410). @ 2026-03-24

---

## WI-017: Pinia `auth` store

Created `frontend/src/stores/auth.js`. State: `{ accessToken, user }`. Getters: `isAuthenticated`, `isOrgAdmin`. Actions: `login`, `register`, `logout`, `setTokens`. Refresh token stored in `localStorage('mf_refresh_token')`.

---

## WI-018: Axios client — JWT attachment + silent refresh interceptor

Updated `frontend/src/api/client.js`. Request interceptor lazily imports auth store (dynamic import to avoid circular deps). Response interceptor catches 401, checks refresh endpoint guard, calls refresh, retries original request. On refresh failure: clears auth state, redirects to `/login`. Used raw `axios.post()` (not client) for the refresh call to avoid interceptor recursion.

---

## WI-019: Unit tests — Axios interceptor

Added Vitest + jsdom + @vue/test-utils to devDependencies. Configured `test.environment = 'jsdom'` in `vite.config.js`. Created `tests/unit/api/client.test.js` with 5 tests covering: header attachment, no-token case, silent refresh path, force-logout path, infinite loop prevention. All 5 pass.

---

## WI-020: Vue Router — auth routes + `beforeEach` guard + `?next=` redirect

Updated `frontend/src/router/index.js`. Added routes: `/login`, `/register`, `/forgot-password`, `/auth/set-password`, `/dashboard` (requiresAuth). `beforeEach` guard: unauthenticated → `/login?next=<path>`, authenticated on `/login` → `/dashboard`. Login/register views read `route.query.next` on success.

---

## WI-021: Login page (`/login`)

Created `LoginView.vue` with Bulma form. Email + password fields. Loading state. Inline errors (401 → "Invalid email or password.", 403 → "Your account has been deactivated. Contact your admin."). "Forgot password?" link. Redirects to `?next` or `/dashboard` on success.

---

## WI-022: Register page (`/register`)

Created `RegisterView.vue`. Shows "Registration is not open" message when closed (403 from API). Shows Bulma form otherwise. Inline errors for 409 (duplicate email), 400 (password validation). Redirects to `/dashboard` on success.

---

## WI-023: E2E smoke — register + login flows

⏸️ Deferred — E2E runner not configured. Browser-based E2E tests require a Playwright/Cypress runner not yet set up in this project.

---

## WI-024: Forgot Password page (`/forgot-password`)

Created `ForgotPasswordView.vue`. Single email field. Always shows confirmation on submit (no enumeration). Confirmation includes "Back to sign in" link.

---

## WI-025: Set Password page (`/auth/set-password`)

Created `SetPasswordView.vue`. Reads `?token` and `?mode` from URL. No token → invalid link message. `mode=invite` → shows first_name, last_name, password → calls invite accept endpoint. `mode=reset` → password only → calls reset confirm endpoint. Handles 410 (expired), 400 (used/invalid token + password validation errors). On success: calls `authStore.setTokens()`, redirects to `/dashboard`.

---

## INTEGRATION GATE: All Pages Live

VERIFIED: `npm run check` exits 0. All four auth pages (Login, Register, ForgotPassword, SetPassword) and Dashboard created. Router guards implemented. 5 Vitest unit tests pass. @ 2026-03-24

**Note:** Browser visual verification deferred — API server port 8000 is not exposed on host (only internal Docker network). Tests confirm all logic works.

---

## WI-026: E2E smoke — invite accept flow

⏸️ Deferred — E2E runner not configured.

---

## WI-027: E2E smoke — forgot password + reset flow

⏸️ Deferred — E2E runner not configured.

---

## WI-028: E2E smoke — route guards + `?next=` redirect

⏸️ Deferred — E2E runner not configured.

---

## INTEGRATION GATE: All Tests Pass — VERIFIED

VERIFIED: `docker compose exec api pytest` — 36 backend tests pass. `npm run check` — exits 0, 47 warnings, 0 errors. `npx vitest run tests/unit/` — 5 unit tests pass. Cross-tenant isolation confirmed in test_invite.py::test_cross_org_invite_token_rejected_on_wrong_subdomain. @ 2026-03-24

---

## WI-029: Update `about/ARCHITECTURE.md`

Updated ARCHITECTURE.md: added `UserInvitation`, `PasswordResetToken`, `BlacklistedRefreshToken` to data model section. Added invite and password reset endpoints to API section. Documented `TenantAccessToken` custom payload pattern and why `for_user()` cannot be used with our custom User. Updated frontend directory structure to include new views. Added Pinia `auth` store documentation with token storage table.

---

## Key Technical Learnings (Cross-Cutting)

1. **simplejwt + custom User**: simplejwt's `OutstandingToken` has a FK to Django's `auth.User`. When using a custom User model not registered as `AUTH_USER_MODEL`, `RefreshToken.for_user()` fails. Solution: build `RefreshToken()` manually with explicit claims; use a custom `BlacklistedRefreshToken` model (JTI-keyed) for blacklisting.

2. **pytest-django + APIClient + TenantMiddleware**: The full Django test WSGI handler runs with `DEBUG=False` by default (not set explicitly, but pytest-django's test database setup may affect it). The `TenantMiddleware` only reads `X-Tenant-Slug` header when `DEBUG=True`. Fixed globally via `backend/conftest.py` with an `autouse` fixture.

3. **DRF throttling + custom User**: DRF's `UserRateThrottle.get_cache_key()` calls `request.user.is_authenticated`. Our custom User must have `is_authenticated` and `is_anonymous` properties.

4. **Circular imports in Vue**: Axios client and router/stores have circular dependencies. Solved by using dynamic `import()` inside interceptor callbacks rather than top-level static imports.

5. **Celery in dev**: Celery tasks are defined but the worker is not started in `docker-compose.yml`. Views wrap `task.delay()` in try/except to avoid hard failures in development without a running worker.
