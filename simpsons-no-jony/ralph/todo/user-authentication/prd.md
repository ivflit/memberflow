# PRD: User Authentication

**branchName:** feature/user-authentication

## Overview

MemberFlow has a working tenant foundation but no user accounts. This feature adds the complete authentication layer: self-registration (gated by tenant flag), admin-invited registration, login with JWT tokens, silent background token refresh, logout, forgot password, and password reset. Four frontend pages are built with Bulma. All auth is tenant-scoped — credentials from one club are useless on another.

## Source Spec

`simpsons-no-jony/lisa/features/user-authentication/spec.md`

**⚠️ READ THE SPEC — it contains implementation patterns, exact error messages, email templates, and Given/When/Then acceptance criteria for every FR.**

## Goals

- Any member can register or accept an invite and receive JWT tokens scoped to their org
- Login is tenant-isolated — org A credentials fail on org B
- Access tokens silently refresh; users never see an unexpected logout
- Password reset is single-use, 24-hour, and auto-logs the user in on completion
- All four auth pages render correctly and apply tenant branding via CSS custom properties

## Testing Requirements (Applies to ALL Work Items)

**⚠️ MANDATORY — every WI acceptance criteria MUST include both:**

1. ✅ **Check gate (frontend WIs):** `cd frontend && npm run check` exits 0
2. ✅ **Test gate (backend WIs):** `docker compose exec api pytest` passes
3. ✅ Manual verification at integration gates

**If ANY check fails:** Fix before marking the WI complete. Do NOT skip.

---

## Work Items

### WI-001: Create `users` Django app

**Priority:** 1
**Effort:** S
**Status:** ❌ Not started

**Description:** Scaffold the `users` app. Register it in `INSTALLED_APPS`. Create empty `models.py`, `serializers.py`, `views.py`, `urls.py`, and a `tests/` package. No models yet — just the skeleton so subsequent WIs have a home.

**Acceptance Criteria:**

- [ ] `backend/apps/users/` exists with `__init__.py`, `models.py`, `serializers.py`, `views.py`, `urls.py`, `tests/__init__.py`
- [ ] `users` added to `INSTALLED_APPS` in `config/settings/base.py`
- [ ] `include('apps.users.urls')` mounted at `/api/v1/auth/` in `config/urls.py`
- [ ] `docker compose exec api python manage.py check` exits 0

**Notes:**
- **Pattern:** Mirror structure of `apps/organizations/` — same layout
- **Reference:** `backend/apps/organizations/` — copy directory structure
- **Hook point:** `backend/config/settings/base.py:INSTALLED_APPS` and `backend/config/urls.py:urlpatterns`

---

### WI-002: `User` model + `UserOrganizationRole` model + migrations

**Priority:** 2
**Effort:** M
**Status:** ❌ Not started

**Description:** Create the `User` model (inheriting `TenantAwareModel`) and the `UserOrganizationRole` model. Email is unique per organisation, not globally. Generate and apply migrations.

**Acceptance Criteria:**

- [ ] `User` inherits `TenantAwareModel`; fields: `email` (EmailField), `first_name`, `last_name`, `is_active` (default=True), `password` (via `AbstractBaseUser` mixin or `set_password`)
- [ ] `UniqueConstraint(fields=['organization', 'email'], name='unique_email_per_org')` on `User.Meta`
- [ ] `UserOrganizationRole` has `user` FK, `organization` FK, `role` CharField with choices `(member, org_staff, org_admin, platform_admin)`, `unique_together = ('user', 'organization')`
- [ ] Migrations generated and `docker compose exec api python manage.py migrate` exits 0
- [ ] `docker compose exec api pytest` passes

**Notes:**
- **Pattern:** See spec "Data Model" and architecture `TenantAwareModel` pattern
- **Reference:** `backend/apps/core/models.py:TenantAwareModel` — inherit from this; `backend/apps/organizations/models.py` — FK pattern
- **Hook point:** `backend/apps/users/models.py`

---

### WI-003: `UserOrganizationRole` — add `allow_self_registration` to `OrganizationConfig` + update seed

**Priority:** 3
**Effort:** S
**Status:** ❌ Not started

**Description:** Add `allow_self_registration = BooleanField(default=False)` to `OrganizationConfig`. Generate migration. Update `seed_dev` command to set `allow_self_registration=True` on the `test-club` org so local development allows registration out of the box.

**Acceptance Criteria:**

- [ ] `OrganizationConfig.allow_self_registration` field exists with `default=False`
- [ ] Migration generated and applied
- [ ] `seed_dev` sets `allow_self_registration=True` on `test-club` org config
- [ ] `docker compose exec api pytest` passes

**Notes:**
- **Pattern:** Simple BooleanField addition to existing model
- **Reference:** `backend/apps/organizations/models.py:OrganizationConfig` — add field here
- **Hook point:** `backend/apps/organizations/management/commands/seed_dev.py` — update `OrganizationConfig` creation/update

---

### WI-004: simplejwt settings + DRF throttle config

**Priority:** 4
**Effort:** S
**Status:** ❌ Not started

**Description:** Configure `djangorestframework-simplejwt` in `base.py`: access token 15 min, refresh token 7 days, rotation enabled, blacklist app added. Configure DRF throttle classes — login endpoint at 10/min per IP, password reset at 5/min per IP.

**Acceptance Criteria:**

