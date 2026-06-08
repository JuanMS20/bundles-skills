# OpenCode Go + Codex CLI Configuration Reference

## Provider Details

- **Provider ID:** `opencodego`
- **Base URL:** `https://opencode.ai/zen/go/v1`
- **Wire API:** `responses` (v0.134.0+)
- **Auth Env Var:** `OPENCODEGO_API_KEY`

## Available Models

| Model | ID | Context |
|-------|-----|---------|
| GLM-5.1 | `glm-5.1` | 205K |
| GLM-5 | `glm-5` | 205K |
| Kimi K2.5 | `kimi-k2.5` | 205K |
| Kimi K2.6 | `kimi-k2.6` | 205K (3x limits) |
| DeepSeek V4 Pro | `deepseek-v4-pro` | 205K |
| DeepSeek V4 Flash | `deepseek-v4-flash` | 205K |
| MiMo V2 Omni | `mimo-v2-omni` | 205K |
| MiMo V2 Pro | `mimo-v2-pro` | 205K |
| MiniMax M2.5 | `minimax-m2.5` | 205K |
| MiniMax M2.7 | `minimax-m2.7` | 205K |
| Qwen 3.5 Plus | `qwen3.5-plus` | 262K |
| Qwen 3.6 Plus | `qwen3.6-plus` | 262K |

## Complete config.toml Template

```toml
# Codex CLI - OpenCode Go Configuration

model = "mimo-v2.5"
model_provider = "opencodego"

[model_providers.opencodego]
name = "OpenCode Go"
base_url = "https://opencode.ai/zen/go/v1"
env_key = "OPENCODEGO_API_KEY"
wire_api = "responses"

# Optional: MCP Servers
# [mcp_servers.example]
# command = "path/to/server"
# args = ["--flag"]

# Optional: Profiles
# [profiles.glm]
# model = "glm-5.1"
# model_provider = "opencodego"

# [profiles.kimi]
# model = "kimi-k2.5"
# model_provider = "opencodego"

# [profiles.deepseek]
# model = "deepseek-v4-pro"
# model_provider = "opencodego"

# [profiles.mimo]
# model = "mimo-v2-pro"
# model_provider = "opencodego"

# [profiles.qwen]
# model = "qwen3.5-plus"
# model_provider = "opencodego"
```

## Setup Script

```bash
#!/bin/bash
# Usage: bash setup-opencodego.sh YOUR_API_KEY

if [ -z "$1" ]; then
    echo "Usage: bash setup-opencodego.sh YOUR_API_KEY"
    echo ""
    echo "Get API key at: https://opencode.ai"
    exit 1
fi

KEY="$1"

# Detect shell profile
if [ -f "$HOME/.bashrc" ]; then
    PROFILE="$HOME/.bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
    PROFILE="$HOME/.bash_profile"
elif [ -f "$HOME/.zshrc" ]; then
    PROFILE="$HOME/.zshrc"
else
    PROFILE="$HOME/.bashrc"
    touch "$PROFILE"
fi

# Remove previous line if exists
sed -i '/export OPENCODEGO_API_KEY=/d' "$PROFILE"

# Add new key
echo "export OPENCODEGO_API_KEY=\"$KEY\"" >> "$PROFILE"
export OPENCODEGO_API_KEY="$KEY"

echo "✓ API key configured in $PROFILE"
echo "✓ Environment variable active in this session"
echo ""
echo "Test with:"
echo "  codex \"di hola\""
echo ""
echo "Available models:"
echo "  codex --profile glm \"your prompt\"      (GLM-5.1 - default)"
echo "  codex --profile kimi \"your prompt\"     (Kimi K2.5)"
echo "  codex --profile deepseek \"your prompt\" (DeepSeek V4 Pro)"
echo "  codex --profile mimo \"your prompt\"     (MiMo V2 Pro)"
echo "  codex --profile qwen \"your prompt\"     (Qwen 3.5 Plus)"
```

## Troubleshooting

### Config not loading

```bash
codex doctor
# Check for: ✓ config loaded
# If ✗, read error message for details
```

### wire_api error

```
Error loading config.toml: `wire_api = "chat"` is no longer supported.
How to fix: set `wire_api = "responses"` in your provider config.
```

**Fix:** Change `wire_api = "chat"` to `wire_api = "responses"` in config.toml.

### Auth error

```
✗ auth active model provider auth env var is missing
```

**Fix:** Set the API key:
```bash
export OPENCODEGO_API_KEY="***"
```

### Model not found

Verify model ID matches the provider's catalog. OpenCode Go uses IDs like `mimo-v2.5`, `glm-5.1`, etc.

## References

- OpenCode Go docs: https://opencode.ai/docs/go
- Codex CLI config: https://developers.openai.com/codex/config-advanced
- wire_api change: https://github.com/openai/codex/discussions/7782
