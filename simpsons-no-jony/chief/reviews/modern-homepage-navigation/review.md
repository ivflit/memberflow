# 🚔 Chief Wiggum PRD Review: Modern Responsive Homepage & Navigation

**PRD Location:** `simpsons-no-jony/ralph/todo/modern-homepage-navigation/prd.md`
**Review Date:** 2026-03-26
**Score:** 78/100
**Verdict:** 🟡 NEEDS WORK (70-84)

---

## 📊 Score Breakdown

| Category           | Score  | Max     | Notes |
| ------------------ | ------ | ------- | ----- |
| Safety Gates       | 12     | 20      | Per-WI gates missing; E2E smoke absent from backend WIs |
| Work Item Sizing   | 20     | 20      | All S or M — clean ✅ |
| E2E Test Placement | 17     | 20      | Well interleaved; minor gap on navbar (8 WIs before test) |
| Integration Gates  | 11     | 15      | WI-009-014 stretch is 6 items; no final gate after WI-021 |
| Work Item Quality  | 11     | 15      | All Notes present; NO TOAST warnings missing from UI WIs |
| Policy Compliance  | 7      | 10      | Testing requirements documented globally but not per-WI |
| **TOTAL**          | **78** | **100** | |

---

## 🔴 Critical Issues (Blocking)

### Issue 1: Safety Gates Not In Every Work Item's Acceptance Criteria

**Observation:** The PRD has a "Testing Requirements" section at the top that describes project-adapted check commands. However, individual WI acceptance criteria don't consistently include BOTH checks:

1. A lint/type check (`cd frontend && npm run check`)
2. An E2E smoke test run equivalent

| Work Item | Has check gate? | Has smoke gate? |
|-----------|----------------|-----------------|
| WI-001 | `pytest` only | ❌ No E2E gate |
| WI-002 | `pytest` only | ❌ No E2E gate |
| WI-003 | `pytest` only | ❌ No E2E gate |
| WI-004 | `pytest` only | ❌ No E2E gate |
| WI-005 | `pytest` only | ❌ No E2E gate |
| WI-006 | `npm run check` ✅ | ❌ No E2E gate |
| WI-007 | `npm run check` ✅ | ❌ No E2E gate |
| WI-008 through WI-014 | `npm run check` ✅ | ❌ No E2E gate |
| WI-015 through WI-022 | ❌ No check gate | `vitest run` ✅ |
| WI-023 | ❌ Neither | ❌ Neither |

**Required fix:** Every WI acceptance criteria must include BOTH:
- `docker compose exec api pytest` (backend gate, all WIs)
- `cd frontend && npm run check` (frontend gate, all WIs)

For WIs that touch user-facing code, additionally: `cd frontend && npx vitest run --config vitest.e2e.config.ts` (or `npm run test:e2e:smoke` if that script exists).

**Points Lost:** -8

---

### Issue 2: WI-009 through WI-014 Stretch Has No Intermediate Gate (6 Items)

**Observation:** After the "Platform Page Above Fold" gate following WI-008, the next gate doesn't appear until after WI-014 — a stretch of 6 work items (Features, Pricing, Carousel, Contact Form, Footer, Assembly). This exceeds the 3-5 item rule.

**Required fix:** Insert an additional gate after WI-011 (Carousel), e.g. "🚦 INTEGRATION GATE: Platform Sections Render" — verify Features, Pricing, and Carousel are all visible before proceeding to Contact Form and Footer.

**Points Lost:** -3

---

## 🟡 Warnings (Should Fix)

### Warning 1: NO TOAST Warnings Missing from All UI Work Items

**Observation:** The following UI work items have no `⚠️ NO TOAST:` note specifying how feedback is delivered:

| Work Item | UI Component | Missing |
|-----------|--------------|---------|
| WI-007 | PlatformNavbar.vue | ⚠️ NO TOAST |
| WI-008 | PlatformHero.vue | ⚠️ NO TOAST |
| WI-009 | PlatformFeatures.vue | ⚠️ NO TOAST |
| WI-010 | PlatformPricing.vue | ⚠️ NO TOAST |
| WI-011 | PlatformCarousel.vue | ⚠️ NO TOAST |
| WI-012 | PlatformContactForm.vue | ⚠️ NO TOAST |
| WI-013 | PlatformFooter.vue | ⚠️ NO TOAST |
| WI-014 | PlatformHomePage.vue | ⚠️ NO TOAST |
| WI-019 | ClubNavbar.vue | ⚠️ NO TOAST |
| WI-020 | ClubHero.vue | ⚠️ NO TOAST |