- [ ] `rest_framework_simplejwt` and `rest_framework_simplejwt.token_blacklist` in `INSTALLED_APPS`
- [ ] `SIMPLE_JWT` config: `ACCESS_TOKEN_LIFETIME=timedelta(minutes=15)`, `REFRESH_TOKEN_LIFETIME=timedelta(days=7)`, `ROTATE_REFRESH_TOKENS=True`, `BLACKLIST_AFTER_ROTATION=True`
- [ ] `SIMPLE_JWT['AUTH_TOKEN_CLASSES']` includes `rest_framework_simplejwt.tokens.AccessToken`
- [ ] Custom throttle classes `LoginRateThrottle` (10/min) and `PasswordResetRateThrottle` (5/min) defined in `core/throttles.py`
- [ ] Blacklist migration applied: `docker compose exec api python manage.py migrate` exits 0

**Notes:**
- **Pattern:** See spec "Implementation Patterns → JWT payload" for required payload fields
- **Reference:** `backend/config/settings/base.py` — add `SIMPLE_JWT` dict; `backend/apps/core/` — add `throttles.py`
- **Hook point:** `backend/config/settings/base.py:INSTALLED_APPS` and `REST_FRAMEWORK` dict

---

### WI-005: Custom JWT token with `organization_id` + `role` in payload

**Priority:** 5
**Effort:** S
**Status:** ❌ Not started

**Description:** Subclass simplejwt's `AccessToken` to inject `organization_id` and `role` into the payload. This is used by every auth endpoint that returns tokens.

**Acceptance Criteria:**

- [ ] `TenantAccessToken(AccessToken)` defined in `apps/users/tokens.py`
- [ ] `get_token(user)` classmethod sets `token['organization_id'] = str(user.organization_id)` and fetches the user's role from `UserOrganizationRole`
- [ ] Token payload matches spec: `{ user_id, organization_id, role, exp }`
- [ ] `docker compose exec api pytest` passes

**Notes:**
- **Pattern:** See spec "Implementation Patterns → JWT payload" — `{ user_id, organization_id, role, exp }`
- **Reference:** simplejwt `AccessToken` subclass pattern; no existing file to extend
- **Hook point:** New file `backend/apps/users/tokens.py`; imported in serializers that issue tokens

---

### 🚦 INTEGRATION GATE: Backend Foundation

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Run: `docker compose exec api python manage.py migrate`
2. [ ] Expected: All migrations apply with no errors (including simplejwt blacklist tables)
3. [ ] Run: `docker compose exec api python manage.py seed_dev`
4. [ ] Expected: `test-club` org created/updated with `allow_self_registration=True`
5. [ ] Run: `docker compose exec api pytest`
6. [ ] Expected: All existing tests still pass
7. [ ] Evidence: Write "VERIFIED: [observation] @ [timestamp]" in learnings.md

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-006: Registration serializer + `POST /api/v1/auth/register/` view

**Priority:** 6
**Effort:** M
**Status:** ❌ Not started

**Description:** Build the self-registration endpoint. Checks `allow_self_registration` flag, validates input, creates `User` and `UserOrganizationRole(role=member)`, returns JWT tokens.

**Acceptance Criteria:**

- [ ] `RegisterSerializer` validates `email`, `password` (via Django validators), `first_name`, `last_name`; checks email uniqueness within `request.tenant`
- [ ] `RegisterView` (APIView, no auth required) creates `User` scoped to `request.tenant` and `UserOrganizationRole(role=member)`
- [ ] Returns `201 { access, refresh, user: { id, email, first_name, last_name, role } }`
- [ ] Returns `403` if `request.tenant.config.allow_self_registration` is False
- [ ] Returns `409` if email already exists in this org
- [ ] Returns `400` with Django validator message if password fails validation
- [ ] Throttled by `AnonRateThrottle` default (no specific throttle needed — registration is less sensitive than login)
- [ ] Registered at `POST /api/v1/auth/register/` in `apps/users/urls.py`
- [ ] `docker compose exec api pytest` passes

**Notes:**
- **Pattern:** See spec FR-1 and "Implementation Patterns → Tenant-scoped user lookup"
- **Reference:** `backend/apps/organizations/views.py:health_check` — how `request.tenant` is used; `backend/apps/users/tokens.py` — for issuing tokens
- **Hook point:** `backend/apps/users/views.py` + `backend/apps/users/urls.py`

---

### WI-007: Custom login view — `POST /api/v1/auth/login/`

**Priority:** 7
**Effort:** M
**Status:** ❌ Not started

**Description:** Custom login endpoint that validates credentials scoped to `request.tenant`, applies the login throttle, and returns `{ access, refresh, user }`. Uses the same error message for wrong email and wrong password (no enumeration).

**Acceptance Criteria:**

- [ ] `LoginView` (APIView, no auth required) looks up user with `User.objects.for_tenant(request.tenant).get(email=email)`
- [ ] Returns `401 { "detail": "Invalid email or password." }` for both wrong email and wrong password
- [ ] Returns `403 { "detail": "Account is inactive." }` if `user.is_active` is False
- [ ] Returns `200 { access, refresh, user: { id, email, first_name, last_name, role } }` on success
- [ ] `LoginRateThrottle` (10/min, from WI-004) applied to this view
- [ ] Registered at `POST /api/v1/auth/login/`
- [ ] `docker compose exec api pytest` passes

**Notes:**
- **Pattern:** See spec FR-3 ACs — especially "same message for wrong email and wrong password"
- **Reference:** `backend/apps/users/tokens.py:TenantAccessToken` — use this to issue tokens
- **Hook point:** `backend/apps/users/views.py` + `backend/apps/users/urls.py`

---

