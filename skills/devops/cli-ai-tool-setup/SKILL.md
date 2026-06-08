---
name: cli-ai-tool-setup
description: Install, configure, and uninstall AI coding tools (Codex CLI, Claude Code, OpenCode, Kilo Code, Gemini CLI) with custom providers. Covers provider configuration, API key setup, wire_api pitfalls, config migration between tools, complete uninstallation, and verification. Use when user wants to install, configure, migrate, or completely remove any AI coding agent.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cli, codex, opencode, claude-code, kilo-code, providers, setup, configuration, migration, kimi-webbridge]
    related_skills: [anti-hallucination]
---

# CLI AI Tool Setup

## Overview

Install and configure CLI AI coding tools to use custom providers (OpenCode Go, OpenRouter, Ollama, etc.) instead of default APIs. Also covers migrating configurations between tools.

## Tool Install Commands

| Tool | Install | Config Location |
|------|---------|-----------------|
| Codex CLI | `npm install -g @openai/codex` | `~/.codex/config.toml` |
| Claude Code | `npm install -g @anthropic-ai/claude-code` | `~/.claude/settings.json` |
| OpenCode | See opencode.ai/docs | `~/.config/opencode/opencode.json` |
| Kilo Code | VS Code Marketplace | `~/.config/kilo/kilo.jsonc` + `~/.kilocode/` |
| Gemini CLI | `npm install -g @google/gemini-cli` | `~/.gemini/settings.json` |
| Gentle-AI | Go binary / Scoop (see section) | `~/.gentle-ai/state.json` |
| Kimi WebBridge | WSL: `curl ... \| bash` (see references/kimi-webbridge-setup.md) | `~/.kimi-webbridge/` |

## Codex CLI Configuration

### Config Format (v0.134.0+)

```toml
model = "<model-id>"
model_provider = "<provider-id>"

[model_providers.<provider-id>]
name = "Display Name"
base_url = "https://api.example.com/v1"
env_key = "ENV_VAR_NAME"
wire_api = "responses"  # CRITICAL: "chat" no longer supported
```

### CRITICAL: wire_api Change

**v0.134.0+:** `wire_api = "chat"` is NO LONGER SUPPORTED. Use `wire_api = "responses"` even for OpenAI Chat Completions-compatible endpoints.

Error if wrong:
```
Error loading config.toml: `wire_api = "chat"` is no longer supported.
How to fix: set `wire_api = "responses"` in your provider config.
```

### Custom Provider Example (OpenCode Go)

```toml
model = "mimo-v2.5"
model_provider = "opencodego"

[model_providers.opencodego]
name = "OpenCode Go"
base_url = "https://opencode.ai/zen/go/v1"
env_key = "OPENCODEGO_API_KEY"
wire_api = "responses"
```

### Environment Variables

```bash
export OPENCODEGO_API_KEY="***"
codex "di hola"
```

### Verification

```bash
codex doctor  # Check config loads correctly
# Look for: ✓ config loaded
```

### Profiles

```toml
[profiles.glm]
model = "glm-5.1"
model_provider = "opencodego"

[profiles.kimi]
model = "kimi-k2.5"
model_provider = "opencodego"
```

Usage: `codex --profile kimi "tu prompt"`

## OpenCode Go Provider

**⚠️ CRITICAL:** OpenCode Go only supports Chat Completions API. Codex CLI v0.134+ only speaks Responses API. These are incompatible — Codex will return 404 errors. Use OpenCode CLI instead for OpenCode Go models. See `references/responses-api-incompatibility.md` for alternatives.

| Model | ID |
|-------|-----|
| GLM-5.1 | `glm-5.1` |
| GLM-5 | `glm-5` |
| Kimi K2.5 | `kimi-k2.5` |
| DeepSeek V4 Pro | `deepseek-v4-pro` |
| MiMo V2 Pro | `mimo-v2-pro` |
| MiniMax M2.5 | `minimax-m2.5` |
| Qwen 3.5 Plus | `qwen3.5-plus` |

Base URL: `https://opencode.ai/zen/go/v1`

## Gentle-AI (Ecosystem Configurator)

