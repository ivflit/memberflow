# PRD: User Date of Birth and Address

**Spec:** `simpsons-no-jony/lisa/features/user-dob-address/spec.md`
**Created:** 2026-04-01
**Revised:** 2026-04-01 (post-Chief review, v2)
**Status:** Ready for Chief re-review

---

## Codebase Context (pre-read by Bart)

- Profile API: `GET/PATCH /api/v1/profile/` — `apps/users/views.py:ProfileView` (**renamed from `/api/v1/me/` — already done**)
- Profile serialisers: `apps/users/serializers.py` — `UserSerializer` (read), `ProfileUpdateSerializer` (write)
- Registration: `apps/users/views.py:RegisterView` + `RegisterSerializer`
- Invite acceptance: `apps/users/views.py:InviteAcceptView` + `InviteAcceptSerializer`
- `authStore.register(payload)` in `frontend/src/stores/auth.js` passes the full payload object directly to the API — no store changes needed when adding new fields to the registration form
- Permissions: `apps/core/permissions.py` — `IsOrgAdmin`, `IsOrgStaff` exist; `IsPlatformAdmin` does **not** exist yet
- `apps/admin_portal` app does **not** exist yet — must be created
- Frontend profile API: `frontend/src/api/profile.js` — `getProfile()`, `updateProfile()`
- URL registration: `backend/config/urls.py`

---

## Work Items

---

### WI-001: Add DOB and address fields to User model

**Priority:** 1
**Effort:** S
**Status:** ❌ Not started

**Description:**
Add five optional nullable fields to the `User` model and generate the migration. This is the foundation all other work items depend on.

**Acceptance Criteria:**
- [ ] `date_of_birth` (`DateField`, `null=True`, `blank=True`) added to `User`
- [ ] `address_street` (`CharField(max_length=255)`, `null=True`, `blank=True`) added
- [ ] `address_city` (`CharField(max_length=100)`, `null=True`, `blank=True`) added
- [ ] `address_postcode` (`CharField(max_length=20)`, `null=True`, `blank=True`) added
- [ ] `address_country` (`CharField(max_length=100)`, `null=True`, `blank=True`) added
- [ ] Migration generated and applies cleanly: `python manage.py migrate` with no errors
- [ ] Existing users are unaffected (all new fields default to `null`)
- [ ] `pytest` passes

**Notes:**
- **Pattern:** Standard nullable field addition — no index needed (not used in filters)
- **Reference:** Extend `apps/users/models.py:User`
- **Hook point:** Run `python manage.py makemigrations users` after adding fields

---

### WI-002: Extend profile serialisers and GET/PATCH /api/v1/profile/

**Priority:** 2
**Effort:** M
**Status:** ❌ Not started

**Description:**
Extend the member-facing profile read and update serialisers to expose and accept the five new fields. Add `date_of_birth` future-date validation. Coerce empty strings to `null` for all five fields so Django stores `null` not `""`. The PATCH endpoint must allow clearing fields by sending `null` or `""`.

**Acceptance Criteria:**
- [ ] `GET /api/v1/profile/` returns `date_of_birth` (ISO 8601 string or `null`), `address_street`, `address_city`, `address_postcode`, `address_country` in the response body
- [ ] `PATCH /api/v1/profile/` accepts all five new fields (all optional)
- [ ] Sending a future date for `date_of_birth` returns HTTP 400 with a field-level validation error
- [ ] Sending `null` or `""` for any field stores `null` in the database (empty string coercion)
- [ ] Sending `null` for a previously set `date_of_birth` clears it to `null`
- [ ] `UserSerializer` includes the five new read fields
- [ ] `ProfileUpdateSerializer` includes the five new writable fields with coercion
- [ ] `pytest` passes

**Notes:**
- **Pattern:** Add fields to both `UserSerializer.Meta.fields` and `ProfileUpdateSerializer`; add a `validate_date_of_birth` method; add `to_internal_value` override or per-field `validate_<field>` for empty-string coercion
- **Reference:** Extend `apps/users/serializers.py:UserSerializer` and `ProfileUpdateSerializer`
- **Hook point:** `ProfileView.patch` in `apps/users/views.py` already calls `ProfileUpdateSerializer` and saves to `user` — add the new fields to the save block following the existing `if 'first_name' in data` pattern

---

### WI-003: Extend registration and invite acceptance to accept new fields

**Priority:** 3
**Effort:** S
**Status:** ❌ Not started

