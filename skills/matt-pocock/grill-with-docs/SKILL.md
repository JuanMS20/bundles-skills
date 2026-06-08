---
name: grill-with-docs
description: Grilling session that challenges your plan against the existing domain model, sharpens terminology, and updates documentation (CONTEXT.md, ADRs) inline as decisions crystallise. Use when user wants to stress-test a plan against their project's language and documented decisions.
---

<what-to-do>

## Step 0: Check memory, then explore

Before asking any questions, check what you ALREADY know:
1. **Memory first**: Run `fact_store search` and `session_search` for the project/domain. If project context is already captured (CONTEXT.md content, architecture decisions, past sessions), use it.
2. **Then codebase**: Only explore the repo if memory doesn't cover what you need. Look for existing docs (CONTEXT.md, PRD.md, README.md), actual code structure, and contradictions between what the user is asking and what already exists.

Don't re-discover what's already in your stores. Cloning a repo and reading files you've already documented is wasted effort.

Surface contradictions immediately: "Your PRD says X, but you're asking for Y — which is it?"

**Remote repos / migration planning:** When the codebase is on GitHub (not local), use the checklist in [references/repo-review-for-migration.md](./references/repo-review-for-migration.md) for systematic exploration via `web_extract`. Covers security red flags, PRD-vs-code contradictions, and migration-readiness signals.

## Step 1: Grill

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing.

If a question can be answered by exploring the codebase, explore the codebase instead.

### Pitfall: Don't force grilling when the task is a review

If the user invokes this skill alongside a request like "review my repo", "check if X is set up right", or "compare A vs B", they probably want a comparison/audit — not a full grilling session. Clarify intent before launching into grilling questions. Grilling is for stress-testing a PLAN against a domain model, not for reviewing whether two setups match.

This holds even when the skill is loaded as part of a bundle with sequential phase instructions. If the user confirms review mode, abort the bundle's phase sequence and proceed with the review directly — the bundle planning pipeline was the wrong tool for this request.

### Pitfall: User invokes this skill for bug reports or feedback

Users sometimes invoke grill-with-docs when they mean "investigate this bug" or "process this client feedback". These are NOT planning tasks. When you see:
- Bug reports ("algo no funciona", "se cierra el modal", "sale en 0")
- Client feedback ("el cliente dice que...", "Alejandro pregunta...")
- Feature requests ("agregar esto", "necesito que...")
- Clarification questions ("¿qué es CC?", "¿cuántos dígitos?")

...shift to the appropriate workflow:
- **Bugs** → Use `diagnose` skill or investigate directly
- **Client feedback** → Translate to requirements, update PRD
- **Feature requests** → Implement or plan (depending on scope)
- **Clarification questions** → Answer directly, update docs if needed

Don't grill the user about a bug report. Just fix it.

### Pitfall: User gives minimal answers signaling "stop asking, start building"

If the user answers your grilling questions with short, cursory engagement (one-word replies, "whatever works", "lo que sea mejor", "you decide", "el que sea más moderno"), and their original request was specific enough to act on, **stop grilling and build**. The user has a clear enough vision and doesn't need the full decision-tree exploration. Continued questioning will feel like friction. Shift directly to implementation.

Signals: answers get shorter, user says "whatever", user prefaces with "quiero probar si puedes" (they want to see capability, not a planning session).

### Pitfall: Misreading "did you ask all the questions?" as a stop signal

When the user asks "seguro que me hiciste todas las preguntas en total?" or similar, they're saying you DIDN'T ask enough questions — they want MORE thorough grilling, not less. This is the opposite of the "stop asking" signal. Double down: ask about timeline, team capacity, integration strategy, deployment constraints, rollback plan, etc.

### Team coordination scenarios

When the user is coordinating with a team (multiple branches, multiple developers, upcoming demo/presentation):
1. **Map the team first**: Who made what? Who can touch which branches? What's the integration strategy?
2. **Identify blockers early**: If branch A depends on branch B's work, surface that immediately.
3. **Propose a document**: For team alignment, create a Word/Markdown document with:
   - Current state of each branch (what exists, what's missing)
   - Inconsistencies found (colors, architecture, naming)
   - Proposed unification plan
   - Who does what by when
4. **Get buy-in before coding**: The user may need team agreement before making changes to shared branches.

</what-to-do>

<supporting-info>

## Domain awareness

During codebase exploration, also look for existing documentation:

### File structure

Most repos have a single context:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Create files lazily — only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update documentation inline

When a term is resolved or a decision is made, update the project's domain documentation right there. Don't batch these up — capture them as they happen.

- Use `CONTEXT.md` for domain glossary and decisions (format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md))
- Use `PRD.md` (or equivalent requirements doc) when grilling reveals a requirement change — e.g., a user story needs updating, scope changes, or access rules shift
- Don't couple documentation to implementation details. Only include terms and requirements meaningful to domain experts.

**Pitfall**: Don't assume every project uses CONTEXT.md. If the project has a PRD.md, update that for requirement changes. If it has both, use each for its purpose.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).

</supporting-info>
