# PRD: Modern Responsive Homepage & Navigation

branchName: feature/modern-homepage-navigation

## Overview

MemberFlow has no public-facing homepage. This PRD delivers two distinct experiences: a fully static platform marketing page (`memberflow.com`) that advertises MemberFlow to prospective club admins, and a tenant-branded club homepage (`springfield-cc.memberflow.com`) for members. Includes a contact form with email delivery, AOS animations, Heroicons, and per-tenant branding.

## Source Spec

`simpsons-no-jony/lisa/features/modern-homepage-navigation/spec.md`

**⚠️ READ THE SPEC — it contains implementation patterns, exact copy, colour values, CSS snippets, and component references.**

## Goals

- Platform homepage loads with Lighthouse performance score ≥ 85
- Contact form delivers email to `ivanflitcroft@gmail.com` within 60 seconds of valid submission
- Club homepage correctly renders tenant branding (colour + logo) for any active tenant
- All 9 E2E smoke tests pass

## Testing Requirements (Applies to ALL Work Items)

**⚠️ MANDATORY — Every WI acceptance criteria MUST include ALL of these:**

1. ✅ **Backend tests:** `docker compose exec api pytest` (MUST pass)
2. ✅ **Frontend check:** `cd frontend && npm run check` (lint + type check — MUST exit 0)
3. ✅ **E2E smoke** (for WIs touching user-facing code): `cd frontend && npx vitest run --config vitest.e2e.config.ts` (MUST pass)
4. ✅ Manual verification: Confirm feature works as expected in browser

**Use `cd frontend && npm run fix`** to auto-fix frontend lint/format issues before committing.

**If ANY check fails:** Fix before marking WI complete. Do NOT skip.

---

## Work Items

### WI-001: TenantMiddleware — Root Domain Pass-Through

**Priority:** 1
**Effort:** S
**Status:** ✅ Complete

**Description:** The current `TenantMiddleware` raises a 404 for any unrecognised subdomain, which means visiting `memberflow.com` (no subdomain) returns a 404. Add a pass-through branch: if the host has no subdomain or matches the root domain, set `request.tenant = None` and continue. Only tenant-scoped views enforce non-null tenant — this change does not affect them.

**Acceptance Criteria:**

- [ ] `GET memberflow.com/` returns non-404 (passes through middleware)
- [ ] `GET springfield-cc.memberflow.com/` still resolves tenant correctly (existing behaviour unchanged)
- [ ] `GET unknown-slug.memberflow.com/` still returns 404 (unrecognised subdomain still blocked)
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "Implementation Patterns → TenantMiddleware" — `if no subdomain present, set request.tenant = None and return self.get_response(request)`
- **Reference:** `core/middleware.py:TenantMiddleware.__call__` — modify the existing try/except block
- **Hook point:** `core/middleware.py` — add subdomain detection before the `Organization.objects.get()` call. Root domain condition: `if subdomain == host` (no dot split) or `subdomain in ('www', 'memberflow')` — check actual deployment domain

---

### WI-002: `apps/contact/` — Serializer + View + Rate Limiting

**Priority:** 2
**Effort:** M
**Status:** ✅ Complete

**Description:** Create the `apps/contact/` Django app with a DRF serializer and view for `POST /api/v1/contact/`. The serializer handles field validation (required, email format, name rules, message length, MX check via `dnspython`). The view handles honeypot detection and IP-based rate limiting (3/hr via Django cache). No tenant scope needed — this endpoint lives on the platform domain.

**Acceptance Criteria:**

- [ ] `POST /api/v1/contact/` with valid data returns 200 `{ "detail": "Thanks! We'll be in touch soon." }`
- [ ] `POST /api/v1/contact/` with invalid email returns 400 with `email` field error
- [ ] `POST /api/v1/contact/` with message < 20 chars returns 400 with `message` field error
- [ ] `POST /api/v1/contact/` with empty name returns 400 with `name` field error
- [ ] `POST /api/v1/contact/` with honeypot `website` field non-empty returns 200 silently (no email queued)
- [ ] `POST /api/v1/contact/` 4th time from same IP within 1 hour returns 429
- [ ] `docker compose exec api pytest apps/contact/` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "FR-6 — Contact Form" for full validation rules and error messages
- **Reference:** `apps/users/serializers.py` for DRF serializer patterns; `apps/users/views.py` for APIView patterns
- **Hook point:** Create `apps/contact/__init__.py`, `apps/contact/serializers.py`, `apps/contact/views.py` — rate limiting via `django.core.cache.cache.get/set` keyed on `f"contact_rate:{request.META.get('REMOTE_ADDR')}"`
- **MX check:** `pip install dnspython`; add to `requirements.txt`; in serializer: `import dns.resolver`; `dns.resolver.resolve(domain, 'MX')` — catch `NXDOMAIN` as invalid, catch `Timeout`/`NoAnswer` as fail-open

