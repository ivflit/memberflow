# Feature: Modern Responsive Homepage & Navigation

## Problem Statement

MemberFlow has no public-facing homepage or navigation. There is no entry point for prospective club admins to discover the platform, and no homepage for club members visiting their club's subdomain. Users arriving at either `memberflow.com` or a club subdomain see nothing useful — blocking any real-world adoption.

---

## Scope

**In:**
- Platform marketing page (`memberflow.com`) — fully static, no auth
- Club homepage (`springfield-cc.memberflow.com`) — tenant-branded, content-focused
- Responsive navbar for both experiences
- Contact/inquiry form on platform page (email notification only)
- AOS scroll animations + subtle hover effects
- Platform branding palette (navy + teal)
- Club homepage uses tenant branding via CSS custom properties

**Out:**
- Membership tier display on club homepage (backend not ready)
- Authentication flows (login/register pages — these exist separately)
- Real testimonials (skipped entirely)
- Platform-level login on `memberflow.com` (not needed — auth is per-subdomain)
- Email provider beyond Django SMTP + Gmail (can swap later)
- Actual social/legal page content (placeholder links only)
- Blocking disposable email providers (MX check only blocks non-existent domains)

---

## Requirements

### FR-1: Platform Marketing Page — Navbar

- A fixed responsive navbar rendered on `memberflow.com`
- **Desktop:** Logo left, nav links centre (Features, Pricing, Contact), "Get Started" CTA button right
- **Mobile:** Hamburger menu collapses nav links and CTA into a dropdown
- On scroll past 50px: navbar gains `box-shadow: 0 2px 8px rgba(0,0,0,0.12)` and background transitions from transparent to white with `transition: all 0.3s ease`
- No login button — `memberflow.com` is marketing-only
- "Get Started" CTA and nav "Contact" link both scroll to the `#contact` section on the same page

**Acceptance Criteria:**

AC-1:
```
Given: User navigates to memberflow.com on desktop
When: The page loads
Then: A fixed navbar is visible containing the MemberFlow logo, three nav links (Features, Pricing, Contact), and a "Get Started" button
```

AC-2:
```
Given: User is on memberflow.com on mobile (viewport < 768px)
When: The page loads
Then: The navbar shows only the logo and a hamburger icon; nav links and CTA are hidden
When: User taps the hamburger
Then: Nav links and "Get Started" button appear in a dropdown
```

AC-3:
```
Given: User is on memberflow.com and scrolls past 50px
When: The scroll position exceeds 50px
Then: The navbar gains a visible box-shadow and its background transitions to white
```

AC-4:
```
Given: User clicks "Get Started" or the "Contact" nav link
When: The click event fires
Then: The page smoothly scrolls to the #contact section
```

- Test Type: **E2E**
- Test: `tests/e2e/homepage/platform-navbar.test.ts`

---

### FR-2: Platform Marketing Page — Hero Section

- Full-viewport hero with diagonal gradient background: `#1B2A4A` (navy) → `#00C9A7` (teal), direction `135deg`
- Headline: **"Membership management, built for clubs."**
- Sub-headline: **"Stop chasing spreadsheets. MemberFlow handles registration, payments, and renewals — so you can focus on your club."**
- "Get Started" CTA button (scrolls to `#contact`)
- Subtle entrance animation via AOS: `data-aos="fade-up"` with 800ms duration
- Responsive: text and CTA stack centrally on mobile

**Acceptance Criteria:**

AC-1:
```
Given: User navigates to memberflow.com
When: The page loads
Then: A full-viewport hero is visible with the headline "Membership management, built for clubs.", a sub-headline, and a "Get Started" button
```

AC-2:
```
Given: User clicks "Get Started" in the hero
When: The click fires
Then: The page scrolls smoothly to the #contact section
```

- Test Type: **E2E**
- Test: `tests/e2e/homepage/platform-hero.test.ts`

---

### FR-3: Platform Marketing Page — Features Section

Six feature cards in a responsive grid (3×2 desktop, 2×3 tablet, 1×6 mobile):

