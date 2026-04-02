# PRD: Club Events

**Spec:** `simpsons-no-jony/lisa/features/club-events/spec.md`
**Created:** 2026-04-02
**Status:** Awaiting Chief review

---

## Overview

Club admins currently have no way to publish upcoming activities (matches, training, socials) inside MemberFlow. This feature adds a fully tenant-scoped Events system: admin CRUD, a public events page with search/filter, membership-tier and role-based exclusivity, and a "My Agenda" section on the member profile page.

## Codebase Context (pre-read by Bart)

- `apps/memberships` does **not** exist yet — must be created; MembershipTier and Membership models are needed for tier-based eligibility checks
- `apps/events` does **not** exist yet — must be created
- Admin views pattern: plain `APIView`, `.for_tenant(request.tenant)` inline, permission classes — see `apps/admin_portal/views.py`
- Serializer pattern: separate admin/member serializers, `SerializerMethodField` for computed values — see `apps/admin_portal/serializers.py`
- URL registration: `config/urls.py` uses `path('api/v1/x/', include('apps.x.urls'))` — see existing entries
- Test pattern: pytest fixtures, `make_user()` helper, `HTTP_AUTHORIZATION` header — see `apps/admin_portal/tests/test_admin_api.py`
- Frontend API module pattern: thin wrappers around `client` — see `frontend/src/api/profile.js`
- SCSS pattern: no `<style>` in Vue SFCs, all styles in `src/styles/`, imported via `main.scss` — see existing partials
- Router pattern: dynamic imports, `meta: { requiresAuth: true }` — see `frontend/src/router/index.js`
- Dashboard card pattern: `.db-card` wrapper, skeleton loading, `var(--bulma-*)` colours — see `frontend/src/components/club/dashboard/`

---

## Work Items

---

### WI-001: Create apps/memberships with MembershipTier and Membership models

**Priority:** 1
**Effort:** M
**Status:** ❌ Not started

**Description:**
Create the `apps/memberships` Django app with two models: `MembershipTier` (a configurable tier per org) and `Membership` (links a user to a tier with a status). Both are required by the events eligibility checker. This is a minimal implementation — full membership management (pricing, Stripe) is a separate future feature.

**Acceptance Criteria:**
- [ ] `apps/memberships/` created with `apps.py`, `models.py`, `__init__.py`
- [ ] `MembershipTier(TenantAwareModel)`: fields `name` (CharField 100, required), `description` (TextField nullable/blank)
- [ ] `Membership(TenantAwareModel)`: fields `user` (FK → User, CASCADE), `tier` (FK → MembershipTier, CASCADE), `status` (CharField choices: `active`/`inactive`, default `inactive`); unique constraint `(organization, user)`
- [ ] `'apps.memberships'` added to `INSTALLED_APPS` in `config/settings/base.py`
- [ ] Migration generated and applies cleanly: `python manage.py migrate` with no errors
- [ ] `pytest` passes with no failures

**Notes:**
- **Pattern:** Follow `apps/users/models.py` — inherit `TenantAwareModel`, no extra manager needed (TenantManager is inherited)
- **Reference:** `apps/users/models.py` for model structure; `config/settings/base.py` for INSTALLED_APPS
- **Hook point:** Register in `config/settings/base.py:INSTALLED_APPS`

---

### WI-002: Create apps/events with EventCategory and Event models

**Priority:** 2
**Effort:** M
**Status:** ❌ Not started

**Description:**
Create the `apps/events` Django app with `EventCategory` and `Event` models as defined in the spec data model section. The `Event` model uses `ArrayField` for `restricted_to_roles` (PostgreSQL-specific, fine per architecture) and an M2M to `MembershipTier` for `restricted_to_tiers`.