### WI-008: Token refresh + logout endpoints

**Priority:** 8
**Effort:** S
**Status:** ❌ Not started

**Description:** Wire up simplejwt's `TokenRefreshView` and a custom logout view that blacklists the refresh token. Both require minimal code — mostly URL wiring and a thin wrapper.

**Acceptance Criteria:**

- [ ] `POST /api/v1/auth/token/refresh/` → simplejwt `TokenRefreshView`; returns `{ access, refresh }` (rotation enabled)
- [ ] `POST /api/v1/auth/logout/` → custom view that blacklists the submitted refresh token, returns `204`
- [ ] Logout returns `400` if token is missing or already blacklisted
- [ ] Both endpoints registered in `apps/users/urls.py`
- [ ] `docker compose exec api pytest` passes

**Notes:**
- **Pattern:** See spec FR-4 and FR-5
- **Reference:** simplejwt `TokenRefreshView` imported from `rest_framework_simplejwt.views`; `OutstandingToken` / `BlacklistedToken` from `rest_framework_simplejwt.token_blacklist.models`
- **Hook point:** `backend/apps/users/views.py` (logout) + `backend/apps/users/urls.py`

---

### 🚦 INTEGRATION GATE: Register + Login API

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] `docker compose up` — all services healthy
2. [ ] Register a user:
   ```
   curl -s -X POST http://localhost:8000/api/v1/auth/register/ \
     -H "Content-Type: application/json" \
     -H "X-Tenant-Slug: test-club" \
     -d '{"email":"test@example.com","password":"Str0ngPass!","first_name":"Test","last_name":"User"}'
   ```
3. [ ] Expected: `201` with `access`, `refresh`, and `user.role = "member"`
4. [ ] Login with the same user and confirm `200` with tokens
5. [ ] Logout with the refresh token and confirm `204`; retry refresh and confirm `401`
6. [ ] Evidence: Write "VERIFIED: [observation] @ [timestamp]" in learnings.md

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-009: `UserInvitation` model + migration

**Priority:** 9
**Effort:** S
**Status:** ❌ Not started

**Description:** Create the `UserInvitation` model in `apps/users/models.py`. It inherits `TenantAwareModel` and stores the invitation token, who sent it, whether it's used, and when it expires.

**Acceptance Criteria:**

- [ ] `UserInvitation(TenantAwareModel)` fields: `email` (EmailField), `token` (UUIDField, unique, default=uuid.uuid4), `invited_by` (FK → User, on_delete=SET_NULL, null=True), `is_used` (BooleanField, default=False), `expires_at` (DateTimeField)
- [ ] `expires_at` set to `timezone.now() + timedelta(days=7)` in model `save()` or manager if not provided
- [ ] Migration generated and applied cleanly
- [ ] `docker compose exec api pytest` passes

**Notes:**
- **Pattern:** See spec "Data Model → UserInvitation"
- **Reference:** `backend/apps/users/models.py` — add after `User` model
- **Hook point:** `backend/apps/users/models.py`

---

### WI-010: Celery email tasks — invite + password reset emails

**Priority:** 10
**Effort:** S
**Status:** ❌ Not started

**Description:** Create `tasks/email.py` with `send_invite_email` and `send_reset_email` Celery tasks. Both send plain-text emails with the exact subject and body defined in the spec. Uses Django's `send_mail`. Retries up to 3 times with 60s backoff.

**Acceptance Criteria:**

- [ ] `send_invite_email(invitation_id, base_url)` task: looks up `UserInvitation`, sends email to `invitation.email` with subject `"You've been invited to join {org.name} on MemberFlow"` and body from spec template
- [ ] `send_reset_email(token_id, base_url)` task: looks up `PasswordResetToken`, sends email with subject `"Reset your MemberFlow password for {org.name}"` and body from spec template
- [ ] Both tasks use `bind=True`, `max_retries=3`, `countdown=60 * (2 ** self.request.retries)`
- [ ] `base_url` is passed explicitly (never inferred from env) — e.g. `"http://test-club.localhost:5173"`
- [ ] `docker compose exec api pytest` passes

**Notes:**
- **Pattern:** See spec "Implementation Patterns → Invite/reset email" for exact subject and body templates
- **Reference:** No existing email tasks — new file `backend/tasks/email.py`
- **Hook point:** `backend/tasks/email.py`; imported in invite and reset views

---

### WI-011: `POST /api/v1/auth/invite/` — send invite

**Priority:** 11
**Effort:** M
**Status:** ❌ Not started

**Description:** Org admin or staff sends an invitation to an email address. Creates a `UserInvitation` record and queues the email task.

**Acceptance Criteria:**

- [ ] `SendInviteView` requires `IsOrgAdmin` or `IsOrgStaff` permission (JWT authenticated)
- [ ] Returns `409` if a `User` with that email already exists in this org
- [ ] Creates `UserInvitation` scoped to `request.tenant` with `invited_by=request.user`
- [ ] Queues `send_invite_email.delay(invitation.id, base_url)` — `base_url` constructed from `request` (e.g. using `request.scheme + "://" + request.tenant.slug + ".localhost:5173"` in dev, configurable)
- [ ] Returns `201 { "message": "Invitation sent" }`
- [ ] Returns `400` for invalid email format
- [ ] Returns `403` if caller is not org_admin or org_staff
- [ ] Registered at `POST /api/v1/auth/invite/`
- [ ] `docker compose exec api pytest` passes