1. Multi-Tenant Isolation — "Every club gets its own fully isolated environment."
2. Stripe Payments — "Payments go directly to your club's Stripe account."
3. Member Self-Service — "Members register, pay, and manage their profile themselves."
4. Membership Tiers — "Flexible tiers for Full, Junior, Social, or any custom category."
5. Automated Reminders — "Expiry and renewal reminders sent automatically."
6. Admin Dashboard — "Full visibility of members, payments, and status in one place."

Each card: Heroicons (`@heroicons/vue`) outline icon + title + one-line description. AOS: `data-aos="slide-up"` triggered on scroll. Hover effect: `transform: translateY(-4px)` + elevated `box-shadow`, `transition: all 0.2s ease`. Icon colour: `var(--bulma-primary)`.

**Acceptance Criteria:**

AC-1:
```
Given: User scrolls to the features section on memberflow.com
When: The section enters the viewport
Then: All 6 feature cards are visible, each showing an icon, title, and description
```

AC-2:
```
Given: User hovers over a feature card on desktop
When: The mouse enters the card
Then: The card lifts slightly (translateY) with an elevated shadow
```

- Test Type: **E2E**
- Test: `tests/e2e/homepage/platform-features.test.ts`

---

### FR-4: Platform Marketing Page — Pricing Section

Three placeholder pricing tiers as Bulma cards:

| Tier | Price | Features |
|---|---|---|
| Starter | £XX/mo | Core membership management, up to 100 members, Stripe payments |
| Pro | £XX/mo | Everything in Starter + unlimited members, custom branding, email reminders |
| Enterprise | Contact us | Everything in Pro + API access, QuickBooks/Sage integration, dedicated support |

"Pro" tier is visually highlighted: primary colour border + "Most Popular" badge. CTA buttons: "Get Started" (Starter/Pro, scrolls to `#contact`), "Contact Us" (Enterprise, scrolls to `#contact`). AOS: `data-aos="fade-in"` on scroll. Hover: subtle card lift.

**Acceptance Criteria:**

AC-1:
```
Given: User scrolls to the pricing section on memberflow.com
When: The section enters the viewport
Then: Three pricing cards are visible (Starter, Pro, Enterprise)
And: The Pro card has a "Most Popular" badge and a highlighted border
```

AC-2:
```
Given: User clicks "Get Started" on the Starter or Pro card
When: The click fires
Then: The page scrolls to the #contact section
```

- Test Type: **E2E**
- Test: `tests/e2e/homepage/platform-pricing.test.ts`

---

### FR-5: Platform Marketing Page — Logo Carousel

- Section heading: "Trusted by clubs & organisations"
- 8 placeholder club logos (SVG placeholders, 120×60px each) in a horizontally scrolling infinite loop
- Pure CSS animation: `@keyframes marquee` — `transform: translateX(0)` to `transform: translateX(-50%)`, `animation: marquee 30s linear infinite`
- Logos duplicated in DOM to create seamless loop
- Responsive: logos scale to 80×40px on mobile
- Respects `prefers-reduced-motion`: animation paused when `@media (prefers-reduced-motion: reduce)`

**Acceptance Criteria:**

AC-1:
```
Given: User scrolls to the carousel section on memberflow.com
When: The section is visible
Then: The heading "Trusted by clubs & organisations" is shown and logos are scrolling horizontally
```

- Test Type: **E2E**
- Test: `tests/e2e/homepage/platform-carousel.test.ts`

---

### FR-6: Platform Marketing Page — Contact Form

**Section id:** `#contact`

Fields: **Name** (required), **Email** (required), **Message** (required, textarea)

Validation rules:
- All fields required; empty field error: "[Field] is required."
- Email: valid RFC format; invalid format error: "Please enter a valid email address."
- Email: server-side MX record check via `dnspython` — blocks non-existent domains (e.g. `user@fakeDomain123.com`); MX fail error: "That email domain doesn't appear to exist. Please check and try again." Note: this does NOT block real providers like Gmail.
- Name: min 2 chars, letters/spaces/hyphens only; error: "Please enter your full name."
- Message: min 20 chars; error: "Message must be at least 20 characters."
- Hidden honeypot field (`website`): if filled, silently return 200 without sending email
- Rate limiting: max 3 submissions per IP per hour (Django cache-based); error response: 429

