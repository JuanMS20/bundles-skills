---
name: write-a-skill
description: Create new agent skills with proper structure, progressive disclosure, and bundled resources. Use when user wants to create, write, or build a new skill.
---

# Writing Skills

## Process

1. **Gather requirements** - ask user about:
   - What task/domain does the skill cover?
   - What specific use cases should it handle?
   - Does it need executable scripts or just instructions?
   - Any reference materials to include?

2. **Draft the skill** - create:
   - SKILL.md with concise instructions
   - Additional reference files if content exceeds 500 lines
   - Utility scripts if deterministic operations needed

3. **Review with user** - present draft and ask:
   - Does this cover your use cases?
   - Anything missing or unclear?
   - Should any section be more/less detailed?

## Skill Structure

```
skill-name/
├── SKILL.md           # Main instructions (required)
├── REFERENCE.md       # Detailed docs (if needed)
├── EXAMPLES.md        # Usage examples (if needed)
└── scripts/           # Utility scripts (if needed)
    └── helper.js
```

## SKILL.md Template

```md
---
name: skill-name
description: Brief description of capability. Use when [specific triggers].
---

# Skill Name

## Quick start

[Minimal working example]

## Workflows

[Step-by-step processes with checklists for complex tasks]

## Advanced features

[Link to separate files: See [REFERENCE.md](REFERENCE.md)]
```

**Para instrucciones complejas** (multiples secciones, reglas anidadas, datos + instrucciones mezclados), XML tags son preferidos segun Anthropic y reconocidos por OpenAI/Google. Ejemplo: `<instructions>`, `<examples>`, `<constraints>`, `<output_format>`. Markdown es valido pero menos preciso para separar boundaries.

## Description Requirements

The description is **the only thing your agent sees** when deciding which skill to load. It's surfaced in the system prompt alongside all other installed skills. Your agent reads these descriptions and picks the relevant skill based on the user's request.

**Goal**: Give your agent just enough info to know:

1. What capability this skill provides
2. When/why to trigger it (specific keywords, contexts, file types)

**Format**:

- Max 1024 chars
- Write in third person
- First sentence: what it does
- Second sentence: "Use when [specific triggers]"

**Good example**:

```
Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction.
```

**Bad example**:

```
Helps with documents.
```

The bad example gives your agent no way to distinguish this from other document skills.

## When to Add Scripts

Add utility scripts when:

- Operation is deterministic (validation, formatting)
- Same code would be generated repeatedly
- Errors need explicit handling

Scripts save tokens and improve reliability vs generated code.

## When to Split Files

Split into separate files when:

- SKILL.md exceeds 200 lines
- Content has distinct domains (finance vs sales schemas)
- Advanced features are rarely needed

## Pitfalls

### Code blocks inflate line count — compress early