**Notes:**
- **Pattern:** See spec FR-2 ACs — happy path send invite
- **Reference:** `backend/apps/core/permissions.py` — `IsOrgAdmin` permission class (create if not yet implemented); `backend/apps/users/models.py:UserInvitation`
- **Hook point:** `backend/apps/users/views.py` + `backend/apps/users/urls.py`

---

### WI-012: `POST /api/v1/auth/invite/accept/` — accept invite

**Priority:** 12
**Effort:** M
**Status:** ❌ Not started

**Description:** Invitee submits their token, password, and name to complete account creation. Returns JWT tokens on success.

**Acceptance Criteria:**

- [ ] Looks up `UserInvitation` by `token`; returns `400` if not found or `is_used=True`
- [ ] Returns `410` if `expires_at < timezone.now()`
- [ ] Creates `User(email=invitation.email, ...)` scoped to `request.tenant`
- [ ] Creates `UserOrganizationRole(role=member)`
- [ ] Sets `invitation.is_used = True`
- [ ] Returns `201 { access, refresh, user: { id, email, first_name, last_name, role } }`
- [ ] Password validated via Django validators; `400` with validator message on failure
- [ ] Registered at `POST /api/v1/auth/invite/accept/`
- [ ] `docker compose exec api pytest` passes

**Notes:**
- **Pattern:** See spec FR-2 ACs — accept invite; "Data Model → UserInvitation"
- **Reference:** `backend/apps/users/views.py:RegisterView` — similar User creation pattern
- **Hook point:** `backend/apps/users/views.py` + `backend/apps/users/urls.py`

---

### 🚦 INTEGRATION GATE: Invitation Flow

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Create an org_admin user for `test-club` (via Django shell or test fixture)
2. [ ] Call `POST /api/v1/auth/invite/` with admin JWT — confirm `201`
3. [ ] Inspect the `UserInvitation` table — confirm record exists with `is_used=False`
4. [ ] Call `POST /api/v1/auth/invite/accept/` with the token — confirm `201` with tokens
5. [ ] Confirm `UserInvitation.is_used = True` and new `User` + `UserOrganizationRole` exist
6. [ ] Run: `docker compose exec api pytest`
7. [ ] Evidence: Write "VERIFIED: [observation] @ [timestamp]" in learnings.md

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-013: `PasswordResetToken` model + migration

**Priority:** 13
**Effort:** S
**Status:** ❌ Not started

**Description:** Create the `PasswordResetToken` model. Not tenant-scoped (the FK to `User` provides the org link implicitly). Tracks token UUID, expiry, and used status.

**Acceptance Criteria:**

- [ ] `PasswordResetToken` model fields: `id` (UUIDField, PK), `user` (FK → User, on_delete=CASCADE), `token` (UUIDField, unique, default=uuid.uuid4), `is_used` (BooleanField, default=False), `expires_at` (DateTimeField), `created_at` (auto_now_add)
- [ ] `expires_at` set to `timezone.now() + timedelta(hours=24)` on creation
- [ ] Migration generated and applied cleanly
- [ ] `docker compose exec api pytest` passes

**Notes:**
- **Pattern:** See spec "Data Model → PasswordResetToken"
- **Reference:** `backend/apps/users/models.py:UserInvitation` — same pattern, different TTL
- **Hook point:** `backend/apps/users/models.py`

---

### WI-014: `POST /api/v1/auth/password/reset/` — request reset

**Priority:** 14
**Effort:** M
**Status:** ❌ Not started

**Description:** Accepts an email, silently does nothing if the user isn't found (no enumeration). If found, invalidates any existing unused token for that user, creates a new `PasswordResetToken`, and queues the reset email.

**Acceptance Criteria:**

- [ ] Always returns `200 { "message": "If that email is registered, a reset link has been sent." }` — no 404
- [ ] If user found: any existing `PasswordResetToken` for that user with `is_used=False` is updated to `is_used=True` before new token is created
- [ ] New `PasswordResetToken` created with 24-hour expiry
- [ ] `send_reset_email.delay(token.id, base_url)` queued
- [ ] `PasswordResetRateThrottle` (5/min from WI-004) applied to this view
- [ ] No authentication required
- [ ] Registered at `POST /api/v1/auth/password/reset/`
- [ ] `docker compose exec api pytest` passes

**Notes:**
- **Pattern:** See spec FR-6 ACs — especially AC-3 (second request invalidates first token)
- **Reference:** `backend/apps/users/models.py:PasswordResetToken`; `backend/tasks/email.py:send_reset_email`
- **Hook point:** `backend/apps/users/views.py` + `backend/apps/users/urls.py`

---

### WI-015: `POST /api/v1/auth/password/reset/confirm/` — complete reset

**Priority:** 15
**Effort:** M
**Status:** ❌ Not started

**Description:** Accepts token + new password. Validates token state and expiry. Sets the new password, marks token used, and returns JWT tokens so the user is automatically logged in.

**Acceptance Criteria:**

- [ ] Returns `400` if token not found or `is_used=True` — message: `"This reset link has already been used or is invalid."`
- [ ] Returns `410` if `expires_at < timezone.now()` — message: `"This reset link has expired."`
- [ ] Returns `400` with Django validator message if password fails validation
- [ ] On success: sets new password, sets `token.is_used=True`, returns `200 { access, refresh, user: { id, email, first_name, last_name, role } }`
- [ ] No authentication required
- [ ] Registered at `POST /api/v1/auth/password/reset/confirm/`
- [ ] `docker compose exec api pytest` passes