**⚠️ NOT an agent installer.** Gentle-AI is an ecosystem configurator that adds persistent memory, SDD workflows, skills, and persona to existing AI coding agents (Claude Code, OpenCode, Cursor, etc.).

### Install Methods (Windows)

| Method | Command | Notes |
|--------|---------|-------|
| **Binary (recommended)** | Download from GitHub releases | No dependencies needed |
| Scoop | `scoop bucket add gentleman https://github.com/Gentleman-Programming/scoop-bucket && scoop install gentle-ai` | Best for upgrades |
| Go install | `go install github.com/Gentleman-Programming/gentle-ai/cmd/gentle-ai@latest` | Requires Go 1.24+ |

**⚠️ CRITICAL: No curl/wget install script exists.** Users frequently confuse this with npm-style tools. The only install methods are Go binary, Scoop, or direct download from GitHub releases.

### Binary Install (Windows)

```bash
# Download latest release (check https://github.com/Gentleman-Programming/gentle-ai/releases)
curl -L -o gentle-ai.zip https://github.com/Gentleman-Programming/gentle-ai/releases/download/v1.34.0/gentle-ai_1.34.0_windows_amd64.zip
unzip gentle-ai.zip
mkdir -p ~/bin
mv gentle-ai.exe ~/bin/
```

**Verification:** `gentle-ai --version` should return version number.

### Post-Install Setup

```bash
gentle-ai doctor          # Health check
/sdd-init                 # In project dir — detect stack
gentle-ai skill-registry refresh  # Scan skills
```

## Complete Uninstall (Windows)

CLI AI tools scatter files across multiple locations. Package manager remove alone is NOT sufficient.

### OpenCode — Full Path Inventory (verified 2026-05-28)

| Location | Contains | How to remove |
|----------|----------|---------------|
| `~/AppData/Local/opencode/` | Desktop app binaries (OpenCode.exe, opencode-cli.exe, uninstall.exe) | Run `uninstall.exe /S` (NSIS silent mode) |
| `~/.bun/bin/opencode` | Bun global CLI binary (15KB shim) | `rm ~/.bun/bin/opencode` — **CRITICAL: `bun remove -g opencode-ai` removes the package but leaves this binary behind** |
| `~/.config/opencode/` | Config (opencode.json), skills, agents, AGENTS.md, node_modules, bun.lock | `rm -rf ~/.config/opencode/` |
| `~/AppData/Roaming/opencode/` | EBWebView data, opencode.json | `rm -rf ~/AppData/Roaming/opencode/` |
| `~/.cache/opencode/` | Cache, bin, models.json, node_modules, packages | `rm -rf ~/.cache/opencode/` |
| `~/.local/share/opencode/` | SQLite DB (opencode.db), auth.json, logs, repos, snapshots, storage, tool-output | `rm -rf ~/.local/share/opencode/` |

### Uninstall Sequence (OpenCode on Windows)

```bash
# 1. Desktop app — silent uninstall
cd ~/AppData/Local/opencode && ./uninstall.exe /S

# 2. Bun global package — remove package
bun remove -g opencode-ai

# 3. CRITICAL — bun remove leaves the binary behind
rm -f ~/.bun/bin/opencode

# 4. Config, data, cache — full purge
rm -rf ~/.config/opencode/
rm -rf ~/AppData/Roaming/opencode/
rm -rf ~/.cache/opencode/
rm -rf ~/.local/share/opencode/

# 5. Verify clean
which opencode  # should return nothing
ls ~/.bun/bin/opencode 2>/dev/null  # should fail
```

### Post-Uninstall Verification

```bash
which opencode                              # not found
reg query "HKCU\Software\...\Uninstall" /s /f "opencode"  # no matches
ls ~/.config/opencode 2>/dev/null           # not found
ls ~/.local/share/opencode 2>/dev/null      # not found
```

See `references/opencode-uninstall-windows.md` for detailed path inventory, sizes, and a ready-to-run removal script.

### Pitfall — bun remove leaves binary behind

**`bun remove -g` does NOT clean `~/.bun/bin/`**. After removing the package, the binary shim persists. Always `rm -f ~/.bun/bin/<tool>` after `bun remove -g`.

## OpenCode Configuration

### Global Rules (AGENTS.md)

