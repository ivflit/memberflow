# 🔍 Marge QA Review: Modern Responsive Homepage & Navigation

**Spec Location:** `simpsons-no-jony/lisa/features/modern-homepage-navigation/spec.md`
**Review Date:** 2026-03-26
**Score:** 76/100
**Verdict:** 🟡 NEEDS WORK (70-89)

---

## 📊 Score Breakdown

| Category                    | Score  | Max     | Notes |
| --------------------------- | ------ | ------- | ----- |
| Functional Clarity          | 21     | 30      | No Given/When/Then AC format; CTA destinations unspecified |
| Technical Specificity       | 19     | 25      | Icon library missing; TenantMiddleware root domain underspecified; CSRF gap |
| Implementation Completeness | 20     | 25      | Frontend validation flow missing; MX check misconception |
| Business Context            | 16     | 20      | Good problem statement; no measurable success metrics |
| **SUBTOTAL**                | **76** | **100** | |
| Interleaving rule penalty   | -5     | —       | Missing explicit ⚠️ INTERLEAVING RULE statement |
| **TOTAL**                   | **71** | **100** | |

---

## 📋 Structural Audit

| Section             | Status | Notes |
| ------------------- | ------ | ----- |
| Problem Statement   | ✅     | Concrete, avoids solution language |
| Scope               | ✅     | Both IN and OUT explicitly listed |
| Requirements        | ✅     | FR-1 through FR-9 present |
| Acceptance Criteria | 🔴     | No Given/When/Then format for any FR — test file references are not AC |
| Data Model          | ✅     | Correctly states no new models; references existing fields |
| API Contracts       | ✅     | Single endpoint with request/response/errors documented |
| UX Flow             | ✅     | Numbered steps present for both page types |
| Edge Cases          | ✅     | Table format, 7 cases covered |
| E2E Test Strategy   | 🟡     | Phases mapped but ⚠️ INTERLEAVING RULE statement missing |
| Open Questions      | ✅     | Empty |

---

## 🔴 Critical Issues (Blocking)

### Issue 1: No Acceptance Criteria in Given/When/Then Format

**Location:** All FRs (FR-1 through FR-9)
**Quote:** `"Test: tests/e2e/homepage/platform-navbar.test.ts — renders desktop and mobile navbar, CTA present"`
**State:** RS2 — Vague Needs (test file references are not acceptance criteria)
**Problem:** Every FR has a test file pointer but zero Given/When/Then acceptance criteria. A test file name does not tell an implementer what "passing" looks like. Bart will not be able to write verifiable work items without these.
**Required:** Each FR needs at minimum one AC block, e.g.:
```
Given: User navigates to memberflow.com
When: The page loads
Then: A fixed navbar is visible with logo, Features/Pricing/Contact links, and a "Get Started" button
```
**Points Lost:** -6

---

### Issue 2: "Get Started" CTA Destination Unspecified

**Location:** FR-1 (Navbar), FR-2 (Hero)
**Quote:** `'"Get Started" CTA button right'` and `'"Get Started" CTA button'`
**State:** RS3 — Hidden Constraint
**Problem:** Both the navbar and hero have a "Get Started" CTA but nowhere in the spec does it say where this button links. Does it scroll to the contact form? Link to an external URL? Open a modal? This will cause an implementation decision to be made without product input.
**Required:** Specify the destination: e.g. "scrolls to the #contact section on the same page" or "links to /contact"
**Points Lost:** -3

---

### Issue 3: Icon Library for Feature Cards Unspecified

**Location:** FR-3
**Quote:** `"Each card: icon, title, one-line description"`
**State:** RS3 — Hidden Constraint
**Problem:** No icon library is specified. The implementer will have to choose between Font Awesome, Heroicons, Material Icons, Lucide, or inline SVGs. This is a real implementation blocker — picking the wrong one means a rework or an unwanted dependency.
**Required:** Specify the icon library (e.g. "Use Heroicons via `@heroicons/vue`") OR specify that icons are inline SVGs.
**Points Lost:** -3

---

### Issue 4: TenantMiddleware Root Domain Handling Unspecified