**Description:**
Allow the five new optional fields to be submitted at registration and invite acceptance. Fields are passed through to user creation. No new validation beyond what was defined for the profile PATCH (empty-string coercion; future-date rejection for DOB).

**Acceptance Criteria:**
- [ ] `POST /api/v1/auth/register/` accepts `date_of_birth`, `address_street`, `address_city`, `address_postcode`, `address_country` as optional fields
- [ ] `POST /api/v1/auth/invite/accept/` accepts the same five optional fields
- [ ] Fields are saved to the newly created `User` on success
- [ ] Omitting all five fields continues to work (existing registration flow unaffected)
- [ ] Future `date_of_birth` is rejected with HTTP 400 at both endpoints
- [ ] Empty strings are coerced to `null` at both endpoints
- [ ] `pytest` passes

**Notes:**
- **Pattern:** Add optional fields to `RegisterSerializer` and `InviteAcceptSerializer`; pass `data.get('date_of_birth')` etc. to the `User(...)` constructor in the view
- **Reference:** `apps/users/serializers.py:RegisterSerializer`, `InviteAcceptSerializer`; `apps/users/views.py:RegisterView`, `InviteAcceptView`
- **Hook point:** `User(organization=..., email=..., first_name=..., ...)` constructor call in both views — add the five new kwargs with `.get()` defaults of `None`

---

### 🚦 INTEGRATION GATE 1: Profile API end-to-end

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] `docker compose up` — API running
2. [ ] Register a new user including `date_of_birth`, `address_street`, `address_city`, `address_postcode`, `address_country` in the POST body
3. [ ] `GET /api/v1/profile/` with the new user's token — confirm all five fields are returned
4. [ ] `PATCH /api/v1/profile/` with `date_of_birth: null` — confirm field is cleared to `null`
5. [ ] `PATCH /api/v1/profile/` with a future `date_of_birth` — confirm HTTP 400
6. [ ] Evidence: Write "VERIFIED: [observation] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-004: Create admin_portal app with member list endpoint

**Priority:** 4
**Effort:** M
**Status:** ❌ Not started

**Description:**
Bootstrap the `admin_portal` Django app. Create a member list endpoint at `GET /api/v1/admin/members/` accessible to org admins and staff. Returns all members for the current tenant. Includes a calculated `age` field (derived from `date_of_birth`); does **not** expose raw DOB or address fields in the list response.

**Acceptance Criteria:**
- [ ] `apps/admin_portal/` app created with `__init__.py`, `apps.py`, `views.py`, `serializers.py`, `urls.py`
- [ ] App registered in `INSTALLED_APPS` in `config/settings/base.py`
- [ ] `GET /api/v1/admin/members/` registered in `config/urls.py`
- [ ] Endpoint requires `IsOrgStaff` permission (admins + staff can access)
- [ ] Response includes: `id`, `email`, `first_name`, `last_name`, `role`, `is_active`, `age` (integer or `null`), `created_at`
- [ ] `age` is calculated as completed years since `date_of_birth`; `null` if DOB is not set
- [ ] Raw `date_of_birth`, `address_*` fields are **not** in the list response
- [ ] Results are scoped to `request.tenant` (uses `TenantScopedViewMixin`)
- [ ] Tenant isolation test: org B admin cannot retrieve org A's members
- [ ] `pytest` passes

**Notes:**
- **Pattern:** New app following `apps/users/` structure; use `TenantScopedViewMixin` as left-most parent on the view; use `from dateutil.relativedelta import relativedelta` for age calculation (already available via `python-dateutil` which is a Django transitive dependency)
- **Reference:** Mirror structure from `apps/users/views.py`; permission pattern from `apps/core/permissions.py:IsOrgStaff`
- **Hook point:** Register `path('api/v1/admin/', include('apps.admin_portal.urls'))` in `config/urls.py`

---

### WI-005: Admin member detail endpoint with full DOB and address

**Priority:** 5
**Effort:** S
**Status:** ❌ Not started

**Description:**
Add `GET /api/v1/admin/members/{id}/` to the admin_portal app. Returns full member detail including `date_of_birth`, all four address fields, and `age`. Uses a separate detail serialiser that is a superset of the list serialiser.

**Acceptance Criteria:**
- [ ] `GET /api/v1/admin/members/{id}/` returns all list fields plus `date_of_birth`, `address_street`, `address_city`, `address_postcode`, `address_country`, `age`
- [ ] `date_of_birth` returned as ISO 8601 string or `null`
- [ ] Endpoint requires `IsOrgStaff` permission
- [ ] Non-existent or cross-tenant member ID returns HTTP 404 (not 403)
- [ ] Tenant isolation test: org B admin cannot retrieve org A member detail
- [ ] `pytest` passes

