# Feature: User Authentication

## Problem Statement

MemberFlow has a working tenant foundation but no way for users to create accounts, log in, or recover access. Club members need to register (either self-initiated or via admin invitation), log in, and stay logged in across their session. Club admins need to be able to invite members by email. Without this, the platform cannot serve any users.

---

## Scope

**In:**
- Self-registration (email + password + first/last name) — gated by `allow_self_registration` flag on `OrganizationConfig`
- Admin-invited registration — admin enters member's email; member receives a link to set their password and complete their profile
- Login (email + password) with JWT tokens (access + refresh)
- Silent token refresh — access token renewed in the background; user never redirected to login on expiry
- Logout — refresh token blacklisted
- Forgot password — member requests reset email; single-use link valid for 24 hours
- Password reset — completing reset automatically logs the user in and redirects to dashboard
- Frontend pages: Login, Register, Set Password (invite + reset share this page), Forgot Password
- Route guard: unauthenticated users redirected to login; redirect back to originally intended route after login
- Post-login redirect to `/dashboard`

**Out:**
- Social / OAuth login
- Two-factor authentication
- Email verification on self-registration (account is active immediately)
- Membership approval workflow (`require_membership_approval` config — deferred to memberships feature)
- Admin management of existing users (edit/delete/role change — deferred to admin portal feature)
- Platform admin user management

---

## Requirements

### FR-1: Self-Registration

A member can register themselves at their club's subdomain if `allow_self_registration` is enabled on the tenant's `OrganizationConfig`.

- **Input:** `{ email, password, first_name, last_name }`
- **Output:** `201` with `{ access, refresh, user: { id, email, first_name, last_name, role } }`
- **Errors:**
  - `400` — missing required field
  - `400` — password fails Django validators (message from Django validator)
  - `409` — email already registered in this organisation
  - `403` — `allow_self_registration` is disabled for this tenant
- **Behaviour:** Creates `User` + `UserOrganizationRole(role=member)` scoped to `request.tenant`. Returns JWT tokens immediately — no email verification step.
- **Test type:** E2E
- **Test:** `tests/e2e/user-authentication/register.test.ts` — happy path self-registration; also tests 403 when flag disabled

**Acceptance Criteria:**

AC-1: Happy path
```
Given: org "springfield-cc" has allow_self_registration=True and no existing user with email "alice@example.com"
When: POST /api/v1/auth/register/ with { email, password, first_name, last_name }
Then: 201 response with access token, refresh token, and user object with role="member"
  AND a User and UserOrganizationRole(role=member) exist in the database scoped to springfield-cc
```

AC-2: Self-registration disabled
```
Given: org "barton-fc" has allow_self_registration=False
When: POST /api/v1/auth/register/ on the barton-fc subdomain
Then: 403 response
  AND the /register frontend page shows "Registration is not open. Contact your club admin."
```

AC-3: Duplicate email
```
Given: a User with email "alice@example.com" already exists in org "springfield-cc"
When: POST /api/v1/auth/register/ with the same email on springfield-cc
Then: 409 response; no new User created
```

---

### FR-2: Admin Invitation

An org admin can invite a new member by email. The invitee receives a time-limited link to set their password and complete registration.

- **Input (send invite):** `POST /api/v1/auth/invite/` — `{ email }` — requires `org_admin` or `org_staff` role
- **Output (send invite):** `201 { message: "Invitation sent" }`
- **Errors (send invite):**
  - `400` — invalid email format
  - `409` — email already registered in this organisation
  - `403` — caller is not org_admin or org_staff
- **Invite token:** UUID stored on a new `UserInvitation` model, expires 7 days from creation
- **Input (accept invite):** `POST /api/v1/auth/invite/accept/` — `{ token, password, first_name, last_name }`
- **Output (accept invite):** `201` with `{ access, refresh, user: { id, email, first_name, last_name, role } }`
- **Errors (accept invite):**
  - `400` — missing required field or password fails validators
  - `400` — token not found or already used
  - `410` — token expired (7 days elapsed)
- **Behaviour:** Creates `User` + `UserOrganizationRole(role=member)`. Marks invitation as used. Returns JWT tokens immediately.
- **Test type:** E2E
- **Test:** `tests/e2e/user-authentication/invite.test.ts` — admin sends invite, invitee accepts, logs in successfully; also tests expired token returns 410