---

### WI-003: Contact Celery Task + Gmail SMTP Settings

**Priority:** 3
**Effort:** M
**Status:** ✅ Complete

**Description:** Create `tasks/contact.py:send_contact_email` Celery task that sends an email to `ivanflitcroft@gmail.com` with the enquiry details. Add Gmail SMTP settings to `config/settings/base.py` (using env vars). Add exponential backoff retry. The view from WI-002 queues this task on successful validation.

**Acceptance Criteria:**

- [ ] `send_contact_email.delay(name, email, message, submitted_at)` sends email with subject `"New MemberFlow Enquiry from [Name]"`
- [ ] Email body contains name, email, message, and timestamp
- [ ] Task retries with exponential backoff on SMTP failure (`self.retry(countdown=60 * (2 ** self.request.retries), max_retries=3)`)
- [ ] Gmail SMTP env vars documented in `config/settings/base.py` comments: `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
- [ ] `docker compose exec api pytest tasks/` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "FR-6 — Email format" for subject/body spec; "Implementation Patterns → Email task"
- **Reference:** Existing Celery task patterns in `tasks/email.py` (exponential backoff pattern already in use)
- **Hook point:** Create `tasks/contact.py`; import and queue from `apps/contact/views.py:ContactView.post()` after serializer `is_valid()`; add `EMAIL_*` settings to `config/settings/base.py`

---

### WI-004: Wire Contact App — INSTALLED_APPS + URLs

**Priority:** 4
**Effort:** S
**Status:** ✅ Complete

**Description:** Register `apps.contact` in `INSTALLED_APPS` and add `POST /api/v1/contact/` to `config/urls.py`. This is the final wiring step that makes the contact endpoint reachable.

**Acceptance Criteria:**

- [ ] `curl -X POST http://memberflow.localhost/api/v1/contact/` reaches the view (no 404)
- [ ] `docker compose exec api python manage.py check` passes (no app config errors)
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "Implementation Patterns → Contact endpoint"
- **Reference:** `config/settings/base.py:INSTALLED_APPS` — append `'apps.contact'`; `config/urls.py` — add `path('api/v1/contact/', include('apps.contact.urls'))`
- **Hook point:** `config/settings/base.py:INSTALLED_APPS` and `config/urls.py:urlpatterns`

---

### 🚦 INTEGRATION GATE: Contact API Live

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Start services: `docker compose up`
2. [ ] Run: `curl -X POST http://memberflow.localhost/api/v1/contact/ -H "Content-Type: application/json" -d '{"name":"Test User","email":"test@example.com","message":"This is a test message for the contact form.","website":""}'`
3. [ ] Expected: `{"detail": "Thanks! We'll be in touch soon."}`
4. [ ] Run: same request with `"email": "notreal"` → Expected: 400 with email error
5. [ ] Run: `GET http://memberflow.localhost/` → Expected: non-404 response
6. [ ] Evidence: Write "VERIFIED: [what you saw] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-005: Unit Tests — Contact Validation + Task

**Priority:** 5
**Effort:** M
**Status:** ✅ Complete

**Description:** Unit tests for the contact app validation logic and Celery task. Tests MX record check edge cases, honeypot detection, rate limiting, and email task content correctness.

**Acceptance Criteria:**

- [ ] Test: valid domain MX → passes validation
- [ ] Test: non-existent domain MX (NXDOMAIN) → returns error "That email domain doesn't appear to exist..."
- [ ] Test: DNS timeout → fails open (submission accepted)
- [ ] Test: honeypot `website` field non-empty → view returns 200, task NOT called
- [ ] Test: 4th submission from same IP within 1hr → 429
- [ ] Test: email task sends correct subject `"New MemberFlow Enquiry from [name]"` and body contains name, email, message
- [ ] `docker compose exec api pytest apps/contact/tests/` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "Test Strategy → Unit Tests" for scenario list
- **Reference:** `apps/users/tests/test_views.py` for DRF test client patterns; `tasks/` tests for Celery task mocking patterns
- **Hook point:** Create `apps/contact/tests/__init__.py`, `apps/contact/tests/test_validation.py`, `apps/contact/tests/test_tasks.py`

---

### WI-006: Frontend Foundation — AOS + Heroicons + Tenant Store `hasTenant`

**Priority:** 6
**Effort:** S
**Status:** ✅ Complete

**Description:** Install AOS (`aos` npm package) and `@heroicons/vue`. Initialise AOS in `main.js` after tenant bootstrap. Add `hasTenant` computed getter to tenant store. Add global reduced-motion CSS override. Add platform colour CSS variables to `main.scss`.