**Location:** Edge Cases table
**Quote:** `"memberflow.com visited (no tenant) | Platform marketing page renders; TenantMiddleware must not 404 on root domain"`
**State:** RS3 — Hidden Constraint
**Problem:** The edge case acknowledges this is a problem but doesn't specify the solution. The current `TenantMiddleware` resolves tenant from subdomain — if `memberflow.com` has no subdomain, what does the middleware do? Does it set `request.tenant = None` and pass through? Does it check for a whitelist of non-tenant domains? Does a new middleware branch handle this? This is an architectural decision, not just a frontend routing concern — it affects the backend too.
**Required:** Specify the exact middleware behaviour: e.g. "If subdomain is `www` or absent, set `request.tenant = None` and continue — do not raise 404. Only tenant-scoped views enforce non-null tenant."
**Points Lost:** -4

---

### Issue 5: MX Record Check Does NOT Block `test@gmail.com`

**Location:** FR-6
**Quote:** `"Email: domain must have valid MX records (checked server-side to block fake submissions like test@gmail.com)"`
**State:** RS2 — Vague Needs (misunderstands what MX check does)
**Problem:** `gmail.com` has valid MX records. An MX check will NOT block `test@gmail.com`, `fake@gmail.com`, or any `@gmail.com` address. The MX check only blocks completely invented domains like `test@notrealdomain12345.com`. The spec's stated justification is factually incorrect, which means the requirement may be misspecified. Either the intent is correct (block non-existent domains) and the example is wrong, or the intent is something else entirely.
**Required:** Correct the spec: "MX record check blocks submissions from non-existent email domains (e.g. `user@fakeDomain123.com`). It does NOT filter disposable email services or specific providers — that is out of scope."
**Points Lost:** -3

---

## 🟡 Warnings (Should Fix)

### Warning 1: Test Strategy Missing Explicit Interleaving Rule Statement

**Location:** Test Strategy section
**Observation:** The table maps tests to "After FR-X" phases, which is good. But the explicit `⚠️ INTERLEAVING RULE: Tests MUST be written immediately after their feature phase, NOT all at end` statement is absent. Bart reads this spec — without the explicit statement, there is a real risk the PRD bunches all E2E tests at the end.
**Required:** Add the explicit interleaving rule statement before the test table.
**Points Lost:** -5 (already applied above)

---

### Warning 2: Frontend Validation Behaviour Not Specified

**Location:** FR-6
**Observation:** The spec thoroughly defines server-side validation but says nothing about frontend behaviour. Does the form validate on submit only? On blur (field by field)? Are error messages shown inline below each field or in a toast? The server returns a 400 with field-level errors — does the frontend parse these and display them under the relevant fields?
**Suggestion:** Add: "Frontend validates on submit. On 400 response, parse field errors and display inline below each input. On 429, display a dismissable banner: 'Too many requests. Please try again later.'"
**Points Lost:** -2

---

### Warning 3: No Success Metrics Defined

**Location:** Business Context / Problem Statement
**Observation:** The problem is well-stated but there are no measurable success criteria. What does "done" look like beyond the code shipping? E.g. "Platform homepage loads in < 2s on 3G", "Contact form receives at least one real submission", "Lighthouse score > 90".
**Suggestion:** Add a lightweight success metric: e.g. "Homepage passes Lighthouse performance score ≥ 85, contact form delivers email within 60 seconds of submission."
**Points Lost:** -2

---

### Warning 4: `tenantStore.hasTenant` Property Assumed to Exist

**Location:** Implementation Patterns
**Quote:** `"check tenantStore.hasTenant (set during bootstrap from /api/v1/config/)"`
**Observation:** This property is assumed to exist on the tenant store but is never defined in the spec. If it doesn't exist today, this is an undocumented dependency that Bart won't know to add.
**Suggestion:** Either confirm this property exists in the current tenant store or add it as an explicit requirement: "Add `hasTenant` computed property to tenant store: returns `true` if `config` is not null."
**Points Lost:** -1

---

### Warning 5: Reduced Motion Accessibility Not Addressed

**Location:** FR-3, FR-5 (animations), Logo Carousel
**Observation:** The spec specifies AOS animations and a CSS `@keyframes scroll` carousel. Neither mentions `prefers-reduced-motion` media query support. Users with vestibular disorders can be harmed by constant motion. This is a basic accessibility requirement.
**Suggestion:** Add: "All CSS animations and AOS transitions must respect `@media (prefers-reduced-motion: reduce)` — pause carousel, disable AOS transitions."
**Points Lost:** -1

