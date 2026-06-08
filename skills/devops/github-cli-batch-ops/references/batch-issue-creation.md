# Batch Issue Creation — Recipe

## Scenario

You have N approved issues (from `to-issues` or similar breakdown) and a GitHub repo with `gh` CLI authenticated. Create all issues in dependency order with labels, then create matching branches.

## Pre-flight checks

```bash
gh auth status | grep -q "Logged in" || { echo "gh not authenticated"; exit 1; }
gh repo view --json name >/dev/null 2>&1 || { echo "Not in a repo"; exit 1; }
```

## Step 1: Triage labels

```bash
LABELS=(
  "needs-triage:D93F0B"
  "scope-ui:0E8A16"
  "scope-db:5319E7"
  "scope-auth:D93F0B"
)
for entry in "${LABELS[@]}"; do
  name="${entry%%:*}"
  color="${entry##*:}"
  gh label create "$name" --color "$color" --force
done
```

`--force` makes it idempotent — re-running updates color/description without erroring on duplicates.

## Step 2: Issue creation (DO NOT inline body)

Anti-pattern (will break on real markdown):
```bash
gh issue create --title "X" --body "Here is some \`code\` and $variable"  # FAILS
```

Correct pattern:
```bash
for issue in "${ISSUES[@]}"; do
  title=$(extract_title "$issue")
  labels=$(extract_labels "$issue")
  body=$(extract_body "$issue")

  # Write to repo-local temp file (works on Windows + Unix)
  echo "$body" > _body.md

  gh issue create \
    --title "$title" \
    --body-file "_body.md" \
    --label "$labels"

  rm -f _body.md
done
```

## Step 3: Branches (one push, not N)

```bash
SLUGS=("001-scaffolding" "002-schema" "003-seed")
for slug in "${SLUGS[@]}"; do
  git branch "feature/$slug"
done

# Single push for all new branches
git push origin --all
```

## Step 4: Verify counts match

```bash
ISSUE_COUNT=$(gh issue list --limit 50 --json number --jq 'length')
BRANCH_COUNT=$(git branch -r | grep -c 'feature/')
echo "Issues: $ISSUE_COUNT  Branches: $BRANCH_COUNT"
```

## Common errors and fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `HTTP 422: Validation Failed` | Invalid label color (e.g. `#FFF`) | Use `FFF` without `#` |
| `resource not found` | Wrong repo context | Run `gh repo set-default` |
| `editor was not provided` | Missing `--title` or `--body-file` | Always pass both in scripts |
| `index.lock` busy | Previous git op was killed | `taskkill //F //IM git.exe; rm -f .git/index.lock` |
| 10k files staged | Missing `.gitignore` on feature branch | Commit `.gitignore` first on every branch |

## See also

- SKILL.md `github-cli-batch-ops` — main skill documentation
- `to-issues` skill (matt-pocock) — produces the breakdown this recipe consumes
