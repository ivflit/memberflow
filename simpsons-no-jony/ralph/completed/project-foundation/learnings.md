# Development Learnings: Project Foundation

_Append entries here as work progresses. One entry per work item completed._

---

## 2026-03-24 — WI-002: Django settings

### Dependencies/Configuration
- SQLite support added to `development.py` via `DATABASE_URL` env var prefix check. Avoids needing `dj-database-url` as an extra dependency while still supporting CI. Pattern: `if _database_url.startswith('sqlite')`.
- `DB_HOST` is a separate env var rather than parsing a full DATABASE_URL for PostgreSQL — keeps settings readable without a URL-parsing library.

---

## 2026-03-24 — WI-010/011: Vite proxy

### Dependencies/Configuration
- `VITE_API_TARGET` is read in `vite.config.js` via `process.env` (not `import.meta.env`) because vite.config.js runs at build/server start on Node, not in the browser. This is a common gotcha with Vite env vars.
- `VITE_TENANT_SLUG` IS read via `import.meta.env` in `client.js` — it's needed at runtime in the browser bundle.
- The Vite proxy means Django never sees a cross-origin request from the browser in development. `CORS_ALLOWED_ORIGINS` in development.py is a fallback for direct curl/test calls only.

---

## 2026-03-24 — WI-012: CI Pipeline

### Better Approaches
- Future: add `pytest-cov` for coverage reporting in CI.
- Frontend `npm run check` runs eslint only. When TypeScript is introduced, add `vue-tsc --noEmit` to the check script.
