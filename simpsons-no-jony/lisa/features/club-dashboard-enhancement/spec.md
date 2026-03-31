# Feature: Club Dashboard Enhancement

## Problem Statement

After logging in, members see only a welcome message and a sign-out button. They cannot determine whether their membership is active, see upcoming club events, or access any useful club information without contacting someone directly. The dashboard provides no value post-login.

## Scope

**In:**
- New `DashboardNavbar` component (separate from `ClubNavbar`)
- Dashboard navbar: club logo/name, nav links, user avatar menu (Profile, Sign out), notification bell
- Dashboard layout: top navbar + responsive card grid
- Four dashboard cards: Membership Status, Upcoming Events, Club Info, Quick Actions
- Greyed-out placeholder/skeleton state for cards with no backend data (Membership, Events)
- Notification bell with empty-state dropdown (no backend)
- Mobile responsive: hamburger menu on mobile, cards stack vertically
- Wires only to existing stores: `authStore` (user name, email) and `tenantStore` (club name, logo, branding)
- Remove existing standalone sign-out button from `DashboardView.vue`
- Only one dropdown (bell or user menu) open at a time — opening one closes the other

**Out:**
- No new backend models or API endpoints in this feature
- No `/profile` page (link is a placeholder only)
- No real membership data (future feature)
- No real events data (future feature)
- No real notifications (future feature)
- No admin-specific dashboard views

## Requirements

### FR-1: Dashboard Navbar

A new `DashboardNavbar` component, used only on the dashboard (not the club homepage).

- **Left:** Club logo (from `tenantStore.config.branding.logo_url`, fallback to club name text) + nav links: Dashboard (active state), Events (placeholder link), Profile (placeholder link)
- **Right:** Notification bell icon + user avatar with dropdown
- **Avatar initials:** Display `first_name[0] + last_name[0]` uppercased (e.g. "JD"). If `last_name` is missing, show `first_name[0]` only. If `first_name` is also missing, show `email[0]` uppercased.
- **Dropdown:** "Profile" (link to `/profile`, placeholder) and "Sign out"
- **Sign out behaviour:** Calls `authStore.logout()`; if logout API fails, clear local tokens regardless and redirect to `/login` — never block the user from signing out
- **Mobile:** Collapses to hamburger menu; links and user menu stack vertically when open
- **Active state:** "Dashboard" link visually highlighted (Bulma `is-active` class) when on `/dashboard`
- **Mutual exclusion:** Opening the user menu dropdown closes the bell dropdown (and vice versa)
- **Route protection:** `/dashboard` is protected by the existing `requiresAuth` router guard — no changes to the guard needed
- **Integration:** Remove the existing standalone sign-out button from `DashboardView.vue`
- Errors: Logout API failure → clear tokens + redirect to `/login`
- Test Type: **E2E**
- Test: `tests/e2e/club-dashboard/navbar.test.ts` — render navbar, open user menu, click sign out, assert redirect to `/login`

**Acceptance Criteria:**

AC-1: Navbar renders with club branding
```
Given: Authenticated member navigates to /dashboard
When: The page loads
Then: DashboardNavbar is visible with the club name (or logo) on the left and the user's initials avatar on the right
```

AC-2: User menu sign out
```
Given: Authenticated member is on /dashboard
When: Member clicks the avatar → clicks "Sign out"
Then: authStore.logout() is called, local tokens are cleared, member is redirected to /login
```

AC-3: Logout API failure still signs out
```
Given: Authenticated member is on /dashboard and the network is unavailable
When: Member clicks the avatar → clicks "Sign out"
Then: Local tokens are cleared and member is redirected to /login (no error message, no blocking)
```

AC-4: Active nav link
```
Given: Member is on /dashboard
When: DashboardNavbar renders
Then: The "Dashboard" nav link has the Bulma is-active class; "Events" and "Profile" do not
```

AC-5: Mutual exclusion of dropdowns
```
Given: The bell dropdown is open
When: Member clicks the user avatar
Then: The bell dropdown closes and the user menu dropdown opens
```

---

### FR-2: Notification Bell

Bell icon in the navbar. On click, opens a small dropdown panel.

- Dropdown shows: bell icon + text "No notifications yet"
- Clicking outside the dropdown closes it
- Opening the bell dropdown closes the user menu dropdown if open
- No badge/count indicator (no backend)
- Mobile: dropdown opens below bell, full-width on the navbar container
- Errors: none
- Test Type: **E2E**
- Test: `tests/e2e/club-dashboard/navbar.test.ts` — click bell, assert dropdown visible, click outside, assert dropdown hidden