OpenCode loads `~/.config/opencode/AGENTS.md` automatically in every session. This is the global rules file — equivalent to Hermes's SOUL.md + AGENTS.md combined.

```bash
mkdir -p ~/.config/opencode
# Write your combined rules to:
# ~/.config/opencode/AGENTS.md
```

**Precedence:** Project-level `AGENTS.md` > global `~/.config/opencode/AGENTS.md` > `~/.claude/CLAUDE.md` (fallback).

### Skills Directory

OpenCode discovers skills from `~/.config/opencode/skills/<skill-name>/SKILL.md`. Each skill needs:
- Directory name matching the skill name (lowercase, hyphens)
- `SKILL.md` with YAML frontmatter: `name` (required) + `description` (required)

```bash
mkdir -p ~/.config/opencode/skills
```

**Discovery paths (in order):**
1. `.opencode/skills/*/SKILL.md` (project)
2. `~/.config/opencode/skills/*/SKILL.md` (global)
3. `.claude/skills/*/SKILL.md` (project, Claude fallback)
4. `~/.claude/skills/*/SKILL.md` (global, Claude fallback)
5. `.agents/skills/*/SKILL.md` (project, agents fallback)
6. `~/.agents/skills/*/SKILL.md` (global, agents fallback)

### Installing Matt Pocock Skills (Global)

```bash
# Clone, copy, clean up
git clone https://github.com/mattpocock/skills.git /tmp/mp-skills
cp -r /tmp/mp-skills/skills/engineering/* ~/.config/opencode/skills/
cp -r /tmp/mp-skills/skills/productivity/* ~/.config/opencode/skills/
cp -r /tmp/mp-skills/skills/misc/* ~/.config/opencode/skills/
rm -rf /tmp/mp-skills
```

Skills already have correct frontmatter (`name` + `description`). No conversion needed.

**Included skills:** caveman, diagnose, grill-me, grill-with-docs, handoff, improve-codebase-architecture, prototype, setup-matt-pocock-skills, tdd, to-issues, to-prd, triage, write-a-skill, zoom-out, + misc (git-guardrails-claude-code, migrate-to-shoehorn, scaffold-exercises, setup-pre-commit).

### Custom Instructions via opencode.json

Reference additional instruction files in `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["CONTRIBUTING.md", "docs/guidelines.md"]
}
```

Glob patterns and remote URLs supported.

### Verification

```bash
opencode --version           # confirms install
ls ~/.config/opencode/       # AGENTS.md + skills/
ls ~/.config/opencode/skills/ # skill directories
```

## Kilo Code Configuration

### Token Consumption Audit

High token usage? See `references/kilo-code-token-audit.md` for the diagnostic methodology: how to identify which rules, skills, agents, and MCP servers are consuming tokens, and how to reduce the budget.

### Directory Structure

Kilo Code uses two config directories:
- `~/.config/kilo/kilo.jsonc` — providers, MCP servers, permissions, instructions
- `~/.kilocode/` — agents, rules, skills, memories

### Config File (kilo.jsonc)

```jsonc
{
  "$schema": "https://app.kilo.ai/config.json",
  "provider": {
    "my-provider": {
      "name": "my-provider",
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "baseURL": "http://localhost:3000/v1"
      },
      "models": {
        "model-name": { "name": "model-name" }
      }
    }
  },
  "permission": { "bash": "allow" },
  "instructions": [".kilocode/rules/*.md"],
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "enabled": true
    }
  }
}
```

### Agents Directory (~/.kilocode/agent/)

Each agent is a `.agent.md` file with role-specific instructions:

```
~/.kilocode/agent/
├── architect.agent.md
├── code-reviewer.agent.md
├── security-reviewer.agent.md
├── tdd-guide.agent.md
└── ...
```

### Rules Directory (~/.kilocode/rules/)

Instruction files loaded into every session via `instructions` glob:

```
~/.kilocode/rules/
├── AGENTS.md                    # Main behavioral protocols
├── coding-style.instructions.md # Code style rules
├── security.instructions.md     # Security rules
├── engineering-rules.instructions.md  # Core engineering principles
└── ...
```

### Skills Directory (~/.kilocode/skills/)