**Notes:**
- **Pattern:** Add a detail view alongside the list view; use `.for_tenant(request.tenant).get(pk=pk)` with a `try/except ObjectDoesNotExist → 404`
- **Reference:** Extend `apps/admin_portal/views.py` and `apps/admin_portal/serializers.py`
- **Hook point:** Add `path('members/<int:pk>/', MemberDetailView.as_view())` in `apps/admin_portal/urls.py`

---

### WI-006: Member CSV export endpoint

**Priority:** 6
**Effort:** M
**Status:** ❌ Not started

**Description:**
Create `GET /api/v1/admin/members/export/` returning a CSV of all members for the current tenant. Accessible to org admins only (not staff). Includes DOB and address columns. This endpoint does not exist anywhere in the codebase yet.

**Acceptance Criteria:**
- [ ] `GET /api/v1/admin/members/export/` returns `Content-Type: text/csv` response
- [ ] `Content-Disposition: attachment; filename="members.csv"` header set
- [ ] CSV columns in order: `id`, `email`, `first_name`, `last_name`, `date_of_birth`, `address_street`, `address_city`, `address_postcode`, `address_country`, `role`, `is_active`, `created_at`
- [ ] `date_of_birth` formatted as `YYYY-MM-DD`; empty string if `null`
- [ ] `role` resolved from `UserOrganizationRole` for each member
- [ ] Endpoint scoped to `request.tenant` — only exports current org's members
- [ ] Requires `IsOrgAdmin` permission (staff cannot trigger export — HTTP 403)
- [ ] Tenant isolation test: org B admin cannot export org A's members
- [ ] `pytest` passes

**Notes:**
- **Pattern:** Use `HttpResponse` with `csv.writer`; set `content_type='text/csv'` and `Content-Disposition` header on the response object
- **Reference:** Add `MemberExportView` to `apps/admin_portal/views.py`
- **Hook point:** Add `path('members/export/', MemberExportView.as_view())` **before** the `<int:pk>` pattern in `apps/admin_portal/urls.py` to avoid URL shadowing

---

### WI-007: IsPlatformAdmin permission + platform admin member edit

**Priority:** 7
**Effort:** M
**Status:** ❌ Not started

**Description:**
Add `IsPlatformAdmin` to `apps/core/permissions.py` (referenced in CLAUDE.md but not yet implemented). Create `GET /api/v1/platform/members/{id}/` and `PATCH /api/v1/platform/members/{id}/` for platform admins to read and edit any member's DOB and address across tenants for support purposes.

**Acceptance Criteria:**
- [ ] `IsPlatformAdmin` added to `apps/core/permissions.py` — checks `role == 'platform_admin'` in `UserOrganizationRole`
- [ ] `GET /api/v1/platform/members/{id}/` requires `IsPlatformAdmin`; returns member including `date_of_birth` and all address fields
- [ ] `PATCH /api/v1/platform/members/{id}/` requires `IsPlatformAdmin`; accepts `date_of_birth` and address fields; same validation as member-facing PATCH (future date rejected, empty string → null)
- [ ] Platform admin can retrieve members across any tenant (cross-tenant access is intentional — no `for_tenant()` filter on these views)
- [ ] Non-platform-admin token (e.g. org admin) calling these endpoints returns HTTP 403
- [ ] `pytest` passes

**Notes:**
- **Pattern:** Add platform views to `apps/admin_portal/` under a separate `platform_urls.py` to keep them distinct from org admin views
- **Reference:** `IsOrgAdmin` in `apps/core/permissions.py` as the structural pattern for `IsPlatformAdmin`
- **Hook point:** Register `path('api/v1/platform/', include('apps.admin_portal.platform_urls'))` in `config/urls.py`

---

### 🚦 INTEGRATION GATE 2: Admin and platform API end-to-end

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] `GET /api/v1/admin/members/` with org admin token — confirm `age` column present, no raw DOB/address in response
2. [ ] `GET /api/v1/admin/members/{id}/` — confirm `date_of_birth` and all address fields returned
3. [ ] `GET /api/v1/admin/members/export/` — confirm CSV download with correct columns
4. [ ] `GET /api/v1/admin/members/export/` with org staff token — confirm HTTP 403
5. [ ] `GET /api/v1/platform/members/{id}/` with platform admin token — confirm member data returned
6. [ ] `GET /api/v1/platform/members/{id}/` with org admin token — confirm HTTP 403
7. [ ] Evidence: Write "VERIFIED: [observation] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-008: Backend E2E tests for admin and platform API