**Notes:**
- **Pattern:** See spec FR-7 ACs — happy path + expired token
- **Reference:** `backend/apps/users/views.py:InviteAcceptView` — similar token validation pattern
- **Hook point:** `backend/apps/users/views.py` + `backend/apps/users/urls.py`

---

### WI-016: Unit tests — password reset + invite token logic

**Priority:** 16
**Effort:** S
**Status:** ❌ Not started

**Description:** Unit tests covering the token validation logic for password reset and invite acceptance. These scenarios are too fine-grained for E2E and have multiple conditional branches worth isolating.

**Acceptance Criteria:**

- [ ] `tests/unit/users/test_password_reset.py`: valid email generates token, unknown email returns 200, second request invalidates first token, used token rejected, expired token returns 410
- [ ] `tests/unit/users/test_invite.py`: used invite token returns 400, expired invite returns 410, cross-org invite token rejected on wrong subdomain
- [ ] All tests pass: `docker compose exec api pytest apps/users/tests/`

**Notes:**
- **Pattern:** See spec "Test Strategy → Unit Tests" and FR-6/FR-7 ACs
- **Reference:** `backend/apps/organizations/tests/test_views.py` — pytest + Django test client pattern
- **Hook point:** `backend/apps/users/tests/test_password_reset.py` and `backend/apps/users/tests/test_invite.py`

---

### 🚦 INTEGRATION GATE: Full Auth API

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Run `docker compose exec api pytest` — all tests pass (including new unit tests)
2. [ ] Test reset flow via curl:
   - `POST /api/v1/auth/password/reset/` with a registered email → `200`
   - Retrieve token from DB; `POST /api/v1/auth/password/reset/confirm/` → `200` with tokens
   - Retry same token → `400`
3. [ ] Confirm second reset request invalidates first: create two tokens, first is `is_used=True`
4. [ ] Evidence: Write "VERIFIED: [observation] @ [timestamp]" in learnings.md

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-017: Pinia `auth` store

**Priority:** 17
**Effort:** M
**Status:** ❌ Not started

**Description:** Create `frontend/src/stores/auth.js`. Manages access token (memory), user state, and `isAuthenticated`. Provides `login`, `register`, `logout`, `setTokens` actions. Access token lives only in Pinia; refresh token in `localStorage` key `mf_refresh_token`.

**Acceptance Criteria:**

- [ ] `auth` store state: `{ accessToken: null, user: null }`
- [ ] `isAuthenticated` getter: `!!state.accessToken`
- [ ] `isOrgAdmin` getter: `state.user?.role === 'org_admin' || state.user?.role === 'org_staff'`
- [ ] `login(email, password)` action: calls `POST /api/v1/auth/login/`, stores access token in state, refresh token in `localStorage('mf_refresh_token')`, sets `user`
- [ ] `register(payload)` action: calls `POST /api/v1/auth/register/`, same token storage pattern
- [ ] `logout()` action: calls `POST /api/v1/auth/logout/`, clears state and localStorage
- [ ] `setTokens({ access, refresh, user })` helper: called by interceptor on silent refresh
- [ ] `cd frontend && npm run check` exits 0

**Notes:**
- **Pattern:** See spec "Implementation Patterns → Token storage"
- **Reference:** `frontend/src/stores/app.js` — existing Pinia store to follow for structure
- **Hook point:** New file `frontend/src/stores/auth.js`; exported and registered in `frontend/src/main.js`

---

### WI-018: Axios client — JWT attachment + silent refresh interceptor

**Priority:** 18
**Effort:** M
**Status:** ❌ Not started

**Description:** Update `frontend/src/api/client.js` to attach `Authorization: Bearer <access>` on every request and intercept 401 responses to silently refresh the access token. If refresh also fails, clear auth state and redirect to `/login`.

**Acceptance Criteria:**

- [ ] Request interceptor reads `authStore.accessToken` and sets `Authorization: Bearer ...` header if present
- [ ] Response interceptor catches `401`, calls `POST /api/v1/auth/token/refresh/` with `localStorage.getItem('mf_refresh_token')`
- [ ] On refresh success: calls `authStore.setTokens(...)` and retries the original request exactly once
- [ ] On refresh failure: calls `authStore.logout()` (clears state) and calls `router.push('/login')`
- [ ] Interceptor does NOT retry if the failing request was itself the refresh endpoint (prevents infinite loop)
- [ ] `cd frontend && npm run check` exits 0

**Notes:**
- **Pattern:** See spec FR-4 ACs — "Silent refresh succeeds" and "Refresh token invalid — force logout"
- **Reference:** `frontend/src/api/client.js` — existing Axios instance to extend
- **Hook point:** `frontend/src/api/client.js` — add interceptors after Axios instance creation

---

### WI-019: Unit tests — Axios interceptor

**Priority:** 19
**Effort:** S
**Status:** ❌ Not started

**Description:** Unit tests for the Axios response interceptor logic. Mocks the 401 response and refresh endpoint to verify silent refresh and force-logout paths.

**Acceptance Criteria:**

- [ ] `tests/unit/api/client.test.js`: mock 401 → refresh succeeds → original request retried with new token
- [ ] `tests/unit/api/client.test.js`: mock 401 → refresh also returns 401 → auth store cleared + redirect to `/login`
- [ ] `tests/unit/api/client.test.js`: refresh endpoint returning 401 does NOT trigger another refresh (no infinite loop)
- [ ] All tests pass: `cd frontend && npx vitest run tests/unit/`
- [ ] `cd frontend && npm run check` exits 0