**Acceptance Criteria:**
- [ ] `apps/events/` created with `apps.py`, `models.py`, `__init__.py`
- [ ] `EventCategory(TenantAwareModel)`: `name` (CharField 50), `colour` (CharField 7, nullable/blank); `unique_together = ('organization', 'name')`
- [ ] `Event(TenantAwareModel)`: all fields per spec — `title` (CharField 200), `description` (TextField nullable), `start_datetime` (DateTimeField), `end_datetime` (DateTimeField nullable), `venue_name` (CharField 200 nullable), `venue_postcode` (CharField 20 nullable), `category` (FK → EventCategory, SET_NULL nullable), `image_url` (URLField 500 nullable), `status` (CharField 20, choices: draft/published/cancelled/archived, default draft), `restricted_to_tiers` (M2M → MembershipTier blank=True), `restricted_to_roles` (ArrayField(CharField(20)) blank=True, default=list)
- [ ] `Meta.indexes`: `[Index(fields=['organization', 'status']), Index(fields=['organization', 'start_datetime'])]`
- [ ] `'apps.events'` added to `INSTALLED_APPS`
- [ ] Migration generated and applies cleanly
- [ ] `pytest` passes

**Notes:**
- **Pattern:** Follow `apps/users/models.py` for TenantAwareModel inheritance; `from django.contrib.postgres.fields import ArrayField` for roles field
- **Reference:** `apps/users/models.py` for model structure; `apps/admin_portal/serializers.py` for how related models are handled
- **Hook point:** Register in `config/settings/base.py:INSTALLED_APPS`; migration goes in `apps/events/migrations/`

---

### WI-003: Eligibility helper function and unit tests

**Priority:** 3
**Effort:** M
**Status:** ❌ Not started

**Description:**
Create a standalone `is_event_eligible(event, user)` function in `apps/events/eligibility.py` implementing the OR logic from FR-5. Immediately write unit tests covering all 6 conditional branches from the spec ACs (AC-5a through AC-5d plus edge cases).

**Acceptance Criteria:**
- [ ] `apps/events/eligibility.py` created with `is_event_eligible(event, user_or_none) -> bool`
- [ ] Rule 1: unrestricted event → always True (both sets empty)
- [ ] Rule 2: unauthenticated (user=None) + restricted → False
- [ ] Rule 3: `restricted_to_tiers` non-empty → True if user has active `Membership` with tier in list (via `Membership.objects.for_tenant(event.organization).filter(user=user, tier__in=event.restricted_to_tiers.all(), status='active').exists()`)
- [ ] Rule 4: `restricted_to_roles` non-empty → True if user's `UserOrganizationRole.role` is in list
- [ ] Rule 5: both sets non-empty → True if rule 3 OR rule 4 satisfied
- [ ] Rule 6: only tiers set → only rule 3 applies; only roles set → only rule 4 applies
- [ ] `apps/events/tests/__init__.py` and `apps/events/tests/test_eligibility.py` created
- [ ] Unit tests cover all ACs from FR-5 (AC-5a, 5b, 5c, 5d) plus: unauthenticated user, roles-only restriction, tiers-only restriction, inactive membership does not grant eligibility
- [ ] `pytest apps/events/tests/test_eligibility.py -v` passes

**Notes:**
- **Pattern:** Standalone function (not a method) for easy unit testing; import `UserOrganizationRole` from `apps.users.models`; import `Membership` from `apps.memberships.models`
- **Reference:** `apps/admin_portal/serializers.py:_calculate_age` for standalone helper pattern
- **Hook point:** Will be imported by `apps/events/serializers.py:EventSerializer.get_is_eligible()`

---

### 🚦 INTEGRATION GATE 1: Data Layer

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] `docker compose exec api python manage.py migrate` — exits 0 with no errors
2. [ ] `docker compose exec api python manage.py shell -c "from apps.events.models import Event, EventCategory; from apps.memberships.models import MembershipTier, Membership; print('OK')"` — prints `OK`
3. [ ] `docker compose exec api pytest apps/events/tests/test_eligibility.py -v` — all tests pass
4. [ ] Evidence: Write "VERIFIED: [observation] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-004: Member-facing event serializers

**Priority:** 4
**Effort:** M
**Status:** ❌ Not started

**Description:**
Create `apps/events/serializers.py` with the public-facing serializers. `EventSerializer` must compute `is_restricted` and `is_eligible` using the eligibility helper. Requires `request` in serializer context.

