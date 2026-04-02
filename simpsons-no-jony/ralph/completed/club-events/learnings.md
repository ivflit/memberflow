# Learnings: Club Events

_Ralph fills this in as work items are completed._

## INTEGRATION GATE 5: Feature Complete

VERIFIED: 134 backend tests pass; 26 new frontend events tests pass (119 total frontend passing, 8 pre-existing failures unchanged); npm run build exits 0; EventsView.vue and ProfileView My Agenda complete @ 2026-04-02T15:45:00Z

- WI-011: EventsView.vue — search/filter bar, event cards, skeleton loading, error state with retry, empty states (with/without filters), cancelled banner, members-only lock badge, pagination, Google Maps link for postcoded venues
- WI-012: SCSS partials _events.scss + _event-card.scss in src/styles/ — imported in main.scss under views and club components respectively
- WI-013: My Agenda section added to ProfileView.vue — calls getAgenda() on mount, silent-fail on error, shows up to 5 events with date/title/venue, loading skeletons, empty state
- WI-014: Agenda SCSS appended to _profile.scss — profile-agenda-list, profile-agenda-item, profile-agenda-skeleton, responsive layout
- WI-015: events-page.test.ts — 16 tests covering all EventsView states and interactions
- WI-016: agenda.test.ts — 10 tests covering My Agenda section on ProfileView
- WI-017: ARCHITECTURE.md updated — apps/events entry in directory tree, events domain description, public + admin events API endpoints, EventsView route

## INTEGRATION GATE 4: Events Page Renders

VERIFIED: npm run build exits 0 (3.57s, EventsView-*.js bundled); EventsView.vue, SCSS partials, and main.scss imports all correct @ 2026-04-02T15:44:00Z

## INTEGRATION GATE 3: Backend Complete

VERIFIED: 134 total tests pass (59 events tests + 75 pre-existing tests); all events tests PASSED @ 2026-04-02T00:00:00Z

- WI-007: AdminEventCategoryListView and AdminEventCategoryDetailView; IsOrgStaff for GET, IsOrgAdmin for mutations; 409 on delete with events
- WI-008: AdminEventListView and AdminEventDetailView with full CRUD; 409 on delete non-draft; all registered under /api/v1/admin/events/
- WI-009: 46 backend E2E tests covering all ACs — public list/detail, agenda (auth required), admin CRUD, permissions, tenant isolation, eligibility integration

## INTEGRATION GATE 2: Public API Responds

VERIFIED: 88 tests pass, Django check clean, URL routing verified via system check, events list/categories/agenda/detail all registered @ 2026-04-02T00:00:00Z

- WI-004: EventSerializer with is_restricted and is_eligible SerializerMethodFields; EventCategorySerializer
- WI-005: AdminEventCategorySerializer with name uniqueness validation; AdminEventSerializer with cross-org category and tier validation, end_datetime > start_datetime check
- WI-006: EventListView, EventCategoryListView, EventDetailView, EventAgendaView; pagination 20 per page; URL order: categories, agenda, pk, list

## INTEGRATION GATE 1: Data Layer

VERIFIED: migrate exits 0, models importable, 13/13 eligibility tests pass @ 2026-04-02T00:00:00Z

- WI-001: apps/memberships created with MembershipTier and Membership models; unique constraint on (organization, user); migration clean
- WI-002: apps/events created with EventCategory and Event models; ArrayField for restricted_to_roles; M2M to MembershipTier; indexes on (organization, status) and (organization, start_datetime)
- WI-003: is_event_eligible() helper in apps/events/eligibility.py; 13 unit tests covering all 6 conditional branches including OR logic and inactive membership edge case
