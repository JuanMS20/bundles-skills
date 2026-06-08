---
name: multi-branch-exploration
description: "Map a brownfield codebase across multiple git branches without switching. Identify existing code, conflicts, missing pieces, and integration scope before merge. Use when: exploring multi-branch repos, preparing integration merges, assessing what exists vs what's needed, or when the working directory is on a different branch than the code you need to inspect."
tags: [git, brownfield, codebase-mapping, integration, branch-analysis]
---

# Multi-Branch Exploration

Map code across git branches without checkout. Identify what exists, what's missing, and what conflicts before merging.

## When to Use

- Brownfield project with code spread across multiple branches
- Preparing for integration merge (multiple feature branches → target)
- Need to understand full codebase scope without switching branches
- User asks "what exists in the repo" or "what do we have to work with"

## Anti-Pattern: Checking Out Each Branch

DO NOT `git checkout branch-a` to read files, then `git checkout branch-b`, etc. This:
- Destructs working tree state
- Breaks any running processes
- Loses uncommitted changes
- Is slow and error-prone

Use **read-only** git commands instead.

## Core Commands

```bash
# List all files on a branch (without switching)
git ls-tree -r --name-only <branch>

# Read a specific file from a branch
git show <branch>:<path>

# Filter for code files only
git ls-tree -r --name-only <branch> | grep -E '\.(ts|tsx|js|jsx|py|go|rs)$'

# Compare file lists between branches
diff <(git ls-tree -r --name-only branch-a | sort) \
     <(git ls-tree -r --name-only branch-b | sort)

# Check what a branch has that another doesn't
git ls-tree -r --name-only branch-a | sort > /tmp/a.txt
git ls-tree -r --name-only branch-b | sort > /tmp/b.txt
comm -23 /tmp/a.txt /tmp/b.txt  # files only in branch-a
```

## Workflow

### Step 1: Identify Branches
```bash
git branch -a                    # local + remote branches
git log --oneline -5 <branch>    # recent commits per branch
```

### Step 2: Map File Structure Per Branch
```bash
git ls-tree -r --name-only <branch> | grep -v node_modules | grep -v '.expo'
```
This gives you the full file tree. Group by directory to understand architecture.

### Step 3: Read Key Files
Focus on:
- `package.json` / `pubspec.yaml` / `requirements.txt` — dependencies per branch
- Entry points (`App.tsx`, `App.js`, `main.ts`)
- Configuration (`tsconfig.json`, `babel.config.js`, `metro.config.js`)
- Core types/entities (`domain/`, `types/`)
- Constants (`colors.ts`, `spacing.ts`, `typography.ts`)

```bash
git show <branch>:package.json
git show <branch>:src/constants/colors.ts
```

### Step 4: Identify Conflicts and Gaps
- **Duplicate files** across branches with different content → will conflict on merge
- **Missing files** in target branch that exist in source → need to be added
- **Dependency differences** → `package.json` merge conflicts
- **Import path mismatches** (`@/` vs relative) → will break at runtime

### Step 5: Produce Integration Map
Format as a summary showing:
- What exists per branch (key files, architecture pattern)
- What's missing in the target branch
- Conflicts to resolve (colors, configs, duplicate components)
- Dependencies to reconcile

## Conflict Detection Patterns

### Color/Theme Conflicts
```bash
# Compare color definitions across branches
git show branch-a:src/constants/colors.ts > /tmp/colors-a.ts
git show branch-b:src/constants/colors.ts > /tmp/colors-b.ts
diff /tmp/colors-a.ts /tmp/colors-b.ts
```

### Dependency Conflicts
```bash
# Extract and compare dependencies
git show branch-a:package.json | python -c "import json,sys; print('\n'.join(sorted(json.load(sys.stdin)['dependencies'].keys())))"
git show branch-b:package.json | python -c "import json,sys; print('\n'.join(sorted(json.load(sys.stdin)['dependencies'].keys())))"
```

### Component Duplication
```bash
# Find files with same name across branches
comm -12 <(git ls-tree -r --name-only branch-a | xargs -I{} basename {} | sort -u) \
         <(git ls-tree -r --name-only branch-b | xargs -I{} basename {} | sort -u)
```

## Team Ownership Constraints

In multi-contributor repos, each team member owns specific branches. Before modifying ANY branch:

1. **Ask the user which branches they own** — do NOT assume
2. **Only checkout/edit branches the user owns** — other branches are read-only
3. **Explore other branches with `git show` / `git ls-tree`** — never checkout
4. **Build on the user's branch** — use other branches as reference only

Pattern: "explore for reference → build on owned branch"

Example constraint: "Juan Esteban owns `camara` and `integration`. Zaira owns `home_screen`. Villalobos owns `mapa`. → Only touch `camara` and `integration`."

**If the user doesn't specify ownership → ASK before modifying anything.**

## Architecture Consistency

When integrating code from branches with different architecture patterns:
- **Do NOT assume the user's branch uses the same pattern as other branches**
- **Ask the user which architecture to follow** before writing any code
- If the user says "use the same pattern as branch X" → study branch X's structure first
- Common conflict: Clean Architecture (domain/application/infrastructure) vs Atomic Design (atoms/molecules/organisms/templates)

Pattern: "match the team's chosen architecture, even if the source code uses a different one"

## Pitfalls

- **`git show` fails on binary files** — use `git show branch:path > /tmp/file` for binaries, or skip them
- **Remote branches need fetch first** — run `git fetch --all` before exploring remote branches
- **Branch names with slashes** — quote them: `git show "origin/feature/camara":path`
- **Large repos** — `git ls-tree -r` on entire repo is slow; filter with `grep` early
- **Assuming branch state is current** — branches may have been updated since last fetch; always `git fetch` first

## Verification

After mapping, verify your understanding:
1. Does the branch list match what the user described?
2. Can you read the key entry point files from each branch?
3. Do dependency lists make sense for the claimed stack?
4. Are there obvious conflicts you can预判 before merge?

## Relationship to Other Skills

- **zoom-out**: Complementary — zoom-out operates on code structure; this operates on branch topology
- **code-review**: Use after merge to review the integrated code
- **anti-hallucination**: Verify stack from `package.json` on each branch, don't assume based on docs