**Acceptance Criteria:**

AC-1: Happy path — send invite
```
Given: authenticated org_admin on "springfield-cc", no existing user with email "bob@example.com"
When: POST /api/v1/auth/invite/ with { email: "bob@example.com" }
Then: 201 { message: "Invitation sent" }
  AND a UserInvitation record exists with is_used=False and expires_at = now + 7 days
  AND an invite email is queued to "bob@example.com"
```

AC-2: Happy path — accept invite
```
Given: a valid, unused, unexpired UserInvitation token for "bob@example.com" on "springfield-cc"
When: POST /api/v1/auth/invite/accept/ with { token, password, first_name, last_name }
Then: 201 with access token, refresh token, and user object
  AND UserInvitation.is_used = True
  AND a User and UserOrganizationRole(role=member) exist scoped to springfield-cc
```

AC-3: Expired invite token
```
Given: a UserInvitation whose expires_at is in the past
When: POST /api/v1/auth/invite/accept/ with that token
Then: 410 response
  AND the Set Password page shows "This invitation has expired. Ask your admin to resend."
```

---

### FR-3: Login

A member logs in with their email and password, scoped to the current tenant.

- **Input:** `POST /api/v1/auth/login/` — `{ email, password }`
- **Output:** `200 { access, refresh, user: { id, email, first_name, last_name, role } }`
- **Errors:**
  - `401` — invalid credentials (same message for both wrong email and wrong password — no enumeration)
  - `403` — user exists but is inactive
- **Behaviour:** Validates credentials against users scoped to `request.tenant` only. JWT access token expires in 15 min. Refresh token expires in 7 days. JWT payload includes `organization_id`, `user_id`, `role`.
- **Rate limiting:** 10 requests/min per IP (DRF throttle on this endpoint).
- **Test type:** E2E
- **Test:** `tests/e2e/user-authentication/login.test.ts` — happy path; wrong password returns 401; wrong tenant (same email, different org) returns 401

**Acceptance Criteria:**

AC-1: Happy path
```
Given: an active User with email "alice@example.com" exists in org "springfield-cc"
When: POST /api/v1/auth/login/ with correct credentials on the springfield-cc subdomain
Then: 200 with access token, refresh token, and user object containing role
  AND frontend stores access token in Pinia (memory) and refresh token in localStorage "mf_refresh_token"
  AND user is redirected to /dashboard (or ?next value if present)
```

AC-2: Wrong password — no enumeration
```
Given: an active User with email "alice@example.com" exists in org "springfield-cc"
When: POST /api/v1/auth/login/ with incorrect password
Then: 401 with message "Invalid email or password." — no indication of which field is wrong
```

AC-3: Cross-tenant credentials rejected
```
Given: User "alice@example.com" exists only in org "springfield-cc"
When: POST /api/v1/auth/login/ with alice's credentials on the "barton-fc" subdomain
Then: 401 — tenant-scoped lookup finds no matching user
```

---

### FR-4: Silent Token Refresh

The Axios client automatically refreshes the access token in the background when it receives a 401, without interrupting the user.

- **Input:** `POST /api/v1/auth/token/refresh/` — `{ refresh }`
- **Output:** `200 { access, refresh }` (rotation enabled — new refresh token returned)
- **Errors:**
  - `401` — refresh token invalid or blacklisted → user is logged out and redirected to login
- **Behaviour:** Axios response interceptor catches 401, calls refresh endpoint, retries original request with new access token. If refresh also fails, clears auth state and redirects to `/login`.
- **Test type:** Unit (interceptor logic)
- **Test:** `tests/unit/api/client.test.ts` — mock 401 response triggers refresh; mock refresh failure clears auth and redirects

**Acceptance Criteria:**

AC-1: Silent refresh succeeds
```
Given: a logged-in user whose access token has just expired
When: any API call returns 401
Then: the interceptor calls POST /api/v1/auth/token/refresh/ with the stored refresh token
  AND retries the original request with the new access token
  AND the user sees no interruption (no redirect, no error message)
```

AC-2: Refresh token invalid — force logout
```
Given: a user whose refresh token has been blacklisted
When: an API call returns 401 and the subsequent refresh call also returns 401
Then: Pinia auth store is cleared and localStorage "mf_refresh_token" is removed
  AND the user is redirected to /login
```