**Priority:** 8
**Effort:** M
**Status:** ❌ Not started

**Description:**
Write E2E-style backend tests covering the admin and platform API endpoints introduced in WI-004 through WI-007. These complement the unit tests in WI-009 and are placed here — immediately after the admin API phase — so failures are caught before frontend work begins.

**Acceptance Criteria:**
- [ ] E2E: Org admin `GET /api/v1/admin/members/` — `age` field present in each row; no `date_of_birth` or address fields in list response
- [ ] E2E: Org admin `GET /api/v1/admin/members/{id}/` — `date_of_birth` and all four address fields present in detail response
- [ ] E2E: Org admin `GET /api/v1/admin/members/export/` — response `Content-Type` is `text/csv`; `date_of_birth` and address columns present in parsed CSV
- [ ] E2E: Org staff `GET /api/v1/admin/members/export/` — returns HTTP 403
- [ ] E2E: Platform admin `PATCH /api/v1/platform/members/{id}/` with new `date_of_birth` — change reflected in subsequent `GET`
- [ ] Tenant isolation: org A admin cannot access org B member via `GET /api/v1/admin/members/{id}/` (expects 404)
- [ ] Tenant isolation: org A admin export does not include org B members
- [ ] All tests use factory_boy factories
- [ ] `pytest` passes

**Notes:**
- **Pattern:** Test files at `apps/admin_portal/tests/test_admin_api.py` and `apps/admin_portal/tests/test_platform_api.py`; each test class creates its own `Organization`
- **Reference:** Follow existing test structure in `apps/users/`; create `apps/admin_portal/tests/` directory with `__init__.py`
- **Hook point:** Run `pytest apps/admin_portal/tests/ -v`

---

### WI-009: Backend unit and tenant isolation tests

**Priority:** 9
**Effort:** M
**Status:** ❌ Not started

**Description:**
Write unit tests covering validation logic, empty-string coercion, and age calculation for the fields added to the profile API in WI-001 through WI-003.

**Acceptance Criteria:**
- [ ] Unit: `date_of_birth` future date is rejected by `ProfileUpdateSerializer`
- [ ] Unit: Empty string `""` for `date_of_birth` is coerced to `None`
- [ ] Unit: Empty string `""` for `address_street` is coerced to `None`
- [ ] Unit: `age` calculation returns correct integer for a known DOB; `None` when DOB is `null`
- [ ] Tenant isolation: Org A member cannot read Org B member's data via `GET /api/v1/profile/`
- [ ] All tests use factory_boy factories
- [ ] `pytest` passes

**Notes:**
- **Pattern:** Test file at `apps/users/tests/test_dob_address.py`; each test class creates its own `Organization`
- **Reference:** Create `apps/users/tests/` directory with `__init__.py` if it does not exist
- **Hook point:** Run `pytest apps/users/tests/test_dob_address.py -v`

---

### WI-010: Update ARCHITECTURE.md

**Priority:** 10
**Effort:** S
**Status:** ❌ Not started

**Description:**
Update `about/ARCHITECTURE.md` to reflect the architectural additions introduced by this feature: the new `apps/admin_portal` app, the `IsPlatformAdmin` permission, and the `/api/v1/admin/` and `/api/v1/platform/` URL namespaces.

**Acceptance Criteria:**
- [ ] `apps/admin_portal` added to the Django project structure diagram in ARCHITECTURE.md with a one-line description
- [ ] `IsPlatformAdmin` added to the permissions table/section alongside `IsOrgAdmin` and `IsOrgStaff`
- [ ] `/api/v1/admin/` and `/api/v1/platform/` added to the URL pattern reference
- [ ] `/api/v1/me/` removed or updated to `/api/v1/profile/` in any URL tables (the rename was done prior to this feature)

**Notes:**
- **Pattern:** Edit in place — do not rewrite sections not touched by this feature
- **Reference:** `about/ARCHITECTURE.md` — App Responsibilities section and URL patterns section
- **Hook point:** No code change — documentation only

---

### 🚦 INTEGRATION GATE 3: Backend complete

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] `pytest` passes with no failures across all apps
2. [ ] `about/ARCHITECTURE.md` reflects `apps/admin_portal`, `IsPlatformAdmin`, and updated URL patterns
3. [ ] Evidence: Write "VERIFIED: [observation] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-011: Profile page — DOB field in Personal details card

