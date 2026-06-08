# Kilo Code Token Consumption Audit

## Why "hola" costs ~47K tokens

Every request sends: system prompt + rules + tool definitions + skill metadata + project context + conversation history. User message is negligible (~5 tokens).

## Architecture: What gets injected per request

### Rules (`.kilocode/rules/`)

Rules with `applyTo: "**"` are injected into EVERY request regardless of file type. This is the biggest controllable cost.

```
applyTo: "**"          → always injected
applyTo: "**/*.ts"     → only when editing .ts files
No applyTo             → manual load only (via mode or skill)
```

**Audit command** (bash):
```bash
# Find all globally-injected rules and their sizes
grep -rl 'applyTo: "\*\*"' ~/.kilocode/rules/ | while read f; do
  wc -c "$f" | awk '{print $1, $2}'
done
```

### Token budget breakdown (typical)

| Component | Tokens | Controllable? |
|-----------|--------|---------------|
| Globally-injected rules | 5,000-8,000 | YES — merge/trim |
| Conditionally-injected rules | 500-2,000 | Partially |
| Kilo Code system prompt | 3,000-5,000 | No |
| Tool definitions | 3,000-8,000 | Partially (disable unused tools) |
| Skill metadata scan | 2,000-4,000 | YES — archive unused skills |
| Agent metadata scan | 1,500-3,000 | YES — archive unused agents |
| Project context | 5,000-25,000 | Partially (context condensing) |
| Conversation history | grows per turn | YES — compact regularly |

### Skills and Agents

- Skills: only name+description scanned at startup. Full SKILL.md loaded on-demand.
- Agents: metadata scanned. Full agent loaded when invoked as subagent.
- 64 skills + 26 agents = significant metadata overhead even without loading content.

## Diagnostic checklist

1. **Count globally-injected rules**: `grep -rl 'applyTo: "\*\*"' ~/.kilocode/rules/`
2. **Sum their byte sizes**: total_bytes / 3 ≈ token estimate
3. **Count skill dirs**: `ls ~/.kilocode/skills/ | wc -l`
4. **Count agent files**: `ls ~/.kilocode/agent/*.agent.md | wc -l`
5. **Check for redundant rules**: rules covering the same domain (e.g., two engineering workflow files)
6. **Run `/context` in Kilo Code**: shows actual token breakdown per section
7. **Check project context**: large repos or many open files inflate this

## Common bloat patterns

### Redundant global rules
Two files covering overlapping concerns (e.g., `engineering-rules` + `elite-engineering` both defining workflow). Merge into one.

### Rules with `applyTo: "**"` that should be conditional
Security rules, testing rules — these only matter when editing relevant files. Change `applyTo: "**"` to specific globs.

### Oversized AGENTS.md / DESIGN.md
A 220-line DESIGN.md loaded per request = ~3,100 tokens. If it has no `applyTo`, it only loads in specific modes — but if it does, it's always there.

### MCP servers
Each MCP server adds tool schemas to the system prompt. One server can cost ~18,000 tokens (per LinkedIn analysis). Disable unused servers.

## Kilo Code specific: applyTo patterns

From `~/.kilocode/rules/`:
- `applyTo: "**"` — matches everything, always injected
- `applyTo: "**/*.{ts,tsx,js,...}"` — only code files
- `applyTo: "**/*.{md,yml,yaml,json,toml}"` — only config/doc files
- No `applyTo` in frontmatter — not auto-injected (loaded by mode or manual reference)

## Cost reduction strategies

1. **Merge overlapping rules** — one canonical file per concern
2. **Narrow `applyTo` patterns** — don't inject testing rules when editing CSS
3. **Archive unused skills** — reduces metadata scan overhead
4. **Use context condensing** — `/compact` or auto-compaction settings
5. **Disconnect unused MCP servers** — biggest single-token savings
6. **Start fresh sessions** between unrelated tasks — conversation history accumulates

## Real-world optimization results (session 2026-05-28)

Baseline: 47K tokens for a single "hola" message.

### Changes applied

| File | Before | After | Savings |
|------|--------|-------|---------|
| `copilot-global.instructions.md` | 4,350 bytes (113 lines) | 1,366 bytes (31 lines) | -68% |
| `engineering-rules.instructions.md` | 6,215 bytes (158 lines) | 3,849 bytes (92 lines) | -38% |
| `elite-engineering.instructions.md` | 4,058 bytes (81 lines) | DELETED (merged into engineering-rules) | -100% |
| `DESIGN.md` | 9,405 bytes (220 lines) | 2,507 bytes (62 lines) | -73% |
| Skills directory | 64 skills | 37 skills (27 archived to `_archive/`) | -42% |

### Globally-injected rules impact

| Metric | Before | After |
|--------|--------|-------|
| Total globally-injected bytes | 16,368 | 7,154 |
| Estimated tokens per request | ~5,456 | ~2,384 |
| **Token savings per request** | | **~3,000** |

### Archived skills (moved to `~/.kilocode/skills/_archive/`)

VibeSec-Skill-main, fal-ai-media, investor-materials, investor-outreach, brand-voice, article-writing, crosspost, content-engine, x-api, video-editing, senior-pm, senior-prompt-engineer, everything-claude-code, excalidraw-diagram-generator, frontend-slides, dmux-workflows, bun-runtime, nextjs-turbopack, agent-introspection-debugging, agent-sort, claude-api, karpathy-guidelines, market-research, product-capability, exa-search, search-first, strategic-compact

### Pitfall: copilot-global.instructions.md referencing non-existent paths

The original file referenced `~/.copilot/`, `~/Downloads/copilot/`, `~/.agents/skills/`, `~/.claude/skills/` — paths from a different tool's ecosystem. Kilo Code doesn't use these paths. These references waste tokens and confuse the model. When porting rules between tools, strip all path references to the source tool.

### Pitfall: DESIGN.md without applyTo

DESIGN.md had no `applyTo` in frontmatter, meaning Kilo Code doesn't auto-inject it. However, it loads when specific modes (Architect, Frontend) are active. At 220 lines, it was the single largest rules file. Trimming to 62 lines preserved all actionable directives while removing boilerplate (build commands, generic code style that overlapped with other rules).

### Pitfall: Redundant workflow rules

`engineering-rules.instructions.md` and `elite-engineering.instructions.md` both defined: task classification, context gathering, implementation standards, debugging, review, verification. The overlap was ~60%. Merged into one canonical `engineering-rules.instructions.md` with the unique parts from each.