**Acceptance Criteria:**

AC-1: Bell opens notification dropdown
```
Given: Authenticated member is on /dashboard
When: Member clicks the bell icon
Then: A dropdown panel appears showing "No notifications yet"
```

AC-2: Dropdown closes on outside click
```
Given: The bell dropdown is open
When: Member clicks anywhere outside the dropdown
Then: The dropdown closes
```

---

### FR-3: Membership Status Card

Card showing the member's current membership status.

- **Placeholder state** (no backend): greyed-out skeleton — two skeleton lines for "tier name" and "expiry date", labelled "Membership Status" with a subtle message: *"Your membership details will appear here"*
- Card is always visible (not hidden when no data)
- Uses Bulma skeleton/placeholder styling: `has-background-grey-lighter` on skeleton lines, `has-text-grey-light` on placeholder message text
- Test Type: **E2E**
- Test: `tests/e2e/club-dashboard/dashboard.test.ts` — assert membership status card renders with placeholder content

**Acceptance Criteria:**

AC-1: Membership status card renders placeholder
```
Given: Authenticated member is on /dashboard (no membership backend data)
When: The dashboard loads
Then: A card labelled "Membership Status" is visible with two greyed-out skeleton lines and the message "Your membership details will appear here"
```

---

### FR-4: Upcoming Events Card

Card showing upcoming club events.

- **Placeholder state** (no backend): greyed-out skeleton — three skeleton list rows, labelled "Upcoming Events" with message: *"Events will appear here when available"*
- Card is always visible
- Uses Bulma skeleton/placeholder styling: `has-background-grey-lighter` on skeleton rows, `has-text-grey-light` on placeholder message text (matches FR-3 styling)
- Test Type: **E2E**
- Test: `tests/e2e/club-dashboard/dashboard.test.ts` — assert events card renders with placeholder content

**Acceptance Criteria:**

AC-1: Events card renders placeholder
```
Given: Authenticated member is on /dashboard (no events backend data)
When: The dashboard loads
Then: A card labelled "Upcoming Events" is visible with three greyed-out skeleton rows and the message "Events will appear here when available"
```

---

### FR-5: Club Info Card

Card showing club name and a welcome message, sourced from the tenant store.

- Displays: club logo (if `branding.logo_url` exists, else omit logo element), club name (`tenantStore.config.name`), static text: *"Welcome to your member portal"*
- No placeholder state needed — `tenantStore` is always populated before app mount (bootstrap blocks on `/api/v1/config/`)
- Test Type: **E2E**
- Test: `tests/e2e/club-dashboard/dashboard.test.ts` — assert club name appears in club info card

**Acceptance Criteria:**

AC-1: Club info card renders club name
```
Given: Authenticated member is on /dashboard
When: The dashboard loads
Then: A card is visible containing the club name from tenantStore and the text "Welcome to your member portal"
```

---

### FR-6: Quick Actions Card

Card with shortcut action buttons.

- Buttons (all placeholder navigation for now):
  - "Renew Membership" → links to `/membership` (placeholder route)
  - "Update Profile" → links to `/profile` (placeholder route)
- Buttons use Bulma `is-primary` class (respects tenant branding via `--bulma-primary` CSS custom property)
- Test Type: **E2E**
- Test: `tests/e2e/club-dashboard/dashboard.test.ts` — assert both buttons render

**Acceptance Criteria:**

AC-1: Quick action buttons render
```
Given: Authenticated member is on /dashboard
When: The dashboard loads
Then: A card is visible with two buttons labelled "Renew Membership" and "Update Profile"
```

---

### FR-7: Responsive Card Grid

The four cards are arranged in a responsive grid below the navbar.

- Desktop (≥ 1024px): 2×2 grid
- Tablet (768–1023px): 2 columns
- Mobile (< 768px): single column, cards stack vertically
- Uses Bulma `columns` + `is-multiline` grid system
- Test Type: **E2E**
- Test: covered by `dashboard.test.ts` — assert all four cards present in DOM

**Acceptance Criteria:**

AC-1: All four cards present
```
Given: Authenticated member is on /dashboard
When: The dashboard loads
Then: All four cards (Membership Status, Upcoming Events, Club Info, Quick Actions) are present in the DOM
```

---

## Data Model

No new backend models in this feature. All data sourced from:

| Source | Data used |
|---|---|
| `authStore.user.first_name` | Avatar initials (primary) |
| `authStore.user.last_name` | Avatar initials (secondary; omit if missing) |
| `authStore.user.email` | Avatar initials fallback if both name fields missing |
| `tenantStore.config.name` | Club name in navbar + club info card |
| `tenantStore.config.branding.logo_url` | Club logo in navbar + club info card (omitted if null/empty) |

## API

No new API endpoints. All data comes from stores already populated at app bootstrap.

## UX Flow

1. Member logs in → redirected to `/dashboard` (protected by existing `requiresAuth` guard)
2. Dashboard mounts → `DashboardNavbar` renders with club logo/name (from tenant store) and user initials avatar
3. Four cards render in a 2×2 grid
4. Membership Status and Events cards show greyed-out skeleton placeholders
5. Club Info card shows club name + welcome text
6. Quick Actions card shows two placeholder buttons
7. Member clicks avatar → user menu dropdown opens (bell dropdown closes if open)
8. Member clicks bell → bell dropdown opens showing "No notifications yet" (user menu closes if open)
9. Member clicks Sign out → `authStore.logout()` called → tokens cleared → redirect to `/login` (even if API call fails)
10. On mobile → navbar collapses to hamburger; cards stack vertically

## Edge Cases

| Case | Behaviour |
|---|---|
| `branding.logo_url` is null/empty | Show club name as text only; no broken image element |
| `user.first_name` and `user.last_name` both present | Avatar shows `first_name[0] + last_name[0]` uppercased (e.g. "JD") |
| `user.last_name` missing | Avatar shows `first_name[0]` only (e.g. "J") |
| `user.first_name` missing | Avatar shows `email[0]` uppercased |
| Bell dropdown open + user avatar clicked | Bell dropdown closes, user menu dropdown opens |
| User menu dropdown open + bell clicked | User menu dropdown closes, bell dropdown opens |
| Either dropdown open + outside click | Dropdown closes |
| Bell dropdown open + navbar hamburger toggled | Bell dropdown closes |
| Logout API call fails (network error) | Clear local tokens, redirect to `/login` — no error shown |
| User clicks Profile or Renew/Update Profile links | Navigates to `/profile` or `/membership` (placeholder routes; router handles if page not found) |

## Test Strategy

### 🎯 Test Philosophy: E2E Smoke First

🔥 E2E Smoke Tests — PREFERRED: Prove features work for real users
📦 Unit Tests — FOR: Complex logic with many edge cases only

⚠️ **INTERLEAVING RULE:** Tests MUST be written immediately after their feature phase, NOT all at end.
⚠️ **FRAMEWORK:** E2E uses **agent-browser** with **Page Object Model** (NOT Playwright).

### Test Phases

| Feature Phase | Test Type | Test File | When to Write |
|---|---|---|---|
| FR-1 + FR-2: Navbar + Bell | E2E smoke | `navbar.test.ts` | After navbar work items |
| FR-3 + FR-4 + FR-5 + FR-6: Cards | E2E smoke | `dashboard.test.ts` | After each card work item |
| FR-7: Responsive grid | E2E smoke | `responsive.test.ts` | After grid work item |

### New Tests Required

| Scenario | File | Phase |
|---|---|---|
| Navbar renders with club name, user avatar | `tests/e2e/club-dashboard/navbar.test.ts` | After FR-1 |
| User menu opens, sign out redirects to /login | `tests/e2e/club-dashboard/navbar.test.ts` | After FR-1 |
| Bell opens "no notifications" dropdown, closes on outside click | `tests/e2e/club-dashboard/navbar.test.ts` | After FR-2 |
| All four cards present in dashboard grid | `tests/e2e/club-dashboard/dashboard.test.ts` | After FR-3–6 |
| Membership status card shows placeholder | `tests/e2e/club-dashboard/dashboard.test.ts` | After FR-3 |
| Events card shows placeholder | `tests/e2e/club-dashboard/dashboard.test.ts` | After FR-4 |
| Club info card shows club name | `tests/e2e/club-dashboard/dashboard.test.ts` | After FR-5 |
| Quick actions buttons render | `tests/e2e/club-dashboard/dashboard.test.ts` | After FR-6 |
| Mobile: hamburger visible, cards stack | `tests/e2e/club-dashboard/responsive.test.ts` | After FR-7 |

### Regression Tests
- `tests/e2e/auth/login.test.ts` — login still redirects to `/dashboard`

### Test Data Requirements
- Seeded tenant with `name` and `branding.logo_url`
- Authenticated member user with `first_name`, `last_name`, and `email`

## Open Questions

None.