**Acceptance Criteria:**
- [ ] `EventCategorySerializer`: fields `id`, `name`, `colour`
- [ ] `EventSerializer`: fields `id`, `title`, `description`, `start_datetime`, `end_datetime`, `venue_name`, `venue_postcode`, `category` (nested `EventCategorySerializer`, nullable), `image_url`, `status`, `is_restricted` (bool), `is_eligible` (bool)
- [ ] `is_restricted`: `True` if `event.restricted_to_tiers.exists() or bool(event.restricted_to_roles)`
- [ ] `is_eligible`: calls `is_event_eligible(event, request.user if request.user.is_authenticated else None)` — `request` passed via serializer context
- [ ] Never exposes `organization`, `organization_id`, `restricted_to_tiers`, or `restricted_to_roles` in output
- [ ] `pytest` passes

**Notes:**
- **Pattern:** `SerializerMethodField` for computed booleans — see `apps/admin_portal/serializers.py:get_role`; pass request via `serializer = EventSerializer(qs, many=True, context={'request': request})`
- **Reference:** `apps/admin_portal/serializers.py` for computed field pattern
- **Hook point:** `apps/events/serializers.py` — imported by views in WI-006

---

### WI-005: Admin event serializers

**Priority:** 5
**Effort:** M
**Status:** ❌ Not started

**Description:**
Create admin serializers for writable event and category management. Include cross-org validation for category and tier foreign keys.

**Acceptance Criteria:**
- [ ] `AdminEventCategorySerializer`: writable; validates name uniqueness within org (excluding self on update); fields `id`, `name`, `colour`
- [ ] `AdminEventSerializer`: writable; all Event fields including `restricted_to_tiers` (list of IDs), `restricted_to_roles` (list of strings); nested read-only `category` (EventCategorySerializer)
- [ ] Validation: `end_datetime` must be after `start_datetime` if both provided → 400 `"end_datetime must be after start_datetime"`
- [ ] Validation: `category` FK must belong to `request.tenant` → 400 `"Category does not belong to this organisation"`
- [ ] Validation: each tier in `restricted_to_tiers` must belong to `request.tenant` → 400 `"One or more tiers do not belong to this organisation"`
- [ ] `pytest` passes

**Notes:**
- **Pattern:** `validate_<field>` methods + `validate()` for cross-field; FK ownership check pattern in `apps/users/serializers.py:validate_date_of_birth`
- **Reference:** `apps/users/serializers.py` for validation patterns; `apps/admin_portal/serializers.py` for admin serializer structure
- **Hook point:** `apps/events/serializers.py` — imported by admin views in WI-007/WI-008

---

### WI-006: Public events views and URL routing

**Priority:** 6
**Effort:** M
**Status:** ❌ Not started

**Description:**
Create the four public/member-facing event views and register them under `/api/v1/events/`. Pagination uses DRF `PageNumberPagination` with page_size=20.

**Acceptance Criteria:**
- [ ] `EventListView(APIView)`: GET `/api/v1/events/` — no auth required; returns published+cancelled events ordered by `start_datetime` ASC; supports `search`, `category`, `date_from`, `date_to`, `page` query params; paginated response `{count, next, previous, results}`
- [ ] `EventCategoryListView(APIView)`: GET `/api/v1/events/categories/` — no auth; returns all categories for tenant
- [ ] `EventDetailView(APIView)`: GET `/api/v1/events/<pk>/` — no auth; 404 if draft/archived or wrong org
- [ ] `EventAgendaView(APIView)`: GET `/api/v1/events/agenda/` — JWT required (401 if missing); returns up to 5 upcoming (start_datetime > now UTC) published events user is eligible for, ordered ASC
- [ ] `apps/events/urls.py` created; URL order: `categories/`, `agenda/`, `<int:pk>/`, `` (list) — specific paths before `<int:pk>`
- [ ] `config/urls.py` includes `path('api/v1/events/', include('apps.events.urls'))`
- [ ] `pytest` passes

**Notes:**
- **Pattern:** Follow `apps/admin_portal/views.py` plain `APIView` pattern; pagination: create `apps/events/pagination.py` with `class EventPagination(PageNumberPagination): page_size = 20`; `from rest_framework.permissions import IsAuthenticated` for agenda
- **Reference:** `apps/admin_portal/views.py:MemberListView` for plain APIView pattern; `config/urls.py` for URL registration
- **Hook point:** `config/urls.py` — add below existing `api/v1/` entries

