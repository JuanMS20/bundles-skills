# Config Migration Reference

## Migration: OpenCode → Kilo Code (2026-05-28)

### What Was Migrated

**Skills (13 Matt Pocock skills):**
- diagnose, grill-me, grill-with-docs, handoff, improve-codebase-architecture
- prototype, to-issues, to-prd, triage, tdd, zoom-out, teach, write-a-skill

**Rules (new file):**
- `engineering-rules.instructions.md` — extracted from AGENTS.md, stripped tool-specific refs

### What Was NOT Migrated

**SOUL.md** — Hermes-specific identity file. References:
- `available_skills` (Hermes tool)
- `fact_store` / `fact_feedback` (Hermes tools)
- `session_search` (Hermes tool)
- `hermes-wiki/` paths (Hermes-specific)

**AGENTS.md (full)** — Contains tool-specific references:
- `skill_view()` → Kilo doesn't have this
- `fact_store add` → Kilo doesn't have this
- `session_search` → Kilo doesn't have this
- `hermes-wiki/Inbox/` → Kilo doesn't have this

### Principles Extracted (kept in engineering-rules.instructions.md)

1. Rule Hierarchy: Security > Honesty > TDD > Surgical > Trivial
2. Code Minimalism: minimum that resolves, nothing speculative
3. Surgical Changes: touch only what you must
4. Verification Before Claims: check docs, check skills, declare confidence
5. Anti-patterns: 8 patterns with consequences and alternatives
6. Context Engineering: just-in-time, progressive disclosure
7. Matt Pocock Skill Map: phase → skill mapping

### Pattern for Future Migrations

When copying between AI tools:
1. Skills (SKILL.md) → copy as-is if frontmatter matches target format
2. Rules/Instructions → extract principles, strip tool-specific API refs
3. Identity files → don't copy (tool-specific)
4. Provider configs → adapt schema to target tool's format
5. MCP configs → usually transfer directly (same JSON structure)