Standard skill structure — each skill is a directory with SKILL.md:

```bash
mkdir -p ~/.kilocode/skills/my-skill
# Write SKILL.md with YAML frontmatter (name + description)
```

### MCP Servers

Kilo Code supports stdio and remote MCP servers. Common setup:

```jsonc
"mcp": {
  "context7": { "type": "remote", "url": "https://mcp.context7.com/mcp", "enabled": true },
  "playwright": { "type": "local", "command": ["npx", "-y", "@playwright/mcp"], "enabled": true },
  "memory": { "type": "local", "command": ["npx", "-y", "@modelcontextprotocol/server-memory"], "enabled": true }
}
```

### Verification

```bash
ls ~/.config/kilo/kilo.jsonc    # Config exists
ls ~/.kilocode/agent/           # Agents present
ls ~/.kilocode/rules/           # Rules present
ls ~/.kilocode/skills/          # Skills present
```

## Config Migration Between AI Tools

When migrating rules, skills, or configurations between AI coding tools (e.g., OpenCode → Kilo Code):

### What Transfers Directly

- **Generic skills** (TDD, debugging, architecture patterns) — copy SKILL.md files as-is
- **Engineering principles** (code minimalism, surgical changes, verification) — rewrite for target tool's format
- **MCP server configs** — same JSON structure works across tools
- **Provider configs** — adapt base URL and model names to target tool's schema

### What Needs Adaptation

- **AGENTS.md / rules files** — strip references to source tool's APIs:
  - `skill_view()` → remove or replace with target tool's skill loading mechanism
  - `fact_store` / `fact_feedback` → remove (tool-specific)
  - `session_search` → remove (tool-specific)
  - `hermes-wiki/` paths → remove or replace with target tool's memory system
- **Identity files** (SOUL.md, persona definitions) — usually tool-specific, don't copy
- **Provider schemas** — each tool has its own config format (JSONC for OpenCode, JSON for Kilo, TOML for Codex)

### What NOT to Copy

- Tool-specific API references (`skill_view`, `fact_store`, `session_search`)
- Identity/persona files that reference the source tool's internals
- Paths to source tool's directories (`~/.config/opencode/`, `~/.hermes/`)

### Migration Pattern

```
1. Identify target tool's config structure
2. Copy generic skills (verify SKILL.md frontmatter matches target format)
3. Extract principles from rules files (strip tool-specific refs)
4. Create new rules file in target tool's format
5. Verify: ls target config dirs, check file counts
6. Restart target tool to load new config
```

## Pitfalls

**`bun remove -g` does NOT clean `~/.bun/bin/`**. After removing the package, the binary shim persists. Always `rm -f ~/.bun/bin/<tool>` after `bun remove -g`.

## Common Pitfalls

