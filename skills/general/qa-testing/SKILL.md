---
name: qa-testing
description: "Quality Assurance and Testing workflow for any software. Discovers bugs via systematic testing, creates structured TODO lists, and fixes incrementally without breaking existing functionality. Use when user says 'test this', 'find bugs', 'QA', 'quality check', 'revisa que funcione', 'pruebas de calidad', or wants comprehensive testing of any codebase."
tags: [testing, qa, quality, bugs, verification]
---

# QA Testing — Quality Assurance for Any Software

## Quick Start

1. **Load this skill** when user wants testing/QA of any codebase
2. **Zoom out** first to understand the codebase structure
3. **Run tests** using existing test infrastructure
4. **Create TODO** with discovered bugs
5. **Fix incrementally** using TDD — never break working code

## Core Principles

- **Verify before claiming**: Never say "it works" without evidence
- **Incremental fixes**: Fix one bug at a time, verify after each
- **Preserve functionality**: If code works, don't touch it unless fixing a specific bug
- **Document everything**: Every bug gets a TODO item with reproduction steps

---

## Workflow

### Phase 0: Understand the Codebase

Before writing ANY test:

1. **Zoom out** — Load `zoom-out` skill to understand the big picture
   - What is this project? What does it do?
   - What's the architecture? (frontend/backend/mobile/game/etc.)
   - What tech stack? (check package.json, requirements.txt, etc.)
   - Where are the main entry points?

2. **Check existing tests** — Run whatever test infrastructure exists
   - `npm test` / `pytest` / `cargo test` / etc.
   - Note: which tests pass, which fail, which don't exist

3. **Map the critical paths** — Identify what MUST work:
   - User-facing features
   - Data persistence
   - Authentication/security
   - Payment/integration flows

**STOP**: Present your understanding to user before proceeding.

### Phase 1: Systematic Testing

Test each critical path using this order:

#### 1.1 Smoke Test (Does it even run?)
- [ ] Can you install dependencies?
- [ ] Can you start the app/service?
- [ ] Does the main page/endpoint respond?
- [ ] Any crashes on startup?

#### 1.2 Functional Testing (Does it do what it should?)
For each critical path:
- [ ] Happy path works (normal usage)
- [ ] Edge cases handled (empty inputs, special characters, limits)
- [ ] Error messages are helpful (not stack traces to users)

#### 1.3 Integration Testing (Do parts work together?)
- [ ] API endpoints return correct data
- [ ] Frontend displays data correctly
- [ ] Database operations persist correctly
- [ ] Third-party integrations work (or fail gracefully)

#### 1.4 Security Quick Check
- [ ] Auth required on protected routes
- [ ] Input validation present
- [ ] No hardcoded secrets in code
- [ ] SQL injection / XSS obvious vectors checked

### Phase 2: Bug Discovery Protocol

When you find a bug:

1. **Reproduce it** — Get exact steps to reproduce
2. **Classify severity**:
   - **CRITICAL**: Data loss, security breach, complete feature broken
   - **HIGH**: Feature broken but workaround exists
   - **MEDIUM**: Feature works incorrectly
   - **LOW**: Cosmetic, minor inconvenience

3. **Create TODO item** (use `todo` tool):
```
[Bug] <severity>: <one-line description>
- Reproduction: <exact steps>
- Expected: <what should happen>
- Actual: <what actually happens>
- File: <path to relevant code>
```

### Phase 3: Fix Plan

**NEVER fix bugs immediately.** First:

1. **List all bugs** found in Phase 2
2. **Sort by severity** (CRITICAL first)
3. **Identify dependencies** (does fixing Bug A affect Bug B?)
4. **Present plan to user**:
   ```
   Found N bugs:
   - CRITICAL: X bugs
   - HIGH: Y bugs
   - MEDIUM: Z bugs
   - LOW: W bugs
   
   Proposed fix order: [list]
   Estimated effort: [brief]
   
   Shall I proceed?
   ```

**WAIT for user approval** before fixing anything.

### Phase 4: Incremental Fixes (TDD)

For each approved fix, use `tdd` skill:

1. **RED**: Write a test that reproduces the bug
   - Test should FAIL before fix
   - This proves the bug exists

2. **GREEN**: Write minimal code to fix the bug
   - Don't refactor unrelated code
   - Don't add features
   - Make the test pass

3. **VERIFY**: Run the test again
   - Confirm it passes
   - Confirm no other tests broke