**Acceptance Criteria:**

- [ ] `npm list aos` and `npm list @heroicons/vue` show installed packages
- [ ] `AOS.init({ duration: 800, once: true })` called in `main.js` after `tenantStore.bootstrap()`
- [ ] `tenantStore.hasTenant` returns `true` when `config` is not null, `false` otherwise
- [ ] `@media (prefers-reduced-motion: reduce)` CSS block in `main.scss` disables AOS and marquee animations
- [ ] Platform colour variables defined in `main.scss`: `--mf-navy: #1B2A4A`, `--mf-teal: #00C9A7`, `--mf-surface: #F8FAFC`, `--mf-text: #334155`
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "Implementation Patterns → AOS" and "Implementation Patterns → Reduced motion"
- **Reference:** `frontend/src/main.js` for bootstrap sequence; `frontend/src/stores/tenant.js` for getter pattern; `frontend/src/styles/main.scss` for CSS variables
- **Hook point:** `main.js` after `await tenantStore.bootstrap()`; `stores/tenant.js:getters`; `styles/main.scss`

---

### WI-007: Platform Navbar Component

**Priority:** 7
**Effort:** M
**Status:** ✅ Complete

**Description:** Build `PlatformNavbar.vue` — fixed responsive navbar for `memberflow.com`. Desktop: logo left, nav links centre, "Get Started" CTA right. Mobile: hamburger toggle. Scroll effect: past 50px, adds box-shadow and white background. All CTAs and "Contact" link scroll to `#contact`.

**Acceptance Criteria:**

- [ ] Navbar is fixed to top (CSS `position: fixed`)
- [ ] Desktop shows: MemberFlow logo, Features / Pricing / Contact links, "Get Started" button
- [ ] Mobile (< 768px): logo + hamburger only; tapping hamburger reveals links and CTA
- [ ] Scrolling past 50px triggers box-shadow + white background transition
- [ ] "Get Started" and "Contact" link scroll to `#contact` (smooth scroll)
- [ ] Verified in browser at `memberflow.localhost`
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "FR-1 — Platform Marketing Page Navbar" for exact layout, scroll threshold, CSS transition values
- **Reference:** `frontend/src/components/` — create `PlatformNavbar.vue` as new component; Bulma `navbar` component for responsive structure (`navbar-burger`, `navbar-menu`)
- **Hook point:** Import into `PlatformHomePage.vue` (WI-014); use `window.addEventListener('scroll')` or a `useScrollPosition` composable in `src/composables/useScrollPosition.js`
- **⚠️ NO TOAST:** This component has no user actions that produce feedback — no notifications of any kind.

---

### WI-008: Platform Hero Section

**Priority:** 8
**Effort:** M
**Status:** ✅ Complete

**Description:** Build `PlatformHero.vue` — full-viewport hero with diagonal navy→teal gradient, headline, sub-headline, and "Get Started" CTA that scrolls to `#contact`. AOS fade-up on load.

**Acceptance Criteria:**

- [ ] Hero is full viewport height (`min-height: 100vh`)
- [ ] Background: `linear-gradient(135deg, #1B2A4A 0%, #00C9A7 100%)`
- [ ] Headline: "Membership management, built for clubs." (white, large)
- [ ] Sub-headline: "Stop chasing spreadsheets..." (white, readable)
- [ ] "Get Started" button scrolls to `#contact` on click
- [ ] AOS `data-aos="fade-up"` applied to content container
- [ ] Verified in browser
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "FR-2 — Hero Section" for exact copy, gradient direction, and AOS attribute
- **Reference:** `frontend/src/views/` — create `frontend/src/components/platform/PlatformHero.vue`; Bulma `hero is-fullheight` class
- **Hook point:** Import into `PlatformHomePage.vue` (WI-014)
- **⚠️ NO TOAST:** CTA scrolls the page — no notification or toast of any kind.

---

### 🚦 INTEGRATION GATE: Platform Page Above Fold

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Start frontend: `cd frontend && npm run dev`
2. [ ] Open: `http://memberflow.localhost` (or `localhost:5173` with no tenant subdomain)
3. [ ] Expected: Fixed navbar with logo + links + "Get Started"; gradient hero with headline visible
4. [ ] Expected: Clicking "Get Started" or "Contact" nav link scrolls to bottom of page
5. [ ] Expected: Scrolling past 50px makes navbar go white with shadow
6. [ ] Evidence: Write "VERIFIED: [what you saw] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-009: Platform Features Section

**Priority:** 9
**Effort:** M
**Status:** ✅ Complete

