# OpenCode Configuration Paths (Windows)

## Directory Structure

```
~/.config/opencode/
├── AGENTS.md              # Global rules (auto-loaded every session)
├── opencode.json          # Provider config, custom instructions
├── skills/                # Global skills
│   ├── tdd/
│   │   └── SKILL.md
│   ├── diagnose/
│   │   └── SKILL.md
│   └── .../
│       └── SKILL.md
└── node_modules/          # (if plugins installed)
```

## Data Locations (post-install, pre-config)

| Path | Purpose | Safe to delete? |
|------|---------|-----------------|
| `~/.config/opencode/` | Config + skills + AGENTS.md | Yes (loses config) |
| `~/AppData/Roaming/opencode/` | EBWebView, session data | Yes |
| `~/.cache/opencode/` | Cache, models.json, bin | Yes (regenerates) |
| `~/.local/share/opencode/` | SQLite DB, auth, logs, repos | Yes (loses auth/sessions) |

## Skill Frontmatter Format

```yaml
---
name: skill-name          # required, lowercase-hyphens, 1-64 chars
description: What it does # required, 1-1024 chars
license: MIT              # optional
metadata:                 # optional
  key: value
---
```

Name must match directory name. Regex: `^[a-z0-9]+(-[a-z0-9]+)*$`

## AGENTS.md Content Structure (recommended)

Combine SOUL.md (identity, tone, anti-patterns) + AGENTS.md (process, rules, skills mapping) into one file. OpenCode injects this into every LLM context.

Key sections to include:
- Identity/role
- Style and tone
- Iron laws (verification, skill loading, surgical changes)
- Engineering flow (skill-to-phase mapping)
- Security rules
