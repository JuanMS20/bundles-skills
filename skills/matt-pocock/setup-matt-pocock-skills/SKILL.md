---
name: setup-matt-pocock-skills
description: "Setup per-repository configuration for Matt Pocock engineering skills: issue tracker, triage labels, domain docs layout. Use when starting to use Matt Pocock skills in a new repo, or when skills like to-issues, to-prd, triage appear to be missing context about the issue tracker or triage labels."
---

# Setup Matt Pocock Skills

Scaffolds per-repository configuration for the engineering skills suite.

## When to Run

- Before first use of: `to-issues`, `to-prd`, `triage`, `diagnose`, `tdd`, `improve-codebase-architecture`, or `zoom-out` in a new repo.
- If those skills appear to be missing context about the issue tracker, triage labels, or domain docs.

## Process

### 1. Explore
Examine the repo's current state:
- `git remote -v` → Determine GitHub/GitLab
- `AGENTS.md` or `CLAUDE.md` at root → Check for existing `## Agent skills` section
- `CONTEXT.md` & `CONTEXT-MAP.md` at root
- `docs/adr/` directories
- `.scratch/` → Local markdown issue tracker convention

### 2. Three Decisions (one at a time)

**A. Issue Tracker**
- Default: `gh` CLI if GitHub, `glab` if GitLab
- Choices: GitHub, GitLab, Local markdown, Other

**B. Triage Label Vocabulary**
- Canonical states: needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix
- Confirm defaults or override

**C. Domain Docs Layout**
- Single-context (default): One CONTEXT.md + docs/adr/ at root
- Multi-context: CONTEXT-MAP.md at root pointing to per-context files

### 3. Write Configuration

Output `## Agent skills` block for AGENTS.md or CLAUDE.md:

```markdown
## Agent skills
### Issue tracker
[one-line summary]. See `docs/agents/issue-tracker.md`.
### Triage labels
[one-line summary]. See `docs/agents/triage-labels.md`.
### Domain docs
[one-line summary]. See `docs/agents/domain.md`.
```

Write supporting docs in `docs/agents/`.

### 4. Done
Confirm setup. List which skills now read the config files.

## Notes
- Never create AGENTS.md if CLAUDE.md exists (or vice versa)
- Users can edit `docs/agents/*.md` directly later
- Re-run only to switch trackers or restart from scratch
