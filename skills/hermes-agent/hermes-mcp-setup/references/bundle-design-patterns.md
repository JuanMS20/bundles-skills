# Bundle Design Patterns — Lessons from Practice

Design principles distilled from building and iterating on Hermes skill bundles for Matt Pocock workflows.

## Golden Rule: Feedback Speed is the Metric

> "The rate of feedback is your speed limit."

Every gate/approval step adds latency. Design for the minimum viable number of phases.

## Anti-Pattern: The Pipeline Pileup

```
FASE 1 → GATE → FASE 2 → GATE → FASE 3 → GATE → FASE 4 → GATE
```

**Problem:** 4 gates for a single feature = frustrated user before writing a line of code. Each gate forces a "continuemos" response.

**Fix:** Max 2–3 phases per bundle. Push optional steps (docs lookup, pattern reference) into on-demand invocation or internal references.

## Pattern: Conditional Branching (A/B)

Detect context before choosing the path. Every bundle should ask PASO 0 questions:

1. Does code exist in the target module?
2. Is there a CONTEXT.md with domain language?
3. Are there relevant ADRs?

Then branch:

```
PASO 0: Detection
├── RAMA A (greenfield): skip zoom-out → go direct to TDD
└── RAMA B (existing):   zoom-out → GATE → TDD
```

This prevents wasted phases (zoom-out on an empty folder is noise).

## Pattern: On-Demand Reference, Not Mandatory Phase

Skills like docs-lookup or pattern reference should be:
- **Invoked by the user** when needed (separate `/command`)
- OR **embedded as internal reference** inside an existing phase's instruction

NOT a mandatory phase in the bundle pipeline. The bundle instruction can say:

```
If you need documentation of [API], ASK the user:
"¿Necesito buscar documentación de [API]?"
and run /skill-name only if they say yes.
```

## Pattern: Anti-Hallucination Protocol

Embed this in any bundle that writes code:

```
REGLA DE ORO:
  NUNCA inventes APIs. Protocolo de duda:
  1. Consulta skill de patrones existente
  2. Context7 MCP → resolve-library-id + query-docs
  3. web_search/web_extract como fallback
  4. CITA la fuente antes de escribir código
  APIs críticas (auth, pagos, persistencia): verifica aunque estés seguro.
```

Context7 MCP tools: `mcp_context7_resolve_library_id` + `mcp_context7_query_docs`.

## Pattern: Stack Detection

Add to PASO 0: inspect `package.json`, `pubspec.yaml`, `requirements.txt`, `go.mod`, `Cargo.toml`, etc.

If a pattern skill exists for the detected stack (e.g., `/roblox-tdd-patterns`), load it as internal reference for the full cycle.

## Pattern: Patterns Inform, Not Follow

Pattern skills (like roblox-tdd-patterns) must be loaded **during** TDD, not as a separate post-TDD phase. Adding patterns after writing code is like reading a design patterns book after finishing the implementation.

## Checklist: Is Your Bundle Lean Enough?

- [ ] Could any phase be on-demand instead of mandatory?
- [ ] Does the user need to say "continuemos" more than twice?
- [ ] Are reference/pattern skills positioned before or during the phase that needs them?
- [ ] Does PASO 0 detect context and skip irrelevant phases?
- [ ] Is there an anti-hallucination protocol?
- [ ] Is stack detection present?

## Bundle Improvements from Gentle-AI Analysis

Patterns from the Gentle-AI ecosystem (github.com/Gentleman-Programming/gentle-ai) that improve Hermes bundles. Research date: 2026-06-04.

### Auto-SDD Trigger

**Problem:** Bundles only activate when the user explicitly loads them. If the user says "implementa auth" without loading a bundle, the agent writes code without spec. Vibe coding.

**Solution:** Add rules to AGENTS.md that trigger bundle loading automatically:

```markdown
## Auto-SDD Triggers
- Solicitud toca 2+ archivos O dice "implementa/crear/agregar" feature → CARGAR grill-me ANTES de código
- Solicitud toca 4+ archivos O es arquitectónica → SUGERIR to-prd primero
- Solicitud dice "fix" con bug conocido → CARGAR diagnose
```

This is 4 lines in AGENTS.md, not a new skill.

### Chained PR Delivery

**Problem:** Large features produce a single massive diff. Unreviewable.

**Solution:** Skill `chained-pr` loaded after `to-issues`. Generates dependency-ordered PR chains:

```
PR-1: schema       [independent]
PR-2: API          [depends on PR-1]
PR-3: UI           [depends on PR-2]
PR-4: tests        [depends on PR-2]
```

Each PR is small, independently reviewable, and mergeable once its dependency is merged. Implement as a new skill that extends `to-issues` output.

### Model Routing by Phase

**Problem:** Same model used for reading files (cheap) and designing architecture (expensive).

**Solution:** Convention in AGENTS.md (not a skill):

