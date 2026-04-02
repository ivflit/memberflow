# Feature: Club Events

## Problem Statement

Club admins have no way to communicate upcoming activities (matches, training sessions, socials, AGMs) to members through MemberFlow. Members check external channels (email, WhatsApp) to find out what's on. Events need to live inside the platform so members have a single place to see what's coming up, and admins have a structured way to publish them.

**Success metric:** A club admin can create and publish an event visible on the public events page within 2 minutes of starting.

---

## Scope

**In:**
- Event model with full field set (title, description, datetime, venue, category, image URL, status, exclusivity)
- Admin CRUD for events and event categories
- Public member-facing events page at `/events` (visible without login)
- Search bar (title/description) + filter bar (category, date range) on events page
- Membership exclusivity: events can be restricted to specific tiers and/or roles
- Restricted events visible to all but show a members-only lock/badge for ineligible viewers
- Four event statuses: draft, published, cancelled, archived
- Cancelled events remain visible with a "Cancelled" banner
- "My Agenda" section on the member profile page — upcoming eligible events

**Out (follow-on spec):**
- Event registration / booking a spot (capacity management)
- Paid event entry
- Bookmarking / saving events
- Email notifications for new events
- Image upload via file picker (images specified as URLs in this spec)
- iCal / calendar export

---

## Requirements

### FR-1: Event Category Management (Admin)

Admins can create, update, and delete event categories scoped to their club.

- Input: `name` (required, max 50 chars), `colour` (optional hex string, e.g. `#3273dc`)
- Output: `{ id, name, colour }`
- Constraints: name unique per organisation; cannot delete a category with attached events
- Errors: 400 name missing or exceeds 50 chars, 400 duplicate name, 409 on delete if category has events

**Acceptance Criteria:**

```
AC-1a: Create category
Given: Admin is authenticated as org_admin
When: POST /api/v1/admin/events/categories/ with { name: "Match Day", colour: "#3273dc" }
Then: 201 response with { id, name: "Match Day", colour: "#3273dc" }; category visible in GET /api/v1/events/categories/

AC-1b: Duplicate name rejected
Given: Category "Match Day" already exists for the org
When: POST /api/v1/admin/events/categories/ with { name: "Match Day" }
Then: 400 response

AC-1c: Delete blocked when events attached
Given: Category "Match Day" has one or more events
When: DELETE /api/v1/admin/events/categories/<id>/
Then: 409 response; category not deleted
```

- Test Type: **E2E smoke** — CRUD covers the full stack
- Test: `tests/e2e/events/admin-events.test.ts`

---

### FR-2: Event CRUD (Admin)

Admins can create, read, update, and delete events for their club.

**Fields:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | CharField(200) | Yes | |
| `description` | TextField | No | Plain text; no max length enforced |
| `start_datetime` | DateTimeField | Yes | Stored as UTC |
| `end_datetime` | DateTimeField | No | Must be after `start_datetime` if provided |
| `venue_name` | CharField(200) | No | e.g. "Springfield Cricket Ground" |
| `venue_postcode` | CharField(20) | No | Used to generate Google Maps link |
| `category` | FK → EventCategory | No | Must belong to same org; nullable SET_NULL |
| `image_url` | URLField(500) | No | Direct URL to event image |
| `status` | CharField(20) | Yes | draft / published / cancelled / archived; default: draft |
| `restricted_to_tiers` | M2M → MembershipTier | No | Empty = open to all tiers |
| `restricted_to_roles` | ArrayField(CharField) | No | Empty = open to all roles; choices: member / org_staff / org_admin |

- Errors: 400 end before start, 400 category belongs to different org, 400 tier belongs to different org, 409 on DELETE if status is not draft

**Acceptance Criteria:**

```
AC-2a: Create draft event
Given: Admin is authenticated
When: POST /api/v1/admin/events/ with valid payload, status: "draft"
Then: 201 response; event NOT returned by GET /api/v1/events/ (public list)

AC-2b: Publish event
Given: Draft event exists
When: PATCH /api/v1/admin/events/<id>/ with { status: "published" }
Then: 200 response; event now returned by GET /api/v1/events/

AC-2c: Delete only allowed on draft
Given: Event with status "published"
When: DELETE /api/v1/admin/events/<id>/
Then: 409 response; event not deleted

AC-2d: end_datetime before start rejected
Given: Admin creates event
When: POST with end_datetime before start_datetime
Then: 400 response
```