---

### FR-5: Logout

A logged-in user can log out. The refresh token is blacklisted server-side.

- **Input:** `POST /api/v1/auth/logout/` — `{ refresh }` — requires valid access token
- **Output:** `204`
- **Errors:**
  - `400` — refresh token missing or already blacklisted
- **Behaviour:** Calls simplejwt token blacklist. Clears Pinia auth store and `localStorage` refresh token on frontend.
- **Test type:** E2E (included in login E2E test as teardown verification)

**Acceptance Criteria:**

AC-1: Logout clears session
```
Given: a logged-in user with a valid refresh token
When: POST /api/v1/auth/logout/ with the refresh token
Then: 204 response
  AND the refresh token is blacklisted (subsequent refresh calls return 401)
  AND Pinia auth store is cleared and localStorage "mf_refresh_token" is removed
```

---

### FR-6: Forgot Password

A user can request a password reset email if they have forgotten their password.

- **Input:** `POST /api/v1/auth/password/reset/` — `{ email }`
- **Output:** `200 { message: "If that email is registered, a reset link has been sent." }` — always 200 (no email enumeration)
- **Errors:** None exposed — always returns 200
- **Behaviour:** Looks up `User` scoped to `request.tenant` by email. If found and active, any existing unused reset token for that user is invalidated first, then a new single-use `PasswordResetToken` (UUID, expires 24 hours, used=False) is created and an email queued. If not found, silently succeeds. Only one active reset token per user at any time.
- **Rate limiting:** 5 requests/min per IP (DRF throttle on this endpoint).
- **Test type:** Unit
- **Test:** `tests/unit/users/test_password_reset.py` — valid email generates token and queues email; unknown email still returns 200; already-used token is rejected; second request invalidates first token

**Acceptance Criteria:**

AC-1: Valid email — token generated
```
Given: an active User with email "alice@example.com" exists in org "springfield-cc"
When: POST /api/v1/auth/password/reset/ with { email: "alice@example.com" } on springfield-cc
Then: 200 { message: "If that email is registered, a reset link has been sent." }
  AND a PasswordResetToken exists for that user with is_used=False and expires_at = now + 24h
  AND a reset email is queued to "alice@example.com"
```

AC-2: Unknown email — no information leaked
```
Given: no User with email "unknown@example.com" exists in org "springfield-cc"
When: POST /api/v1/auth/password/reset/ with { email: "unknown@example.com" }
Then: 200 with the same message — no 404, no difference in response
  AND no PasswordResetToken is created
```

AC-3: Second request invalidates first token
```
Given: an existing unused PasswordResetToken T1 for "alice@example.com"
When: POST /api/v1/auth/password/reset/ is called again for the same email
Then: T1.is_used is set to True (invalidated)
  AND a new token T2 is created
  AND only T2 can be used for the reset
```

---

### FR-7: Password Reset

A user clicks the reset link, enters a new password, and is automatically logged in.

- **Input:** `POST /api/v1/auth/password/reset/confirm/` — `{ token, password }`
- **Output:** `200 { access, refresh, user: { id, email, first_name, last_name, role } }`
- **Errors:**
  - `400` — password fails Django validators
  - `400` — token not found or already used
  - `410` — token expired (24 hours elapsed)
- **Behaviour:** Validates token, checks not used and not expired. Sets new password. Marks token `used=True`. Returns JWT tokens so the frontend can log the user in directly.
- **Test type:** Unit (covered in FR-6 test file)

**Acceptance Criteria:**

AC-1: Happy path — reset and auto-login
```
Given: a valid, unused, unexpired PasswordResetToken for "alice@example.com"
When: POST /api/v1/auth/password/reset/confirm/ with { token, password }
Then: 200 with access token, refresh token, and user object
  AND PasswordResetToken.is_used = True
  AND alice's password is updated
  AND frontend stores tokens and redirects to /dashboard
```

AC-2: Expired token
```
Given: a PasswordResetToken whose expires_at is in the past
When: POST /api/v1/auth/password/reset/confirm/ with that token
Then: 410 response
  AND the Set Password page shows "This reset link has expired. Request a new one."
```

---

### FR-8: Route Guards and Redirect

