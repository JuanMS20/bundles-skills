---
name: anti-hallucination
description: Protocol for preventing hallucinated APIs — detect stack, verify docs before coding, cite sources, never assume.
tags: [guardrails, verification, accuracy, documentation]
---

# Anti-Hallucination Protocol

## When to Trigger

Apply this protocol during ANY coding task where you interact with external APIs, frameworks, libraries, or services. Especially critical for:

- Auth, payments, persistence, and security-sensitive APIs
- Lesser-known libraries or recent versions
- APIs you haven't used in the last 30 days
- Stack-specific APIs (React hooks, Flutter widgets, Roblox services, Python stdlib)
- When the user says "verifica", "revisa", "check if that API exists", or "don't assume"

## The Protocol

### Step 0: Stack Detection
Before coding, identify the exact tech stack by inspecting project config files:
- `package.json` (Node/React/React Native) — read the `dependencies` and `devDependencies`
- `pubspec.yaml` (Flutter/Dart)
- `requirements.txt` / `pyproject.toml` (Python)
- `go.mod` (Go)
- `Cargo.toml` (Rust)
- `.csproj` (C# / .NET)

Knowing exact package names + versions tells you which docs to consult. **Don't assume the latest version** — read the lockfile.

### Step 1: When in Doubt — Verify
If you are NOT 100% sure about an API's existence, signature, or behavior:

1. Check for a loaded pattern/reference skill first (e.g., `/roblox-tdd-patterns`, `/react-patterns`)
2. Search official documentation:
   a. `web_search` targeting `site:docs.example.com` or the official docs domain
   b. `web_extract` for plain-text docs pages
   c. **invisible-browser MCP** (stealth_extract / stealth_navigate / stealth_meta) — use when sites block scraping or need JS rendering to display content
3. **Cite the source** before writing the code — include URL + relevant excerpt
4. Only proceed with implementation after verification

### Step 2: Critical APIs — Verify Even When Sure
If the API handles **auth, payments, data persistence, security, or external service integration**:
→ Run one quick verification search regardless of confidence level. No exceptions.

### Step 3: Never Assume
- "This method name makes sense" is NOT evidence it exists
- "This is how similar libraries do it" is NOT evidence
- "I've seen this before" is NOT evidence for the current version
- TypeScript types in `node_modules` prove existence — gut feeling does not
- If searching yields no results, the API likely doesn't exist (or has a different name)

## Relationship to Existing Skills

- **tdd (matt-pocock):** Anti-hallucination applies during the GREEN phase — writing implementation code that must use real, existing APIs to pass the test.
- **dev-cycle bundle:** Loads this protocol as part of PASO 0 / stack detection, before zoom-out or TDD.
- **diagnose (matt-pocock):** If a bug was caused by a hallucinated API, anti-hallucination prevents the root cause from recurring.

## Pitfalls

- **Familiarity trap:** You used this API 6 months ago. It may have changed. Verify.
- **Logical-sounding names:** React has `useState` but not `useHistory` (React Router v6 uses `useNavigate`). Don't guess by analogy.
- **Version mismatch:** `pip install` / `npm install` gives you X.Y but mental model is from docs for X.Z. Check the lockfile version.
- **Multiple libraries with similar names:** Flask vs FastAPI, React Router v5 vs v6, Express 3 vs 4. Confirm WHICH one the project uses.
- **Deprecated APIs:** The method exists but is deprecated with a different replacement. Verify current best practice, not just existence.
- **TDD false confidence:** A test that passes with a hallucinated API gives false confidence. Verify APIs BEFORE writing code, not after a test fails.
- **Assuming UI works without visual verification:** When the user reports "UI not visible" / "solo se ve una linea azul" / similar visual issues, do NOT assume the code is correct. Create a **diagnostic test component** (e.g., a bright-colored frame in a separate ScreenGui) to confirm the rendering pipeline works, then narrow down from there. Guessing causes without physical evidence is a form of hallucination.
- **Claiming a fix works without runtime verification:** Telling the user "done" or "it should work now" without having actually run the code in Play mode / test environment is a form of hallucination. You are stating a fact you have not verified. The fix is: run it, check the output, then report only what you observed. If the tool can't verify (e.g., `get_console_output` is unreliable), say so explicitly: "I've changed X but I can't visually confirm — please test and tell me what you see."
- **Leaving diagnostic artifacts in the user's environment:** If you create test/debug instances (debug GUIs, test scripts, sample data) during diagnosis, you MUST remove them when the diagnosis is complete. Leftover artifacts confuse the user and waste their time. Add cleanup as the last step of any diagnostic workflow.
- **Not searching documentation before assuming:** When a framework behaves unexpectedly (e.g., `WaitForChild` blocking in Roblox, `Players.LocalPlayer` being nil), do NOT guess the cause or the fix. Search the official docs first (`web_search` targeting devforum/create.roblox.com). The documentation exists and is searchable. Using it is the protocol, not optional.