Each SQL/YAML/shell code block eats 5-15 lines (including ```fences, comments, and blank lines). A skill with 4 code blocks easily spends 40-60 lines on examples alone. Skills that include workflows (SQL examples, config templates, command snippets) frequently exceed 200 lines on first draft.

**Symptom:** skill is 210-250 lines, ~80-100 of those are code blocks.
**Fix (in priority order):**
1. Compress verbose code blocks into inline references: `` `CREATE INDEX CONCURRENTLY` (no bloquea escrituras) `` instead of a full ```sql block with comments.
2. Move exhaustive examples to `references/<topic>.md`.
3. Merge related short snippets into a single bullet list.
4. Delete redundant comments inside code blocks (the skill body explains context).

Real example: migration-safety went 239 → 189 lines by compressing 3 SQL blocks + feature flags section into inline references, losing zero information.

### Redundant skills — check existing coverage FIRST

Before proposing ANY new skill, do a thorough search of existing skills. Load every skill in the same domain with `skill_view()` and read its full content including linked files. This session revealed that 3 out of 6 planned skills were redundant because existing skills (roblox-game-systems, roblox-ui-patterns, roblox-studio-development) already had comprehensive coverage.

**Process:**
1. `skills_list()` — list all skills
2. Filter by domain keyword (e.g., "roblox", "security", "web")
3. `skill_view()` EACH candidate — read SKILL.md + linked files
4. Check: does the proposed skill's content overlap >30% with an existing one?
5. If yes → PATCH the existing skill instead of creating new
6. Only create new if the domain genuinely has no coverage

**Anti-pattern:** "I'll create a new skill for X" without checking if X is already covered. This inflates the skill library with redundant entries that compete for attention in `available_skills`.

### Actual AI reasoning vs. hardcoded logic

When building a skill that demonstrates "AI agents" doing something (trading, blockchain, API calls, etc.), the agent behavior MUST use actual LLM reasoning — NOT hardcoded if/else logic or pre-scripted responses.

Users will immediately notice and call out "¿dónde está la parte agéntica?" if the agent is just a script with conditionals. The whole point of using an LLM-based agent is that it *reasons* about data and *decides* what to do.

**Right**: Build a skill that tells Hermes "Connect to the API, read the state, analyze it, and decide what action to take." Hermes uses its LLM to reason about the data.
**Wrong**: Write a Python script with `if balance < 40: request_funds()` and call it an "AI agent."

If the task involves creating educational demos or tutorials, verify early with the user: "Do you want the agent part to use a real LLM, or is a scripted simulation acceptable?" Document the answer in the skill or PRD.

### Simulation fidelity

When building simulated environments (blockchains, marketplaces, external services), separate the simulation layer from the agent interaction layer. The agent should talk to the simulation the same way it would talk to a real system (API calls, structured data). This makes the skill reusable when the real system is available later.

### Testing/interaction skills must include BOTH observation AND interaction

When creating a skill that tests, audits, or interacts with a system (exploratory testing, security audit, chaos testing), the skill MUST include both:
1. **Observation mode** — look at the system, report what you see (UI review, headers, config)
2. **Interaction mode** — actually do things, verify results (click buttons, fill forms, check DB)

**Why:** A skill that only observes finds surface-level issues. A skill that only interacts misses context. The user will ask "but would it actually DO X?" if you only cover observation.

**Pattern:**
```
## FASE 1 — Observation
[look, don't touch]

## FASE 2 — Interaction
[do things, verify in DB/state]

## FASE 3 — Verification
[confirm results match expectations]
```

**Anti-pattern:** Creating a "testing" skill that only describes what to look at without describing what to click, type, or submit. The whole point is simulating a real user who ACTS, not just OBSERVES.

### General-purpose skills: language-agnostic, but platform-aware

When creating a skill for general software development (code-review, testing, architecture):
- NEVER split by **language/framework** (### React, ### Python, ### Go). Use generic heuristics (e.g., "eval( = code injection" applies to JS, Python, Ruby) and pattern tables with a "Donde buscar" column listing multiple languages.
- DO split by **deployment platform** when the testing/auditing method differs fundamentally (web vs mobile vs games vs CLI vs desktop). A security audit on a web app tests XSS/CSRF; on a game tests economy duping; on a CLI tests path traversal. These are NOT language differences — they are different attack surfaces, metrics, and verification methods.

Pattern: **FASE 0 platform detection** → then apply platform-specific budgets/checklists/vectors via a table. This was applied across 7+ skills (judge-performance-budget, judge-security-gates, judge-ux-vibe-check, judge-launch-readiness, user-chaos-tester, reverse-audit) and is proven to work.

If the skill needs language/framework-specific depth, that's a separate skill (use write-stack-skill).

## Review Checklist

After drafting, verify:

- [ ] Description includes triggers ("Use when...")
- [ ] SKILL.md under 200 lines (not 100 — 200 is the real limit)
- [ ] No time-sensitive info
- [ ] Consistent terminology
- [ ] Concrete examples included
- [ ] References one level deep
- [ ] AI agent demonstrations use actual LLM reasoning, not hardcoded logic
- [ ] Instructions use positive framing by default ("use X" > "don't use Y")
- [ ] Scope is explicit when rules apply to multiple elements
- [ ] Adaptations are GENERIC (language-agnostic patterns), not stack-specific sections
- [ ] If skill covers testing/auditing across platforms: FASE 0 detects platform, platform-specific items in tables
- [ ] Code blocks compressed — no verbose SQL/YAML when an inline reference conveys the same info
- [ ] Report/output formats handle empty sections (N=0 → omit, don't show empty headers)
- [ ] Security sections use concrete detection heuristics (patterns to search), not abstract checklists

## Relacion con otras skills

- **prompt-engineering**: Base de conocimiento sobre redaccion de prompts (XML tags, few-shot, framing, ajuste por provider). Consultar cuando la skill creada necesita estructura de instrucciones compleja.