4. **UPDATE TODO**: Mark bug as fixed

**Between each fix**: Run full test suite to ensure nothing broke.

### Phase 5: Final Verification

After all fixes:

1. **Run complete test suite** — everything should pass
2. **Smoke test again** — app still works end-to-end
3. **Review changes** — only fix what was in the plan
4. **Document** — update TODO with final status

---

## Anti-Patterns (What NOT to Do)

### ❌ "It should work" without testing
Never claim code works without running it. Evidence required.

### ❌ Fixing multiple bugs at once
One bug, one fix, one verification. Batch fixes = hidden regressions.

### ❌ Refactoring while fixing
Refactor AFTER all bugs are fixed. Mixing = new bugs.

### ❌ Ignoring low-severity bugs
They often indicate deeper issues. Note them, but fix critical first.

### ❌ Deleting "dead code" during QA
You don't know if it's dead. Note it, ask user after QA completes.

---

## Integration with Other Skills

### anti-hallucination
**WHEN**: During ANY code analysis or fix
**HOW**: Before claiming "this code does X" — verify. Before writing a fix — verify the API exists.

### zoom-out
**WHEN**: At Phase 0 (understanding codebase) and when confused about code
**HOW**: Load skill, ask for high-level view of relevant modules

### tdd
**WHEN**: During Phase 4 (fixing bugs)
**HOW**: Load skill, follow red-green-refactor loop for each fix

### diagnose
**WHEN**: When a bug is hard to reproduce or understand
**HOW**: Load skill, follow the 6-phase diagnosis loop

---

## Quality Gate (Before Declaring Done)

```
[ ] All critical bugs fixed
[ ] All high-severity bugs fixed (or documented why deferred)
[ ] Full test suite passes
[ ] No new bugs introduced
[ ] No unrelated code changed
[ ] TODO updated with final status
[ ] User informed of results
```

---

## Relationship to Other Skills

- **tdd**: Use for the actual fix cycle (red-green-refactor)
- **anti-hallucination**: Use to verify code understanding before fixing
- **zoom-out**: Use to understand codebase structure before testing
- **diagnose**: Use for hard-to-reproduce bugs
- **write-a-skill**: If you discover a testing pattern, consider extracting it

---

## Pitfalls

### False positives in testing
A test that passes might be testing the wrong thing. Verify assertions check real behavior, not just "no crash".

### Breaking working code
If code works and you didn't touch it, it should still work. If it breaks after your fix, you have a regression.

### Scope creep
"while I'm here, I could also improve X..." — NO. Stay in scope. Note improvements for later.

### Missing the forest for the trees
Don't get lost testing utility functions. Focus on user-facing critical paths first.

### Dev server HTML 200 ≠ JS bundle compiles
Expo, Webpack dev server, Vite, and similar tools serve an HTML shell that returns 200 even when the JS bundle has module resolution errors. Testing only the HTML endpoint gives false confidence. Always verify the **bundle/compilation output** directly (curl the bundle endpoint, check the terminal for transform errors, or open browser console for runtime errors). See `references/react-native-expo-testing.md` for Expo-specific pitfalls.

### Canvas games: synthetic events don't work
Dispatching `MouseEvent` via JS (`canvas.dispatchEvent(new MouseEvent(...))`) won't trigger canvas event handlers reliably — the browser marks synthetic events as `isTrusted: false` and some handlers ignore them. For canvas-based games and apps, **code review is more effective than runtime testing**. Read the source, trace the logic, identify bugs statically. Use runtime testing only for non-interactive verification (console state checks, function existence, etc.).

### Single-file projects: review > infrastructure
For single-file HTML/JS projects (<500 lines), skip the "check existing tests" step — there are none. Go straight to code review. The test infrastructure is the code itself. Focus on logic errors, collision detection, state management, and edge cases.

### When user says "go fast" after approving a plan
If the user approves a fix plan and says "no te detengas" / "go ahead" / "do it all", execute the entire plan without pausing between fixes. The approval covers all items. Don't ask for per-fix confirmation after blanket approval.

### React Native / Expo: "Cannot find module" in compiled bundle is a false positive
When grep-ing the Metro bundle for errors, `grep "Cannot find module"` will match 2 lines of Metro runtime boilerplate (throw statements in the require() polyfill). These are NOT real errors. Search for `UnableToResolve` or `TransformError` instead to find actual resolution failures. See `react-native-expo-patterns` skill for full diagnostic flow.