---

### 🚦 INTEGRATION GATE 2: Public API Responds

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] `docker compose exec api pytest --tb=short -q` — all tests pass
2. [ ] `curl -s -H "Host: test-club.localhost" http://localhost:8000/api/v1/events/` — returns `{"count":0,"next":null,"previous":null,"results":[]}`
3. [ ] `curl -s -H "Host: test-club.localhost" http://localhost:8000/api/v1/events/categories/` — returns `[]`
4. [ ] Evidence: Write "VERIFIED: [observation] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-007: Admin event category views

**Priority:** 7
**Effort:** M
**Status:** ❌ Not started

**Description:**
Create admin views for managing event categories. Only org admins can create/edit/delete categories; org staff can list.

**Acceptance Criteria:**
- [ ] `AdminEventCategoryListView(APIView)`: GET returns all categories for tenant; POST creates category (IsOrgAdmin)
- [ ] `AdminEventCategoryDetailView(APIView)`: PATCH updates (IsOrgAdmin); DELETE — 409 if any events reference this category, else delete (IsOrgAdmin)
- [ ] All views use `.for_tenant(request.tenant)` for all queries
- [ ] GET list: `IsOrgStaff`; POST/PATCH/DELETE: `IsOrgAdmin`
- [ ] `pytest` passes

**Notes:**
- **Pattern:** `apps/admin_portal/views.py:MemberListView` for GET; permission classes `from apps.core.permissions import IsOrgAdmin, IsOrgStaff`; check event count before delete: `if event.events.exists(): return Response(status=409)`
- **Reference:** `apps/admin_portal/views.py` for view structure
- **Hook point:** `apps/events/admin_urls.py` (new file) — registered in `config/urls.py` as `path('api/v1/admin/events/', include('apps.events.admin_urls'))`

---

### WI-008: Admin event views and admin URL routing

**Priority:** 8
**Effort:** M
**Status:** ❌ Not started

**Description:**
Create admin views for full event CRUD and register all admin event URLs.

**Acceptance Criteria:**
- [ ] `AdminEventListView(APIView)`: GET all events for org (all statuses), supports `status`, `category`, `search` params, paginated; POST creates event (status defaults to draft)
- [ ] `AdminEventDetailView(APIView)`: GET single event (including draft/archived); PATCH partial update; DELETE — 409 if status != draft, else delete
- [ ] All views: `IsOrgStaff` for GET, `IsOrgAdmin` for mutations; `.for_tenant(request.tenant)` on all queries
- [ ] `apps/events/admin_urls.py` created: `categories/`, `categories/<int:pk>/`, `<int:pk>/`, `` (list+create) — URL order: specific before parameterised
- [ ] `config/urls.py` includes `path('api/v1/admin/events/', include('apps.events.admin_urls'))`
- [ ] `pytest` passes

**Notes:**
- **Pattern:** Follow `apps/admin_portal/views.py` pattern; `AdminEventSerializer(data=request.data, context={'request': request})` to pass tenant context for validation; set `event.organization = request.tenant` before first save
- **Reference:** `apps/admin_portal/views.py` for pattern; `config/urls.py` for registration
- **Hook point:** `config/urls.py` — add alongside `path('api/v1/admin/', include('apps.admin_portal.urls'))`

---

### WI-009: Backend E2E and tenant isolation tests

**Priority:** 9
**Effort:** M
**Status:** ❌ Not started

**Description:**
Write comprehensive backend tests for the full events API: public list/detail, admin CRUD, eligibility logic integration, and mandatory tenant isolation tests per spec.

**Acceptance Criteria:**
- [ ] `apps/events/tests/test_events_api.py` created
- [ ] Public list: published returned, draft excluded, cancelled included with status; search filters by title; category filter works; date_from/date_to filter works
- [ ] Public detail: published → 200; draft → 404; archived → 404
- [ ] Agenda: auth required (401 without JWT); returns only upcoming eligible published events; ineligible events excluded
- [ ] Admin CRUD: create draft (not visible in public list); publish → visible; cancel → visible with status; archive → 404 on public detail; delete draft → 200; delete published → 409
- [ ] Admin categories: create, update, delete; delete with events → 409
- [ ] Admin permissions: org member cannot access admin endpoints (403)
- [ ] Tenant isolation: org A admin cannot GET/PATCH/DELETE org B's event (404); org A public list does not include org B events; org A admin cannot assign org B's category/tier to their event (400)
- [ ] `pytest` passes with no failures