**Description:** Build `PlatformFeatures.vue` — 6 feature cards in a responsive Bulma grid. Each card has a Heroicons outline icon, title, and one-line description. AOS slide-up on scroll. Hover: `translateY(-4px)` + elevated shadow.

**Acceptance Criteria:**

- [ ] All 6 feature cards render with correct title and description (see spec FR-3 for exact copy)
- [ ] Grid: 3 columns desktop, 2 tablet, 1 mobile (Bulma `columns is-multiline`)
- [ ] Each card has a Heroicons outline icon using `var(--bulma-primary)` colour
- [ ] AOS `data-aos="slide-up"` on each card (staggered with `data-aos-delay`)
- [ ] Hover effect: card lifts on mouse-enter, resets on mouse-leave
- [ ] Verified in browser (scroll to reveal AOS)
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "FR-3" for card titles, descriptions, AOS attributes, and hover CSS values
- **Reference:** Create `frontend/src/components/platform/PlatformFeatures.vue`; icon imports from `@heroicons/vue/24/outline` (e.g. `ShieldCheckIcon`, `CreditCardIcon`, `UserGroupIcon`)
- **Hook point:** Import into `PlatformHomePage.vue` (WI-014)
- **⚠️ NO TOAST:** Static display section — no user interactions produce feedback.

---

### WI-010: Platform Pricing Section

**Priority:** 10
**Effort:** M
**Status:** ✅ Complete

**Description:** Build `PlatformPricing.vue` — 3 pricing tier cards (Starter, Pro, Enterprise). Pro tier highlighted with primary colour border and "Most Popular" badge. CTAs scroll to `#contact`. AOS fade-in on scroll. Hover lift effect.

**Acceptance Criteria:**

- [ ] 3 pricing cards render: Starter (£XX/mo), Pro (£XX/mo), Enterprise (Contact us)
- [ ] Pro card has "Most Popular" badge and a highlighted border using `var(--mf-teal)`
- [ ] Each tier lists correct feature set (see spec FR-4 table)
- [ ] "Get Started" (Starter/Pro) and "Contact Us" (Enterprise) CTAs scroll to `#contact`
- [ ] AOS `data-aos="fade-in"` on cards
- [ ] Hover: card lift effect
- [ ] Verified in browser
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "FR-4 — Pricing Section" for tier details, feature lists, and highlighted card spec
- **Reference:** Create `frontend/src/components/platform/PlatformPricing.vue`; Bulma `card` + `tag is-warning` for badge
- **Hook point:** Import into `PlatformHomePage.vue` (WI-014)
- **⚠️ NO TOAST:** CTA buttons scroll the page — no notification or toast.

---

### WI-011: Platform Logo Carousel

**Priority:** 11
**Effort:** M
**Status:** ✅ Complete

**Description:** Build `PlatformCarousel.vue` — "Trusted by clubs & organisations" section with 8 placeholder SVG logos in an infinite CSS marquee animation. Pure CSS, no JS animation library. Respects `prefers-reduced-motion`.

**Acceptance Criteria:**

- [ ] Section heading "Trusted by clubs & organisations" renders
- [ ] 8 placeholder logos scroll horizontally in an infinite loop
- [ ] Animation uses `@keyframes marquee` (`transform: translateX(0)` → `translateX(-50%)`, 30s linear infinite)
- [ ] Logo list duplicated in DOM for seamless loop
- [ ] Logos scale to 80×40px on mobile (120×60px desktop)
- [ ] `@media (prefers-reduced-motion: reduce)` pauses the animation
- [ ] Verified in browser (logos scroll smoothly)
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "FR-5 — Logo Carousel" and "Implementation Patterns → Carousel CSS"
- **Reference:** Create `frontend/src/components/platform/PlatformCarousel.vue`; add `@keyframes marquee` to `frontend/src/styles/_variables.scss`
- **Hook point:** Import into `PlatformHomePage.vue` (WI-014)
- **⚠️ NO TOAST:** Passive display — no user interactions.

---

### 🚦 INTEGRATION GATE: Platform Sections Render

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Open: `http://memberflow.localhost`
2. [ ] Scroll to Features section → Expected: 6 cards visible with icons and text, AOS slide-in works
3. [ ] Scroll to Pricing section → Expected: 3 cards visible, Pro card has "Most Popular" badge
4. [ ] Scroll to Logo Carousel → Expected: logos scrolling smoothly in infinite loop
5. [ ] Test reduced motion: open DevTools → Rendering → enable "Emulate CSS prefers-reduced-motion" → Expected: carousel stops
6. [ ] Evidence: Write "VERIFIED: [what you saw] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-012: Platform Contact Form

**Priority:** 12
**Effort:** M
**Status:** ✅ Complete

