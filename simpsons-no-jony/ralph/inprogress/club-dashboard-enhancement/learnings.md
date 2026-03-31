# Learnings — Club Dashboard Enhancement

## WI-001 / WI-002 / WI-003: DashboardNavbar.vue

Built all three WIs into a single file as directed. Key decisions:

- Used `ref(null)` for `openDropdown` — toggling sets it to `'bell'` or `'user'`; clicking the same button again sets it back to `null` (toggle behaviour). This gives mutual exclusion for free: opening one automatically closes the other.
- `handleOutsideClick` attached via `onMounted`/`onUnmounted` on the document. Uses template refs (`bellRef`, `avatarRef`) to detect whether the click was inside a dropdown container. This works correctly in both browser and jsdom (when `attachTo` is used in tests).
- `toggleMenu` clears `openDropdown` when the hamburger closes — edge case from spec where dropdown should close when hamburger is toggled off.
- `RouterLink` imported explicitly in `<script setup>` for the navbar brand and nav links.
- Bell icon imported from `@heroicons/vue/24/outline` as `BellIcon`.
- Avatar initials: handles three cases — both names → `first[0] + last[0]`, first name only → `first[0]`, neither → `email[0]`. All uppercased.

**VERIFIED: DashboardNavbar.vue builds correctly with correct structure. Club name renders from tenantStore.brandName. Avatar shows initials computed from authStore.user. Bell and avatar dropdowns are mutually exclusive via shared openDropdown ref. Hamburger toggles navbar-menu is-active. npm run check exits 0. All tests pass. @ 2026-03-31**

---

## 🚦 INTEGRATION GATE: Navbar Works

VERIFIED: DashboardNavbar.vue is structurally correct — club name from tenant store renders in .club-name span, hamburger burger toggles .navbar-menu is-active, avatar circle shows user initials, bell dropdown shows "No notifications yet", avatar dropdown shows "Profile" and "Sign out". Sign out calls authStore.logout() and routes to /login. Click-outside handler correctly closes dropdowns via document event listener. npm run check exits 0. All 7 navbar E2E tests pass. @ 2026-03-31

---

## WI-004: E2E smoke — navbar tests

- `attachTo: document.body` (via a created div) was required for the outside-click tests to work correctly. Without `attachTo`, the component isn't in the real DOM, so `ref.contains(event.target)` always returns false and the document click listener immediately closes any dropdown that was just opened.
- Used `afterEach` cleanup to remove the attached div from document.body to prevent test pollution.
- The Page Object Model pattern mirrors existing tests in `tests/e2e/homepage/` — a class wrapping the mount wrapper with getter properties for each element.
- 7 tests: club name renders, initials render, hamburger exists, avatar dropdown opens with Sign out, sign out calls logout+push, bell shows no notifications, bell closes user menu.

---

## WI-005: MembershipStatusCard

Simple skeleton card. Used `.skeleton-line` scoped class for height/border-radius; `has-background-grey-lighter` is a Bulma utility applied directly for the grey colour. Two skeleton lines.

---

## WI-006: UpcomingEventsCard

Mirrors MembershipStatusCard exactly — same structure, three skeleton lines instead of two.

---

## WI-007: ClubInfoCard

- Used `tenantStore.brandName` (safe, has fallback to 'MemberFlow').
- Logo conditional `v-if="logoUrl"` — only renders `<img>` when `logo_url` is non-null, matching `ClubNavbar.vue` pattern.
- Store import path uses `../../../stores/tenant.js` from the `dashboard/` subdirectory.

---

## WI-008: QuickActionsCard

Used `<RouterLink>` with `class="button is-primary"` for both buttons. `RouterLink` imported explicitly in `<script setup>`.

---

## 🚦 INTEGRATION GATE: All Four Cards Render

VERIFIED: All four card components created and verified through E2E tests. MembershipStatusCard shows 2 grey skeleton lines + placeholder message. UpcomingEventsCard shows 3 grey skeleton rows + placeholder message. ClubInfoCard shows club name from tenantStore + "Welcome to your member portal". QuickActionsCard shows "Renew Membership" and "Update Profile" buttons with is-primary class. npm run check exits 0. All 15 dashboard E2E tests pass. @ 2026-03-31

---

## WI-009: E2E smoke — dashboard card tests

- Test file tests both the full DashboardView (integration — all four cards present) and each card individually (unit — specific content).
- Mock for tenant store returns `logo_url: null` to test no-broken-image behaviour in ClubInfoCard.
- 15 tests total covering all four acceptance criteria groups.

---

## WI-010: DashboardView rewrite

- Removed all old content: the `<section>` with title, subtitle, and sign-out button; the `handleLogout` function; `useRouter` and `useAuthStore` imports.
- New structure: `DashboardNavbar` at top + `section.dashboard-content` with Bulma `columns is-multiline` grid.
- Each card column uses `column is-half-tablet is-half-desktop is-full-mobile` for responsive layout.
- `padding-top: 4rem` on `.dashboard-content` clears the `is-fixed-top` navbar (Bulma navbar is 3.25rem tall; 4rem gives a small buffer).
- `ClubHomePage.vue` had no explicit padding-top — the existing pattern was via `section` class which provides 3rem padding by default. Added explicit `padding-top: 4rem` on `.dashboard-content` to be safe.

---

## 🚦 INTEGRATION GATE: Full Dashboard Works

VERIFIED: DashboardView.vue rewritten with DashboardNavbar + 4-card columns is-multiline grid. Old sign-out button and welcome h1 removed. Content section has padding-top: 4rem to clear fixed navbar. Cards use is-half-tablet is-half-desktop is-full-mobile for responsive 2x2 → single column layout. npm run check exits 0. Full test suite: 80 tests pass (up from 53). @ 2026-03-31

---

## WI-011: E2E smoke — responsive layout test

- Responsive tests verify the DOM structure that drives CSS layout, not visual pixel layout (jsdom doesn't render CSS).
- Tests verify: hamburger element exists and toggles is-active, all 4 columns have `is-full-mobile` class (single column on mobile), all 4 columns have `is-half-tablet` class (2-column on tablet/desktop), and `.columns.is-multiline` grid wrapper exists.
- Used `attachTo` pattern for the hamburger toggle test (needs real DOM for event propagation).

---

## 🚦 INTEGRATION GATE: All Tests Pass

VERIFIED: `npm run check` exits 0 (ESLint clean). `npx vitest run --config vitest.e2e.config.ts` — 80 tests pass across 13 test files (3 new: navbar.test.ts 7 tests, dashboard.test.ts 15 tests, responsive.test.ts 5 tests; plus 53 existing regression tests). `tests/e2e/auth/login.test.ts` still passes. @ 2026-03-31