Frontend validation: validates on submit only. On 400 response, parses field-level errors from response body and displays them inline below the relevant input. On 429, displays a dismissable banner: "Too many requests. Please try again later."

On submit:
1. Frontend sends `POST /api/v1/contact/` with form data
2. Backend validates (returns 400 with field errors on failure)
3. On success: queues Celery task to send email to `ivanflitcroft@gmail.com`
4. Returns 200 immediately — does not wait for email send
5. Frontend shows success message replacing the form: "Thanks! We'll be in touch soon."

Email format:
- Subject: `New MemberFlow Enquiry from [Name]`
- Body: Name, Email, Message, timestamp (UTC)

Email backend: `EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'` with Gmail SMTP via env vars (`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_HOST='smtp.gmail.com'`, `EMAIL_PORT=587`, `EMAIL_USE_TLS=True`).

**Acceptance Criteria:**

AC-1:
```
Given: User fills in Name, a valid Email, and a Message of 20+ chars, and submits
When: The form is submitted
Then: The form is replaced by the message "Thanks! We'll be in touch soon."
```

AC-2:
```
Given: User submits with an invalid email format
When: The 400 response is received
Then: An error message "Please enter a valid email address." appears inline below the email field
```

AC-3:
```
Given: User submits with an empty Name field
When: The form is submitted
Then: "Name is required." appears inline below the name field and no API call is made
```

AC-4:
```
Given: A bot fills the hidden honeypot field and submits
When: The backend receives the request
Then: A 200 is returned silently; no email is sent
```

- Test Type: **E2E** + **Unit**
- E2E: `tests/e2e/homepage/contact-form.test.ts`
- Unit: `apps/contact/tests/test_validation.py` — MX record check, honeypot detection, rate limit logic, email task content

---

### FR-7: Platform Marketing Page — Footer

Four-column layout (collapses to stacked on mobile):

- **Col 1:** MemberFlow logo + tagline ("Membership management, built for clubs.") + `© 2026 MemberFlow`
- **Col 2 — Product:** Features, Pricing, Contact (all scroll-link or `#` placeholder)
- **Col 3 — Company:** About (`#`), Contact (scrolls to `#contact`)
- **Col 4 — Social:** Twitter/X, LinkedIn, GitHub icons (placeholder `#` links)

Divider line above footer (`border-top: 1px solid #e2e8f0`). No animations.

**Acceptance Criteria:**

AC-1:
```
Given: User scrolls to the bottom of memberflow.com
When: The footer is visible
Then: The MemberFlow logo, tagline, copyright "© 2026 MemberFlow", and four columns of links are present
```

- Test Type: **E2E**
- Test: `tests/e2e/homepage/platform-footer.test.ts`

---

### FR-8: Club Subdomain Homepage — Navbar

- Fixed responsive navbar on all club subdomains
- **Left:** Club logo (`OrganizationConfig.branding.logo_url`) + club name. If no logo, show club name only.
- **Right:** "Log in" (ghost/outline button, links to `/login`) + "Join Now" (`var(--bulma-primary)` filled button, links to `/register`)
- **Mobile:** Hamburger collapses to stacked buttons
- Club logo/name sourced from tenant store (bootstrapped before mount)
- `tenantStore.hasTenant` computed property: returns `true` if tenant config is not null (add if not already present)

**Acceptance Criteria:**

AC-1:
```
Given: User navigates to springfield-cc.memberflow.com
When: The page loads and tenant bootstrap completes
Then: The navbar shows the club logo (or name fallback), a "Log in" button, and a "Join Now" button
```

AC-2:
```
Given: User is on the club subdomain on mobile (viewport < 768px)
When: The hamburger is tapped
Then: "Log in" and "Join Now" buttons appear in the collapsed menu
```

- Test Type: **E2E**
- Test: `tests/e2e/homepage/club-navbar.test.ts`

---

### FR-9: Club Subdomain Homepage — Hero Section

- Full-viewport hero using `var(--bulma-primary)` as background with a `rgba(0,0,0,0.4)` dark overlay for text legibility
- Fallback if no primary colour configured: `#1B2A4A` navy
- Displays: club logo (120px), club name (H1, white), welcome tagline ("Welcome to [Club Name]", white), "Join Now" CTA (links to `/register`)
- If no logo: display club initials in a circular avatar
- AOS: `data-aos="fade-up"`, 800ms
- Responsive: logo + text stack centrally on mobile
- All animations respect `prefers-reduced-motion`

