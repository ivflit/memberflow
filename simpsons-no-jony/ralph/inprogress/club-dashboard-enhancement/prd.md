# PRD: Club Dashboard Enhancement

**branchName:** feature/club-dashboard-enhancement

## Overview

After login, members land on a near-empty dashboard with only a welcome message and a sign-out button — they cannot tell if their membership is active, see club events, or navigate anywhere useful. This PRD replaces that stub with a proper dashboard: a new `DashboardNavbar` (separate from `ClubNavbar`) plus a 2×2 card grid with Membership Status, Upcoming Events, Club Info, and Quick Actions. Membership and Events cards show greyed-out placeholders (no backend models yet); Club Info and Quick Actions wire to existing `authStore` and `tenantStore`.

## Source Spec

`simpsons-no-jony/lisa/features/club-dashboard-enhancement/spec.md`

**⚠️ READ THE SPEC — it contains full acceptance criteria and edge cases.**

## Goals

- Member can see club name, their initials avatar, and navigate from a real dashboard navbar
- Member can identify that membership and events sections exist (placeholders signal future data)
- Member can sign out via navbar dropdown (not a standalone button)
- Dashboard is mobile-responsive

## Testing Requirements (Applies to ALL Work Items)

**⚠️ MANDATORY — Every WI acceptance criteria MUST include both:**

1. ✅ **Check gate:** `cd frontend && npm run check` (MUST exit 0)
2. ✅ **Smoke tests:** `cd frontend && npx vitest run --config vitest.e2e.config.ts` (MUST pass)
3. ✅ **Manual verification:** Confirm feature works as expected in browser

**Use `cd frontend && npm run fix`** to auto-fix lint issues before committing.

**If ANY check fails:** Fix before committing. Do NOT mark WI complete until ALL checks pass.

---

## Work Items

### WI-001: DashboardNavbar — shell with branding and nav links

**Priority:** 1
**Effort:** M
**Status:** ✅ Complete

**Description:** Create `frontend/src/components/club/DashboardNavbar.vue` — the navbar used exclusively on the dashboard. Left side: club logo (if `branding.logo_url` exists) + club name, then nav links: Dashboard (active), Events (placeholder `/events`), Profile (placeholder `/profile`). Right side: empty slot for bell + avatar (added in WI-002/003). Hamburger collapses menu on mobile. "Dashboard" nav link gets Bulma `is-active` class.

**Acceptance Criteria:**

- [ ] `DashboardNavbar.vue` created at `frontend/src/components/club/DashboardNavbar.vue`
- [ ] Club logo renders when `tenantStore.config.branding.logo_url` is non-null; club name text renders always
- [ ] Nav links present: "Dashboard" (`/dashboard`, `is-active`), "Events" (`/events`), "Profile" (`/profile`)
- [ ] Hamburger burger button toggles `is-active` on `.navbar-menu` on mobile
- [ ] `cd frontend && npm run check` exits 0
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts` passes

**Notes:**

- **Pattern:** Mirror `ClubNavbar.vue` structure — same `navbar is-fixed-top`, `navbar-brand`, `navbar-burger`, `navbar-menu` Bulma markup
- **Reference:** Copy base from `frontend/src/components/club/ClubNavbar.vue` — reuse `menuOpen` ref, logo/name pattern, hamburger toggle, and scoped styles
- **Hook point:** Component not yet used in any view — that happens in WI-010
- **⚠️ NO TOAST:** This component has no user-initiated state changes — do not add toast notifications

---

### WI-002: DashboardNavbar — user avatar with dropdown

**Priority:** 2
**Effort:** M
**Status:** ✅ Complete

**Description:** Add user avatar to the right of the navbar. Avatar displays two-letter initials (`first_name[0] + last_name[0]` uppercased; single letter if `last_name` missing; `email[0]` if both name fields missing). On click, a dropdown opens with two items: "Profile" (link to `/profile`) and "Sign out" (calls `authStore.logout()` then routes to `/login`). Only one dropdown open at a time (shared `openDropdown` ref introduced here, defaulting to `null`).

**Acceptance Criteria:**

- [ ] Avatar circle renders in navbar-end with correct initials (test all three fallback cases in browser: both names, no last name, no first name)
- [ ] Clicking avatar opens dropdown with "Profile" and "Sign out" items
- [ ] Clicking "Sign out" calls `authStore.logout()` and pushes router to `/login`
- [ ] Clicking outside the dropdown closes it (click-outside handler)
- [ ] `openDropdown` reactive ref introduced — set to `'user'` when user menu opens, `null` when closed
- [ ] `cd frontend && npm run check` exits 0
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts` passes

