---
name: github-cli-batch-ops
description: Batch operations with GitHub CLI (gh) — create issues, labels, branches in bulk from a plan or PRD. Complements to-issues skill by handling the gh CLI mechanics that to-issues leaves implicit.
---

# GitHub CLI Batch Operations

Batch creation of issues, labels, and branches using `gh` CLI. Use when you have a list of approved slices (typically output of `to-issues` skill) and need to materialize them in a GitHub repo.

## When to use

- After `to-issues` produces an approved breakdown AND a GitHub repo exists with `gh` authenticated
- Bulk label creation for an issue triage vocabulary
- Bulk branch creation (one per issue, prefixed `feature/NNN-`)
- Any workflow that needs >3 `gh` calls in sequence

## Prerequisites (verify before starting)

```bash
gh auth status                          # must show authenticated user with `repo` scope
gh repo view --json name,owner          # confirms you're in a repo
```

If either fails, DO NOT proceed with batch operations. Fix auth first.

## Workflow

### 1. Create labels (idempotent)

Labels rarely change. Create them once, ignore "already exists" errors:

```bash
LABELS="needs-triage: D93F0B,scope-ui: 0E8A16,scope-db: 5319E7,scope-auth: D93F0B"
for entry in $LABELS; do
  name="${entry%%:*}"
  color="${entry##*: }"
  gh label create "$name" --color "$color" --force 2>&1
done
```

`--force` updates color/description if label exists. Avoids needing error suppression.

### 2. Create issues — CRITICAL: use --body-file

**NEVER** pass issue body inline via `--body "..."`. Shell escaping will bite you with markdown content (backticks, $, quotes, !).

**ALWAYS** write body to a temp file, then use `--body-file`:

```bash
printf '%s' "$body" > /tmp/issue-body.md
gh issue create \
  --title "001: Project scaffolding" \
  --body-file "/tmp/issue-body.md" \
  --label "needs-triage,scaffolding"
rm /tmp/issue-body.md
```

On Windows (git-bash / MSYS), use `C:/Users/<user>/AppData/Local/Temp/` or repo-local `_body.md`. Avoid `/tmp/` if it doesn't resolve.

### 3. Create branches — one per issue

After committing the docs (PRD, CONTEXT) to `main`:

```bash
for n in 001 002 003 ... 013; do
  git branch "feature/${n}-<slug>"
done
git push origin --all      # one push, not N
```

Use `git push origin --all` once instead of N individual pushes — order of magnitude faster.

### 4. Verify

```bash
gh issue list --limit 20
git branch -r | grep feature/
gh label list
```

## Branch audit and cleanup

### Auditar si branches tienen trabajo real

Antes de confiar que un set de branches representa progreso, verificar que cada una tenga commits propios — no que todas apunten al mismo SHA base:

```bash
# Si todas las branches apuntan al mismo commit, son placeholders vacíos
gh api repos/<owner>/<repo>/branches --jq '.[] | select(.name != "main") | "\(.name): \(.commit.sha[:7])"'
```

Si ves 10+ branches con el mismo SHA de 7 chars, son ficticias. Alguien (o tú en sesión pasada) las creó sin hacer commits.

### Limpieza batch de branches remotas

```bash
for b in feature/001-foo feature/002-bar feature/003-baz; do
  gh api -X DELETE "repos/<owner>/<repo>/git/refs/heads/$b" 2>&1 && echo "deleted: $b"
done
```

Para branches locales, ejecuta por separado (ver P7 abajo):

```bash
for b in feature/001-foo feature/002-bar; do git branch -D "$b"; done
```

## Pitfalls

### P1: Defaulting to local files when tracker exists

`to-issues` skill offers "local file mode" as fallback. When `gh` is authenticated AND a repo exists, GitHub Issues is the default. Local files are the exception, not the rule. **Failing to detect the tracker and writing markdown files into the repo when GitHub Issues was expected = wasted work and frustrated user.**

Decision tree:
1. `gh auth status` works AND `gh repo view` works → use GitHub Issues mode
2. Either fails AND cannot be fixed quickly → local file mode
3. User explicitly asks for local files → local file mode

### P2: Shell escaping with --body

Markdown bodies contain: backticks (`), dollar signs ($), exclamation marks (!), single AND double quotes. Inline `--body "..."` will mangle them. `--body-file` is the only safe path.

### P3: Branch created without parent's .gitignore

When you create `feature/002` from `main` BEFORE the scaffolding branch merges, the new branch lacks `.gitignore`. `git add -A` then tries to stage `node_modules/` (10k+ files). 

**Fix**: either (a) merge scaffolding to `main` first, or (b) commit a minimal `.gitignore` on every feature branch as the first action.

### P4: Git index lock on Windows

If a `git commit` is interrupted (timeout, Ctrl-C), `.git/index.lock` may remain held. Subsequent git commands fail with "Another git process seems to be running".

**Fix**:
```bash
taskkill //F //IM git.exe     # MSYS syntax: double slash for Windows flag
sleep 2
rm -f .git/index.lock
```

Do NOT use `rm -f` alone if a git process is still running — the OS holds the file. Kill the process first.

### P5: gh issue create hangs in CI / non-interactive shells

`gh issue create` opens an editor if `--title` or `--body-file` is missing. In a script, ALWAYS pass both. Set `GIT_EDITOR=true` as belt-and-suspenders if calling from automation.

### P6: Label colors must be hex without `#`

`--color "D93F0B"` ✓  
`--color "#D93F0B"` ✗ (will fail or be stored literally)

### P7: Branches vacías = ficción, no progreso

Crear N branches `feature/NNN-*` sin commits NO es planificación — es ruido. Si todas apuntan al mismo SHA base, no hay trabajo real detrás. El usuario descubrirá que "lo que hiciste ayer" no existe y perderás credibilidad.

**Regla**: un branch sin commits propios no representa progreso verificable. Si creas branches anticipadas, decláralo explícitamente: "Estos son placeholders vacíos, cero código". No dejes que parezca trabajo hecho.

### P8: No mezclar operaciones destructivas con seguras en un solo terminal()

Cuando encadenas `git checkout && git checkout -b && rm -rf X && echo done` en una sola llamada a terminal, el BLOCK del usuario aplica al comando entero. Pierde las operaciones seguras (checkout, branch creation) junto con las destructivas (rm -rf, branch -D).

**Regla**: separa en llamadas distintas. Primero las operaciones seguras (checkout, branch), después las destructivas (delete, rm) en otra llamada. El usuario puede bloquear selectivamente sin perder el trabajo previo.

## Reference files

- `references/batch-issue-creation.md` — full reproduction recipe with loops and idempotency patterns

## Companion skills

- `to-issues` (matt-pocock) — produces the approved slice breakdown; this skill materializes it
- `pr-description` — for PR creation when slices merge back