**Priority:** 11
**Effort:** S
**Status:** ❌ Not started

**Description:**
Add a date of birth field to the existing "Personal details" form card in `ProfileView.vue`. DOB is positioned below last name, above the email field. Saves with the existing "Save changes" button and existing `saveProfile()` handler.

**Acceptance Criteria:**
- [ ] `date_of_birth` field added to `editForm` ref in `ProfileView.vue` (default: `''`)
- [ ] `date` input rendered below last name, above email, with label `Date of birth`
- [ ] On `getProfile()` response, `editForm.date_of_birth` is populated from `data.date_of_birth` (ISO string or `null` → `''`)
- [ ] `saveProfile()` sends `date_of_birth` in the PATCH payload; empty string sends `""` (backend coerces to `null`)
- [ ] Saving with an empty date field clears the stored DOB
- [ ] `npm run check` passes

**Notes:**
- **Pattern:** Follow the existing `first_name`/`last_name` field pattern in the form
- **Reference:** `frontend/src/views/ProfileView.vue` — extend `editForm` ref and the form template
- **Hook point:** SCSS for any label/input styling goes in `frontend/src/styles/views/_profile.scss` — no `<style>` block in the Vue file

---

### WI-012: Profile page — Address card with separate save

**Priority:** 12
**Effort:** M
**Status:** ❌ Not started

**Description:**
Add a new "Address" card to the profile page, following the same card pattern as the "Change password" card. The address card has its own save button, loading state, and success/error messages — it is independent of the "Personal details" save.

**Acceptance Criteria:**
- [ ] New address card rendered below the "Personal details" card in the right column (`profile-forms`)
- [ ] Card title: `Address`
- [ ] Four fields: Street address, City, Postcode, Country (all optional text inputs)
- [ ] Separate `addressForm` ref: `{ address_street, address_city, address_postcode, address_country }`
- [ ] Separate `saveAddress()` async function: calls `updateProfile(addressForm.value)`, handles loading/success/error
- [ ] Success message: `✓ Address updated` (auto-clears after 3s, same pattern as `profileSuccess`)
- [ ] On `getProfile()` response, `addressForm` is populated from the returned data
- [ ] Saving with all empty fields clears all address fields
- [ ] `savingAddress`, `addressSuccess`, `addressError` refs added (no collision with profile form state)
- [ ] SCSS for the address card reuses `.profile-card`, `.profile-section-title`, `.profile-label`, `.profile-input` — no new classes needed unless layout requires it
- [ ] `npm run check` passes

**Notes:**
- **Pattern:** Mirror the "Change password" card structure (lines 118–221 of `ProfileView.vue`); mirror `saveProfile()` for `saveAddress()`
- **Reference:** `frontend/src/views/ProfileView.vue`
- **Hook point:** SCSS partial `frontend/src/styles/views/_profile.scss` — add any new rules to existing file; no new partial needed

---

### WI-013: Registration form — DOB and address fields

**Priority:** 13
**Effort:** S
**Status:** ❌ Not started

**Description:**
Add the five optional fields to `RegisterView.vue`. Fields appear below the password input, before the submit button. Grouped with a subtle label. Submitted with the existing `handleSubmit()` call to `authStore.register()`.

**Acceptance Criteria:**
- [ ] `date_of_birth`, `address_street`, `address_city`, `address_postcode`, `address_country` refs added (all default `''`)
- [ ] DOB date input rendered with label `Date of birth`
- [ ] A subtle visual grouping label `Address (optional)` separates the DOB and address fields
- [ ] Four address text inputs rendered (Street address, City, Postcode, Country)
- [ ] All five fields included in the `authStore.register({...})` payload
- [ ] No `required` attribute on any of the five new fields
- [ ] `npm run check` passes

**Notes:**
- **Pattern:** Follow existing `firstName`/`lastName` ref + input pattern; pass new fields into the register payload object
- **Reference:** `frontend/src/views/RegisterView.vue` — extend `handleSubmit` payload and add refs
- **Hook point:** `authStore.register(payload)` in `frontend/src/stores/auth.js` passes the entire payload object directly to `POST /api/v1/auth/register/` — confirmed, no store changes needed

---

### WI-014: Invite acceptance form — DOB and address fields

**Priority:** 14
**Effort:** S
**Status:** ❌ Not started