**Notes:**

- **Pattern:** Use Bulma `navbar-item has-dropdown` adapted for click-based toggle — implement as a `div.navbar-item` with a `div.navbar-dropdown` child toggled by `v-show`
- **Reference:** `frontend/src/components/club/ClubNavbar.vue` for navbar-end placement; `frontend/src/stores/auth.js:logout()` — already silently swallows API failures and clears tokens
- **Hook point:** Add to `DashboardNavbar.vue` navbar-end alongside bell (WI-003)
- **⚠️ NO TOAST:** Sign out failure is handled silently in `authStore.logout()` — do not add a toast for logout errors

---

### WI-003: DashboardNavbar — notification bell with empty dropdown

**Priority:** 3
**Effort:** S
**Status:** ✅ Complete

**Description:** Add a bell icon to the navbar (left of avatar). On click, opens a small dropdown showing "No notifications yet". Uses the shared `openDropdown` ref from WI-002 — set to `'bell'` when open. Opening bell closes user menu dropdown (and vice versa). Clicking outside closes it. On mobile, dropdown is full-width of the navbar container.

**Acceptance Criteria:**

- [ ] Bell icon (`BellIcon` from `@heroicons/vue/24/outline`) renders in navbar-end, left of avatar
- [ ] Clicking bell sets `openDropdown` to `'bell'`; dropdown shows "No notifications yet"
- [ ] If user menu was open when bell clicked, user menu closes
- [ ] Clicking outside closes the bell dropdown
- [ ] `cd frontend && npm run check` exits 0
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts` passes

**Notes:**

- **Pattern:** Same click-toggle + click-outside pattern as WI-002 user dropdown — reuse `openDropdown` ref
- **Reference:** `@heroicons/vue` is installed — import `BellIcon` from `@heroicons/vue/24/outline`; see `frontend/src/components/platform/PlatformNavbar.vue` for any heroicon usage, else follow `@heroicons/vue` docs
- **Hook point:** Add to `DashboardNavbar.vue` navbar-end, before avatar div (WI-002)
- **⚠️ NO TOAST:** Bell dropdown is display-only — do not add toast notifications

---

### 🚦 INTEGRATION GATE: Navbar Works

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**

1. [ ] Start dev server: `docker compose up` (or `cd frontend && npm run dev` if running standalone)
2. [ ] Log in as a test member and navigate to `http://test-club.localhost/dashboard`
3. [ ] Confirm: `DashboardNavbar` renders with club name, "Dashboard" nav link is highlighted
4. [ ] Confirm: Click avatar → dropdown opens with "Profile" and "Sign out"
5. [ ] Confirm: Click "Sign out" → redirected to `/login`
6. [ ] Confirm: Click bell → "No notifications yet" dropdown opens; avatar dropdown closes if it was open
7. [ ] Confirm: Click outside any open dropdown → it closes
8. [ ] Confirm: Resize browser to mobile width → hamburger appears, links collapse
9. [ ] Evidence: Write "VERIFIED: [what you saw] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-004: E2E smoke — navbar tests

**Priority:** 4
**Effort:** M
**Status:** ✅ Complete

**Description:** Write E2E smoke tests for the dashboard navbar: renders with club name + avatar, user menu opens and sign out redirects to `/login`, bell dropdown opens and closes on outside click.

**Test File:** `frontend/tests/e2e/club-dashboard/navbar.test.ts`

**Acceptance Criteria:**

