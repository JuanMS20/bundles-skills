---
name: tdd
description: Test-driven development with red-green-refactor loop. Use when user wants to build features or fix bugs using TDD, mentions "red-green-refactor", wants integration tests, or asks for test-first development.
---

# Test-Driven Development

## Philosophy

**Core principle**: Tests should verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't.

**Good tests** are integration-style: they exercise real code paths through public APIs. They describe _what_ the system does, not _how_ it does it. A good test reads like a specification - "user can checkout with valid cart" tells you exactly what capability exists. These tests survive refactors because they don't care about internal structure.

**Bad tests** are coupled to implementation. They mock internal collaborators, test private methods, or verify through external means (like querying a database directly instead of using the interface). The warning sign: your test breaks when you refactor, but behavior hasn't changed. If you rename an internal function and tests fail, those tests were testing implementation, not behavior.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines. For frontend-specific bug patterns (modal event propagation, async timing), see [references/frontend-bug-patterns.md](references/frontend-bug-patterns.md).

## Anti-Pattern: Horizontal Slices

**DO NOT write all tests first, then all implementation.** This is "horizontal slicing" - treating RED as "write all tests" and GREEN as "write all code."

This produces **crap tests**:

- Tests written in bulk test _imagined_ behavior, not _actual_ behavior
- You end up testing the _shape_ of things (data structures, function signatures) rather than user-facing behavior
- Tests become insensitive to real changes - they pass when behavior breaks, fail when behavior is fine
- You outrun your headlights, committing to test structure before understanding the implementation

**Correct approach**: Vertical slices via tracer bullets. One test → one implementation → repeat. Each test responds to what you learned from the previous cycle. Because you just wrote the code, you know exactly what behavior matters and how to verify it.

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  RED→GREEN: test3→impl3
  ...
```

## Workflow

### 1. Planning

When exploring the codebase, use the project's domain glossary so that test names and interface vocabulary match the project's language, and respect ADRs in the area you're touching.

Before writing any code:

- [ ] Confirm with user what interface changes are needed
- [ ] Confirm with user which behaviors to test (prioritize)
- [ ] Identify opportunities for [deep modules](deep-modules.md) (small interface, deep implementation)
- [ ] Design interfaces for [testability](interface-design.md)
- [ ] List the behaviors to test (not implementation steps)
- [ ] Get user approval on the plan

Ask: "What should the public interface look like? Which behaviors are most important to test?"

**You can't test everything.** Confirm with the user exactly which behaviors matter most. Focus testing effort on critical paths and complex logic, not every possible edge case.

### 2. Tracer Bullet

Write ONE test that confirms ONE thing about the system:

```
RED:   Write test for first behavior → test fails
GREEN: Write minimal code to pass → test passes
```

This is your tracer bullet - proves the path works end-to-end.

### 3. Incremental Loop

For each remaining behavior:

```
RED:   Write next test → fails
GREEN: Minimal code to pass → passes
```

Rules:

- One test at a time
- Only enough code to pass current test
- Don't anticipate future tests
- Keep tests focused on observable behavior

### 4. Refactor

After all tests pass, look for [refactor candidates](refactoring.md):

- [ ] Extract duplication
- [ ] Deepen modules (move complexity behind simple interfaces)
- [ ] Apply SOLID principles where natural
- [ ] Consider what new code reveals about existing code
- [ ] Run tests after each refactor step

**Never refactor while RED.** Get to GREEN first.

## When NOT to Use TDD

### Pitfall: TDD vs Post-Implementation Verification

TDD is for BUILDING features (test-first). When the user says "verify it works", "check nothing broke", or "revisa que funciona", they want POST-IMPLEMENTATION VERIFICATION — not TDD.

Don't force red-green-refactor when the code is already written. Instead:
1. Syntax checks (node -c for JS, lint for other languages)
2. Structure verification (grep for correct references, function definitions)
3. Logic tests with mock data (Node.js scripts simulating the behavior)
4. Cross-check related code wasn't broken

If the user loaded TDD but asks for verification, acknowledge it and shift approach. The skill is about test-first development; verification is a different workflow.

### Pitfall: Bundle loads TDD but user wants fast implementation

When a skill bundle (e.g. `dev-cycle`) includes TDD as a mandatory phase, but the user's instruction is "implementa todas las features" or "adelante" — this is NOT a test-first request. The user wants working code, not test-first code.

**Resolution:** Follow the bundle's phases but adapt:
- **zoom-out** → Execute fully (understanding codebase is always valuable)
- **tdd** → Acknowledge the phase but pivot to "post-implementation verification" mode if the user hasn't explicitly asked for test-first. Do: syntax checks, structure verification, logic tests with mock data.
- **code-review** → Execute fully (static review is always valuable)

**Never force TDD when the user's intent is speed/implementation.** The tdd skill exists for test-first workflows; if the user wanted TDD, they would say "test-first" or "red-green-refactor".

## Adaptations: Roblox Studio MCP

When using TDD with Roblox Studio via MCP (no traditional test runner):

- RED: `execute_luau` with `assert()` to confirm behavior absent
- GREEN: `execute_luau` or `multi_edit` to create minimal code
- VERIFY: `search_game_tree` / `inspect_instance` / `script_read`
- INTEGRATION: Play mode → `get_console_output` for runtime errors

See [references/roblox-studio-mcp-tdd.md](references/roblox-studio-mcp-tdd.md)
for the full adapted workflow.

## Checklist Per Cycle

```
[ ] Test describes behavior, not implementation
[ ] Test uses public interface only
[ ] Test would survive internal refactor
[ ] Code is minimal for this test
[ ] No speculative features added
```