- Test Type: **E2E smoke**
- Test: `tests/e2e/events/admin-events.test.ts`

---

### FR-3: Public Events List

A public endpoint returns all published + cancelled events for the tenant, ordered by `start_datetime` ascending. Draft and archived events excluded.

- Auth: None required
- Pagination: offset-based, page size 20. Query param `?page=2`. Response: `{ results: [...], count: <total matching>, next: <url or null>, previous: <url or null> }`
- Query params: `search` (case-insensitive match on title and description), `category` (category ID), `date_from` (ISO date; events with start_datetime >= date_from), `date_to` (ISO date; events with start_datetime <= date_to)
- Response per event: `{ id, title, description, start_datetime, end_datetime, venue_name, venue_postcode, category: { id, name, colour } | null, image_url, status, is_restricted, is_eligible }`
  - `is_restricted`: true if event has any tier or role restrictions
  - `is_eligible`: true if authenticated user passes eligibility check; false for unauthenticated requests on restricted events; always true for unrestricted events

**Acceptance Criteria:**

```
AC-3a: Published events returned, draft excluded
Given: Org has one published event and one draft event
When: GET /api/v1/events/ (unauthenticated)
Then: Response contains published event; draft event absent

AC-3b: Cancelled events included with status field
Given: Org has a cancelled event
When: GET /api/v1/events/
Then: Cancelled event in results with status: "cancelled"

AC-3c: Search filters by title
Given: Two events: "Summer BBQ" and "AGM"
When: GET /api/v1/events/?search=bbq
Then: Only "Summer BBQ" returned

AC-3d: Category filter
Given: Two events, one with category "Match Day", one with "Social"
When: GET /api/v1/events/?category=<match_day_id>
Then: Only Match Day event returned
```

- Test Type: **E2E smoke**
- Test: `tests/e2e/events/events-list.test.ts`

---

### FR-4: Event Detail (Public)

- Auth: None required
- 404 if event is draft or archived
- 404 if event belongs to different org (tenant isolation)
- Response: same shape as list item

**Acceptance Criteria:**

```
AC-4a: Draft returns 404
Given: Draft event with known ID
When: GET /api/v1/events/<id>/ (unauthenticated)
Then: 404

AC-4b: Published event returns detail
Given: Published event
When: GET /api/v1/events/<id>/
Then: 200 with full event shape
```

- Test Type: **E2E smoke** — covered in `events-list.test.ts`

---

### FR-5: Membership Exclusivity Logic

An event is "restricted" (`is_restricted: true`) if `restricted_to_tiers` or `restricted_to_roles` is non-empty.

**Eligibility rules:**
1. Unrestricted event → always eligible (`is_eligible: true`)
2. Unauthenticated request on restricted event → `is_eligible: false`
3. `restricted_to_tiers` non-empty → user must have an active membership with a tier in the list
4. `restricted_to_roles` non-empty → user's role must be in the list
5. If both are set → OR logic — user is eligible if either condition 3 OR condition 4 is satisfied
6. If only tiers set → only tier check applies; if only roles set → only role check applies

**Acceptance Criteria:**

```
AC-5a: Unrestricted event — all eligible
Given: Event with no restricted_to_tiers and no restricted_to_roles
When: GET /api/v1/events/ (any user or unauthenticated)
Then: is_eligible: true

AC-5b: Tier-restricted — eligible member
Given: Event restricted to tier "Full Member"; authenticated user has active "Full Member" membership
When: GET /api/v1/events/
Then: is_eligible: true for that event

AC-5c: Tier-restricted — ineligible member
Given: Event restricted to tier "Full Member"; user has "Junior" membership
When: GET /api/v1/events/
Then: is_eligible: false; is_restricted: true

AC-5d: OR logic — role satisfies when tier does not
Given: Event restricted to tiers: ["Full Member"] AND roles: ["org_staff"]
       User has "Junior" membership but role is org_staff
When: GET /api/v1/events/
Then: is_eligible: true (role condition satisfied)
```

