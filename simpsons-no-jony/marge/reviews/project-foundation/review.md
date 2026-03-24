# 🔍 Marge QA Review: Project Foundation

**Spec Location:** `simpsons-no-jony/lisa/features/project-foundation/spec.md`
**Review Date:** 2026-03-24
**Score:** 92/100
**Verdict:** 🟢 APPROVED (90+)

---

## 📊 Score Breakdown

| Category | Score | Max | Notes |
|---|---|---|---|
| Functional Clarity | 26 | 30 | Missing per-FR Given/When/Then; user not explicitly named |
| Technical Specificity | 20 | 25 | CORS origins unspecified; VITE URL Docker ambiguity; SECRET_KEY absent |
| Implementation Completeness | 23 | 25 | Minor entrypoint retry inconsistency; slug validation unstated |
| Business Context | 13 | 20 | Problem statement uses solution language; no success metrics |
| **Subtotal** | **82** | **100** | |
| AC Bonus | +10 | +15 | Strong test strategy; missing per-FR Given/When/Then |
| **TOTAL** | **92** | **115** | |

---

## 📋 Structural Audit

| Section | Status | Notes |
|---|---|---|
| Problem Statement | 🟡 | Present but uses solution language |
| Scope | ✅ | In/Out clearly defined |
| Requirements | ✅ | FR-1 through FR-9 with Input/Output/Errors |
| Acceptance Criteria | 🟡 | Test Strategy present; no per-FR Given/When/Then |
| Data Model | ✅ | Organization model fully typed with constraints |
| API Contracts | ✅ | Health endpoint with all response shapes |
| UX Flow | ✅ | Step-by-step developer flow, numbered |
| Edge Cases | ✅ | Table format, 6 cases covered |
| E2E Test Strategy | ✅ | Interleaving rule stated; test phases mapped to FRs |
| Open Questions | ✅ | Empty |

---

## 🟡 Warnings (Should Fix Before Bart Writes PRD)

### Warning 1: Problem statement uses solution language

**Location:** Problem Statement section
**Quote:** *"the project needs a working full-stack skeleton: a Django backend and Vue.js frontend running together in Docker"*
**Problem:** This describes the solution, not the problem. Marge's rule: problem statements describe the need, not what to build.
**Required:** Rewrite as: *"Developers cannot begin building features because no runnable project environment exists. Every feature spec has no codebase to land in."*
**Points Lost:** -4 (Business Context)

---

### Warning 2: VITE_API_BASE_URL is ambiguous in Docker context

**Location:** FR-8, `.env.development` value
**Quote:** *"`VITE_API_BASE_URL=http://localhost:8000`"*
**Problem:** This is a real implementation trap. Vite environment variables are baked into the browser bundle at build time. The frontend container and the browser are different network contexts:
- Inside the Docker network: the API is reachable at `http://api:8000`
- In the browser: the API is reachable at `http://localhost:8000`

If the Docker `frontend` service tries to proxy API calls through Vite's dev server, `localhost:8000` works. If it calls the API directly from the browser, `localhost:8000` works because port is exposed. But the spec must be explicit about which approach is used — otherwise Bart will guess.
**Required:** Specify one of:
- A) Browser calls `http://localhost:8000` directly (api port must be exposed in compose)
- B) Vite dev server proxies `/api/` to `http://api:8000` (no CORS needed in dev)
**Points Lost:** -2 (Technical Specificity)

---

### Warning 3: CORS configuration not specified

**Location:** FR-1, package list includes `django-cors-headers`
**Problem:** The package is listed but the configuration is not specified. Which origins are allowed in development? `http://localhost:5173`? All origins? This affects whether the frontend can reach the backend without browser errors.
**Required:** Add to FR-1 or a new FR: *"In development, `CORS_ALLOWED_ORIGINS = ['http://localhost:5173']`."*
**Points Lost:** -2 (Technical Specificity)

---

### Warning 4: SECRET_KEY and ALLOWED_HOSTS not mentioned

**Location:** FR-1, settings split description
**Problem:** `SECRET_KEY` and `ALLOWED_HOSTS` are required Django settings. The spec says settings are split across three files but doesn't specify how `SECRET_KEY` is handled (env var via `python-decouple`?) or what `ALLOWED_HOSTS` contains in development (`['*']`? `['localhost']`?). Bart needs to know this to write the settings files correctly.
**Required:** Add one line to FR-1: *"`SECRET_KEY` read from env via `python-decouple`. `ALLOWED_HOSTS = ['*']` in development."*
**Points Lost:** -1 (Technical Specificity)

---

