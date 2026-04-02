# Chief Review — user-dob-address PRD

**PRD:** `simpsons-no-jony/ralph/todo/user-dob-address/prd.md`
**Reviewed:** 2026-04-01
**Score: 71 / 100**
**Result: ❌ FAIL — return to Bart for revision**

Threshold is 85. Three structural violations must be fixed before this PRD reaches Ralph.

---

## What the PRD does well

- **Sizing:** All 13 work items are S or M. No L or XL. ✅
- **Notes quality:** Every WI has Pattern, Reference, and Hook point. ✅
- **Acceptance criteria:** Specific and verifiable throughout. ✅
- **Codebase context block:** Names exact files, flags missing app and missing permission — Ralph won't be surprised. ✅
- **Gate verification steps:** Concrete, observable, require written evidence. ✅
- **Tenant isolation in admin WIs:** WI-004, WI-005, WI-006 each include isolation tests in their acceptance criteria. ✅

---

## Violations that must be fixed

### VIOLATION 1 — E2E tests are bunched at the end (-18 pts)

This is an explicit rule in CLAUDE.md:

> *"E2E tests are interleaved, not bunched at the end. A test work item follows immediately after the feature phase it covers."*

WI-013 is a single E2E test work item placed after all 12 other work items. It bundles tests for three entirely separate phases: backend admin API, member-facing profile flow, and auth flows. This defeats the purpose of interleaving — if the admin API is broken, Ralph won't find out until WI-013, long after building the frontend.

**Required fix:** Split WI-013 into at minimum two test WIs placed immediately after the phase they cover:

- **WI-008b (new):** Backend API E2E tests — placed after Gate 2 (admin API verified), covering: admin list `age` field, admin detail DOB/address, export CSV format, staff 403 on export
- **WI-013 (revised):** Frontend E2E tests — placed after Gate 4 (frontend verified), covering: profile page persist/clear, registration flow, invite acceptance flow

The backend unit/isolation tests in current WI-008 are correctly placed. Only the E2E layer is misaligned.

---

### VIOLATION 2 — Gate 3 covers only 2 work items (-7 pts)

CLAUDE.md requires: *"Integration gates every 3–5 items."*

Gate 3 sits between WI-007 and Gate 3, covering only WI-007 + WI-008 (2 items). This is below the minimum of 3.

**Required fix:** Either:
- a) Merge WI-007 into the admin phase (move it before Gate 2, making Gate 2 cover WI-004 + WI-005 + WI-006 + WI-007 = 4 items), then drop Gate 3 and renumber, OR
- b) Move WI-008 (backend tests) to before Gate 3, then use Gate 3 to cover WI-007 + WI-008 + backend E2E (new) = 3 items

Option (b) fits naturally if VIOLATION 1 is also fixed by splitting WI-013.

---

### VIOLATION 3 — No ARCHITECTURE.md update work item (-10 pts)

CLAUDE.md states: *"If a feature changes the architecture, Bart adds a work item to update `about/ARCHITECTURE.md`."*

This PRD introduces structural architectural changes:
- Creates `apps/admin_portal` — a new Django app not currently in the architecture diagram
- Creates `IsPlatformAdmin` permission — currently missing from `core/permissions.py` despite being documented
- Introduces platform admin API endpoints (`/api/v1/platform/`) — not present in the URL pattern table in ARCHITECTURE.md

A work item must be added to update `about/ARCHITECTURE.md` to reflect these additions.

---

## Minor observations (not blocking, Bart should note)

- **WI-007 — cross-tenant test missing from the WI itself:** WI-008 covers the platform admin isolation test globally, but WI-007's own acceptance criteria has no isolation or permission test. Since WI-007 is where the endpoint is built, it should verify that a non-platform-admin token returns 403. Currently the only criterion is `pytest` passes — Ralph won't know what to test for until WI-008. Add one criterion: `Non-platform-admin token returns HTTP 403` (this is already in the description but not in the AC checklist).

- **WI-011 — authStore.register() pass-through unverified:** The hook point note says "it likely does via spread or direct pass-through" — this is a guess. Bart should read `frontend/src/stores/auth.js` and confirm the register call signature before writing this note. If `authStore.register()` only passes named fields, Ralph will need to update the store too, which would be an unlisted task.

---

## Required actions for Bart

1. Split WI-013 into two interleaved test WIs — one after Gate 2 (backend E2E), one after Gate 4 (frontend E2E).
2. Adjust gate boundaries so Gate 3 covers at least 3 work items.
3. Add a new WI to update `about/ARCHITECTURE.md` (S effort, placed at or near the end).
4. Add the 403 permission test to WI-007's acceptance criteria checklist.
5. Verify `authStore.register()` signature and update the WI-011 hook point note accordingly.