**Acceptance Criteria:**

AC-1:
```
Given: User navigates to springfield-cc.memberflow.com (club has branding configured)
When: The hero section loads
Then: The club logo, club name as H1, welcome tagline, and "Join Now" button are visible
And: The hero background uses the club's primary colour
```

AC-2:
```
Given: A club has no primary colour configured
When: The hero renders
Then: The hero background falls back to #1B2A4A navy
```

AC-3:
```
Given: A club has no logo configured
When: The navbar and hero render
Then: The navbar shows the club name only; the hero shows a circular initials avatar instead of a logo
```

- Test Type: **E2E**
- Test: `tests/e2e/homepage/club-hero.test.ts`

---

## Data Model

No new database models required. This feature uses:
- `OrganizationConfig.branding` (existing) — club logo URL, primary colour
- `Organization.name` (existing) — club display name
- Contact form submissions are **not persisted** — fire-and-forget via Celery

---

## API

### POST /api/v1/contact/

**Auth:** None (public endpoint)
**Tenant scope:** None — this endpoint lives on the platform domain, not a club subdomain

**Request:**
```json
{
  "name": "Ivan Flitcroft",
  "email": "ivan@example.com",
  "message": "I'd love to set up MemberFlow for our cricket club.",
  "website": ""
}
```
(`website` is the honeypot field — hidden from users, must be empty)

**Response 200:**
```json
{ "detail": "Thanks! We'll be in touch soon." }
```

**Response 400:**
```json
{
  "email": ["Please enter a valid email address."],
  "message": ["Message must be at least 20 characters."]
}
```

**Response 429:**
```json
{ "detail": "Too many requests. Please try again later." }
```

---

## UX Flow

### Platform Marketing Page (`memberflow.com`)

1. User lands → fixed navbar visible (logo, nav links, "Get Started")
2. Hero fades up — gradient background, headline, sub-headline, "Get Started" CTA
3. User scrolls → Features section slides in (6 cards with hover effects)
4. User scrolls → Pricing section fades in (3 tiers, Pro highlighted)
5. User scrolls → Logo carousel auto-scrolls ("Trusted by clubs & organisations")
6. User scrolls → Contact form (`#contact`) appears
7. User fills form and submits:
   - Valid → form replaced with success message
   - Invalid → inline field errors shown, form stays
   - Rate limited → dismissable banner shown
8. Footer at bottom

### Club Subdomain Homepage (`springfield-cc.memberflow.com`)

1. Tenant bootstraps → club branding applied to CSS custom properties
2. Club navbar renders: club logo/name (left), Log in + Join Now (right)
3. Hero fades up: club logo, club name H1, welcome tagline, Join Now CTA
4. (Membership tiers section: deferred to later PRD)

---

## Edge Cases

| Case | Behaviour |
|---|---|
| Club has no logo configured | Navbar: club name only. Hero: circular initials avatar |
| Club has no primary colour configured | Hero background falls back to `#1B2A4A` navy |
| Contact form honeypot field (`website`) filled | Silently return 200; no email sent; no indication to bot |
| Contact form rate limit exceeded (3/hr/IP) | Return 429 with "Too many requests. Please try again later." |
| Email send fails (SMTP error) | Celery retries with exponential backoff; user already received 200 |
| MX record DNS timeout | Fail open — allow submission; log warning; do not block legitimate users |
| `memberflow.com` visited (no subdomain) | `TenantMiddleware` sets `request.tenant = None` and passes through; does NOT raise 404. Only tenant-scoped views enforce non-null tenant. |
| User with `prefers-reduced-motion` enabled | All CSS animations and AOS transitions are disabled/paused |
| Authenticated user visits club subdomain `/` | Club homepage renders regardless of auth state (no redirect) |

---

## Implementation Patterns

