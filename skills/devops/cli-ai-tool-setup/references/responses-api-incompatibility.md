# Responses API vs Chat Completions Incompatibility

## Problem

Codex CLI v0.134.0+ only supports `wire_api = "responses"` (OpenAI Responses API format).
This sends requests to `/v1/responses` endpoint.

Many providers (including OpenCode Go) only support Chat Completions API (`/v1/chat/completions`).

Result: **404 Not Found** when Codex tries to call `/v1/responses` on a provider that doesn't support it.

## Timeline

- **Dec 9, 2025:** Deprecation announced (discussion #7782)
- **Feb 1, 2026:** `wire_api = "chat"` removed (PR #10157)
- **May 2026:** Current state — hard error, no fallback

## Evidence

```
# Error when using Codex v0.134 with OpenCode Go:
⚠ Model metadata for `mimo-v2.5` not found. Defaulting to fallback metadata
■ unexpected status 404 Not Found: ... url: https://opencode.ai/zen/go/v1/responses
```

OpenCode Go endpoint only supports:
- `POST /v1/chat/completions` ✓
- `POST /v1/responses` ✗ (404)

## Workarounds

### Option 1: Use OpenCode CLI (Recommended)

OpenCode CLI natively supports OpenCode Go with all models.
No bridge, no compatibility layer needed.

```bash
# Install OpenCode CLI (see opencode.ai/docs)
opencode init
# Connect to OpenCode Go via /connect command
```

### Option 2: VibeAround API Bridge

Local bridge that translates Responses API ↔ Chat Completions API.

```
Codex (responses) → VibeAround (localhost) → Chat Completions → Provider
```

- Repo: https://github.com/jazzenchen/VibeAround
- Supports: function tool calls, streaming, reasoning metadata
- Tradeoff: additional local process, maintenance burden

### Option 3: Downgrade Codex CLI

Last version with `wire_api = "chat"` support (deprecated but functional):
```bash
npm install -g @openai/codex@0.100
```

Tradeoff: Missing recent features, security patches.

### Option 4: Use provider that supports Responses API

Some providers have added Responses API support:
- OpenRouter (partial)
- LM Studio (via conversion)
- vLLM (limited)

Check provider docs for `/v1/responses` endpoint support.

## Provider Compatibility Matrix

| Provider | Chat Completions | Responses API | Codex v0.134+ compatible? |
|----------|-----------------|---------------|---------------------------|
| OpenAI | ✓ | ✓ | ✓ |
| OpenCode Go | ✓ | ✗ | ✗ (use OpenCode CLI) |
| OpenRouter | ✓ | Partial | Maybe |
| Ollama | ✓ | ✗ | ✗ (use --oss flag) |
| LM Studio | ✓ | Via conversion | Maybe |
| Anthropic | ✓ (Messages) | ✗ | ✗ (use Claude Code) |
| Google Gemini | ✓ | ✓ | ✓ |

## Key Insight

The Responses API is OpenAI's proprietary format optimized for reasoning models and agentic workflows. It's not a standard. Non-OpenAI providers adopting it is optional and slow. For maximum provider compatibility, tools other than Codex CLI (like OpenCode, Claude Code) may be better choices.

## References

- Discussion: https://github.com/openai/codex/discussions/7782
- PR removing chat: https://github.com/openai/codex/pull/10157
- VibeAround bridge: https://github.com/jazzenchen/VibeAround
- OpenCode Go docs: https://opencode.ai/docs/go