**Notes:**
- **Pattern:** Follow `apps/admin_portal/tests/test_admin_api.py` — pytest fixtures, `make_user()` helper, `HTTP_AUTHORIZATION` + `HTTP_HOST` headers for tenant; create `conftest.py` in `apps/events/tests/` if needed or reuse root conftest pattern
- **Reference:** `apps/admin_portal/tests/test_admin_api.py` for complete test pattern
- **Hook point:** Run with `pytest apps/events/tests/ -v`

---

### 🚦 INTEGRATION GATE 3: Backend Complete

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] `docker compose exec api pytest --tb=short -q` — ALL tests pass (including new events tests)
2. [ ] `docker compose exec api pytest apps/events/ -v` — every events test listed with PASSED
3. [ ] Evidence: Write "VERIFIED: [pytest output summary] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-010: Frontend API module and /events route

**Priority:** 10
**Effort:** S
**Status:** ❌ Not started

**Description:**
Create the `events.js` API module with one function per endpoint, and register the `/events` public route in the Vue Router.

**Acceptance Criteria:**
- [ ] `frontend/src/api/events.js` created with: `getEvents(params)`, `getEvent(id)`, `getCategories()`, `getAgenda()`
- [ ] All functions call the shared `client` Axios instance (from `src/api/client.js`)
- [ ] `/events` route added to `frontend/src/router/index.js` as a public route (no `requiresAuth` meta) with lazy-loaded component `() => import('../views/EventsView.vue')`
- [ ] `npm run check` passes
- [ ] `npx vitest run tests/e2e/` — no new test failures introduced

**Notes:**
- **Pattern:** Follow `frontend/src/api/profile.js` exactly — one-liner functions, named exports
- **Reference:** `frontend/src/api/profile.js`
- **Hook point:** `frontend/src/router/index.js` — add after `/register` or alongside other public routes

---

### WI-011: EventsView.vue component

**Priority:** 11
**Effort:** M
**Status:** ❌ Not started

**Description:**
Create `frontend/src/views/EventsView.vue` — the public events page. No auth required. Includes search, category filter, date filter, event cards, loading/error/empty states, cancelled banner, members-only badge.

**Acceptance Criteria:**
- [ ] `EventsView.vue` created using `<script setup>` Composition API; no `<style>` block
- [ ] `ClubNavbar` used for navigation (same pattern as `RegisterView.vue`)
- [ ] Calls `getEvents(params)` on mount and on filter change
- [ ] Search input: debounced 300ms using `watchDebounced` (from `@vueuse/core`) or manual `setTimeout`; re-fetches on change
- [ ] Category dropdown: populated from `getCategories()` on mount; re-fetches events on selection
- [ ] Date from/Date to inputs: re-fetch on change
- [ ] "Clear filters" link resets all filters and re-fetches
- [ ] Loading state: 3 skeleton card placeholders (class `event-card-skeleton`) while API in flight
- [ ] Error state: "Failed to load events. Please try again." with retry button
- [ ] Empty state (no events): "No upcoming events"
- [ ] Empty state (filters active, no results): "No events match your search"
- [ ] Event card renders: image (with `@error` handler swapping to placeholder), category badge (colour from `category.colour`, fallback `var(--bulma-primary)`), title, formatted date (`toLocaleString()`), venue name + Google Maps link if `venue_postcode`, cancelled banner if `status === 'cancelled'`, members-only lock icon (`LockClosedIcon` from `@heroicons/vue/24/outline`) if `is_restricted && !is_eligible`
- [ ] `npm run check` passes
- [ ] `npx vitest run tests/e2e/` — no new test failures introduced

