# 🔍 Marge QA Review: User Authentication (Re-review)

**Spec Location:** `simpsons-no-jony/lisa/features/user-authentication/spec.md`
**Review Date:** 2026-03-24
**Score:** 96/100
**Verdict:** 🟢 APPROVED (90+)

---

## 📊 Score Breakdown

| Category                    | Score  | Max     | Notes |
|-----------------------------|--------|---------|-------|
| Functional Clarity          | 30     | 30      | Given/When/Then ACs present for every FR; inputs/outputs/errors complete |
| Technical Specificity       | 23     | 25      | Rate limiting specified; email content defined; minor: Celery task failure retry not described |
| Implementation Completeness | 25     | 25      | 13 edge cases; all error messages specific; token invalidation rule defined |
| Business Context            | 18     | 20      | Clear problem statement; auth infra has no measurable KPIs — acceptable |
| **TOTAL**                   | **96** | **100** | |

---

## 📋 Structural Audit

| Section             | Status | Notes |
|---------------------|--------|-------|
| Problem Statement   | ✅     | Concrete, no solution language |
| Scope               | ✅     | In/Out explicit; six items explicitly out of scope |
| Requirements        | ✅     | FR-1 through FR-9 with inputs/outputs/errors |
| Acceptance Criteria | ✅     | Given/When/Then for every FR — all measurable and unambiguous |
| Data Model          | ✅     | `UserInvitation` and `PasswordResetToken` fully typed; existing models noted |
| API Contracts       | ✅     | All 8 endpoints with methods, request/response, error codes |
| UX Flow             | ✅     | Numbered steps for all 5 flows |
| Edge Cases          | ✅     | 13 cases including new ones (multiple reset tokens, no-token URL) |
| E2E Test Strategy   | ✅     | Interleaving rule present; E2E/Unit split justified; phases mapped |
| Open Questions      | ✅     | Empty |

---

## 🟡 Minor Observations (Not Blocking)

### Observation 1: Celery Email Task Failure — Not Specified

**Location:** Implementation Patterns → Invite/reset email
**Observation:** The spec states emails are queued via Celery but does not specify what happens if the email task fails (e.g. SMTP unavailable). Does the invite still get created? Is there a retry? Does the admin see an error? This is a low-risk gap since Celery retry behavior is defined at the platform level, but Bart may want to note it in the work item.
**Recommendation:** Add a one-liner: "Email task uses Celery default retry (3 attempts, 60s backoff). Invite/reset token is persisted regardless of email delivery — admin can resend."
**Points Lost:** 2 (already accounted for in score)

---

## 🟢 Verified Sections

- ✅ **Given/When/Then ACs**: Every FR has at least one AC covering happy path and at least one covering an error state — all are specific and pass/fail unambiguous
- ✅ **Rate limiting**: Login throttled at 10 req/min, reset at 5 req/min — both specified on the relevant FRs
- ✅ **Multiple reset tokens**: FR-6 Behaviour now explicitly states previous unused token is invalidated before new one is created; AC-3 verifies this
- ✅ **Email content**: Subject and body template defined for both invite and reset emails; `{org.name}` and `{link}` placeholders named
- ✅ **No-token edge case**: Added to both Edge Cases table and FR-9 AC — "This link is invalid. Request a new invitation or password reset."
- ✅ **Interleaving rule**: `⚠️ INTERLEAVING RULE` warning present in Test Strategy header with framework note
- ✅ **Security posture**: No-enumeration on both login and forgot-password; single-use tokens; tenant-scoped credential lookup
- ✅ **Tenant isolation**: Cross-tenant login AC explicitly tested; invite token cross-tenant isolation in unit tests
- ✅ **Token storage**: Access in Pinia memory, refresh in localStorage `mf_refresh_token` — matches architecture
- ✅ **Shared Set Password page**: `?mode=invite|reset` pattern avoids page duplication; both modes have ACs

---

## 🧠 Health Check Questions

1. ✅ Does the problem statement avoid solution language?
2. ✅ Could someone unfamiliar understand the need?
3. ✅ Can each requirement be tested? — Yes, Given/When/Then ACs are specific
4. ✅ Are all assumptions explicitly stated?
5. ✅ Is scope achievable with stated constraints?
6. ✅ Is "out of scope" explicitly listed?
7. ✅ Does it avoid "what I know how to build" bias?
8. ✅ If this failed, is the likely reason documented?
9. ✅ Does each FR have measurable acceptance criteria?
10. ✅ Is E2E test strategy defined with interleaving rule?
11. ✅ Does each FR specify its E2E test file?

---

## Summary

**Score: 96/100** | **Target: 90+**

All six issues from the first review have been resolved cleanly. The spec is thorough, unambiguous, and ready for PRD generation. The single minor observation (Celery email task retry behaviour) is low-risk and can be addressed in a work item note rather than requiring a spec change.

**This spec is approved for PRD generation.**

`@bart create prd simpsons-no-jony/lisa/features/user-authentication/spec.md`
