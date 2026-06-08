# Kilo Code — Config Structure Reference

## Directory Layout

```
~/.kilocode/
├── rules/                    # Instruction files (auto-injected by applyTo)
│   ├── *.instructions.md     # Rules with YAML frontmatter + applyTo
│   ├── DESIGN.md             # System role (no applyTo = manual load)
│   └── *.md                  # Pattern files, style guides
├── skills/                   # Skill definitions
│   ├── skill-name/
│   │   ├── SKILL.md          # Main instructions (required)
│   │   ├── references/       # Detailed docs (loaded on demand)
│   │   ├── scripts/          # Executable code
│   │   └── assets/           # Templates, images
│   └── _archive/             # Archived (inactive) skills
├── agent/                    # Subagent definitions
│   ├── *.agent.md            # Agent configs (all mode: subagent)
│   └── _archive/             # Archived agents
└── node_modules/             # SDK dependencies
```

## Rules Injection Mechanics

Rules with `applyTo: "**"` in YAML frontmatter are injected into EVERY API request.
Rules with specific patterns (e.g., `applyTo: "**/*.{ts,tsx}"`) inject only for matching files.
Rules without `applyTo` are NOT auto-injected — loaded manually or by mode.

## Token Cost Breakdown (typical Kilo Code request)

| Component | Tokens | Notes |
|-----------|--------|-------|
| Kilo base system prompt | ~3,000-5,000 | Built-in, not configurable |
| Tool definitions | ~3,000-8,000 | Depends on enabled tools |
| Global rules (applyTo: **) | ~2,000-6,000 | YOUR biggest lever |
| Skill metadata | ~100 × N_skills | Name + description only |
| Agent metadata | ~200 × N_agents | Name + role description |
| Project context | ~15,000-25,000 | File tree, indexed code |
| Conversation history | grows per turn | Compacted at ~80% |

## Archived Skills Location

Archived skills go to `~/.kilocode/skills/_archive/` — they are NOT loaded but remain recoverable.