- [ ] Test: navbar renders with club name visible
- [ ] Test: clicking avatar opens dropdown containing "Sign out"; clicking "Sign out" redirects to `/login`
- [ ] Test: clicking bell shows "No notifications yet"; clicking outside closes it
- [ ] Uses agent-browser + Page Object Model pattern
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts` passes (including this new test)
- [ ] `cd frontend && npm run check` exits 0

**Notes:**

- **Pattern:** Agent-browser POM pattern — see `.github/skills/e2e-testing/SKILL.md` for framework conventions; reference existing `frontend/tests/e2e/auth/login.test.ts` for file structure and import patterns
- **Reference:** `frontend/tests/e2e/auth/login.test.ts` — existing auth E2E test as structural reference
- **Hook point:** New test file — `frontend/tests/e2e/club-dashboard/navbar.test.ts`

---

### WI-005: Membership Status card — skeleton placeholder

**Priority:** 5
**Effort:** S
**Status:** ✅ Complete

**Description:** Create `frontend/src/components/club/dashboard/MembershipStatusCard.vue`. Card header: "Membership Status". Body: two skeleton lines (for tier name and expiry date) using `has-background-grey-lighter` + a message "Your membership details will appear here" in `has-text-grey-light`. Card is always visible.

**Acceptance Criteria:**

- [ ] Component created at `frontend/src/components/club/dashboard/MembershipStatusCard.vue`
- [ ] Card renders with title "Membership Status", two grey skeleton lines, and the placeholder message
- [ ] Uses Bulma `card` / `card-header` / `card-content` markup
- [ ] Skeleton lines use `has-background-grey-lighter`; message uses `has-text-grey-light`
- [ ] `cd frontend && npm run check` exits 0
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts` passes

**Notes:**

- **Pattern:** Bulma card skeleton — `<div class="card"><div class="card-header">...</div><div class="card-content"><p class="block has-background-grey-lighter">&nbsp;</p></div></div>`
- **Reference:** No existing skeleton card in codebase — create fresh; Bulma v1.x card docs
- **Hook point:** Component consumed by `DashboardView.vue` grid (WI-010)
- **⚠️ NO TOAST:** Static placeholder component — do not add toast notifications

---

### WI-006: Upcoming Events card — skeleton placeholder

**Priority:** 6
**Effort:** S
**Status:** ✅ Complete

**Description:** Create `frontend/src/components/club/dashboard/UpcomingEventsCard.vue`. Card header: "Upcoming Events". Body: three skeleton list rows using same `has-background-grey-lighter` style as WI-005, plus message "Events will appear here when available" in `has-text-grey-light`.

**Acceptance Criteria:**

- [ ] Component created at `frontend/src/components/club/dashboard/UpcomingEventsCard.vue`
- [ ] Card renders with title "Upcoming Events", three grey skeleton rows, and the placeholder message
- [ ] Skeleton rows use `has-background-grey-lighter`; message uses `has-text-grey-light` — visually consistent with `MembershipStatusCard`
- [ ] `cd frontend && npm run check` exits 0
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts` passes

**Notes:**

- **Pattern:** Mirror `MembershipStatusCard.vue` (WI-005) — same card structure, three rows instead of two
- **Reference:** `frontend/src/components/club/dashboard/MembershipStatusCard.vue` (created in WI-005)
- **Hook point:** Component consumed by `DashboardView.vue` grid (WI-010)
- **⚠️ NO TOAST:** Static placeholder component — do not add toast notifications

---

### WI-007: Club Info card — live tenant data

**Priority:** 7
**Effort:** S
**Status:** ✅ Complete

**Description:** Create `frontend/src/components/club/dashboard/ClubInfoCard.vue`. Displays: club logo (if `tenantStore.config.branding.logo_url` non-null, else omit `<img>` entirely), club name (`tenantStore.brandName`), and static text "Welcome to your member portal". No placeholder needed — tenant store is always populated at mount.

**Acceptance Criteria:**

- [ ] Component created at `frontend/src/components/club/dashboard/ClubInfoCard.vue`
- [ ] Club name from `tenantStore.brandName` renders in card
- [ ] Club logo renders only when `logo_url` is non-null (no broken image if missing)
- [ ] Static text "Welcome to your member portal" present
- [ ] `cd frontend && npm run check` exits 0
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts` passes

**Notes:**

- **Pattern:** Same logo/name conditional as `ClubNavbar.vue` — `v-if="logoUrl"` on the `<img>` element
- **Reference:** `frontend/src/components/club/ClubNavbar.vue` lines 13–19 for logo conditional; `frontend/src/stores/tenant.js:brandName` getter
- **Hook point:** Component consumed by `DashboardView.vue` grid (WI-010)
- **⚠️ NO TOAST:** Display-only component — do not add toast notifications

---