**Notes:**
- **Pattern:** Composition API with `ref`, `onMounted`, `watch`; use `useAuthStore` to check `isAuthenticated` for future richer display; date format: `new Date(dt).toLocaleString('en-GB', { weekday:'short', day:'numeric', month:'short', hour:'2-digit', minute:'2-digit' })`
- **Reference:** `frontend/src/views/DashboardView.vue` for page shell + navbar pattern; `frontend/src/views/RegisterView.vue` for ClubNavbar usage; `frontend/src/views/ProfileView.vue` for onMounted + async pattern
- **Hook point:** File is lazy-loaded by router; uses `getEvents` and `getCategories` from `src/api/events.js`
- **⚠️ NO TOAST:** Do not add any toast/notification popups. Use inline error state ("Failed to load events. Please try again.") and skeleton loading states only, as specified in the ACs.

---

### WI-012: SCSS for events page and event card

**Priority:** 12
**Effort:** M
**Status:** ❌ Not started

**Description:**
Create all SCSS partials for the events feature and register them in `main.scss`. No inline styles in Vue SFCs.

**Acceptance Criteria:**
- [ ] `frontend/src/styles/views/_events.scss` created: `.events-page` (min-height 100vh, background var(--db-bg)), `.events-content` (container with padding), `.events-heading`, `.events-filter-bar` (flex row, gap, wraps on mobile), `.events-grid` (CSS grid, responsive columns), `.events-empty` (centred text)
- [ ] `frontend/src/styles/components/club/_event-card.scss` created: `.event-card` (border-radius 12px, overflow hidden, card shadow), `.event-card-image` (aspect-ratio 16/9, object-fit cover, fallback background), `.event-card-body` (padding), `.event-card-category` (small pill badge, uses inline `background-color` set via CSS variable `--category-colour`), `.event-card-title`, `.event-card-meta` (date + venue row), `.event-card-cancelled` (red overlay banner), `.event-card-members-only` (lock icon badge), `.event-card-skeleton` (shimmer animation, matches `@keyframes shimmer` from `_db-card.scss`)
- [ ] `@use 'views/events'` added to `frontend/src/styles/main.scss` under views group
- [ ] `@use 'components/club/event-card'` added to `main.scss` under club components group
- [ ] `npm run check` passes
- [ ] `npx vitest run tests/e2e/` — no new test failures introduced

**Notes:**
- **Pattern:** Follow `_dashboard.scss` for page-level tokens; follow `_db-card.scss` for shimmer keyframe (reuse `@keyframes shimmer` if already defined, otherwise redefine); category badge colour set via `style="--category-colour: #hex"` on the element — CSS var scoped to that element
- **Reference:** `frontend/src/styles/views/_dashboard.scss` for page layout; `frontend/src/styles/components/club/dashboard/_db-card.scss` for shimmer + card base
- **Hook point:** `frontend/src/styles/main.scss` — add `@use` lines in correct groups

---

### 🚦 INTEGRATION GATE 4: Events Page Renders

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] `npm run build` — exits 0 with no errors
2. [ ] `npm run dev` — dev server starts
3. [ ] Navigate to `http://test-club.localhost:5173/events` — page loads, "Upcoming Events" heading visible, filter bar visible
4. [ ] Create a published event via Django shell or admin API, refresh page — event card appears with correct title and date
5. [ ] Evidence: Write "VERIFIED: [observation] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-013: My Agenda section on ProfileView

**Priority:** 13
**Effort:** M
**Status:** ❌ Not started

**Description:**
Add a "My Agenda" card to `ProfileView.vue` below the Change Password card. Calls `GET /api/v1/events/agenda/` on mount. Silent-fail: if the API call errors, the card shows "No upcoming events" without breaking the profile page.

**Acceptance Criteria:**
- [ ] `getAgenda` imported from `src/api/events.js` in `ProfileView.vue`
- [ ] `agendaEvents` ref (array, default `[]`), `agendaLoading` ref (bool, default true) added
- [ ] `getAgenda()` called in `onMounted` inside try/catch; on error sets `agendaEvents = []` silently; `agendaLoading` set false in `finally`
- [ ] "My Agenda" card added after Change Password card (`.profile-card` wrapper, `h2.profile-section-title` "My Agenda")
- [ ] Loading state: 3 skeleton rows (class `agenda-skeleton-row`) while `agendaLoading` is true
- [ ] Each event row shows: title, formatted date, venue name (plain text)
- [ ] Maximum 5 rows (API already limits to 5; frontend renders `agendaEvents.slice(0,5)` as safety)
- [ ] "View all events →" `RouterLink` to `/events` at card bottom (always visible)
- [ ] Empty state: "No upcoming events" when `agendaEvents.length === 0 && !agendaLoading`
- [ ] No `<style>` block added
- [ ] `npm run check` passes
- [ ] `npx vitest run tests/e2e/` — no new test failures introduced