**Notes:**
- **Pattern:** See spec FR-4 ACs
- **Reference:** `frontend/src/api/client.js` — the file under test; mock with `vi.mock` (Vitest)
- **Hook point:** New file `frontend/tests/unit/api/client.test.js`

---

### WI-020: Vue Router — auth routes + `beforeEach` guard + `?next=` redirect

**Priority:** 20
**Effort:** M
**Status:** ❌ Not started

**Description:** Add all auth routes to the Vue Router. Implement the `beforeEach` guard: unauthenticated users hitting protected routes are redirected to `/login?next=<route>`. Authenticated users hitting `/login` are redirected to `/dashboard`. After login, the auth store reads `?next` and redirects there.

**Acceptance Criteria:**

- [ ] Routes added: `/login`, `/register`, `/forgot-password`, `/auth/set-password`, `/dashboard` (placeholder component for now)
- [ ] Protected routes carry `meta: { requiresAuth: true }`
- [ ] `beforeEach` guard: if `requiresAuth` and `!authStore.isAuthenticated` → redirect to `/login?next=<to.fullPath>`
- [ ] `beforeEach` guard: if route is `/login` and `authStore.isAuthenticated` → redirect to `/dashboard`
- [ ] After successful login/register, auth store reads `router.currentRoute.query.next` and navigates there (or `/dashboard`)
- [ ] `cd frontend && npm run check` exits 0

**Notes:**
- **Pattern:** See spec FR-8 ACs — all three AC scenarios
- **Reference:** `frontend/src/router/index.js` — existing router to extend
- **Hook point:** `frontend/src/router/index.js`

---

### 🚦 INTEGRATION GATE: Frontend Auth Foundation

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] `docker compose up`
2. [ ] Open `http://localhost:5173/dashboard` in browser
3. [ ] Expected: redirected to `/login` (route guard fires)
4. [ ] Open `http://localhost:5173/login` while logged in (after manually seeding a token) — expected: redirected to `/dashboard`
5. [ ] Run `cd frontend && npm run check` — exits 0
6. [ ] Evidence: Write "VERIFIED: [observation] @ [timestamp]" in learnings.md

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-021: Login page (`/login`)

**Priority:** 21
**Effort:** M
**Status:** ❌ Not started

**Description:** Build the Login page using Bulma. Email and password fields, submit button, "Forgot password?" link, inline error display. On success, reads `?next` and redirects.

**Acceptance Criteria:**

- [ ] Bulma `box` / `field` / `input` / `button is-primary` components used — no hardcoded hex colours
- [ ] Submits to `authStore.login(email, password)` on form submit
- [ ] On success: redirects to `route.query.next` or `/dashboard`
- [ ] On `401`: displays "Invalid email or password." below the form (not an alert/toast)
- [ ] On `403` (inactive): displays "Your account has been deactivated. Contact your admin."
- [ ] "Forgot password?" link navigates to `/forgot-password`
- [ ] Loading state: button shows "Signing in…" and is disabled during request
- [ ] `cd frontend && npm run check` exits 0

**Notes:**
- **Pattern:** See spec FR-9 (Login page) and UX Flow → Login
- **Reference:** `frontend/src/views/HomeView.vue` — existing view structure to follow; `frontend/src/styles/main.scss` — Bulma already imported
- **Hook point:** New file `frontend/src/views/LoginView.vue`; registered in `frontend/src/router/index.js`
- ⚠️ **NO TOAST:** Display all errors inline below the form. Never use browser alerts, confirm dialogs, or toast notifications.

---

### WI-022: Register page (`/register`)

**Priority:** 22
**Effort:** M
**Status:** ❌ Not started

**Description:** Build the Register page. If `allow_self_registration` is disabled (reads from tenant store config), shows a disabled message instead of the form. Otherwise shows email, password, first name, last name fields.

**Acceptance Criteria:**

- [ ] If `tenantStore.config?.allow_self_registration === false`: renders "Registration is not open. Contact your club admin." with no form
- [ ] Otherwise: Bulma form with `email`, `password`, `first_name`, `last_name` fields
- [ ] Submits to `authStore.register(payload)` on form submit
- [ ] On success: redirects to `/dashboard`
- [ ] On `409`: displays "An account with this email already exists."
- [ ] On `400`: displays the password validator message from the API response
- [ ] Loading state: button disabled during request
- [ ] `cd frontend && npm run check` exits 0

**Notes:**
- **Pattern:** See spec FR-1 AC-2 (disabled state) and FR-9 (Register page)
- **Reference:** `frontend/src/views/LoginView.vue` (from WI-021) — follow same form pattern; `frontend/src/stores/tenant.js` — read `config.allow_self_registration`
- **Hook point:** New file `frontend/src/views/RegisterView.vue`; registered in router
- ⚠️ **NO TOAST:** Display all errors inline below the form. Never use browser alerts, confirm dialogs, or toast notifications.

---

### WI-023: E2E smoke — register + login flows

**Priority:** 23
**Effort:** M
**Status:** ❌ Not started

**Description:** E2E smoke tests proving self-registration and login work end-to-end through the browser, including the disabled-registration state and wrong-password error.

**Acceptance Criteria:**

- [ ] `tests/e2e/user-authentication/register.test.ts`: happy path — fills form, submits, lands on `/dashboard`
- [ ] `tests/e2e/user-authentication/register.test.ts`: registration disabled — page shows disabled message, no form rendered
- [ ] `tests/e2e/user-authentication/login.test.ts`: happy path — login, lands on `/dashboard`
- [ ] `tests/e2e/user-authentication/login.test.ts`: wrong password — error message displayed, no redirect
- [ ] `tests/e2e/user-authentication/login.test.ts`: cross-tenant credentials — `401` displayed as error
- [ ] Uses agent-browser + Page Object Model pattern
- [ ] `cd frontend && npm run check` exits 0