- Test Type: **Unit** — OR logic with 6 conditional branches justifies isolated testing
- Test: `tests/unit/events/eligibility.test.ts`

---

### FR-6: Events Page (Frontend `/events`)

Public-facing page available at `/events`. No authentication required.

**Layout:**
1. Page heading "Upcoming Events"
2. Loading state: skeleton cards (3 placeholder cards) while API call is in flight
3. Error state: "Failed to load events. Please try again." with retry button if API call fails
4. Search bar (text input, debounced 300ms, searches title and description)
5. Filter bar: Category dropdown (populated from `/api/v1/events/categories/`), Date From / Date To date pickers; "Clear filters" link when any filter active
6. Event cards grid, ordered soonest first
7. Empty state: "No upcoming events" when list is empty (no events exist); "No events match your search" when filters return nothing

**Event card:**
- Image: full-width top of card; fallback placeholder shown if `image_url` is null OR if the image URL fails to load (onerror handler sets fallback)
- Category badge: coloured chip with `category.colour`; if category has no colour, use `var(--bulma-primary)`; if no category, badge omitted
- Title
- Date and time: formatted as "Sat 12 Apr · 2:00 PM" in browser local time using `toLocaleString()` with appropriate locale options
- Venue name with Google Maps link (`https://maps.google.com/?q=<venue_postcode>` in new tab) if `venue_postcode` is set; plain text if no postcode
- "CANCELLED" banner overlaid on card (red ribbon or full-width bar) if `status === 'cancelled'`
- Members-only lock icon (visible to all) if `is_restricted: true` and `is_eligible: false`

**Acceptance Criteria:**

```
AC-6a: Page renders published events
Given: Org has two published events
When: EventsView component is mounted (mocked API returns two events)
Then: Two event cards rendered in the DOM

AC-6b: Cancelled banner shown
Given: One event has status "cancelled"
When: Component mounted
Then: Card includes an element with class or text "CANCELLED"

AC-6c: Members-only badge shown for ineligible restricted events
Given: Event has is_restricted: true, is_eligible: false
When: Component mounted
Then: Lock badge element is present on that card

AC-6d: Empty state shown
Given: API returns empty results
When: Component mounted
Then: "No upcoming events" text present; no card elements rendered
```

- Test Type: **E2E smoke**
- Test: `tests/e2e/events/events-page.test.ts`

---

### FR-7: My Agenda (Profile Page)

New "My Agenda" card added to `/profile` below the existing Change Password card.

- Endpoint: `GET /api/v1/events/agenda/` — auth required (401 if unauthenticated)
- Returns: upcoming (start_datetime > now, UTC) published events the authenticated user is eligible for; ordered by start_datetime ASC; maximum 5 items; same response shape as events list item
- Frontend: up to 5 rows, each showing: event title, formatted date (same format as FR-6), venue name (plain text, no map link needed here)
- "View all events →" link at bottom of card; navigates to `/events`
- Empty state: "No upcoming events" if zero eligible upcoming events
- Loading state: 3 skeleton rows while in flight
- Error state: silent fail — if /agenda/ call errors, the card shows "No upcoming events" (profile page should not break due to events API failure)

**Acceptance Criteria:**

```
AC-7a: Agenda section renders on profile page
Given: Authenticated user; mocked /agenda/ returns two events
When: ProfileView is mounted
Then: "My Agenda" heading visible; two event rows rendered

AC-7b: Empty state shown
Given: Mocked /agenda/ returns empty results
When: ProfileView mounted
Then: "No upcoming events" text present in agenda section

AC-7c: View all events link present
When: ProfileView mounted (any agenda state)
Then: "View all events" link present pointing to /events

AC-7d: Agenda endpoint requires auth
When: GET /api/v1/events/agenda/ without JWT
Then: 401 response
```

- Test Type: **E2E smoke**
- Test: `tests/e2e/events/agenda.test.ts`

---

## Data Model

### EventCategory