**Description:** Build `PlatformContactForm.vue` — the `#contact` section with name/email/message fields and a hidden honeypot. Calls `POST /api/v1/contact/`. On success shows success message replacing form. On 400 shows inline field errors. On 429 shows dismissable banner. Frontend validates on submit only.

**Acceptance Criteria:**

- [ ] Form has Name, Email, Message fields + hidden `website` honeypot input
- [ ] Submitting valid data calls `POST /api/v1/contact/` and shows "Thanks! We'll be in touch soon." replacing the form
- [ ] On 400 response: field errors appear inline below relevant inputs
- [ ] On 429 response: dismissable banner "Too many requests. Please try again later." shown above form
- [ ] Submit button shows loading state while request is in flight
- [ ] Section has `id="contact"` for scroll targeting
- [ ] Verified in browser: submit valid form → success; submit empty → errors
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "FR-6 — Contact Form" for field validation rules, error messages, and success state behaviour
- **Reference:** Create `frontend/src/components/platform/PlatformContactForm.vue`; `frontend/src/api/` — create `frontend/src/api/contact.js` service module for the POST call
- **Hook point:** Import into `PlatformHomePage.vue` (WI-014); API call via `src/api/contact.js` (never call Axios directly from component)
- **⚠️ NO TOAST:** Success state REPLACES the form with an inline message — never use a toast. Error messages appear INLINE below each field, not in a toast. The 429 banner is a dismissable inline element, not a toast.

---

### WI-013: Platform Footer

**Priority:** 13
**Effort:** M
**Status:** ✅ Complete

**Description:** Build `PlatformFooter.vue` — 4-column footer with MemberFlow logo + tagline + copyright, Product links, Company links, and Social icons. Divider line above. Collapses to stacked on mobile.

**Acceptance Criteria:**

- [ ] Footer renders with 4 columns: branding, Product, Company, Social
- [ ] Column 1: MemberFlow logo, "Membership management, built for clubs.", `© 2026 MemberFlow`
- [ ] Column 2 (Product): Features, Pricing, Contact links
- [ ] Column 3 (Company): About, Contact links
- [ ] Column 4: Twitter/X, LinkedIn, GitHub icons (placeholder `#`)
- [ ] Divider line above footer (`border-top`)
- [ ] Collapses to stacked on mobile
- [ ] Verified in browser
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "FR-7 — Footer" for exact column content
- **Reference:** Create `frontend/src/components/platform/PlatformFooter.vue`; social icons from `@heroicons/vue` or inline SVGs
- **Hook point:** Import into `PlatformHomePage.vue` (WI-014)
- **⚠️ NO TOAST:** Static footer — no interactive feedback elements.

---

### WI-014: Assemble `PlatformHomePage.vue` + Router Route

**Priority:** 14
**Effort:** S
**Status:** ✅ Complete

**Description:** Create `PlatformHomePage.vue` that assembles all platform sections in order. Add a Vue Router route: when `!tenantStore.hasTenant`, render `PlatformHomePage` at `/`. Ensure smooth scroll behaviour is set globally (`html { scroll-behavior: smooth }`).

**Acceptance Criteria:**

- [ ] `PlatformHomePage.vue` renders all sections in order: Navbar, Hero, Features, Pricing, Carousel, ContactForm, Footer
- [ ] Router route for `/` renders `PlatformHomePage` when `tenantStore.hasTenant` is false
- [ ] `html { scroll-behavior: smooth }` in `main.scss` (if not already set)
- [ ] Navigating to `memberflow.localhost/` shows the full platform page end-to-end
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "Implementation Patterns → Routing" — `if (!tenantStore.hasTenant)` route guard
- **Reference:** `frontend/src/router/index.js` — add route; create `frontend/src/views/PlatformHomePage.vue`
- **Hook point:** `frontend/src/router/index.js:routes` array; `frontend/src/styles/main.scss`
- **⚠️ NO TOAST:** Routing and layout only — no user feedback required.

---

### 🚦 INTEGRATION GATE: Full Platform Marketing Page

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Open: `http://memberflow.localhost` (or `localhost:5173` with no tenant subdomain)
2. [ ] Scroll through full page — all 7 sections visible: Navbar, Hero, Features, Pricing, Carousel, Contact Form, Footer
3. [ ] AOS animations trigger on scroll (features slide in, pricing fades in)
4. [ ] Logo carousel scrolls infinitely
5. [ ] Click "Get Started" in navbar → scrolls to contact form
6. [ ] Submit contact form with valid data → success message shown; check backend logs show email task queued
7. [ ] Submit contact form with invalid email → inline error shown below email field (no toast)
8. [ ] Evidence: Write "VERIFIED: [what you saw] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-015: E2E Smoke — Platform Navbar + Hero