Unauthenticated users attempting to access protected routes are redirected to `/login`. After successful login, they are redirected to the originally intended route. Post-login (without a prior redirect) lands on `/dashboard`.

- **Behaviour:** Vue Router `beforeEach` guard reads `auth.isAuthenticated`. If the user navigates to a protected route while logged out, the intended path is stored (e.g. in query param `?next=/memberships`) and the user is sent to `/login`. On successful login, the frontend reads `next` and redirects there; otherwise `/dashboard`.
- **Test type:** E2E
- **Test:** `tests/e2e/user-authentication/guards.test.ts` — unauthenticated visit to `/dashboard` redirects to login; after login, lands on `/dashboard`; direct visit to `/memberships` while logged out → redirects to `/memberships` after login

**Acceptance Criteria:**

AC-1: Direct login → dashboard
```
Given: an unauthenticated user visits /login directly
When: they log in successfully
Then: they are redirected to /dashboard
```

AC-2: Intended route restored after login
```
Given: an unauthenticated user navigates directly to /memberships
When: the route guard fires
Then: user is redirected to /login?next=/memberships
  AND after successful login, user is redirected to /memberships (not /dashboard)
```

AC-3: Already-authenticated user cannot access /login
```
Given: a logged-in user navigates to /login
Then: they are redirected to /dashboard immediately
```

---

### FR-9: Frontend Pages

Four pages required. All pages use Bulma components. No hardcoded brand colours — tenant theme is applied via CSS custom properties on bootstrap.

| Page | Route | Purpose |
|---|---|---|
| Login | `/login` | Email + password form. Link to forgot password. |
| Register | `/register` | Email + password + first/last name form. Hidden if `allow_self_registration` is disabled. |
| Set Password | `/auth/set-password?token=...` | Shared by invite-accept and password-reset flows. First/last name fields shown only for invite flow. |
| Forgot Password | `/forgot-password` | Email input only. Shows confirmation message after submit. |

- **Test type:** E2E (covered by FR-1, FR-2, FR-3, FR-6/7 tests)

**Acceptance Criteria:**

AC-1: Set Password page — no token param
```
Given: a user navigates to /auth/set-password with no token query parameter
Then: the page shows "This link is invalid. Request a new invitation or password reset."
  AND no form is shown
```

---

## Data Model

### New model: `UserInvitation`

Inherits `TenantAwareModel`.

| Field | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `organization` | FK → Organization | from TenantAwareModel |
| `email` | EmailField | — |
| `token` | UUIDField | unique, default=uuid4 |
| `invited_by` | FK → User | — |
| `is_used` | BooleanField | default=False |
| `expires_at` | DateTimeField | set to now + 7 days on create |
| `created_at` | DateTimeField | auto_now_add |

### New model: `PasswordResetToken`

Not tenant-scoped (password reset is per-user, not per-org — but user is already scoped).

| Field | Type | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `user` | FK → User | — |
| `token` | UUIDField | unique, default=uuid4 |
| `is_used` | BooleanField | default=False |
| `expires_at` | DateTimeField | set to now + 24 hours on create |
| `created_at` | DateTimeField | auto_now_add |

### Existing model: `User`

Already defined in architecture as `TenantAwareModel` with `email`, `first_name`, `last_name`, `is_active`. No schema changes required.

### Existing model: `UserOrganizationRole`

Already defined. Role assigned on registration = `member`.

---

## API

### POST /api/v1/auth/register/
Request: `{ "email": "string", "password": "string", "first_name": "string", "last_name": "string" }`
Response 201: `{ "access": "...", "refresh": "...", "user": { "id": "uuid", "email": "string", "first_name": "string", "last_name": "string", "role": "member" } }`
Errors: 400 (validation), 403 (self-registration disabled), 409 (email exists in org)

### POST /api/v1/auth/invite/
Request: `{ "email": "string" }`
Response 201: `{ "message": "Invitation sent" }`
Errors: 400, 403 (not org admin/staff), 409 (already registered)

### POST /api/v1/auth/invite/accept/
Request: `{ "token": "uuid", "password": "string", "first_name": "string", "last_name": "string" }`
Response 201: `{ "access": "...", "refresh": "...", "user": { ... } }`
Errors: 400 (validation/invalid token), 410 (expired)

