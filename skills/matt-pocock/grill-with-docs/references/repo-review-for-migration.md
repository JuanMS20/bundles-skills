# Repo Review Checklist for Migration Planning

When the grill session is about migrating a legacy/demo app to a modern stack, use this checklist during Step 0 (explore before grilling).

## Remote repo review (GitHub via web_extract)

Extract in this order — each layer informs the next:

1. **Repo root page** — folder structure, commit count, languages, README
2. **Key config files** — `package.json`, `.gitignore`, any `*.config.*` files
3. **Documentation** — `PRD.md`, `README.md`, `CONTEXT.md`, `docs/`
4. **Entry points** — `index.html`, `src/main.*`, `app.*`
5. **Core modules** — read the actual source of business-logic files (not just list them)
6. **Tests** — `__tests__/`, `*.test.*`, `*.spec.*` — count and coverage area
7. **Subfolders** — role-based or feature-based directories (`admin/`, `staff/`, etc.)

Use `raw.githubusercontent.com` for file contents (faster, no HTML noise). Use `github.com/tree/` for directory listings.

## Security red flags (vanilla JS + GAS pattern)

These are common in demo/prototype apps built with Google Apps Script backends:

| Flag | Where to look | Severity |
|------|--------------|----------|
| Hardcoded credentials in source | `common.js`, `config.*`, constants at top of files | CRITICAL |
| API URL/token exposed in frontend | Any `const *_URL = 'https://script.google.com/...'` | HIGH |
| Passwords stored in plaintext | localStorage, JSON objects, no hashing | CRITICAL |
| localStorage as primary DB | `localStorage.setItem` for business data | MEDIUM |
| No CORS handling | `fetch()` calls to external services without headers | MEDIUM |
| No input sanitization | Direct DOM insertion without `escHtml` or equivalent | MEDIUM |

## PRD vs Code contradictions

Always compare what the PRD says against what the code actually does:
- PRD says "manual testing only" but tests exist → PRD is outdated
- PRD describes 4 features but code has 6+ modules → scope grew
- PRD says "no pagination" but data model could grow → future problem

Surface these contradictions in your first grill message. It builds credibility and grounds the conversation.

## Migration-readiness signals

Look for these to determine how much of the existing code is salvageable:

| Signal | Meaning |
|--------|---------|
| Modular JS files with clear responsibilities | Good — can port logic module by module |
| Business logic mixed into HTML onclick handlers | Bad — needs full rewrite |
| Tests exist and are structured | Good — test cases define expected behavior |
| Data model in a single file (leader-model.js) | Good — can map to DB schema directly |
| Hardcoded geographic data | Neutral — can seed a DB table or keep as config |
| Role-based folder structure (admin/, lider/, staff/) | Good — maps naturally to route groups |

## Common migration paths

| From | To | Key decision |
|------|-----|-------------|
| Vanilla JS + GAS | React/Vue + Supabase | Framework choice first |
| localStorage | Supabase DB | Schema design from existing data model |
| GAS API endpoints | Supabase Edge Functions or client-side SDK | Keep server logic or go BaaS? |
| Hardcoded auth | Supabase Auth | Role mapping (admin/staff/leader → RLS policies) |
| Inline CSS | Component styles / Tailwind | Design system or utility-first |