**Notes:**
- **Pattern:** Follow existing `onMounted` async pattern in `ProfileView.vue` (see `saveProfile` / `getProfile` calls); `RouterLink` already imported; silent-fail is intentional per spec AC-7c
- **Reference:** `frontend/src/views/ProfileView.vue` — extend `onMounted` and add new card after "Change password" card template block
- **Hook point:** `ProfileView.vue:onMounted()` — add `getAgenda()` call alongside `getProfile()`
- **⚠️ NO TOAST:** Do not add any toast/notification popups. Use inline states only: skeleton rows while loading, "No upcoming events" for empty/error. Profile page must not break if /agenda/ errors.

---

### WI-014: SCSS for My Agenda section

**Priority:** 14
**Effort:** S
**Status:** ❌ Not started

**Description:**
Add agenda-specific styles to the profile SCSS partial.

**Acceptance Criteria:**
- [ ] `frontend/src/styles/views/_profile.scss` extended with: `.agenda-event-row` (flex row, gap, border-bottom on all-but-last), `.agenda-event-title` (font-weight 600), `.agenda-event-meta` (font-size 0.875rem, `var(--auth-text-muted)` or equivalent), `.agenda-skeleton-row` (shimmer animation, height 18px, border-radius 4px, margin-bottom 0.5rem)
- [ ] Shimmer uses existing `@keyframes shimmer` (imported via `_db-card.scss` which is already in `main.scss`) — no duplicate `@keyframes` definition
- [ ] `npm run check` passes
- [ ] `npx vitest run tests/e2e/` — no new test failures introduced

**Notes:**
- **Pattern:** Follow `.skeleton-line` pattern in `_db-card.scss` for shimmer rows; profile SCSS already exists at `frontend/src/styles/views/_profile.scss` — extend it, do not create a new file
- **Reference:** `frontend/src/styles/views/_profile.scss`; `frontend/src/styles/components/club/dashboard/_db-card.scss` for shimmer
- **Hook point:** `frontend/src/styles/views/_profile.scss` — append at end of file

---

### WI-015: Frontend E2E smoke tests — events page

**Priority:** 15
**Effort:** M
**Status:** ❌ Not started

**Description:**
Write frontend E2E smoke tests for `EventsView.vue` using the Vitest + vue-test-utils Page Object Model pattern.

**Acceptance Criteria:**
- [ ] `frontend/tests/e2e/events/events-page.test.ts` created with Page Object Model class `EventsPage`
- [ ] `renders published event cards`: 2 mocked events → 2 card elements in DOM
- [ ] `shows cancelled banner`: event with `status: 'cancelled'` → element with "CANCELLED" text present
- [ ] `shows members-only lock icon`: event with `is_restricted: true, is_eligible: false` → lock icon element present
- [ ] `shows empty state`: empty results → "No upcoming events" text present
- [ ] `does not show lock icon for eligible events`: `is_restricted: true, is_eligible: true` → no lock icon
- [ ] All 5 tests pass: `npx vitest run tests/e2e/events/events-page.test.ts` exits 0
- [ ] `npm run check` passes

**Notes:**
- **Pattern:** Follow `frontend/tests/e2e/profile/dob-address.test.ts` — `vi.mock` at module top level (never in `beforeEach`), Page Object Model class, `mount()` from `@vue/test-utils`; mock `src/api/events.js`, `src/stores/tenant.js`, `src/stores/auth.js`, `vue-router`, `src/composables/useTheme.js`
- **Reference:** `frontend/tests/e2e/profile/dob-address.test.ts` for complete test pattern
- **Hook point:** New file `frontend/tests/e2e/events/events-page.test.ts`

---