- **Routing:** Vue Router — `/` renders `PlatformHomePage.vue` when `!tenantStore.hasTenant`, `ClubHomePage.vue` when `tenantStore.hasTenant`
- **`tenantStore.hasTenant`:** Add computed property to `stores/tenant.js` — `return config.value !== null`
- **TenantMiddleware:** Add root domain pass-through — if no subdomain present, set `request.tenant = None` and `return self.get_response(request)` without 404
- **AOS:** Initialise in `main.js` after tenant bootstrap: `AOS.init({ duration: 800, once: true })`; import `aos/dist/aos.css`
- **Reduced motion:** Add global CSS: `@media (prefers-reduced-motion: reduce) { [data-aos] { transition: none !important; animation: none !important; } .marquee { animation-play-state: paused; } }`
- **Icon library:** `@heroicons/vue` — outline variants. e.g. `import { ShieldCheckIcon } from '@heroicons/vue/24/outline'`
- **Contact endpoint:** New `apps/contact/` Django app — `views.py`, `serializers.py`, `tasks.py`; register in `INSTALLED_APPS` and `config/urls.py`
- **Email task:** `tasks/contact.py:send_contact_email(name, email, message, submitted_at)` — receives all fields explicitly; no tenant context needed
- **Carousel CSS:** `@keyframes marquee` in `_variables.scss`; duplicate logo list in DOM for seamless loop
- **Navbar scroll effect:** Vue composable `useScrollPosition` — watch `window.scrollY > 50`

---

## Test Strategy

### 🎯 Test Philosophy: E2E Smoke First

```
🔥 E2E Smoke Tests - PREFERRED: Prove features work for real users
📦 Unit Tests - FOR: Complex logic with many edge cases only
```

⚠️ **INTERLEAVING RULE:** Tests MUST be written immediately after their feature phase, NOT all at the end.
⚠️ **FRAMEWORK:** E2E uses **agent-browser** with **Page Object Model** (NOT Playwright).

### E2E Smoke Tests

| Scenario | File | Phase |
|---|---|---|
| Platform navbar renders: logo, links, CTA | `platform-navbar.test.ts` | After FR-1 |
| Navbar collapses on mobile, hamburger works | `platform-navbar.test.ts` | After FR-1 |
| Platform hero: headline + CTA visible | `platform-hero.test.ts` | After FR-2 |
| "Get Started" scrolls to #contact | `platform-hero.test.ts` | After FR-2 |
| 6 feature cards render with titles | `platform-features.test.ts` | After FR-3 |
| 3 pricing cards render, Pro highlighted | `platform-pricing.test.ts` | After FR-4 |
| Logo carousel section renders | `platform-carousel.test.ts` | After FR-5 |
| Contact form: valid submit → success message | `contact-form.test.ts` | After FR-6 |
| Contact form: invalid email → inline error | `contact-form.test.ts` | After FR-6 |
| Platform footer: copyright + columns visible | `platform-footer.test.ts` | After FR-7 |
| Club navbar: club name + Log in + Join Now | `club-navbar.test.ts` | After FR-8 |
| Club hero: club name H1 + Join Now CTA | `club-hero.test.ts` | After FR-9 |

### Unit Tests

| Scenario | File | Phase |
|---|---|---|
| MX record validation: valid domain passes | `test_validation.py` | After FR-6 |
| MX record validation: non-existent domain fails | `test_validation.py` | After FR-6 |
| MX record DNS timeout: fails open | `test_validation.py` | After FR-6 |
| Honeypot filled: returns 200, no email sent | `test_validation.py` | After FR-6 |
| Rate limit: 4th submission within 1hr returns 429 | `test_validation.py` | After FR-6 |
| Email task: correct subject and body format | `test_tasks.py` | After FR-6 |

### Regression Tests
- [ ] `tests/e2e/auth/login.test.ts` — login page still reachable via `/login` from club navbar

### Test Data Requirements
- Club fixture: `Organization(name="Springfield CC", slug="springfield-cc")` with `OrganizationConfig(primary_color="#E63946", logo_url="/fixtures/springfield-logo.svg")`
- Club fixture (no branding): `Organization(name="Barton FC", slug="barton-fc")` with `OrganizationConfig()` — no colour or logo

### Success Metrics
- Platform homepage Lighthouse performance score ≥ 85
- Contact form delivers email within 60 seconds of valid submission
- All 9 E2E smoke tests pass

---

## Open Questions

None.