### POST /api/v1/auth/login/
Request: `{ "email": "string", "password": "string" }`
Response 200: `{ "access": "...", "refresh": "...", "user": { "id": "uuid", "email": "string", "first_name": "string", "last_name": "string", "role": "string" } }`
Errors: 401 (invalid credentials), 403 (inactive)

### POST /api/v1/auth/token/refresh/
Request: `{ "refresh": "string" }`
Response 200: `{ "access": "...", "refresh": "..." }`
Errors: 401 (invalid/blacklisted)

### POST /api/v1/auth/logout/
Request: `{ "refresh": "string" }`
Response 204
Errors: 400

### POST /api/v1/auth/password/reset/
Request: `{ "email": "string" }`
Response 200: `{ "message": "If that email is registered, a reset link has been sent." }`
Errors: none exposed

### POST /api/v1/auth/password/reset/confirm/
Request: `{ "token": "uuid", "password": "string" }`
Response 200: `{ "access": "...", "refresh": "...", "user": { ... } }`
Errors: 400 (validation/invalid token), 410 (expired)

---

## UX Flow

### Self-Registration
1. Member visits `springfield-cc.memberflow.com/register`
2. If `allow_self_registration` is disabled → page shows "Registration is not open. Contact your club admin."
3. Member fills email, password, first name, last name → submits
4. On success → JWT tokens stored, redirected to `/dashboard`
5. On validation error → inline field errors shown

### Admin Invitation
1. Admin visits invite form (in admin portal — UI for this is a single email input field on a later admin portal page; for this feature, the API only is sufficient; the Set Password page is what the invitee uses)
2. Admin enters member email → POST /api/v1/auth/invite/
3. Member receives email with link: `springfield-cc.memberflow.com/auth/set-password?token=...&mode=invite`
4. Member clicks link → Set Password page loads, shows first name, last name, and password fields
5. On submit → account created, JWT tokens stored, redirected to `/dashboard`
6. If token expired → page shows "This invitation has expired. Ask your admin to resend."

### Login
1. Member visits `/login`
2. Enters email + password → submits
3. On success → redirected to `?next` value, or `/dashboard` if none
4. On failure → "Invalid email or password." (single message, no enumeration)

### Forgot Password
1. Member clicks "Forgot password?" on login page → `/forgot-password`
2. Enters email → submits
3. Page shows: "If that email is registered, a reset link has been sent. Check your inbox."
4. Member receives email with link: `springfield-cc.memberflow.com/auth/set-password?token=...&mode=reset`
5. Member clicks link → Set Password page loads, shows password field only (no name fields)
6. On submit → password updated, JWT tokens returned, redirected to `/dashboard`
7. If token expired → "This reset link has expired. Request a new one."

### Silent Token Refresh
1. Axios interceptor receives 401 on any request
2. Calls POST /api/v1/auth/token/refresh/ with stored refresh token
3. On success → retries original request with new access token (transparent to user)
4. On failure → clears auth state, redirects to `/login`

---

## Edge Cases

| Case | Behaviour |
|---|---|
| Self-registration with `allow_self_registration=False` | 403 from API; frontend shows disabled message |
| Duplicate email in same org (register or invite) | 409; frontend shows "An account with this email already exists" |
| Same email in different org | Allowed — `User.email` unique per org, not globally |
| Invite token used twice | 400 "This invitation has already been used." |
| Invite token expired (>7 days) | 410; frontend shows expiry message |
| Reset token expired (>24 hours) | 410; frontend shows expiry message with link to request new one |
| Reset token used twice | 400 "This reset link has already been used." |
| Login with credentials from a different org's user | 401 — tenant-scoped lookup means the user simply isn't found |
| Refresh token blacklisted mid-session | Silent refresh fails → user logged out and redirected to login |
| User navigates to protected route while logged out | Stored in `?next=`, redirected after login |
| Admin invites email that already has an account | 409 "A member with this email already exists in this organisation." |
| User requests second password reset before first expires | Previous token marked is_used=True; new token created; only new token works |
| Set Password page accessed with no `token` param | Page shows "This link is invalid. Request a new invitation or password reset." — no form shown |

---

## Implementation Patterns

### Token storage
- `access` token: Pinia `auth` store (memory only — not persisted)
- `refresh` token: `localStorage` key `mf_refresh_token`

