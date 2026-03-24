# 🚔 Chief Wiggum PRD Review: User Authentication

**PRD Location:** `simpsons-no-jony/ralph/todo/user-authentication/prd.md`
**Review Date:** 2026-03-24
**Score:** 93/100
**Verdict:** 🟢 CLEARED (85+)

---

## 📊 Score Breakdown

| Category           | Score  | Max     | Notes |
|--------------------|--------|---------|-------|
| Safety Gates       | 18     | 20      | pytest + npm run check adapted correctly; WI-001/004/029 lack explicit check gate (acceptable for scaffold/config/doc WIs) |
| Work Item Sizing   | 20     | 20      | All 29 WIs are S or M — zero L or XL found |
| E2E Test Placement | 20     | 20      | Tests correctly interleaved; WI-023 follows login/register pages; WI-026-028 follow Set Password page |
| Integration Gates  | 15     | 15      | 7 well-structured gates; all have numbered steps, evidence requirement, and "if fails" instruction |
| Work Item Quality  | 15     | 15      | Every WI has Pattern + Reference + Hook point in Notes |
| Policy Compliance  | 5      | 10      | NO TOAST warnings missing from Notes on 8 UI WIs; intent captured in ACs but convention not followed |
| **TOTAL**          | **93** | **100** | |

---

## 🔴 Critical Issues (Blocking)

None. No L/XL items. No E2E tests bunched at end.

---

## 🟡 Warnings (Should Fix)

### Warning 1: `⚠️ NO TOAST:` missing from UI work item Notes

**Affected WIs:** WI-021, WI-022, WI-023, WI-024, WI-025, WI-026, WI-027, WI-028

The intent is correctly captured in acceptance criteria (WI-021 says "not an alert/toast", WI-022 implies inline errors), but the `⚠️ NO TOAST:` line must also appear in each UI work item's **Notes** section so Ralph sees it at the point he's about to write code, not just buried in the ACs.

**Required addition** to Notes of each affected WI:
```
⚠️ NO TOAST: Display all errors inline (below the relevant field or form). Never use browser alerts, confirm dialogs, or toast/snackbar notifications.
```

**Points Lost:** -5 (capped at NO TOAST allocation)

### Warning 2: WI-001, WI-004, WI-029 — no check gate in acceptance criteria

- WI-001 (scaffold): has `manage.py check` but not `pytest` — acceptable since no tests exist yet
- WI-004 (settings config): has migration check but not `pytest` — minor gap
- WI-029 (architecture doc): no check gate — acceptable for a doc-only WI

These are edge cases, not violations. Noted for awareness, not blocking.

---

## ✅ Verified Sections

- ✅ **Work item sizing**: 12 S items + 17 M items — zero L or XL. Clean.
- ✅ **E2E interleaving**: WI-023 (register/login E2E) immediately follows WI-022 (register page). WI-026-028 immediately follow WI-025 (Set Password page, their last dependency). Correct.
- ✅ **Integration gates**: 7 gates across 29 WIs — average ~4 WIs per gate. Gate verifications are specific (exact curl commands, DB inspection steps). All have evidence requirements.
- ✅ **Notes quality**: Every WI has all three fields. Hook points are specific file paths and function names.
- ✅ **Dependency order**: models → settings → serializers/views → frontend stores → router → pages → tests → docs. Correct throughout.
- ✅ **Testing requirements section**: Present at top with backend/frontend check commands adapted for MemberFlow stack.
- ✅ **Status tracking**: All 29 WIs show `❌ Not started` consistently.
- ✅ **Unit tests placement**: WI-016 (password reset unit tests) immediately follows WI-015 (reset confirm endpoint). WI-019 (Axios interceptor unit tests) immediately follows WI-018 (Axios client). Correct.
- ✅ **Tenant isolation**: Cross-tenant login test and cross-tenant invite token test both explicitly included in WI-016/028.

---

## 🧠 Chief's Checklist

1. ✅ **SAFETY GATES: Every backend WI has `pytest` in acceptance criteria?** — Yes (except WI-001 scaffold and WI-029 doc, acceptable)
2. ✅ **SAFETY GATES: Every frontend WI has `npm run check` in acceptance criteria?** — Yes, all 12 frontend WIs
3. ✅ All work items S or M effort?
4. ✅ E2E infrastructure noted (agent-browser + POM) before UI work items?
5. ✅ E2E tests interleaved (not bunched at end)?
6. ✅ Integration gate every 3-5 work items?
7. ✅ All work items have Notes with Pattern + Hook point?
8. ❓ All UI work items have NO TOAST warning? — Intent in ACs but not in Notes
9. ✅ Dependency order correct (API before UI)?
10. ✅ Testing requirements section at top?
11. ✅ Last phase is NOT "E2E Tests" (WI-029 is architecture update)?
12. ✅ Work items numbered sequentially (WI-001 through WI-029)?

---

## 📝 Action Items for Bart

One warning to fix before Ralph executes (not blocking — Ralph may proceed, but should fix first):

- [ ] Add `⚠️ NO TOAST:` line to Notes section of WI-021, WI-022, WI-023, WI-024, WI-025, WI-026, WI-027, WI-028 (+5 points → 98/100)

---

## Summary

**Score: 93/100** | **Target: 85+**

29 work items, all S or M. 7 integration gates. Tests correctly interleaved. Every WI has complete Notes. The only issue is a convention gap — `⚠️ NO TOAST:` belongs in the Notes section of UI work items, not just buried in acceptance criteria.

**Chief says:** "Looks clean to me. Ralph, you're cleared to proceed. Just put the no-toast thing where it belongs, capisce?"