**Priority:** 15
**Effort:** M
**Status:** ✅ Complete

**Description:** E2E smoke tests proving the platform navbar and hero work end-to-end for a real user visiting `memberflow.com`.

**Test File:** `frontend/tests/e2e/homepage/platform-navbar.test.ts` and `platform-hero.test.ts`

**Acceptance Criteria:**

- [ ] Test: navbar renders with logo, Features/Pricing/Contact links, "Get Started" button
- [ ] Test: on mobile viewport, hamburger is visible; tapping it reveals nav links
- [ ] Test: "Get Started" in hero scrolls to `#contact` section
- [ ] Uses agent-browser + Page Object Model pattern
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts tests/e2e/homepage/platform-navbar.test.ts` passes

**Notes:**

- **Pattern:** See spec "Test Strategy → E2E Smoke Tests" and `simpsons-no-jony/ralph/SKILL.md` for agent-browser POM patterns
- **Reference:** Existing E2E tests in `frontend/tests/e2e/` for POM structure
- **Hook point:** Create `frontend/tests/e2e/homepage/` directory; `platform-navbar.test.ts`, `platform-hero.test.ts`

---

### WI-016: E2E Smoke — Features + Pricing + Carousel

**Priority:** 16
**Effort:** M
**Status:** ✅ Complete

**Description:** E2E smoke tests for the features section, pricing section, and logo carousel on the platform page.

**Test File:** `frontend/tests/e2e/homepage/platform-features.test.ts`, `platform-pricing.test.ts`, `platform-carousel.test.ts`

**Acceptance Criteria:**

- [ ] Test: all 6 feature cards render with correct titles
- [ ] Test: 3 pricing cards render; Pro card has "Most Popular" badge
- [ ] Test: carousel section renders with heading "Trusted by clubs & organisations"
- [ ] Uses agent-browser + POM
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts tests/e2e/homepage/` passes

**Notes:**

- **Pattern:** See spec "Test Strategy → E2E Smoke Tests — After FR-3, FR-4, FR-5"
- **Reference:** `frontend/tests/e2e/homepage/` directory (created in WI-015)
- **Hook point:** `platform-features.test.ts`, `platform-pricing.test.ts`, `platform-carousel.test.ts`

---

### WI-017: E2E Smoke — Contact Form

**Priority:** 17
**Effort:** M
**Status:** ✅ Complete

**Description:** E2E smoke tests for the contact form: happy path (valid submission → success message) and error path (invalid email → inline error).

**Test File:** `frontend/tests/e2e/homepage/contact-form.test.ts`

**Acceptance Criteria:**

- [ ] Test: fill valid name/email/message → submit → see "Thanks! We'll be in touch soon." (form replaced, no toast)
- [ ] Test: submit with invalid email format → see inline error "Please enter a valid email address." below email field
- [ ] Test: submit with empty name → see inline error "Name is required." below name field
- [ ] Uses agent-browser + POM
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts tests/e2e/homepage/contact-form.test.ts` passes

**Notes:**

- **Pattern:** See spec "FR-6 — Contact Form AC-1, AC-2, AC-3"
- **Reference:** `frontend/tests/e2e/homepage/` (from WI-015)
- **Hook point:** `frontend/tests/e2e/homepage/contact-form.test.ts`

---

### WI-018: E2E Smoke — Platform Footer

**Priority:** 18
**Effort:** S
**Status:** ✅ Complete

**Description:** E2E smoke test for the platform footer.

**Test File:** `frontend/tests/e2e/homepage/platform-footer.test.ts`

**Acceptance Criteria:**

- [ ] Test: footer renders with "© 2026 MemberFlow" and four link columns
- [ ] Uses agent-browser + POM
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts tests/e2e/homepage/platform-footer.test.ts` passes

**Notes:**

- **Pattern:** See spec "FR-7 — Footer AC-1"
- **Reference:** `frontend/tests/e2e/homepage/` (from WI-015)
- **Hook point:** `frontend/tests/e2e/homepage/platform-footer.test.ts`

---

### 🚦 INTEGRATION GATE: Platform E2E Tests Pass

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Run: `cd frontend && npx vitest run --config vitest.e2e.config.ts tests/e2e/homepage/`
2. [ ] Expected: All platform homepage E2E tests pass (navbar, hero, features, pricing, carousel, contact form, footer)
3. [ ] Evidence: Write "VERIFIED: [test output summary] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-019: Club Navbar Component

**Priority:** 19
**Effort:** M
**Status:** ✅ Complete