**Description:**
Add the five optional fields to `SetPasswordView.vue` in invite mode (`mode === 'invite'`). Fields appear below the first/last name inputs, above the password field. Same field set and layout as registration.

**Acceptance Criteria:**
- [ ] `date_of_birth`, `address_street`, `address_city`, `address_postcode`, `address_country` refs added (all default `''`)
- [ ] All five fields rendered inside `<template v-if="mode === 'invite'">`, below name fields, above password
- [ ] DOB date input + address group label + four address inputs (same layout as registration)
- [ ] All five fields included in the invite-mode `payload` sent to `/api/v1/auth/invite/accept/`
- [ ] Fields do not appear when `mode === 'reset'`
- [ ] No `required` attribute on any of the five new fields
- [ ] `npm run check` passes

**Notes:**
- **Pattern:** The invite mode block already exists at line 29 of `SetPasswordView.vue` — add new fields inside that `<template v-if="mode === 'invite'">` block
- **Reference:** `frontend/src/views/SetPasswordView.vue`
- **Hook point:** `payload` object in `handleSubmit()` — the invite branch already builds `{ token, password, first_name, last_name }`; extend it with the five new fields

---

### 🚦 INTEGRATION GATE 4: Frontend end-to-end

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] `npm run dev` — dev server running
2. [ ] Navigate to `/register` — confirm DOB + address fields are present below password
3. [ ] Register with DOB + address populated — navigate to `/profile` — confirm all fields show the entered values
4. [ ] Clear DOB on profile page, save — confirm DOB field shows empty on reload
5. [ ] Navigate to `/set-password?mode=invite&token=<valid-token>` — confirm DOB + address fields appear below name fields
6. [ ] Navigate to `/set-password?mode=reset&token=<valid-token>` — confirm DOB + address fields do **not** appear
7. [ ] Evidence: Write "VERIFIED: [observation] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-015: Frontend E2E smoke tests

**Priority:** 15
**Effort:** M
**Status:** ❌ Not started

**Description:**
Write E2E tests covering the member-facing frontend flows introduced by this feature: profile page persist/clear, registration with DOB/address, and invite acceptance with DOB/address.

**Acceptance Criteria:**
- [ ] E2E: Member fills in DOB + address on profile page; values persist on reload
- [ ] E2E: Member clears DOB by submitting empty date field; DOB shows blank on reload
- [ ] E2E: Member provides DOB + address during registration; profile page shows the values after login
- [ ] E2E: Member provides DOB + address during invite acceptance; profile page shows the values
- [ ] Test file at `frontend/tests/e2e/profile/dob-address.test.ts`
- [ ] All tests pass

**Notes:**
- **Pattern:** Follow Page Object Model pattern established in existing E2E tests (see `frontend/tests/e2e/auth/login.test.ts`)
- **Reference:** Existing test files in `frontend/tests/e2e/`
- **Hook point:** Create `frontend/tests/e2e/profile/` directory if not present

---

## Summary

| WI | Title | Effort | Phase |
|---|---|---|---|
| WI-001 | User model fields + migration | S | Backend – Data |
| WI-002 | Profile serialisers + GET/PATCH /api/v1/profile/ | M | Backend – Data |
| WI-003 | Register + invite acceptance new fields | S | Backend – Data |
| 🚦 Gate 1 | Profile API end-to-end | — | — |
| WI-004 | admin_portal app + member list (age only) | M | Backend – Admin |
| WI-005 | Admin member detail (full DOB + address) | S | Backend – Admin |
| WI-006 | Member CSV export endpoint | M | Backend – Admin |
| WI-007 | IsPlatformAdmin + platform admin member edit | M | Backend – Platform |
| 🚦 Gate 2 | Admin and platform API end-to-end | — | — |
| WI-008 | Backend E2E tests — admin + platform API | M | Backend – Tests |
| WI-009 | Backend unit + tenant isolation tests | M | Backend – Tests |
| WI-010 | Update ARCHITECTURE.md | S | Docs |
| 🚦 Gate 3 | Backend complete | — | — |
| WI-011 | Profile page — DOB field | S | Frontend |
| WI-012 | Profile page — Address card | M | Frontend |
| WI-013 | Registration form — new fields | S | Frontend |
| WI-014 | Invite acceptance form — new fields | S | Frontend |
| 🚦 Gate 4 | Frontend end-to-end | — | — |
| WI-015 | Frontend E2E smoke tests | M | Tests |

**Total:** 15 work items (7S + 8M), 4 integration gates