---

## 🟢 Verified Sections

- ✅ **Problem Statement:** Concrete, no solution language, identifies both user types
- ✅ **Scope:** Clean in/out split, membership tiers correctly deferred
- ✅ **FR-6 Honeypot:** Silent 200 on filled honeypot — correct anti-detection behaviour
- ✅ **FR-6 Rate Limiting:** 3 req/hr per IP, Django cache-based — specific and implementable
- ✅ **FR-6 Email Task:** Async Celery pattern correctly specified; fire-and-forget with retry
- ✅ **FR-4 Pricing:** Placeholder pricing with progressive feature sets clearly structured
- ✅ **Edge Cases:** Root domain, branding fallbacks, SMTP failure all covered
- ✅ **Data Model:** Correctly identifies no new models needed; existing fields referenced
- ✅ **API Contract:** POST /api/v1/contact/ has 200, 400, 429 responses all typed
- ✅ **Test Philosophy:** E2E smoke tests correctly preferred; Unit tests justified for complex validation logic only

---

## 🧠 Health Check Questions

1. ✅ Does the problem statement avoid solution language?
2. ✅ Could someone unfamiliar understand the need?
3. ❓ Can each requirement be tested? — FR-1 through FR-9 have test files but no formal AC; unclear what "passing" means
4. ❓ Are all assumptions explicitly stated? — `tenantStore.hasTenant`, icon library, CTA destination all assumed
5. ✅ Is scope achievable with stated constraints?
6. ✅ Is "out of scope" explicitly listed?
7. ✅ Does it avoid "what I know how to build" bias?
8. ❓ If this failed, is the likely reason documented as a risk? — No risk section; TenantMiddleware root domain change is a real risk
9. ❓ Does each FR have measurable acceptance criteria? — No, test file pointers only
10. 🟡 Is E2E test strategy defined with interleaving rule? — Partially; phases mapped but rule not stated
11. ✅ Does each FR specify its E2E test file?

---

## 📝 Lisa Re-engagement Required

**Spec:** `simpsons-no-jony/lisa/features/modern-homepage-navigation/spec.md`
**Score:** 71/100 (Target: 90+)
**Verdict:** 🟡 NEEDS WORK

### Issues for Lisa to Resolve (via user interview)

| # | Issue | Type | Question for User |
|---|-------|------|-------------------|
| 1 | All FRs missing Given/When/Then AC | Requirement Gap | Lisa to add AC blocks to each FR (no user input needed — spec author task) |
| 2 | "Get Started" CTA destination | Hidden Constraint | "When a visitor clicks 'Get Started' on the platform homepage, where should they go — scroll to the contact form on the same page, or navigate to a separate /contact page?" |
| 3 | Icon library for feature cards | Hidden Constraint | "Which icon library should we use for the 6 feature cards — Heroicons, Font Awesome, or something else?" |
| 4 | TenantMiddleware root domain | Architecture Gap | "When someone visits memberflow.com (no subdomain), how should the backend middleware behave — silently pass through with no tenant, or is there a special domain allowlist needed?" |
| 5 | MX record check clarification | Factual Error | Lisa to correct the spec: MX check blocks fake domains, not gmail.com addresses — no user input needed |
| 6 | Frontend form validation UX | Missing Detail | "When the contact form has errors, should they appear inline under each field (on submit), or in a banner at the top?" |

### Re-review Trigger

Once Lisa updates the spec with resolved issues:
`@marge review spec simpsons-no-jony/lisa/features/modern-homepage-navigation/spec.md`

---

## Summary

**Current Score: 71/100** | **Target: 90+**

The spec has a solid foundation — clear problem statement, good scope definition, well-specified contact form security, and correct test philosophy. The main gap is structural: **no Given/When/Then acceptance criteria exist for any of the 9 FRs**, which means Bart cannot write verifiable work items. Several hidden constraints also need resolving: the CTA destination, icon library choice, and TenantMiddleware root domain behaviour. Fix these and the spec should clear 90+.

This spec is not ready for PRD. Address the critical issues above.
