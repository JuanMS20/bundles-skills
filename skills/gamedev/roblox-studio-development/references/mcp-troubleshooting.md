# Roblox Studio MCP Troubleshooting

## Context: Two MCP Eras

| Era | Transport | Binary | Status |
|-----|-----------|--------|--------|
| **Old** (2024) | Port-based (19199) | `MCPPlugin.rbxmx` (plugin) | ❌ Deprecated by Roblox |
| **New** (2025+) | stdio | `StudioMCP.exe` (built-in) | ✅ Recommended |

The new built-in MCP ships with Roblox Studio — no plugin installation needed. It communicates via **stdio transport**, not a network port.

**The old port 19199 is no longer used.** If you see port 19199 in use, it's from a stale old instance.

## Hermes MCP Config (Windows)

```yaml
mcp_servers:
  Roblox_Studio:
    command: cmd.exe
    args:
    - /c
    - '%LOCALAPPDATA%\Roblox\mcp.bat'
    timeout: 60
```

The `mcp.bat` file resolves `StudioMCP.exe` from the current Roblox Studio version:

```batch
@echo off
if exist "%LOCALAPPDATA%\Roblox\Versions\version-*\StudioMCP.exe" (
    "%LOCALAPPDATA%\Roblox\Versions\version-*\StudioMCP.exe" %*
) else (for /f "tokens=2*" %%A in (
    'reg query HKEY_CURRENT_USER\Software\Roblox\RobloxStudio /v ContentFolder'
) do (
    "%%B/..\StudioMCP.exe" %*
))
```

## Symptom: MCP tools fail intermittently ("Target is not reachable" / "unreachable")

### Diagnostic Steps

```bash
# 0. CRITICAL: Is a Place/Map loaded in Studio? (most common "works but doesn't" cause)
#    The MCP needs an active place as target. If Studio shows only the start screen
#    or no viewport, ALL tools fail with "doesn't have a place opened" or "Target is not reachable".
#    Fix: File → New (Baseplate) or File → Open. Confirm 3D viewport is visible.

# 1. Is Roblox Studio running?
tasklist.exe | grep -i "roblox"

# 2. Does the MCP binary exist?
ls "%LOCALAPPDATA%\Roblox\Versions\version-*\StudioMCP.exe"

# 3. Is the old port-based MCP still running?
netstat -ano | findstr "19199"

# 4. List old plugin files that can interfere
ls "%LOCALAPPDATA%\Roblox\Plugins\"

# 5. Check studio connection (try this tool first — it's most resilient)
# → list_roblox_studios
```

### Error Decoding

| Error | Meaning |
|-------|---------|
| `list_roblox_studios` succeeds → other tools fail with "doesn't have a place opened" | **No Place/Map loaded in Studio.** The MCP is alive but has no target. Fix: File → New (or Open), ensure a Baseplate/place is loaded in the viewport. Then toggle MCP OFF/ON. |
| `list_roblox_studios` succeeds → other tools fail (generic) | MCP server is running but the active session is broken. Toggle "Enable Studio as MCP server" OFF/ON in Assistant → Manage MCP Servers. If persistent, check "no Place opened" first (see row above). |
| `list_roblox_studios` succeeds → "Target is not reachable" | MCP process is alive but Studio plug-in session dropped. Same fix: restart both. |
| "MCP server is unreachable after N consecutive failures" | The MCP process crashed or was killed. Restart Studio or restart the MCP process. |
| All tools return "[error]" with no detail | `action=write` may have hit the timeout limit. Increase `timeout` in Hermes config. |

### Root Cause: Old Plugin Interference

Old plugin files in `%LOCALAPPDATA%\Roblox\Plugins\` can conflict with the built-in MCP:

```
%LOCALAPPDATA%\Roblox\Plugins\
├── MCPPlugin.rbxmx        ← OBSOLETE (~69 KB) — community MCP plugin
├── MCPStudioPlugin.rbxm   ← OBSOLETE (~7 KB) — old Studio plugin
└── RojoManagedPlugin.rbxm ← unrelated (Rojo, safe to keep)
```

Roblox Studio auto-loads all `.rbxmx`/`.rbxm` files from this directory. The old MCP plugin can:
- Compete for the same MCP port/session
- Create duplicate tool registrations
- Cause "Target is not reachable" errors because the built-in MCP and old plugin both try to control the same resources

### Fix

```bash
# Rename (not delete — backup first):
mv "%LOCALAPPDATA%\Roblox\Plugins\MCPPlugin.rbxmx" "%LOCALAPPDATA%\Roblox\Plugins\MCPPlugin.rbxmx.bak"
mv "%LOCALAPPDATA%\Roblox\Plugins\MCPStudioPlugin.rbxm" "%LOCALAPPDATA%\Roblox\Plugins\MCPStudioPlugin.rbxm.bak"

# Then restart Roblox Studio completely.
```

### Additional Troubleshooting

1. **Enable Studio as MCP server** — In Studio: Assistant → … → Manage MCP Servers → toggle ON "Enable Studio as MCP server"
2. **Quick connect** — Same menu → expand "Quick connect" → toggle on your client (e.g., "Hermes CLI" if listed)
3. **Restart both** — Restart Roblox Studio AND the Hermes client
4. **Play mode tool restrictions** — `execute_luau`, `search_game_tree`, `inspect_instance`, `script_read`, `multi_edit` do NOT work in Play mode. Only `get_console_output` and `start_stop_play` work during play. Stop play to resume Edit mode tools. Scripts created via `multi_edit` DO auto-execute in Play mode.