**Note:** WI-012 (Contact Form) is especially important — the spec correctly says the success state REPLACES the form (not a toast). This should be explicit in Notes: `⚠️ NO TOAST: Success state replaces the form with a message. Never use a toast notification for form submission feedback.`

**Points Lost:** -4

---

### Warning 2: No Final Integration Gate After WI-021

**Observation:** WI-021 (Club E2E), WI-022 (Regression), and WI-023 (Architecture) have no final gate. Ralph could mark WI-023 complete without confirming the full feature works end-to-end.

**Suggestion:** Add a final gate after WI-022: "🚦 INTEGRATION GATE: Feature Complete" — run all E2E tests, verify both platform and club pages, confirm architecture docs are accurate.

**Points Lost:** -2

---

## ✅ Verified Sections

- ✅ **Work Item Sizing:** All 23 WIs are S or M — zero L or XL. Clean.
- ✅ **Dependency Order:** Backend (WI-001-005) → Frontend Foundation (WI-006-007) → Platform UI (WI-008-014) → Platform E2E (WI-015-018) → Club UI (WI-019-020) → Club E2E (WI-021-022) → Docs (WI-023). Correct.
- ✅ **E2E Tests Interleaved:** Platform E2E tests (WI-015-018) follow immediately after platform assembly (WI-014); Club E2E (WI-021) follows club UI (WI-020).
- ✅ **Integration Gates Present:** 5 gates with numbered verification steps, evidence requirements, and "If gate fails" instructions.
- ✅ **All Notes Sections Complete:** Every WI has Pattern + Reference + Hook point. Actionable.
- ✅ **Status Tracking Consistent:** All WIs marked `❌ Not started`.
- ✅ **Test Work Items Correct Type:** E2E for UI features, Unit for complex validation logic (MX check, honeypot, rate limiting) — correct philosophy applied.
- ✅ **No L/XL Items:** Full compliance with sizing rules.

---

## 🧠 Chief's Checklist

1. ❓ **SAFETY GATES: Every WI has check gate in acceptance criteria?** — No; E2E test WIs missing `npm run check`; backend WIs missing frontend check
2. ❓ **SAFETY GATES: Every WI has smoke test gate in acceptance criteria?** — No; most WIs missing explicit E2E smoke command
3. ✅ All work items S or M effort?
4. ✅ E2E infrastructure exists before UI work items?
5. ✅ E2E tests interleaved (not bunched at end)?
6. ❓ Integration gate every 3-5 work items? — WI-009-014 stretch is 6 items
7. ✅ All work items have Notes with Pattern + Hook point?
8. ❓ All UI work items have NO TOAST warning? — Missing on all 10 UI WIs
9. ✅ Dependency order correct (API before UI)?
10. ✅ Testing requirements section at top?
11. ✅ Phase 10 is NOT "E2E Tests"? — Tests correctly interleaved
12. ✅ Work items numbered sequentially (WI-001 through WI-023)?

---

## 📝 Action Items for Bart

Before Ralph can execute (to reach 85+ points):

- [ ] **Issue 1 (+8 pts):** Add `docker compose exec api pytest` AND `cd frontend && npm run check` to EVERY WI's acceptance criteria. Add E2E smoke command to WIs that touch user-facing functionality (WI-006 through WI-020).
- [ ] **Issue 2 (+3 pts):** Insert intermediate integration gate between WI-011 and WI-012 — "Platform Sections Render" gate covering Features, Pricing, Carousel.
- [ ] **Warning 1 (+4 pts):** Add `⚠️ NO TOAST:` to Notes of all 10 UI WIs. WI-012 must explicitly state: success replaces form, no toast.
- [ ] **Warning 2 (+2 pts):** Add final integration gate "Feature Complete" after WI-022.

---

## Summary

**Current Score: 78/100** | **Target: 85+**

Solid PRD with correct sizing, good dependency ordering, and well-interleaved tests. The main issues are structural: safety gates are defined globally but not repeated per-WI as required, NO TOAST warnings are missing from all UI work items, and one section stretches to 6 items without a gate. These are mechanical fixes — content quality is high.

**Chief says:** "Looks like we got ourselves a code crime in progress. Not a bad one — more like jaywalking than grand larceny. Bart, fix those safety gates and toast warnings and I'll clear it."

PRD rejected. Back to Bart for fixes.