**Description:** Build `ClubNavbar.vue` — fixed responsive navbar for club subdomains. Left: club logo (from tenant store `config.branding.logo_url`) + club name. Right: "Log in" (outline button → `/login`) and "Join Now" (primary button → `/register`). Mobile hamburger. Fallback: no logo → club name only.

**Acceptance Criteria:**

- [ ] Navbar renders with club logo (if configured) + club name from `tenantStore.config.name`
- [ ] "Log in" button links to `/login`; "Join Now" button links to `/register`
- [ ] If `branding.logo_url` is null/empty: shows club name only (no broken image)
- [ ] "Join Now" button uses `var(--bulma-primary)` colour
- [ ] Mobile: hamburger collapses Log in + Join Now
- [ ] Verified in browser at `springfield-cc.memberflow.localhost`
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "FR-8 — Club Subdomain Navbar" for exact layout and fallback behaviour
- **Reference:** Create `frontend/src/components/club/ClubNavbar.vue`; `frontend/src/stores/tenant.js` for `config.name` and `config.branding`
- **Hook point:** Import into `ClubHomePage.vue` (WI-020)
- **⚠️ NO TOAST:** Navigation links only — no user feedback required.

---

### WI-020: Club Hero + `ClubHomePage.vue` + Router Route

**Priority:** 20
**Effort:** M
**Status:** ✅ Complete

**Description:** Build `ClubHero.vue` (full-viewport branded hero: club logo/initials avatar, club name H1, welcome tagline, "Join Now" CTA) and assemble `ClubHomePage.vue`. Add router route: when `tenantStore.hasTenant`, render `ClubHomePage` at `/`.

**Acceptance Criteria:**

- [ ] Hero background uses `var(--bulma-primary)` with `rgba(0,0,0,0.4)` dark overlay
- [ ] Club logo (120px) displayed; if no logo: circular initials avatar with club initials
- [ ] Club name rendered as H1 in white
- [ ] Tagline: "Welcome to [Club Name]" in white
- [ ] "Join Now" button links to `/register`
- [ ] Fallback: no primary colour → `#1B2A4A` navy background
- [ ] AOS `data-aos="fade-up"` on hero content
- [ ] Router `/` renders `ClubHomePage` when `tenantStore.hasTenant` is true
- [ ] Verified in browser at `springfield-cc.memberflow.localhost`
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "FR-9 — Club Subdomain Hero" for overlay CSS, initials avatar, and fallback colour
- **Reference:** Create `frontend/src/components/club/ClubHero.vue` and `frontend/src/views/ClubHomePage.vue`; update `frontend/src/router/index.js`
- **Hook point:** `frontend/src/router/index.js:routes`; computed CSS: `:style="{ background: tenantStore.config?.branding?.primary_color || '#1B2A4A' }"`
- **⚠️ NO TOAST:** "Join Now" links to `/register` — no toast or notification.

---

### 🚦 INTEGRATION GATE: Club Homepage Works

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Open: `http://springfield-cc.memberflow.localhost`
2. [ ] Expected: Club navbar with club name/logo, Log in + Join Now buttons
3. [ ] Expected: Branded hero with club name as H1, welcome tagline, "Join Now" CTA
4. [ ] Expected: Hero background uses club's primary colour (or navy fallback if unconfigured)
5. [ ] Test fallback: temporarily remove branding from test org → hero should show navy
6. [ ] Evidence: Write "VERIFIED: [what you saw] @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

### WI-021: E2E Smoke — Club Navbar + Hero

**Priority:** 21
**Effort:** M
**Status:** ✅ Complete

**Description:** E2E smoke tests for the club subdomain homepage — navbar and hero section.

**Test File:** `frontend/tests/e2e/homepage/club-navbar.test.ts`, `frontend/tests/e2e/homepage/club-hero.test.ts`

**Acceptance Criteria:**