| Field | Type | Constraints |
|---|---|---|
| `id` | AutoField | PK |
| `organization` | FK → Organization | via TenantAwareModel; cascade delete |
| `name` | CharField(50) | unique per org |
| `colour` | CharField(7) | nullable/blank; hex e.g. `#3273dc` |
| `created_at` | DateTimeField | auto |
| `updated_at` | DateTimeField | auto |

### Event

| Field | Type | Constraints |
|---|---|---|
| `id` | AutoField | PK |
| `organization` | FK → Organization | via TenantAwareModel; cascade delete |
| `title` | CharField(200) | required |
| `description` | TextField | nullable/blank |
| `start_datetime` | DateTimeField | required |
| `end_datetime` | DateTimeField | nullable |
| `venue_name` | CharField(200) | nullable/blank |
| `venue_postcode` | CharField(20) | nullable/blank |
| `category` | FK → EventCategory | nullable; on_delete=SET_NULL |
| `image_url` | URLField(500) | nullable/blank |
| `status` | CharField(20) | choices: draft/published/cancelled/archived; default: draft |
| `restricted_to_tiers` | M2M → MembershipTier | blank=True; through table EventTierRestriction |
| `restricted_to_roles` | ArrayField(CharField(20)) | blank=True; default=list; choices: member/org_staff/org_admin |
| `created_at` | DateTimeField | auto |
| `updated_at` | DateTimeField | auto |

**Indexes:** `(organization_id, status)`, `(organization_id, start_datetime)`

**Relationships:**
- EventCategory: 1 org → N categories
- Event → EventCategory: N:1 (nullable)
- Event → MembershipTier: M:N via `restricted_to_tiers`

---

## API

### Public endpoints (no auth required)

#### GET /api/v1/events/
Params: `search`, `category`, `date_from`, `date_to`, `page`
Response: `{ count, next, previous, results: [EventSummary] }`
EventSummary: `{ id, title, description, start_datetime, end_datetime, venue_name, venue_postcode, category: {id, name, colour}|null, image_url, status, is_restricted, is_eligible }`

#### GET /api/v1/events/<id>/
Response: EventSummary shape
Errors: 404 if draft, archived, or wrong org

#### GET /api/v1/events/categories/
Response: `[{ id, name, colour }]`
No pagination (categories are few per org)

### Authenticated member endpoint

#### GET /api/v1/events/agenda/
Auth: JWT required → 401 if absent
Response: `{ count, results: [EventSummary] }` — max 5, upcoming + eligible only

### Admin endpoints (IsOrgAdmin or IsOrgStaff)

#### GET /api/v1/admin/events/
All statuses. Params: `status`, `category`, `search`, `page` (page size 20)
Response: same paginated shape as public list (without is_eligible)

#### POST /api/v1/admin/events/
Body: all Event fields except id/timestamps
Errors: 400 end before start; 400 category/tier from wrong org

#### GET /api/v1/admin/events/<id>/
Full detail including draft/archived

#### PATCH /api/v1/admin/events/<id>/
Partial update. Same validation as POST.

#### DELETE /api/v1/admin/events/<id>/
Errors: 409 if status != draft

#### GET /api/v1/admin/events/categories/
Response: `[{ id, name, colour }]`

#### POST /api/v1/admin/events/categories/
Body: `{ name, colour }`
Errors: 400 missing/duplicate name

#### PATCH /api/v1/admin/events/categories/<id>/
Body: `{ name?, colour? }`

#### DELETE /api/v1/admin/events/categories/<id>/
Errors: 409 if category has events

---

## UX Flow

### Public visitor browses events

1. Visitor lands on `/events`
2. 3 skeleton cards shown while API call in flight
3. Published + cancelled events displayed soonest first; 20 per page
4. Visitor types in search bar → list re-fetches after 300ms debounce
5. Visitor selects category from dropdown → list re-fetches immediately
6. Visitor sets date range → list re-fetches immediately
7. Restricted events visible with lock badge; cancelled events visible with "CANCELLED" banner
8. Visitor clicks Google Maps postcode link → opens maps in new tab
9. If API call fails → error message with retry button

### Member views their agenda

