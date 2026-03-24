---
name: lisa
description: Interview-driven feature specification. Asks probing questions until requirements are crystal clear. Triggers on - lisa, spec out, interview me about, define this feature, requirements gathering.
metadata:
  version: "1.0.0"
  argument-hint: <feature name>
---

# Lisa - Feature Specification Interview

Interview to turn vague ideas into clear specs. Save to `simpsons/lisa/features/[feature-name]/spec.md`.

**CRITICAL: Ask ONE question at a time and WAIT for the user's response before asking the next. Do NOT generate the spec until the interview is complete.**

## Phase 0: Project Context (DO FIRST)

**Before starting the interview, read the target project's context:**

```
[Project]/about/PURPOSE.md    # What the project does, who it's for
[Project]/about/ARCHITECTURE.md  # Tech stack, patterns, structure
```

This ensures you understand:

- What the project is for (don't ask questions the PURPOSE.md already answers)
- Technical constraints and patterns (align with existing architecture)
- What's in/out of scope for this project

## Phase 1: First Principles (3-5 questions)

Challenge before diving in:

1. "What specific problem led to this idea?" (get concrete examples)
2. "What happens if we don't build this?"
3. "What's the simplest thing that might solve this?"
4. "What would make this the wrong approach?"
5. "Is there an existing solution?"

Only proceed if approach is validated.

## Phase 2: Deep Interview

Cover systematically. Keep asking until answers are specific.

**Scope:** What's OUT of scope? MVP vs full vision? What must NOT change?

**Functional:** Exact user actions? Inputs/outputs? All states (empty, loading, error, success)? Failure behavior?

**Data:** Schema? Types? Constraints? Migrations?

**API:** Endpoints? Methods? Auth? Request/response formats? Errors?

**UX:** Step-by-step flow? Each screen/state? Error messages (exact wording)?

**Edge Cases:** Wrong input? Network failure? Missing data? Concurrent access?

**Performance:** Load expectations? Response time requirements?

**Security:** Auth required? Authorization rules? Input validation?

## Detecting Vagueness

Dig deeper on:

- "Works well" → "What's the acceptance criteria?"
- "Handle edge cases" → "List every edge case"
- "Similar to X" → "What specifically? What's different?"
- "Standard behavior" → "Describe step by step"
- "Proper error handling" → "What message for each error type?"

## Output Format

```markdown
# Feature: [Name]

## Problem Statement

[Concrete problem with examples]

## Scope

**In:** [list]
**Out:** [list]

## Requirements

### FR-1: [Name]

- Input: [format]
- Output: [format]
- Errors: [list]
- Test Type: **Unit** | **Integration** | **E2E** (justify choice)
- Test: `tests/[unit|e2e]/[feature]/[name].test.ts` - [brief scenario]

## Data Model

| Field | Type | Constraints |
| ----- | ---- | ----------- |

## API

### POST /api/[endpoint]

Request: `{...}`
Response: `{...}`
Errors: 400, 401, 404

## UX Flow

1. User does X → System shows Y

## Edge Cases

| Case | Behavior |
| ---- | -------- |

## Test Strategy (MANDATORY)

### 🎯 Test Philosophy: E2E Smoke Tests First

**Prefer E2E smoke tests over unit tests.** A high-level smoke test that proves the feature works end-to-end is more valuable than isolated unit tests.
```

🔥 E2E Smoke Tests - PREFERRED: Prove features work for real users
📦 Unit Tests - FOR: Complex logic, many edge cases, algorithmic code

```

**Default to E2E smoke tests for:**
- Any new feature (prove it works end-to-end first)
- User-facing functionality
- CRUD operations
- Form submissions
- Navigation flows
- Data display/rendering

**Use Unit tests ONLY when:**
- Complex algorithmic logic (price calculations, discounts)
- Many edge cases (10+ conditional branches)
- Pure functions with no side effects
- State machine with complex transitions
- Validation logic with many rules

**Test Selection Decision:**
| Scenario | Test Type | Rationale |
|----------|-----------|----------|
| New feature works? | **E2E smoke** | Proves real user value |
| CRUD operations | **E2E smoke** | Full stack integration |
| Form validation (simple) | **E2E smoke** | Test in real context |
| Complex calculation (10+ cases) | Unit | Too many permutations for E2E |
| Algorithm with edge cases | Unit | Isolate complexity |
| Pure utility function | Unit | Fast, deterministic |

⚠️ **INTERLEAVING RULE:** E2E tests MUST be written immediately after their feature phase, NOT all at end.

⚠️ **FRAMEWORK:** Uses **agent-browser** with **Page Object Model** (NOT Playwright). See `.github/skills/e2e-testing/SKILL.md` for patterns.

### Test Phases (Map to Feature Phases)

| Feature Phase | E2E Test | When to Write |
|--------------|----------|---------------|
| Phase 2: API Layer | `api.test.ts` | Immediately after API work items |
| Phase 3: UI Components | `ui.test.ts` | Immediately after UI work items |
| ... | ... | ... |

### Regression Tests (Run Existing)
- [ ] `tests/e2e/xxx.test.ts` - Why relevant

### New Tests Required
| Scenario | File | Phase |
|----------|------|-------|
| [Scenario] | `[file].test.ts` | After Phase X |

### Test Data Requirements
- [Fixtures/seeds needed]

## Open Questions
[Should be empty when done]
```

## Done When

- First principles validated
- Scope crystal clear (in AND out)
- All requirements specific and verifiable
- **Each FR has test type specified (Unit/Integration/E2E with justification)**
- **Test Strategy follows Testing Pyramid (E2E only for critical journeys)**
- Data model defined
- API contracts complete with errors
- Edge cases listed
- Open questions empty
