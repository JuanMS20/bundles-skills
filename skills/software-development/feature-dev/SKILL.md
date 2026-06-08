---
name: feature-dev
description: |
  Structured 7-phase workflow for building features systematically.
  Deploys three specialized agents (code-explorer, code-architect, code-reviewer)
  to guide through discovery, exploration, clarification, architecture, implementation,
  quality review, and summary. Use when the user wants to build a new feature,
  refactor existing code, or implement any non-trivial functionality.
  Do NOT use for trivial one-line fixes or simple bug patches.
---

# Feature Development

7-phase workflow for building features systematically.

## Quick Start

```
User: "Add OAuth authentication"
→ Phase 1: Ask which provider, JWT vs sessions, existing user model
→ Phase 2: Inspect routes/, models/, middleware/
→ Phase 3: "Found Express + Passport. Propose OAuth 2.0 with Google, JWT tokens. OK?"
→ Phase 4: Plan with 2-3 approaches, choose one, present for approval
→ Phase 5: TDD — tests first, atomic commits
→ Phase 6: Review for duplication, security, regression
→ Phase 7: Document, list files, ask to commit/PR/iterate
```

## Phase 1: Discovery

Extract from user:
- **Purpose**: what problem does this solve?
- **Target audience**: who uses it?
- **Constraints**: time, budget, compatibility, performance
- **Acceptance criteria**: how do we know it works?

If user is vague, brainstorm 3-5 approaches. Confirm scope before proceeding.

## Phase 2: Codebase Exploration (code-explorer agent)

Inspect existing codebase with file tool:
- Map project structure (folders, entry points)
- Identify relevant files, dependencies, patterns
- Trace execution paths related to feature area
- Document: tech stack, key modules, existing similar features

Search web if external APIs, libraries, or standards needed.

## Phase 3: Clarification

Summarize to user: "The codebase uses X, existing patterns are Y, I propose Z."

Ask clarifying questions about:
- Edge cases
- Performance requirements
- Compatibility constraints
- Data flow expectations

**Wait for explicit user confirmation** ("yes, proceed" or "go ahead") BEFORE Phase 4.

**NEVER proceed to Phase 4 without user approval.**

## Phase 4: Architecture Design (code-architect agent)

Propose 2-3 implementation approaches with clear trade-offs (pros/cons table).

For each approach define:
- New files vs files to modify
- Interfaces, types, data contracts
- Dependencies introduced
- Risk level

Choose the approach that best fits existing codebase and constraints.
Write step-by-step implementation plan.

**Present plan to user and request approval before Phase 5.**

## Phase 5: Implementation

Follow TDD where possible: tests first, then minimal code to pass.

Rules:
- Atomic commits with descriptive messages
- NO mega-commits
- Large feature → split into sub-tasks, one at a time
- Use subagents if needed (backend, frontend, tests)
- Handle errors gracefully, add basic logging
- Respect conventions found in Phase 2

## Phase 6: Quality Review (code-reviewer agent)

Review own code as strict colleague:
- Duplication, unclear names, missing error handling
- Security: input validation, injection risks, exposed secrets
- Run tests and linters, fix failures
- Regression check: no existing features broken
- Convention compliance with Phase 2 patterns

Score findings by confidence: HIGH (fix now), MEDIUM (fix if time), LOW (note for later).

## Phase 7: Summary

Document:
- What was built and why
- How to use it
- Files changed/created

Ask user: commit, create PR, or continue iterating?

## Pitfalls

- **NEVER** jump to Phase 5 without Phase 3 approval
- **NEVER** skip tests. TDD is mandatory when applicable
- **NEVER** make a single massive commit. Atomic commits always
- **NEVER** assume the user wants the most complex solution. Propose minimal viable first
- **NEVER** leave code without error handling or basic logging
- **NEVER** ignore existing codebase patterns. Consistency is key

## Verification Checklist

```
[ ] Phase 3 approval obtained before coding
[ ] Phase 4 plan approved before implementation
[ ] Tests written before or alongside implementation
[ ] Atomic commits with descriptive messages
[ ] Code review conducted with confidence scoring
[ ] No regressions in existing features
[ ] Documentation of what was built
[ ] User asked for next step (commit/PR/iterate)
```