- [ ] Test: club navbar renders with club name, "Log in" button, "Join Now" button
- [ ] Test: club hero renders with club name as H1 and "Join Now" CTA
- [ ] Test: "Log in" links to `/login`; "Join Now" links to `/register`
- [ ] Uses agent-browser + POM; runs against a club subdomain fixture
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts tests/e2e/homepage/club-navbar.test.ts tests/e2e/homepage/club-hero.test.ts` passes

**Notes:**

- **Pattern:** See spec "FR-8 AC-1 and FR-9 AC-1"
- **Reference:** `frontend/tests/e2e/homepage/` (from WI-015); test fixture: `Organization(name="Springfield CC", slug="springfield-cc")` with branding config
- **Hook point:** `frontend/tests/e2e/homepage/club-navbar.test.ts`, `club-hero.test.ts`

---

### WI-022: Regression — Login Page Still Reachable

**Priority:** 22
**Effort:** S
**Status:** ✅ Complete

**Description:** Verify the existing login page is still reachable via the "Log in" link in the club navbar, and that the router changes haven't broken existing auth routes.

**Acceptance Criteria:**

- [ ] `tests/e2e/auth/login.test.ts` still passes after router changes
- [ ] `/login` route renders `LoginView.vue` on a club subdomain
- [ ] `/register` route renders `RegisterView.vue` on a club subdomain
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes
- [ ] `cd frontend && npx vitest run --config vitest.e2e.config.ts tests/e2e/auth/` passes

**Notes:**

- **Pattern:** See spec "Regression Tests — login.test.ts"
- **Reference:** `frontend/src/router/index.js` — confirm `/login` and `/register` routes are not overridden by the new `/` routing logic
- **Hook point:** `frontend/tests/e2e/auth/login.test.ts` (existing file — run, don't modify)

---

### WI-023: Update `about/ARCHITECTURE.md`

**Priority:** 23
**Effort:** S
**Status:** ✅ Complete

**Description:** Update `about/ARCHITECTURE.md` to document: (1) `TenantMiddleware` root domain pass-through behaviour, (2) new `apps/contact/` app and its endpoint, (3) homepage routing logic (`PlatformHomePage` vs `ClubHomePage`), (4) `tenantStore.hasTenant` getter.

**Acceptance Criteria:**

- [ ] ARCHITECTURE.md "Tenant Resolution Middleware" section updated to describe root domain pass-through
- [ ] ARCHITECTURE.md "App Responsibilities" section includes `contact` app description
- [ ] ARCHITECTURE.md frontend "Directory Structure" updated with new view/component files
- [ ] ARCHITECTURE.md `stores/tenant.js` docs mention `hasTenant` getter
- [ ] Changes reviewed for accuracy against the actual implementation
- [ ] `docker compose exec api pytest` passes
- [ ] `cd frontend && npm run check` passes

**Notes:**

- **Pattern:** See spec "Implementation Patterns" section for what changed
- **Reference:** `about/ARCHITECTURE.md` — edit existing sections in-place
- **Hook point:** `about/ARCHITECTURE.md`

---

### 🚦 INTEGRATION GATE: Feature Complete

**STOP. DO NOT PROCEED until this gate passes.**

**Verify:**
1. [ ] Run all E2E tests: `cd frontend && npx vitest run --config vitest.e2e.config.ts tests/e2e/homepage/ tests/e2e/auth/`
2. [ ] Run all backend tests: `docker compose exec api pytest`
3. [ ] Run frontend check: `cd frontend && npm run check`
4. [ ] Open platform page `http://memberflow.localhost` — scroll through full page, submit contact form
5. [ ] Open club page `http://springfield-cc.memberflow.localhost` — verify branding, navbar, hero
6. [ ] Open `about/ARCHITECTURE.md` — confirm documented changes are accurate
7. [ ] Evidence: Write "VERIFIED: all tests green, both pages working @ [timestamp]" in `learnings.md`

**If gate fails:** Fix before proceeding. Do NOT skip.

---

## Functional Requirements

- FR-1: Fixed responsive platform navbar with scroll effect and `#contact` scroll targeting
- FR-2: Full-viewport platform hero with navy→teal gradient, AOS, and "Get Started" CTA
- FR-3: 6 feature cards with Heroicons, AOS slide-in, hover lift
- FR-4: 3 placeholder pricing tiers, Pro highlighted
- FR-5: Infinite CSS logo carousel respecting `prefers-reduced-motion`
- FR-6: Contact form with MX validation, honeypot, rate limiting, Celery email task
- FR-7: 4-column platform footer
- FR-8: Club navbar with tenant branding and auth CTAs
- FR-9: Club hero using `var(--bulma-primary)` with fallback

## Non-Goals

- Membership tier display on club homepage
- Real testimonials
- Platform-level login/auth
- Email provider beyond Gmail SMTP
- Blocking disposable email services (MX check only, not provider blocklist)
- Per-tenant CSS builds

## Technical Notes

- `dnspython` must be added to `requirements.txt`
- `@heroicons/vue` and `aos` must be added to `frontend/package.json`
- TenantMiddleware change affects `core/middleware.py` — test existing tenant resolution still works
- Contact endpoint has no `TenantScopedViewMixin` — intentionally platform-level
- AOS `once: true` prevents re-triggering animations on scroll-back
- `hasTenant` getter addition is additive — no existing code affected

## Success Metrics

- Platform homepage Lighthouse performance score ≥ 85
- Contact form delivers email to `ivanflitcroft@gmail.com` within 60 seconds of valid submission
- All 9 E2E smoke tests pass
- `docker compose exec api pytest` passes (all backend tests green)
- `cd frontend && npm run check` exits 0