### WI-008: Quick Actions card — placeholder buttons

**Priority:** 8
**Effort:** S
**Status:** ✅ Complete

**Description:** Create `frontend/src/components/club/dashboard/QuickActionsCard.vue`. Card header: "Quick Actions". Body: two `<RouterLink>` buttons — "Renew Membership" → `/membership` and "Update Profile" → `/profile`. Both use Bulma `button is-primary` class.

**Acceptance Criteria:**

- [ ] Component created at `frontend/src/components/club/dashboard/QuickActionsCard.vue`
- [ ] "Renew Membership" button renders and links to `/membership`
- [ ] "Update Profile" button renders and links to `/profile`
- [ ] Both buttons use `is-primary` class (tenant branding applied via `--bulma-primary`)
- [ ] `cd frontend && npm run check` exits 0
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts` passes

**Notes:**

- **Pattern:** Use Vue `<RouterLink>` with `class="button is-primary"` — not `<a href>` — so Vue router handles navigation
- **Reference:** `frontend/src/router/index.js` for route names; Bulma button docs
- **Hook point:** Component consumed by `DashboardView.vue` grid (WI-010)
- **⚠️ NO TOAST:** Navigation-only component — do not add toast notifications

---

### 🚦 INTEGRATION GATE: All Four Cards Render

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**

1. [ ] Import all four card components into `DashboardView.vue` temporarily and render them side by side (before WI-010 grid layout)
2. [ ] Navigate to `http://test-club.localhost/dashboard`
3. [ ] Confirm: Membership Status card shows two grey skeleton lines + placeholder message
4. [ ] Confirm: Upcoming Events card shows three grey skeleton rows + placeholder message
5. [ ] Confirm: Club Info card shows club name and "Welcome to your member portal"
6. [ ] Confirm: Quick Actions card shows both buttons
7. [ ] Evidence: Write "VERIFIED: [what you saw] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-009: E2E smoke — dashboard card tests

**Priority:** 9
**Effort:** M
**Status:** ✅ Complete

**Description:** Write E2E smoke tests for the four dashboard cards: all cards present in DOM, membership status shows placeholder text, events shows placeholder text, club info shows club name, quick actions buttons render.

**Test File:** `frontend/tests/e2e/club-dashboard/dashboard.test.ts`

**Acceptance Criteria:**

- [ ] Test: all four cards present in dashboard DOM
- [ ] Test: Membership Status card contains text "Your membership details will appear here"
- [ ] Test: Upcoming Events card contains text "Events will appear here when available"
- [ ] Test: Club Info card contains club name from tenant config
- [ ] Test: Quick Actions card contains "Renew Membership" and "Update Profile" buttons
- [ ] Uses agent-browser + Page Object Model pattern
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts` passes (including this new test)
- [ ] `cd frontend && npm run check` exits 0

**Notes:**

- **Pattern:** Agent-browser POM — same conventions as `navbar.test.ts` (WI-004)
- **Reference:** `frontend/tests/e2e/club-dashboard/navbar.test.ts` (WI-004) for imports and POM structure
- **Hook point:** New test file — `frontend/tests/e2e/club-dashboard/dashboard.test.ts`

---

### WI-010: Responsive card grid layout in DashboardView

**Priority:** 10
**Effort:** M
**Status:** ✅ Complete

**Description:** Rewrite `DashboardView.vue` to use: (1) `DashboardNavbar` at the top, (2) a Bulma `columns is-multiline` grid of four cards below, (3) remove the existing standalone sign-out button and welcome text. Grid breakpoints: desktop 2×2 (`is-half`), tablet 2 columns (`is-half`), mobile single column (`is-full`). Add `padding-top` to the content section to clear the fixed navbar height.

**Acceptance Criteria:**

- [ ] `DashboardNavbar` rendered at top of `DashboardView.vue`
- [ ] Four card components laid out in `columns is-multiline` grid
- [ ] Each card column uses `column is-half-tablet is-half-desktop is-full-mobile`
- [ ] Old sign-out button and plain welcome `<h1>` removed from `DashboardView.vue`
- [ ] Content section has sufficient top padding to clear the fixed navbar (`padding-top: 4rem` or `section` class)
- [ ] `cd frontend && npm run check` exits 0
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts` passes

**Notes:**