**Notes:**
- **Pattern:** See spec "Test Strategy → E2E Smoke Tests"
- **Reference:** `simpsons-no-jony/ralph/SKILL.md` — agent-browser POM pattern (if available); otherwise standard Vitest + jsdom
- **Hook point:** New directory `frontend/tests/e2e/user-authentication/`
- ⚠️ **NO TOAST:** Tests should assert errors appear inline, not as alerts or toasts.

---

### WI-024: Forgot Password page (`/forgot-password`)

**Priority:** 24
**Effort:** S
**Status:** ❌ Not started

**Description:** Simple page with a single email field. On submit, calls the reset endpoint and switches to a confirmation message. Always shows the same confirmation regardless of whether the email exists.

**Acceptance Criteria:**

- [ ] Bulma form with `email` field and submit button
- [ ] On submit: calls `POST /api/v1/auth/password/reset/` via the API service
- [ ] On success (always `200`): replaces form with message "If that email is registered, a reset link has been sent. Check your inbox."
- [ ] Loading state: button disabled during request
- [ ] Link back to `/login` shown on the confirmation screen
- [ ] `cd frontend && npm run check` exits 0

**Notes:**
- **Pattern:** See spec FR-6 and UX Flow → Forgot Password
- **Reference:** `frontend/src/views/LoginView.vue` — follow form pattern; no store action needed (one-off API call)
- **Hook point:** New file `frontend/src/views/ForgotPasswordView.vue`; registered in router
- ⚠️ **NO TOAST:** Show confirmation state inline (replace form with message). Never use browser alerts or toast notifications.

---

### WI-025: Set Password page (`/auth/set-password`)

**Priority:** 25
**Effort:** M
**Status:** ❌ Not started

**Description:** Shared page for invite-accept and password-reset flows. Reads `?token` and `?mode` from the URL. Shows first_name + last_name fields only in `mode=invite`. No form if `token` is absent. On submit, calls the correct endpoint and stores tokens in auth store.

**Acceptance Criteria:**

- [ ] No `?token` param: renders "This link is invalid. Request a new invitation or password reset." — no form
- [ ] `mode=invite`: shows `first_name`, `last_name`, `password` fields; submits to `POST /api/v1/auth/invite/accept/`
- [ ] `mode=reset`: shows `password` field only; submits to `POST /api/v1/auth/password/reset/confirm/`
- [ ] On `200`: stores tokens via `authStore.setTokens(...)`, redirects to `/dashboard`
- [ ] On `410` (expired): "This invitation has expired. Ask your admin to resend." (invite) or "This reset link has expired. Request a new one." with link to `/forgot-password` (reset)
- [ ] On `400` (used token): "This link has already been used."
- [ ] On `400` (password validation): displays validator message from API
- [ ] `cd frontend && npm run check` exits 0

**Notes:**
- **Pattern:** See spec FR-9 AC-1 (no token), FR-2 AC-3 (expired invite), FR-7 AC-2 (expired reset); UX Flow → Admin Invitation + Forgot Password
- **Reference:** `frontend/src/views/LoginView.vue` — follow form pattern
- **Hook point:** New file `frontend/src/views/SetPasswordView.vue`; registered in router at `/auth/set-password`
- ⚠️ **NO TOAST:** Display expired/invalid token errors inline on the page. Never use browser alerts or toast notifications.

---

### 🚦 INTEGRATION GATE: All Pages Live

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] `docker compose up`
2. [ ] Visit `http://localhost:5173/login` — login form renders with Bulma styling
3. [ ] Visit `http://localhost:5173/register` — registration form renders (test-club has `allow_self_registration=True`)
4. [ ] Register a new user end-to-end: fill form → submit → land on `/dashboard`
5. [ ] Log out and log back in — redirected to `/dashboard`
6. [ ] Visit `http://localhost:5173/forgot-password` — form renders; submit → confirmation message
7. [ ] Visit `http://localhost:5173/auth/set-password` (no token) — invalid link message shown
8. [ ] `cd frontend && npm run check` exits 0
9. [ ] Evidence: Write "VERIFIED: [observation] @ [timestamp]" in learnings.md

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-026: E2E smoke — invite accept flow

**Priority:** 26
**Effort:** M
**Status:** ❌ Not started

**Description:** E2E smoke test for the admin invite → Set Password → dashboard flow, including the expired token error state.

**Acceptance Criteria:**

- [ ] `tests/e2e/user-authentication/invite.test.ts`: admin sends invite (API call), invitee visits Set Password link, fills form, lands on `/dashboard`
- [ ] `tests/e2e/user-authentication/invite.test.ts`: expired token — page shows expiry message, no form
- [ ] Uses agent-browser + POM pattern
- [ ] `cd frontend && npm run check` exits 0

**Notes:**
- **Pattern:** See spec FR-2 ACs and Test Strategy → Invite tests
- **Reference:** `frontend/tests/e2e/user-authentication/register.test.ts` (from WI-023) — follow same pattern
- **Hook point:** `frontend/tests/e2e/user-authentication/invite.test.ts`
- ⚠️ **NO TOAST:** Tests should assert expiry/error messages appear inline on the Set Password page.

---

### WI-027: E2E smoke — forgot password + reset flow

**Priority:** 27
**Effort:** M
**Status:** ❌ Not started

