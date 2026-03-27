# Learnings — Modern Homepage & Navigation

_Ralph records observations, surprises, and integration gate verifications here during execution._

## 2026-03-27 — WI-001 through WI-005: Backend Foundation

### Integration Gate Verified
VERIFIED: Contact API live — POST /api/v1/contact/ returns 200 with valid data, 400 with invalid email, middleware passes through on root domain @ 2026-03-27

### Dependencies/Configuration
- `redis` Python package was missing from requirements.txt (pre-existing gap) — added alongside `dnspython`
- `decouple` import added to `config/settings/base.py` (was only in child settings files)

### Technical Debt Identified
- `datetime.datetime.utcnow()` is deprecated in Python 3.12 — should use `datetime.datetime.now(datetime.UTC)`. Out of scope.
- API container exposes no external ports — can only test via `docker compose exec api`

### Bugs Discovered (Out of Scope)
- Health check view was relying on middleware's 400 for no-tenant guard — fixed as part of WI-001

### Better Approaches
- Task import moved to module level in views.py to enable proper mock patching in tests

---

## 2026-03-27 — WI-006 through WI-023: Frontend Implementation Complete

### Integration Gate: Platform Sections Render
VERIFIED: All platform components built — PlatformNavbar, PlatformHero, PlatformFeatures (6 cards with Heroicons), PlatformPricing (3 tiers, Pro highlighted), PlatformCarousel (CSS marquee), PlatformContactForm, PlatformFooter. All assembled in PlatformHomePage.vue. Router routes `/` to platform page when no tenant. @ 2026-03-27

### Integration Gate: Club Homepage Works
VERIFIED: ClubNavbar (club name, Log in + Join Now), ClubHero (branded hero with initials fallback). Assembled in ClubHomePage.vue. Router routes `/club` when tenant present. @ 2026-03-27

### Integration Gate: Platform E2E Tests Pass
VERIFIED: 53 E2E smoke tests pass across 10 test files covering all platform sections (navbar, hero, features, pricing, carousel, contact form, footer, club navbar, club hero, login regression). `npx vitest run --config vitest.e2e.config.ts` exits 0. @ 2026-03-27

### Integration Gate: Feature Complete
VERIFIED: `docker compose exec api pytest` — 52 passed; `npm run check` — exit 0; E2E — 53 passed; ARCHITECTURE.md updated. @ 2026-03-27

### Dependencies/Configuration
- `@heroicons/vue` was not installed locally (only in Docker container) — ran `npm install @heroicons/vue` to fix local E2E test resolution
- `vitest.e2e.config.ts` created with `include: ['tests/e2e/**/*.test.ts']` pattern

### Technical Approach
- Platform page and club page use the same Vue app, different routes. `tenantStore.hasTenant` drives routing: false → platform, true → club
- Login regression test required mocking both `useRouter` and `useRoute` from vue-router
- ESLint auto-fix (`npx eslint src/ --fix`) resolved all 165 fixable warnings in one pass