### WI-016: Frontend E2E smoke tests — My Agenda

**Priority:** 16
**Effort:** M
**Status:** ❌ Not started

**Description:**
Write frontend E2E smoke tests for the My Agenda section added to `ProfileView.vue`.

**Acceptance Criteria:**
- [ ] `frontend/tests/e2e/events/agenda.test.ts` created with Page Object Model class `AgendaSection`
- [ ] `renders My Agenda section on profile page`: mocked agenda returns 2 events → "My Agenda" heading + 2 row elements present
- [ ] `shows empty state when no events`: empty agenda → "No upcoming events" in agenda section
- [ ] `shows View all events link`: `RouterLink` to `/events` always present in agenda card
- [ ] All 3 tests pass: `npx vitest run tests/e2e/events/agenda.test.ts` exits 0
- [ ] Existing profile tests still pass: `npx vitest run tests/e2e/profile/` exits 0
- [ ] `npm run check` passes

**Notes:**
- **Pattern:** Follow `frontend/tests/e2e/profile/dob-address.test.ts` — same mock pattern for `src/api/profile.js` (already mocked in that file) + add `src/api/events.js` mock for `getAgenda`
- **Reference:** `frontend/tests/e2e/profile/dob-address.test.ts`; `frontend/src/views/ProfileView.vue` for expected DOM structure
- **Hook point:** New file `frontend/tests/e2e/events/agenda.test.ts`

---

### WI-017: Update ARCHITECTURE.md

**Priority:** 17
**Effort:** S
**Status:** ❌ Not started

**Description:**
Update `about/ARCHITECTURE.md` to reflect the two new Django apps and new URL namespaces introduced by this feature.

**Acceptance Criteria:**
- [ ] `apps/memberships/` added to Django project structure diagram with description: "Membership tiers and user enrolments (tenant-scoped)"
- [ ] `apps/events/` added to Django project structure diagram with description: "Event categories, events, eligibility logic (tenant-scoped)"
- [ ] `/api/v1/events/` added to URL patterns section: "Public + member events list, detail, agenda"
- [ ] `/api/v1/admin/events/` added to URL patterns section: "Org admin event and category management"
- [ ] Frontend route `/events` noted in frontend section (if such a section exists, otherwise add alongside other routes)
- [ ] No other sections changed

**Notes:**
- **Pattern:** Edit in place — minimal changes, only sections affected by this feature
- **Reference:** `about/ARCHITECTURE.md` — App Responsibilities and URL Patterns sections
- **Hook point:** `about/ARCHITECTURE.md` — apps list and URL table

---

### 🚦 INTEGRATION GATE 5: Feature Complete

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] `docker compose exec api pytest --tb=short -q` — ALL backend tests pass
2. [ ] `npx vitest run tests/e2e/events/` — all 8 new events tests pass
3. [ ] `npx vitest run tests/e2e/profile/` — existing profile tests still pass
4. [ ] `npm run build` — exits 0
5. [ ] Navigate to `/events` — published events visible, filter/search work, cancelled banner shown
6. [ ] Navigate to `/profile` — "My Agenda" section visible with upcoming eligible events
7. [ ] Evidence: Write "VERIFIED: [full observation] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

## Non-Goals

- Event registration / booking (follow-on feature)
- Paid event entry (follow-on feature)
- Email notifications for new events
- Image file upload (URL-only in this version)
- iCal / calendar export
- Full membership management (pricing, Stripe) — only minimal MembershipTier + Membership for eligibility

## Technical Notes

- `ArrayField` for `restricted_to_roles` requires PostgreSQL — confirmed in architecture (PostgreSQL 15)
- Eligibility helper is a pure function to enable unit testing without database
- Silent-fail on `/agenda/` in profile page is intentional — profile must not break if events service errors
- URL order in `apps/events/urls.py` matters: `categories/` and `agenda/` must come before `<int:pk>/`
- `@keyframes shimmer` already defined in `_db-card.scss` — reference it in agenda SCSS, do not redefine

## Success Metrics

- Club admin can create and publish an event visible on the public page within 2 minutes
- Public `/events` page loads and renders with correct data
- Members-only badge correctly shows/hides based on user eligibility
