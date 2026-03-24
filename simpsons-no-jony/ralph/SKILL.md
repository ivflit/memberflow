---
name: ralph
description: Convert PRD to prd.md for Ralph autonomous execution. Triggers on - convert to ralph, create prd markdown, ralph prd.
metadata:
  version: "1.2.0"
  argument-hint: <path to PRD markdown>
---

# Ralph PRD Converter

Convert PRD to `simpsons/ralph/todo/[feature-name]/prd.md` in structured markdown format.

**Reference Example:** See `.github/skills/ralph/reference/prd.md.example` for a complete example.

## Output Format

```markdown
# [Project Name]

**Branch:** `ralph/[feature-name]`

**Description:** [Feature description]

---

## WI-001: [Title]

**Priority:** 1

**Description:**
[Brief what and why]

**Acceptance Criteria:**

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Check gate passes (`cd ChatAgent && npm run check` exits 0 — runs Biome lint/format + tsc)
- [ ] Smoke tests pass (`cd ChatAgent && npm run test:e2e:smoke`)

**Status:** ❌ Not started

**Notes:**
_None_

---
```

## Key Rules

**Size:** Each work item must complete in ONE iteration (one context window). If too big, split it.

**Tracer Bullets:** Each work item should ideally be a complete vertical slice (end-to-end) where possible. Instead of separating by layer (schema, then API, then UI), each work item should touch all affected layers for one piece of functionality. This ensures every work item produces working, verifiable software.

**Tracer Bullet Example:**

- ❌ WI-001: Create schema, WI-002: Add API, WI-003: Build UI (layer-by-layer)
- ✅ WI-001: Display single item (schema + API + UI), WI-002: List all items (schema + API + UI), WI-003: Add filtering (API + UI)

**When tracer bullets don't apply:** Single-layer work (pure UI tweaks, schema-only migrations) doesn't need vertical slicing—just order by dependency.

**Order:** Dependencies first (schema → backend → UI). Earlier items must not depend on later ones.

**Criteria:** Must be verifiable. Always include "Check gate passes (`cd ChatAgent && npm run check` exits 0 — runs `ultracite check && tsc --noEmit`)" and "Smoke tests pass (`cd ChatAgent && npm run test:e2e:smoke`)". UI items add "Verify in browser".

**Only use `npm run check`** — it runs Biome lint/format check + TypeScript compilation. Use `npm run fix` to auto-fix lint/format issues.

## E2E Testing with agent-browser (TypeScript/vitest)

For features with UI/chat interactions, use `BrowserManager` API with vitest.

**Reference:** https://github.com/vercel-labs/agent-browser/blob/main/test/serverless.test.ts

**Test file pattern:** `ChatAgent/tests/e2e/<feature>/<name>.test.ts`

**Run tests:**

```bash
cd ChatAgent && npm start  # Start dev server
npx vitest run tests/e2e/finance-navigator/vehicle-specs.test.ts
```

**Example test structure:**

```typescript
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { BrowserManager } from "agent-browser/dist/browser.js";

describe("Feature E2E", () => {
  let browser: BrowserManager;

  beforeAll(async () => {
    browser = new BrowserManager();
    await browser.launch({ action: "launch", id: "e2e-test", headless: true });
    const page = browser.getPage();
    await page.goto("http://localhost:3000/test-harness.html");
  });

  afterAll(async () => {
    if (browser?.isLaunched()) await browser.close();
  });

  it("user flow", async () => {
    const page = browser.getPage();
    await page.locator("textarea").fill("Hello");
    await page.keyboard.press("Enter");
    await page.waitForTimeout(5000);
    expect(await page.locator(".response").innerText()).toBeTruthy();
  });
});
```

**After EVERY work item:** Run check gate first (`npm run check`), then smoke tests (`npm run test:e2e:smoke`), then applicable E2E tests to catch regressions.

## Sizing Examples

**Right size:**

- Add database column + migration
- Add UI component to existing page
- Add filter dropdown

**Too big (split):**

- "Build dashboard" → schema, queries, UI components, filters
- "Add auth" → schema, middleware, login UI, session handling

## Checklist

- [ ] Folder: `simpsons/ralph/todo/[feature-name]/`
- [ ] File: `prd.md` (markdown format, not JSON)
- [ ] File: `learnings.md` (for capturing insights during development)
- [ ] Each work item completable in one iteration
- [ ] Ordered by dependency
- [ ] All have "Check gate passes (`cd ChatAgent && npm run check` exits 0 — runs Biome lint/format + tsc)"
- [ ] All have "Smoke tests pass (`cd ChatAgent && npm run test:e2e:smoke`)"
- [ ] UI items have "Verify in browser"
- [ ] No vague criteria
- [ ] Each work item has clear status checkbox

## Learnings File

Ralph must maintain `learnings.md` in the PRD folder, appending entries as development progresses:

```markdown
# Development Learnings: [Project Name]

## [Date] - WI-XXX: [Work Item Title]

### Technical Debt Identified

- [Issue found but not addressed in this WI]

### Bugs Discovered (Out of Scope)

- [Bug found but not part of current work]

### Better Approaches

- [Alternative implementation that could be considered]

### Missing Tests/Edge Cases

- [Test scenarios identified but not covered]

### Documentation Gaps

- [Missing or unclear documentation]

### Performance Concerns

- [Potential performance issues noticed]

### Refactoring Opportunities

- [Code that should be refactored later]

### Dependencies/Configuration

- [Package updates needed, config improvements]

---
```

**When to add entries:**

- After completing each work item
- When discovering technical debt
- When finding bugs outside current scope
- When identifying better patterns
- When noticing missing tests or docs