1. Member navigates to `/profile`
2. "My Agenda" card visible below Change Password card
3. 3 skeleton rows while /agenda/ call in flight
4. Up to 5 upcoming eligible events shown with title, date, venue
5. "View all events →" link at card bottom navigates to `/events`
6. If /agenda/ fails → card shows "No upcoming events" (silent fail)

### Admin creates and publishes an event

1. Admin creates event — status defaults to draft; not visible publicly
2. Admin fills all fields, saves
3. Admin sets status=published → event immediately visible on GET /api/v1/events/
4. Admin sets status=cancelled → event stays on public page with "CANCELLED" banner
5. Admin sets status=archived → event disappears from public page (404 on direct URL)
6. Admin may only DELETE events in draft status; published/cancelled/archived must use archived

---

## Edge Cases

| Case | Behaviour |
|---|---|
| Event with no `image_url` | Placeholder shown on card |
| `image_url` set but image fails to load | onerror handler on `<img>` swaps to placeholder |
| `end_datetime` before `start_datetime` | 400 validation error |
| Category deleted while events use it | Prevented — 409 on category delete |
| Tier from different org on event | 400 validation error |
| Archived event accessed by direct URL | 404 |
| Draft event accessed by direct URL | 404 |
| No events match search/filter | "No events match your search" empty state |
| No events at all | "No upcoming events" empty state |
| Unauthenticated user hits /agenda/ | 401 |
| Event with both tier and role restrictions | OR logic — eligible if either condition met |
| Member with no active membership viewing tier-restricted event | `is_eligible: false`; lock badge shown |
| Category with no colour set | Category badge uses `var(--bulma-primary)` |
| Org has zero categories | Category filter dropdown shows "All categories" only; no error |
| Admin attempts to delete published event | 409 response; suggest using "archived" status |

---

## Test Strategy

### 🎯 Test Philosophy: E2E Smoke First

🔥 E2E Smoke Tests — PREFERRED: prove features work for real users
📦 Unit Tests — FOR: complex logic with multiple conditional branches only

⚠️ **INTERLEAVING RULE:** E2E tests MUST be written immediately after their feature phase. NOT all at the end.

### Test Type by FR

| FR | Test Type | Justification |
|----|-----------|---------------|
| FR-1: Category CRUD | E2E smoke | Full stack CRUD |
| FR-2: Event CRUD | E2E smoke | Full stack CRUD |
| FR-3: Public events list | E2E smoke | User-facing, full stack |
| FR-4: Event detail | E2E smoke | Covered alongside FR-3 |
| FR-5: Eligibility logic | Unit | OR logic with 6 conditional branches |
| FR-6: Events page (frontend) | E2E smoke | User-facing component |
| FR-7: My Agenda | E2E smoke | User-facing component |

### Test Phases

| Phase | Test Type | File | When |
|-------|-----------|------|------|
| Backend — Event + Category models | E2E smoke | `tests/e2e/events/admin-events.test.ts` | After model + admin API WIs |
| Backend — Public events API | E2E smoke | `tests/e2e/events/events-list.test.ts` | After public API WIs |
| Backend — Eligibility logic | Unit | `tests/unit/events/eligibility.test.ts` | After eligibility helper WI |
| Frontend — Events page | E2E smoke | `tests/e2e/events/events-page.test.ts` | After EventsView WIs |
| Frontend — My Agenda | E2E smoke | `tests/e2e/events/agenda.test.ts` | After Agenda WIs |

### Tenant Isolation (mandatory)

- Org A admin cannot read/write org B events via admin endpoints (expects 404)
- Org A public events list does not include org B events
- These tests are required per endpoint, not optional

### Regression

- `tests/e2e/profile/dob-address.test.ts` — profile page gains My Agenda card; existing profile tests must still pass
- `tests/e2e/club-dashboard/dashboard.test.ts` — unaffected
- `tests/e2e/auth/login.test.ts` — unaffected

### Test Data Requirements

- Factory: `EventCategoryFactory` with name, colour, org
- Factory: `EventFactory` with status, start_datetime, category, optional restrictions
- Factory: `MembershipTierFactory` (may already exist in `apps/memberships`)

---

## Open Questions

None.