### Warning 5: No success metrics

**Location:** Business Context — missing section
**Problem:** The spec never states how we know the foundation is complete and working. "Docker compose up and the frontend renders the health check response" is implied by FR-6 + FR-8 but never stated as the definition of done.
**Required:** Add a one-line success metric: *"Success: `docker compose up` starts all services, `GET /api/v1/health/` returns 200 with `{"status": "ok", "tenant": "test-club"}`, and the Vue home view renders that response without errors."*
**Points Lost:** -3 (Business Context)

---

### Warning 6: No per-FR Given/When/Then acceptance criteria

**Location:** All FR sections
**Problem:** FRs have Input/Output/Errors (good) but no formal Given/When/Then acceptance criteria. The Test Strategy compensates partially with a scenario list, but Bart's work item acceptance criteria will be weaker without formal AC to reference.
**Required:** Each FR needs at minimum one Given/When/Then. Example for FR-2:
```
Given: DEBUG=True and request has header X-Tenant-Slug: test-club
When: GET /api/v1/health/ is called
Then: response is 200 {"status": "ok", "tenant": "test-club"}
```
**Points Lost:** -4 (Functional Clarity, partially offset by AC bonus)

---

## 🔴 Critical Issues

None. No blocking issues found.

---

## ✅ Verified Sections

- ✅ **Scope:** In/Out boundary is unambiguous. 9 things explicitly out of scope.
- ✅ **FR-2 (Middleware):** Resolution logic specified with exact code pattern. Both dev and production paths defined.
- ✅ **FR-7 (seed_dev):** Idempotency requirement explicit. `get_or_create` specified. Auto-run on container start specified.
- ✅ **FR-6 (Health check):** All three response shapes documented (200, 404, 400).
- ✅ **Edge cases:** DB not ready retry, seed idempotency, inactive org, missing env var — all covered.
- ✅ **Implementation Patterns:** Four concrete code patterns provided. Bart can reference these directly in work item Notes.
- ✅ **Test Strategy:** Interleaving rule stated. Test type per FR justified. Specific test files named. No E2E tests bunched at end.
- ✅ **Docker services:** Four services defined, three excluded with explicit rationale.
- ✅ **Open Questions:** Empty. No ambiguity left unresolved.

---

## 🧠 Health Check Questions

1. ✅ Does the problem statement avoid solution language? — 🟡 Partially (flagged in Warning 1)
2. ✅ Could someone unfamiliar understand the need? — Yes
3. ✅ Can each requirement be tested? — Yes, test scenarios are specific and file-named
4. ✅ Are all assumptions explicitly stated? — 🟡 Most are; CORS and VITE URL are implicit (flagged)
5. ✅ Is scope achievable with stated constraints? — Yes, this is a straightforward scaffold
6. ✅ Is "out of scope" explicitly listed? — Yes, 9 items
7. ✅ Does it avoid "what I know how to build" bias? — Yes
8. ✅ If this failed, is the likely reason documented as a risk? — DB not ready is covered; partial
9. ✅ Does each FR have measurable acceptance criteria? — 🟡 Input/Output/Errors yes; Given/When/Then no
10. ✅ Is E2E test strategy defined with interleaving rule? — Yes
11. ✅ Does each FR specify its test type with justification? — Yes, table format in Test Strategy

---

## 📝 Action Items

The spec is approved for PRD generation. These warnings are passed to Bart as known gaps — he should account for them in work item Notes:

- [ ] **Warning 2 (VITE URL):** Bart must decide: browser calls API directly (port exposed) vs Vite proxy. Add a work item Note on this decision.
- [ ] **Warning 3 (CORS):** Bart's settings work item must include `CORS_ALLOWED_ORIGINS = ['http://localhost:5173']` in `development.py`.
- [ ] **Warning 4 (SECRET_KEY):** Bart's settings work item must include `SECRET_KEY` via `python-decouple` and `ALLOWED_HOSTS = ['*']` in development.

Warnings 1, 5, and 6 are quality improvements for future specs — they do not block this PRD.

---

## Summary

**Score: 92/100** | **Target: 90+** | **🟢 APPROVED**

Strong spec. Nine functional requirements with code patterns, clear edge cases, and a well-structured test strategy. The main weaknesses are a solution-forward problem statement, two unresolved implementation specifics (CORS config and Vite/Docker URL context), and the absence of Given/When/Then per FR. None of these are blockers — Bart must absorb the CORS and VITE URL decisions into the relevant work item Notes.

**Marge says:** "It's not perfect, but it's the most complete foundation spec I've seen all week. Send it to Bart."
