---
name: to-issues
description: Break a plan, spec, or PRD into independently-grabbable issues on the project issue tracker using tracer-bullet vertical slices. Use when user wants to convert a plan into issues, create implementation tickets, or break down work into issues.
---

# To Issues

Break a plan into independently-grabbable issues using vertical slices (tracer bullets).

The issue tracker and triage label vocabulary should have been provided to you — run `/setup-matt-pocock-skills` if not.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes an issue reference (issue number, URL, or path) as an argument, fetch it from the issue tracker and read its full body and comments.

### 2. Explore the codebase (REQUERIDO cuando hay decisions de diseño)

**No es opcional** si el PRD contiene decisiones de diseño (colores, patrones, arquitectura, naming). Analizar el código fuente para verificar que las acceptance criteria reflejan lo que realmente existe. Si la documentación dice una cosa y el código dice otra, las acceptance criteria deben apuntar al código.

Si el código no existe aún (feature nueva), las acceptance criteria deben ser suficientemente específicas para que un dev las implemente sin preguntar.

### 3. Draft vertical slices

Break the plan into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

Slices may be 'HITL' or 'AFK'. HITL slices require human interaction, such as an architectural decision or a design review. AFK slices can be implemented and merged without human interaction. Prefer AFK over HITL where possible.

<vertical-slice-rules>
- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Prefer many thin slices over few thick ones
</vertical-slice-rules>

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Type**: HITL / AFK
- **Blocked by**: which other slices (if any) must complete first
- **User stories covered**: which user stories this addresses (if the source material has them)

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL and AFK?

Iterate until the user approves the breakdown.

### 5. Publish the issues to the issue tracker

Before publishing, detect if an issue tracker exists (GitHub Issues, Jira, Linear, etc.). If no tracker is configured or the user has no repo, use **local file mode** instead.

#### Local file mode

- Create an `issues/` directory at the project root (or the user's working directory).
- **CRITICAL: ONE file per issue**. Each approved slice becomes a separate file: `issues/<NNN>-<kebab-title>.md` where `NNN` is a 3-digit zero-padded sequence number matching the dependency order (blockers get lower numbers).
- **NEVER create a single combined file** (e.g., `issues.md`) — the user WILL reject this format. Each issue must be independently readable, movable, and trackable.
- Use the issue body template below for each file. Each file is self-contained with its own title, what-to-build, acceptance criteria, and blocked-by.
- If the user later sets up a tracker, the local files serve as the source of truth for batch import.

#### Issue tracker mode

For each approved slice, publish a new issue to the issue tracker. Use the issue body template below. Apply the `needs-triage` triage label so each issue enters the normal triage flow.

Publish issues in dependency order (blockers first) so you can reference real issue identifiers in the "Blocked by" field.

<issue-template>
## Parent

A reference to the parent issue on the issue tracker (if the source was an existing issue, otherwise omit this section).

## What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Blocked by

- A reference to the blocking ticket (if any)

Or "None - can start immediately" if no blockers.

</issue-template>

Do NOT close or modify any parent issue.

## Pitfalls

### Shell escaping with `gh` CLI (Windows/MSYS)

When creating issues via `gh issue create` inside `execute_code` → `terminal()`, complex body text (backticks, brackets, special chars) breaks bash quoting. **Never pass body inline.** Write the body to a temp file first and use `--body-file`:

```bash
# WRONG — breaks on special chars
gh issue create --title "X" --body "text with backticks `code`"

# RIGHT — write to file first
echo "body content" > /tmp/issue-body.md
gh issue create --title "X" --body-file /tmp/issue-body.md
```

### `write_file` path vs `gh` native path mismatch

`write_file` (hermes tool) writes to MSYS paths (e.g., `/c/Users/...`), but `gh` is a native Windows binary that expects `C:\Users\...` paths. Files written via `write_file` may not be visible to `gh issue create --body-file`.

**Workaround**: Use `write_file` to the project directory (local file mode), then use `terminal` with `cat` heredoc to write temp files that `gh` can read. Or better: write all issues as local files first, git commit+push, then create GitHub issues one at a time via terminal with `--body-file`.

### Recommended flow when gh CLI is available

1. Write all issue files locally via `write_file` to `issues/` directory
2. `git add && git commit && git push`
3. For each issue, create a temp file via `terminal` (cat heredoc), then `gh issue create --body-file`
4. Clean up temp files

### Recommended flow when gh CLI is NOT available or user wants local mode

1. Write all issue files via `write_file` to `issues/` directory (one file per issue)
2. `git add && git commit && git push`
3. Tell user: "Issues created as local files in issues/. You can import them to your tracker later."

### User frustration signal: "no entiendo que estas haciendo"

If the user says they don't understand what you're doing, you're overcomplicating it. **Stop immediately, simplify, and ask what they want.** In to-issues: default to local file mode unless the user explicitly asks for GitHub Issues. Don't fight with tooling — write the files first, push them, deal with the tracker separately.