- **Pattern:** Bulma responsive columns — `<div class="columns is-multiline">` with `<div class="column is-half-tablet is-full-mobile">` per card
- **Reference:** `frontend/src/views/DashboardView.vue` (existing stub to replace); `frontend/src/views/ClubHomePage.vue` for fixed-navbar padding pattern
- **Hook point:** `frontend/src/views/DashboardView.vue` — already registered in `frontend/src/router/index.js` at path `/dashboard`
- **⚠️ NO TOAST:** Layout-only view wiring — do not add toast notifications

---

### 🚦 INTEGRATION GATE: Full Dashboard Works

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**

1. [ ] `docker compose up` (or `cd frontend && npm run dev`)
2. [ ] Log in and navigate to `http://test-club.localhost/dashboard`
3. [ ] Confirm: `DashboardNavbar` visible at top; no old sign-out button or plain title visible
4. [ ] Confirm: 2×2 card grid renders on desktop
5. [ ] Confirm: Resize to mobile → cards stack vertically in single column
6. [ ] Confirm: Cards do not overlap the fixed navbar
7. [ ] Confirm: `cd frontend && npm run check` exits 0
8. [ ] Evidence: Write "VERIFIED: [what you saw] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-011: E2E smoke — responsive layout test

**Priority:** 11
**Effort:** S
**Status:** ✅ Complete

**Description:** Write E2E smoke test verifying mobile responsiveness: hamburger visible at mobile width, cards stack in single column.

**Test File:** `frontend/tests/e2e/club-dashboard/responsive.test.ts`

**Acceptance Criteria:**

- [ ] Test: at mobile viewport width (<768px), hamburger burger button is visible
- [ ] Test: at mobile viewport width, cards are stacked vertically (single column)
- [ ] Uses agent-browser + Page Object Model pattern
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts` passes (including this new test)
- [ ] `cd frontend && npm run check` exits 0

**Notes:**

- **Pattern:** Agent-browser viewport resize — see existing E2E tests or framework docs for viewport control
- **Reference:** `frontend/tests/e2e/club-dashboard/dashboard.test.ts` (WI-009) for POM reuse
- **Hook point:** New test file — `frontend/tests/e2e/club-dashboard/responsive.test.ts`

---

### 🚦 INTEGRATION GATE: All Tests Pass

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**

1. [ ] Run: `cd frontend && npm run check` — exits 0
2. [ ] Run: `cd frontend && npx vitest run --config vitest.e2e.config.ts` — all tests pass (3 new files + existing regression)
3. [ ] Confirm: `tests/e2e/auth/login.test.ts` still passes (login redirects to `/dashboard`)
4. [ ] Evidence: Write "VERIFIED: [what you saw] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

## Functional Requirements

- FR-1: `DashboardNavbar` with club branding, nav links, avatar dropdown, notification bell
- FR-2: Notification bell with "No notifications yet" dropdown; mutually exclusive with user menu
- FR-3: Membership Status card — skeleton placeholder always visible
- FR-4: Upcoming Events card — skeleton placeholder always visible
- FR-5: Club Info card — live club name + logo from tenant store
- FR-6: Quick Actions card — placeholder nav buttons
- FR-7: Responsive 2×2 card grid (mobile: single column)

## Non-Goals

- No new backend models or API endpoints
- No `/profile` or `/membership` pages
- No real membership, events, or notifications data
- No admin dashboard views

## Technical Notes

- `authStore.logout()` already swallows API failures silently (`try/catch` that ignores errors) — no additional error handling needed in the component
- `tenantStore.brandName` returns `'MemberFlow'` as fallback if `config.name` is null — safe to use without null check
- `/dashboard` route already has `meta: { requiresAuth: true }` and the guard in `router/index.js` handles redirect to `/login`
- `@heroicons/vue` is already installed locally
- Bulma `is-fixed-top` on navbar requires `padding-top` on the page content — match existing pattern in `ClubHomePage.vue`
- E2E test config: `frontend/vitest.e2e.config.ts` — run with `npx vitest run --config vitest.e2e.config.ts`

## Success Metrics

- Member can determine their club name and navigate from the dashboard on first login
- Member can sign out via navbar dropdown
- All four cards visible with appropriate placeholder or live content
- Dashboard is usable on mobile (hamburger nav, stacked cards)