```markdown
## Model Routing
- Lectura/exploración: modelo barato
- Spec/diseño: modelo más capaz
- Implementación: modelo medio
```

If the bundle uses `delegate_task` per phase, each child can specify a model override.

### Spec Archive Post-Judge

**Problem:** After judge approves, the spec stays wherever it was. No cleanup, no sync with what was actually built.

**Solution:** Skill `spec-archive` as final step in judge bundles. It reads the original spec, diffs against actual implementation, updates CONTEXT.md with lasting decisions, and archives completed specs to `specs/archive/`.

## Pattern: Perspective-Based Gap Analysis

Every bundle chain covers a **perspective**. Before creating a new bundle, map what perspectives exist:

| Bundle | Perspective | What it sees |
|---|---|---|
| dev-cycle | Builder | Code quality, anti-hallucination, patterns |
| qa-bundle | Tester (internal) | Tests pass, happy paths, edge cases |
| judge | Verifier (technical) | Functional, errors, security, perf, UX, launch |
| user-chaos (proposed) | Clueless user | Flows confuse, buttons mislead, forms accept garbage |

**Gap signal:** If all bundles share the same perspective (e.g., all assume system knowledge), a perspective-shift bundle will find bugs the others can't. The "dumb user" finds what the expert developer never tests.

**How to apply:**
1. List all bundles in the chain
2. For each, name the perspective (who is looking?)
3. If all perspectives are "knowledgeable insider" → propose a "clueless outsider" bundle
4. If all perspectives are "pre-launch" → propose a "post-mortem" bundle

**Example:** Judge verifies security from developer perspective (XSS in code). User-chaos verifies security from attacker perspective (click random things, inject garbage, break flows). Different bugs surfaced.

## Pattern: Checklist-in-Bundle

**Problem:** Agent advances through phases without completing all checks in the current one. Critical items get skipped because the model "feels done" and moves on.

**Solution:** Embed a structured checkbox checklist in the bundle instruction. The agent MUST mark each item before advancing to the next phase.

```yaml
instruction: |
  ## Checklist de Trabajo
  Marca cada item cuando se complete. NO avances a la siguiente fase si hay items sin marcar en la actual.

  ### FASE 1 — [Name]
  - [ ] Step A done
  - [ ] Step B done
  - [ ] Output generated
  - [ ] Gate condition met (e.g., CRITICAL = 0)

  ### FASE 2 — [Name]
  ...
```

**Why it works:** Checklists create explicit completion criteria per phase. Without them, the agent's internal "am I done?" heuristic is unreliable — especially for multi-step phases with 5+ items.

**When to use:**
- Phases with 5+ discrete steps (testing, auditing, multi-file review)
- Phases where skipping an item has consequences (security checks, DB verification)
- Post-gate phases where the gate condition must be verified, not assumed

**When NOT to use:**
- Simple 1-2 step phases (zoom-out, handoff)
- Phases that are purely generative (write spec, create issues)

**Pitfall:** Don't make the checklist SO long that it becomes noise. Group related items under sub-headers. If a phase has 15+ items, split it into two phases.

## Principle: Research Before Creation

Before creating ANY bundle, the agent MUST:
1. **Inventario**: List all existing bundles and what they cover
2. **Gap analysis**: Identify missing perspectives, phases, or domains
3. **Propuesta**: Present findings + options to the user BEFORE implementing
4. **Aprobación**: Wait for user to choose before creating anything

This prevents redundant bundles and ensures each one fills a real gap. The user explicitly expects this: "antes de implementar primero haz la investigacion y propuesta y me la traes."

## Reference: Our Bundle Catalog

| Bundle | Skills | Phases | Design Notes |
|---|---|---|---|
| `/dev-cycle` | zoom-out, tdd | 2 + A/B | Reference: anti-hallucination + stack detection |
| `/tdd-roblox` | zoom-out, tdd | 2 + A/B | Patterns embedded in TDD instruction |
| `/plan-sprint` | grill-with-docs, to-prd, to-issues | 3 | CONTEXT.md enforced between phases |
| `/close-out` | improve-codebase-architecture, diagnose, handoff | 3 | Clean sequential close-out |
| `/qa-bundle` | qa-testing, tdd + others | 5 | Testing sistemático, detecta si ya pasó por dev-cycle |
| `/judge` | judge-functional-test, judge-error-handling, judge-security-gates, judge-performance-budget, judge-ux-vibe-check, judge-launch-readiness | 6 | Veredicto final con evidencia por fase |
| `/skill-forge` | write-a-skill, write-stack-skill | 2 | Creación/auditoría/mantenimiento de skills |
| `/user-chaos` | user-chaos-tester, reverse-audit, anti-hallucination, zoom-out | 3 | Post-judge: usuario torpe + auditoría externa. Checklist embedido. |
| Skill individual | post-mortem-forense | — | RCA blameless post-mortem. Carga bajo demanda con diagnose/close-out. |