1. **Kimi WebBridge install.sh fails on Windows.** The script only supports macOS and Linux. On Windows, run through WSL: `wsl curl -fsSL https://cdn.kimi.com/webbridge/install.sh | wsl bash`. See `references/kimi-webbridge-setup.md`.
2. **Gentle-AI has no curl install script.** Users try `curl ... | bash` — this does not work. Gentle-AI is a Go binary. Use direct download from GitHub releases, Scoop, or `go install`.
2. **CRITICAL — Responses API incompatibility:** v0.134.0+ requires `wire_api = "responses"`, which sends requests to `/v1/responses` (OpenAI's proprietary format). Providers that only support Chat Completions API (`/v1/chat/completions`) — like OpenCode Go — return **404 Not Found**. See `references/responses-api-incompatibility.md` for details and workarounds.
2. **wire_api mismatch:** v0.134.0+ requires `wire_api = "responses"` for all providers. `"chat"` throws a hard error since Feb 2026 (PR #10157, discussion #7782).
3. **env_key is a variable NAME, not the key itself:** `env_key = "OPENCODEGO_API_KEY"` tells Codex to read from the env var named `OPENCODEGO_API_KEY`. Do NOT paste the actual API key into `env_key`.
4. **Config not loading:** Run `codex doctor` to diagnose. Check for parse errors.
5. **API key missing:** Set env var before running codex. Use `export` in bash or add to `.bashrc`.
6. **Model not found:** Verify model ID matches provider's catalog exactly.
7. **Model metadata warning:** `Model metadata for X not found` — non-OpenAI models lack Codex metadata. Functionality degrades but works.
8. **Security — API keys in terminal output:** Codex may echo API key in error messages. Never paste API keys into config files or share terminal output with keys visible. Rotate immediately if exposed.

## Verification Checklist

- [ ] Tool installed and accessible via PATH
- [ ] Config file exists at correct location
- [ ] `wire_api = "responses"` (not `"chat"`)
- [ ] Provider actually supports Responses API (`/v1/responses`) — if not, see `references/responses-api-incompatibility.md`
- [ ] API key env var set and exported
- [ ] `codex doctor` shows config loaded
- [ ] Test prompt works: `codex "di hola"`

---

## AI Assistant Configuration Optimization

Subsumed from `ai-assistant-config-optimization`. Audit and optimize AI coding assistant configurations to reduce token overhead per request.

### Investigation Phase

**1. Locate Config Directory**

| Assistant | Config Path |
|-----------|-------------|
| Kilo Code | `~/.kilocode/` |
| Claude Code | `~/.claude/` or project `.claude/` |
| Copilot | `~/.copilot/` or `.github/copilot-instructions.md` |
| Roo Code | `.roo/` |
| Cline | `.cline/` |

**2. Analyze Rules (Highest Impact)** — Rules with `applyTo: "**"` inject into EVERY request:
- Count files with `applyTo: "**"`
- Check for conceptual overlap between global rules
- Check if rules duplicate skill content (rules auto-inject; skills load on-demand)
- Measure total bytes of globally-injected rules → divide by 3 for estimated tokens

**3. Analyze Skills** — 60+ skill descriptions ≈ ~6,000 tokens of metadata:
- Target: 30-40 active skills
- Identify overlapping pairs and irrelevant skills

**4. Analyze Agents** — Each agent ≈ 150-400 bytes of metadata per request:
- Target: 12-18 active agents
- Archive language-specific reviewers not in use

**5. Estimate Total Overhead**

```
Static overhead per request:
  Global rules:    N_rules × ~500 bytes ÷ 3 = ~tokens
  System prompt:   ~3,000-5,000 tokens
  Tool definitions: ~3,000-8,000 tokens
  Skill metadata:  N_skills × ~100 tokens
  Agent metadata:  N_agents × ~200 tokens
  ─────────────────────────────────────
  TOTAL STATIC:    ~10,000-20,000 tokens (before project context)
```

### Optimization Phase (priority order)

1. **Merge overlapping global rules** — saves ~500-2,000 tokens/request
2. **Delete rules that duplicate skills** — rules auto-inject; skills load on-demand
3. **Delete redundant small rules** — saves ~50 tokens/request
4. **Archive irrelevant skills** — move to `_archive/` (never delete)
5. **Archive unused agents** — move to `_archive/`
6. **Fix broken references** — scan all agents for backtick references to archived skills

### Rules vs Skills Decision Matrix

| Scenario | Action |
|----------|--------|
| Rule has `applyTo: "**"` + skill exists | Delete rule, keep skill |
| Rule has specific `applyTo` + skill exists | Keep both |
| Rule has no `applyTo` + skill exists | Delete rule |
| Rule covers topic well + no skill needed | Keep rule |

**Rule of thumb**: If topic is relevant to <50% of requests → skill (on-demand), not rule (always injected).

### Skill Merging Workflow

1. Read both SKILL.md files completely
2. Identify unique content in each
3. Choose the better structure as base
4. Write merged SKILL.md targeting <150 lines
5. Move unique linked files into the kept skill's directory
6. Archive absorbed skill to `_archive/`
7. Scan all agents for references to archived skill — fix immediately

### Pitfalls

- **Broken references after archiving is #1 post-optimization bug** — scan every agent file
- **Token savings compound** — removing 3 rules + archiving 30 skills + archiving 10 agents ≈ 6,500 tokens saved per request
- **Verify after every batch** — check no broken references, no accidental deletions

### References
- `references/kilo-code-config-structure.md` — directory layout, token cost breakdown
- `references/kilo-code-real-world-findings.md` — real optimization session results
