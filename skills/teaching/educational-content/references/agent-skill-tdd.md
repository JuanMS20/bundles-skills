# Agent Skill TDD Pattern — TDD for Hermes skills against simulated backends

Use TDD (vertical tracer bullets) when building or extending a Hermes agent skill
that interacts with a simulated REST backend (py-chain or similar).

## The problem it solves

When you write a skill that says "Hermes can do X", you're making a claim. Without
testing, you don't know if:
- The API endpoint actually exists with the right shape
- Error responses are parseable
- The sequence of operations (send → mine → check balance) works end-to-end
- Edge cases (insufficient balance, unknown accounts) produce usable errors

Testing these against the live API *before* writing the skill means:
- The skill documents what actually works, not what was imagined
- Hermes (the LLM) gets realistic response shapes in its context
- Errors are documented correctly, not guessed

## Workflow

```
1. Pick ONE behavior from the acceptance criteria
2. Write a test that hits the API directly (curl via subprocess → JSON parse)
3. Run it — RED means the behavior doesn't work as expected (fix API or fix test)
4. Once GREEN, document the verified response shape in the skill
5. Repeat for the next behavior
6. After all behaviors are GREEN, write/update the skill
```

## Test structure

Place tests alongside issues:

```
issues/
├── 02-send-mine.md              # Issue: what to build
└── tests/
    └── test_02_send_mine.py      # TDD tests: one function per behavior
```

Each test function is independent and tests one behavior through the public API.

## Key `curl` test helpers (reusable)

```python
import subprocess, json

BASE = "http://localhost:5050"

def api_get(path):
    r = subprocess.run(["curl", "-s", f"{BASE}{path}"],
                       capture_output=True, text=True, timeout=5)
    return json.loads(r.stdout)

def api_post(path, data=None):
    cmd = ["curl", "-s", "-X", "POST", f"{BASE}{path}",
           "-H", "Content-Type: application/json"]
    if data:
        cmd += ["-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    return json.loads(r.stdout)
```

Use `subprocess.run` with `curl` rather than `urllib` or `requests` because:
- It bypasses Python HTTP error handling quirks (urllib can hang on 4xx)
- It's the same tool the skill documents, so you're testing the actual agent path
- No extra dependencies

## Common gotchas when testing APIs for skills

| Gotcha | What happens | Fix |
|--------|-------------|-----|
| `/chain` returns `{"blocks": [...]}` not a list | `len(chain)` counts dict keys, not blocks | Use `len(chain["blocks"])` |
| `/send` nests `tx_hash` inside a `tx` object | `resp["tx_hash"]` is `None` | Use `resp["tx"]["tx_hash"]` |
| `/mine` uses `block_index` not `index` | Assertion on wrong key | Check the actual POST response first |
| Variable gets reassigned in test | Print shows stale value | Use distinct variable names per state snapshot |
| Previous test side-effects affect next test | Chain length, pending count are wrong | Reset before test run, or design independent tests |

## TDD vertical — one at a time

**Do NOT write all tests at once.** Follow the vertical tracer bullet pattern:

```
Test 1 → Implement → Test 2 → Implement → ...
```

For agent skills, "implement" means either (a) fixing the API, or (b) documenting
the verified behavior in the skill. Often the API already works and "GREEN" is
just confirming the path.

## When to skip

- Simple GET endpoints with no side effects (e.g. `/balance/{addr}`)
- API trivially verified with one curl call
- Backend hasn't been built yet (test models instead)
