# Kilo Code Configuration Reference

## Verified Config Structure (2026-05-28)

### Provider Format (kilo.jsonc)

```jsonc
{
  "provider": {
    "<provider-name>": {
      "name": "<display-name>",
      "npm": "@ai-sdk/openai-compatible",  // for OpenAI-compatible APIs
      "options": {
        "baseURL": "http://localhost:3000/v1",
        "apiKey": "sk-..."  // optional for local proxies
      },
      "models": {
        "<model-id>": { "name": "<model-id>" },
        "<model-id>-no-thinking": { "name": "<model-id>-no-thinking" }
      }
    }
  }
}
```

### MCP Server Format

```jsonc
"mcp": {
  "<server-name>": {
    "type": "remote" | "local",
    "url": "https://...",           // for remote
    "command": ["npx", "-y", "..."], // for local
    "environment": {},               // optional env vars
    "enabled": true
  }
}
```

### Permissions Format

```jsonc
"permission": {
  "bash": "allow"  // or "deny" or "ask"
}
```

### Instructions Glob

```jsonc
"instructions": [".kilocode/rules/*.md"]
```

## Directory Layout

```
~/.config/kilo/
├── kilo.jsonc          # Main config
├── package.json        # Dependencies
└── bun.lock

~/.kilocode/
├── agent/              # Specialized agents (.agent.md files)
│   ├── architect.agent.md
│   ├── code-reviewer.agent.md
│   └── ...
├── rules/              # Global instructions (.instructions.md files)
│   ├── AGENTS.md
│   ├── coding-style.instructions.md
│   ├── engineering-rules.instructions.md
│   └── ...
├── skills/             # Skills (SKILL.md in each directory)
│   ├── caveman/
│   ├── tdd/
│   └── ...
└── memories/           # Persistent memory files
```

## Matt Pocock Skills in Kilo (verified 2026-05-28)

Skills migrated from OpenCode:
- caveman, diagnose, grill-me, grill-with-docs, handoff
- improve-codebase-architecture, prototype, to-issues, to-prd
- triage, tdd, zoom-out, teach, write-a-skill

Total skills in Kilo: 94

## Known Quirks

- Kilo uses `@ai-sdk/openai-compatible` npm package for OpenAI-compatible providers
- `disabled_providers` array in kilo.jsonc can disable built-in providers
- Rules files use `.instructions.md` extension with YAML frontmatter (`description`, `applyTo`)
- Agent files use `.agent.md` extension