### JWT payload
```json
{ "user_id": "uuid", "organization_id": "uuid", "role": "member|org_staff|org_admin|platform_admin", "exp": 1234567890 }
```

### Tenant-scoped user lookup (login)
```python
user = User.objects.for_tenant(request.tenant).get(email=email)
```

### Invite/reset email
Emails are plain text for now (no HTML template). Queued via Celery task `tasks/email.py`. No club branding in this feature.

**Invite email:**
```
Subject: You've been invited to join {org.name} on MemberFlow
Body:
You've been invited to create an account for {org.name}.

Click the link below to set your password and complete your registration.
This link expires in 7 days.

{link}

If you didn't expect this invitation, you can ignore this email.
```

**Password reset email:**
```
Subject: Reset your MemberFlow password for {org.name}
Body:
We received a request to reset the password for your {org.name} account.

Click the link below to set a new password.
This link expires in 24 hours and can only be used once.

{link}

If you didn't request a password reset, you can ignore this email.
```

### Set Password page (shared)
`/auth/set-password?token=<uuid>&mode=invite|reset`
- `mode=invite` → show first_name, last_name, password fields → calls `POST /api/v1/auth/invite/accept/`
- `mode=reset` → show password field only → calls `POST /api/v1/auth/password/reset/confirm/`

---

## Test Strategy

### 🎯 Test Philosophy: E2E Smoke First

🔥 E2E Smoke Tests — PREFERRED: Prove features work for real users
📦 Unit Tests — FOR: Complex logic with many edge cases only

⚠️ **INTERLEAVING RULE:** Tests MUST be written immediately after their feature phase, NOT all at the end.
⚠️ **FRAMEWORK:** E2E uses **agent-browser** with **Page Object Model** (NOT Playwright).

### E2E Smoke Tests (preferred)

| Scenario | File | Phase |
|---|---|---|
| Self-registration happy path | `tests/e2e/user-authentication/register.test.ts` | After FR-1 API + UI |
| Self-registration disabled (403) | `tests/e2e/user-authentication/register.test.ts` | After FR-1 |
| Invite send + accept happy path | `tests/e2e/user-authentication/invite.test.ts` | After FR-2 API + UI |
| Expired invite token (410) | `tests/e2e/user-authentication/invite.test.ts` | After FR-2 |
| Login happy path + redirect to dashboard | `tests/e2e/user-authentication/login.test.ts` | After FR-3 API + UI |
| Wrong password returns 401 | `tests/e2e/user-authentication/login.test.ts` | After FR-3 |
| Cross-tenant login blocked | `tests/e2e/user-authentication/login.test.ts` | After FR-3 |
| Route guard redirects + restores intended route | `tests/e2e/user-authentication/guards.test.ts` | After FR-8 |

### Unit Tests

| Scenario | File | Phase |
|---|---|---|
| Forgot password: valid email generates token | `tests/unit/users/test_password_reset.py` | After FR-6 API |
| Forgot password: unknown email still returns 200 | `tests/unit/users/test_password_reset.py` | After FR-6 API |
| Reset confirm: used token rejected | `tests/unit/users/test_password_reset.py` | After FR-7 API |
| Reset confirm: expired token returns 410 | `tests/unit/users/test_password_reset.py` | After FR-7 API |
| Axios interceptor: 401 triggers refresh + retry | `tests/unit/api/client.test.ts` | After FR-4 |
| Axios interceptor: refresh failure clears auth | `tests/unit/api/client.test.ts` | After FR-4 |

### Tenant Isolation Tests (mandatory per CLAUDE.md)

| Scenario | File |
|---|---|
| User from org A cannot log in on org B subdomain | `tests/e2e/user-authentication/login.test.ts` |
| Invite token from org A cannot be accepted on org B | `tests/unit/users/test_invite.py` |

### Regression Tests
- `tests/e2e/project-foundation/health.test.ts` — ensure tenant middleware still resolves correctly after User model is added

### Test Data Requirements
- Fixture: active `Organization` with `allow_self_registration=True`
- Fixture: active `Organization` with `allow_self_registration=False`
- Fixture: existing `User` in org A (for cross-tenant tests)
- Seed: `test-club` org extended with `OrganizationConfig.allow_self_registration=True`

---

## Open Questions

None.