**Description:** E2E smoke test for the full forgot password → email link → Set Password → auto-login flow, including the expired token error state.

**Acceptance Criteria:**

- [ ] `tests/e2e/user-authentication/reset.test.ts`: visits `/forgot-password`, submits email, retrieves token from DB, visits reset link, enters new password, lands on `/dashboard`
- [ ] `tests/e2e/user-authentication/reset.test.ts`: expired token — page shows expiry message with link to request new one
- [ ] Uses agent-browser + POM pattern
- [ ] `cd frontend && npm run check` exits 0

**Notes:**
- **Pattern:** See spec FR-6/FR-7 ACs and UX Flow → Forgot Password
- **Reference:** `frontend/tests/e2e/user-authentication/invite.test.ts` (from WI-026) — similar token-based flow
- **Hook point:** `frontend/tests/e2e/user-authentication/reset.test.ts`
- ⚠️ **NO TOAST:** Tests should assert expiry messages appear inline on the Set Password page.

---

### WI-028: E2E smoke — route guards + `?next=` redirect

**Priority:** 28
**Effort:** M
**Status:** ❌ Not started

**Description:** E2E smoke tests for the route guard behaviour: unauthenticated redirect, `?next=` restoration after login, and authenticated-user redirect away from `/login`.

**Acceptance Criteria:**

- [ ] `tests/e2e/user-authentication/guards.test.ts`: unauthenticated visit to `/dashboard` → redirected to `/login`
- [ ] `tests/e2e/user-authentication/guards.test.ts`: unauthenticated visit to `/memberships` → redirected to `/login?next=/memberships` → after login, lands on `/memberships`
- [ ] `tests/e2e/user-authentication/guards.test.ts`: authenticated user visits `/login` → redirected to `/dashboard`
- [ ] Uses agent-browser + POM pattern
- [ ] `cd frontend && npm run check` exits 0

**Notes:**
- **Pattern:** See spec FR-8 ACs — all three scenarios
- **Reference:** `frontend/tests/e2e/user-authentication/register.test.ts` (from WI-023) — follow POM pattern
- **Hook point:** `frontend/tests/e2e/user-authentication/guards.test.ts`
- ⚠️ **NO TOAST:** Guard redirects should happen silently — no user-visible error messages for unauthorised navigation.

---

### 🚦 INTEGRATION GATE: All Tests Pass

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Run: `docker compose exec api pytest` — all backend tests pass
2. [ ] Run: `cd frontend && npm run check` — exits 0
3. [ ] Run: `cd frontend && npx vitest run tests/unit/` — unit tests pass
4. [ ] Confirm cross-tenant isolation: log in on `test-club`, confirm credentials fail when `X-Tenant-Slug: other-club` is sent
5. [ ] Evidence: Write "VERIFIED: [observation] @ [timestamp]" in learnings.md

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-029: Update `about/ARCHITECTURE.md`

**Priority:** 29
**Effort:** S
**Status:** ❌ Not started

**Description:** Update the architecture document to reflect the `users` app, auth endpoints, JWT token payload pattern, and the Pinia auth store. This feature introduces significant new patterns that future features will reference.

**Acceptance Criteria:**

- [ ] `apps/users/` added to Django app list with description
- [ ] `UserInvitation` and `PasswordResetToken` added to Data Model section
- [ ] Auth endpoints table (`/api/v1/auth/*`) added or updated in API section
- [ ] `TenantAccessToken` custom payload pattern documented in Backend Architecture
- [ ] Pinia `auth` store added to Frontend Directory Structure
- [ ] Token storage pattern (memory vs localStorage) documented in Frontend Architecture

**Notes:**
- **Pattern:** Architecture update — no code pattern
- **Reference:** `about/ARCHITECTURE.md` — extend existing sections in-place
- **Hook point:** `about/ARCHITECTURE.md` — sections 2 (Backend), 3 (Frontend), 4 (Data Model), 5 (API)

---

## Functional Requirements

- FR-1: Self-registration gated by `allow_self_registration` flag
- FR-2: Admin invitation (send + accept) with 7-day token
- FR-3: Tenant-scoped login returning JWT + user object
- FR-4: Silent token refresh via Axios interceptor
- FR-5: Logout with refresh token blacklist
- FR-6: Forgot password (no enumeration, previous token invalidated)
- FR-7: Password reset confirm with auto-login
- FR-8: Route guards with `?next=` restoration
- FR-9: Four Bulma frontend pages (Login, Register, Set Password, Forgot Password)

## Non-Goals

- Social / OAuth login
- Two-factor authentication
- Email verification on self-registration
- Membership approval workflow
- Admin management of existing users (edit/delete/role change)
- HTML email templates (plain text only for now)

## Technical Notes

- `User.email` is unique per organisation — `UniqueConstraint(fields=['organization', 'email'])`
- JWT access token: 15 min, memory only. Refresh token: 7 days, `localStorage('mf_refresh_token')`
- All Celery email tasks: `max_retries=3`, exponential backoff
- `allow_self_registration` defaults to `False` — must be explicitly enabled per tenant
- `base_url` for email links is passed explicitly to Celery tasks, never inferred from environment

## Success Metrics

- A new user can self-register on a tenant with `allow_self_registration=True` and land on `/dashboard`
- An invited user can accept an invite and complete registration end-to-end
- An expired reset link shows a clear error message; a fresh link logs the user in automatically
- A user whose session has expired is silently refreshed without any visible interruption
- `pytest` passes with zero cross-tenant isolation failures
