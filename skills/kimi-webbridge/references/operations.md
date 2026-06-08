# Operations: install, lifecycle, diagnose

Read this file when the health check in SKILL.md indicates the daemon is missing, not running, or the extension isn't connected — or when the user explicitly asks to install, start, stop, restart, or troubleshoot kimi-webbridge.

## Windows Setup (WSL2)

The binary is Linux-only (no Windows build). On Windows, the daemon runs inside WSL2 Ubuntu and a thin wrapper on the Windows side forwards commands to WSL.

### Install (fresh)

```bash
# From Git Bash / MSYS2 — installs inside WSL2 Ubuntu
wsl -d Ubuntu -- bash -c "curl -fsSL https://cdn.kimi.com/webbridge/install.sh | bash -s -- --no-skill"
```

Use `--no-skill` to avoid the installer overwriting this skill with a generic one.

Then create the Windows-side wrapper at `~/.kimi-webbridge/bin/kimi-webbridge`:

```bash
#!/bin/bash
# Wrapper: forwards kimi-webbridge commands to WSL Ubuntu
wsl -d Ubuntu -- bash -c "cd ~ && ./.kimi-webbridge/bin/kimi-webbridge $*"
```

`chmod +x` the wrapper. After this, all commands in this file (`status`, `start`, `stop`, `logs`) work identically from Git Bash.

### Network

WSL2 localhost forwarding means `curl` to `http://localhost:10086` from Windows reaches the daemon inside WSL automatically (HTTP + WebSocket). Do NOT use `--addr 0.0.0.0` — it causes `extension_connected: false` because the Chrome extension's WebSocket connection breaks when the bind address changes from loopback.

## Path convention

- **Linux/macOS:** binary at `~/.kimi-webbridge/bin/kimi-webbridge`
- **Windows (WSL2):** actual binary inside WSL at `/home/<user>/.kimi-webbridge/bin/kimi-webbridge`; Windows wrapper at `~/.kimi-webbridge/bin/kimi-webbridge` (Git Bash)

## Routing table (what to do based on status)

Run: `~/.kimi-webbridge/bin/kimi-webbridge status`

| Observed | Action |
|---|---|
| `command not found` or binary missing | Not installed. Run: `curl -fsSL https://cdn.kimi.com/webbridge/install.sh \| bash` |
| `{"running": false, ...}` | Daemon not running. Run: `~/.kimi-webbridge/bin/kimi-webbridge start` |
| `{"running": true, "extension_connected": false, ...}` | Extension not connected. Tell the user: "If you've already installed the Kimi WebBridge extension, please open your browser and try again. If not yet installed, see https://www.kimi.com/features/webbridge (中文: https://www.kimi.com/zh-cn/features/webbridge) for install instructions." |
| `{"running": true, "extension_connected": true, ...}` | Healthy. Return to the main SKILL.md to make tool calls. |

## /status JSON fields

- `running` (bool) — daemon listening on `:10086`
- `port` (int) — 10086
- `version` (string) — daemon build version
- `extension_connected` (bool) — a WebSocket client is attached
- `extension_id` (string) — the Chrome/Edge extension ID, empty if none
- `uptime_seconds` (int)

## Daily operations

- **Check status:** `~/.kimi-webbridge/bin/kimi-webbridge status`
- **Start:** `~/.kimi-webbridge/bin/kimi-webbridge start` (idempotent — safe to call when already running)
- **Stop:** `~/.kimi-webbridge/bin/kimi-webbridge stop`
- **Restart after unexpected state:** `~/.kimi-webbridge/bin/kimi-webbridge restart`
- **View recent logs:** `~/.kimi-webbridge/bin/kimi-webbridge logs -n 100`
- **Follow logs live:** `~/.kimi-webbridge/bin/kimi-webbridge logs -f`
- **View previous run's logs:** `~/.kimi-webbridge/bin/kimi-webbridge logs --prev`

## Install flags (install.sh)

When running `install.sh`:

- Default: install binary + start daemon + install skills to all detected AI agents
- `--no-start`: install binary + skills, but don't start the daemon
- `--no-skill`: install binary + start daemon, but skip skill installation
- `-h` or `--help`: show usage

## Diagnosing common failures

| Symptom | Action |
|---|---|
| `start` fails with "write pid: open daemon.pid: file exists" | Stale PID file from a crash. Fix: `rm -f ~/.kimi-webbridge/daemon.pid` then `start` again. On Windows: `wsl -d Ubuntu -- bash -c "rm -f ~/.kimi-webbridge/daemon.pid && ~/.kimi-webbridge/bin/kimi-webbridge start"`. |
| `start` fails with "address already in use" | `~/.kimi-webbridge/bin/kimi-webbridge stop && ~/.kimi-webbridge/bin/kimi-webbridge start`; if that fails, `lsof -i :10086` to find the conflicting process. |
| Tool calls time out | `~/.kimi-webbridge/bin/kimi-webbridge logs -n 100` — check for `[error]` / `panic` lines. |
| `extension_connected` stays `false` after install | Browser extension not running. If the user has it installed, ask them to open the browser and retry; otherwise direct them to https://www.kimi.com/features/webbridge (中文: https://www.kimi.com/zh-cn/features/webbridge). |
| `extension_connected` goes `false` after changing `--addr` | Don't use `--addr 0.0.0.0`. The Chrome extension WebSocket connects to loopback. Restart with default addr: `stop && rm -f daemon.pid && start`. |
| `status` returns `extension_connected: true` but tool call fails | May be a multi-browser conflict. `~/.kimi-webbridge/bin/kimi-webbridge logs` will show recent upgrade rejections. |
