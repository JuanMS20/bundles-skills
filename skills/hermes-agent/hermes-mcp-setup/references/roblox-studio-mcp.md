# Roblox Studio MCP + Hermes Agent

## Architecture

Roblox Studio has a **native built-in MCP server** (since 2025). The old `studio-rust-mcp-server` (GitHub: Roblox/studio-rust-mcp-server) is deprecated — Roblox shifted engineering to the built-in version.

The MCP server runs as a subprocess (`StudioMCP.exe`) launched via `cmd.exe /c %LOCALAPPDATA%\Roblox\mcp.bat`.

## Config for Hermes

```yaml
mcp_servers:
  Roblox_Studio:
    command: cmd.exe
    args:
      - /c
      - '%LOCALAPPDATA%\\Roblox\\mcp.bat'
    timeout: 60
    supports_parallel_tool_calls: false
```

## Enabling in Studio

1. Open Roblox Studio → Assistant (tab)
2. Click `...` → **Manage MCP Servers**
3. Toggle **Enable Studio as MCP server**
4. Green indicator shows connected clients

## All 25 Tools

### Scripts
| Tool | Description |
|------|-------------|
| `script_read` | Read script via dot-path (`game.ServerScriptService.MyScript`). Supports line ranges. |
| `multi_edit` | Apply multiple edits to a script. Creates if not exists. |
| `script_search` | Fuzzy search scripts by name (max 10 results). |
| `script_grep` | Search string pattern across all scripts (max 50 matches). |

### Asset & Content Generation
| Tool | Description |
|------|-------------|
| `generate_mesh` | Generate textured 3D mesh from prompt. |
| `generate_material` | Generate custom material/texture. |
| `generate_procedural_model` | Generate scalable procedural models. |
| `insert_from_creator_store` | Insert assets/plugins/models from Creator Store. |
| `search_creator_store` | Search Creator Store for assets. |
| `store_image` | Load image from local file path. |

### Data Model
| Tool | Description |
|------|-------------|
| `search_game_tree` | Explore instance hierarchy as flat JSON. Filter by path/type/keywords. |
| `inspect_instance` | Get detailed instance info (properties, attributes, children). |
| `subagent` | Launch subagent for complex multi-step investigation. |

### Luau Execution
| Tool | Description |
|------|-------------|
| `execute_luau` | Run Luau code in Studio. Returns result or error. |

### Playtesting
| Tool | Description |
|------|-------------|
| `start_stop_play` | Start or stop playtesting. |
| `get_console_output` | Retrieve output logs while game runs. |
| `screen_capture` | Capture current Studio viewport (edit or play mode). |
| `wait_job_finished` | Wait for generation job to complete. |

### Player Input Simulation
| Tool | Description |
|------|-------------|
| `character_navigation` | Move player to position or instance. |
| `keyboard_input` | Simulate key presses, holds, text input. |
| `mouse_input` | Simulate mouse clicks, movement, scrolling. |

### Session Management
| Tool | Description |
|------|-------------|
| `list_roblox_studios` | List all connected Studio instances. |
| `set_active_studio` | Set target Studio instance for subsequent calls. |

### Utility
| Tool | Description |
|------|-------------|
| `http_get` | Fetch URL content via HTTP GET. |
| `skill` | Retrieve Roblox-specific knowledge/best practices. |

## Verification

```bash
# From terminal:
hermes mcp test Roblox_Studio

# Expected output:
# ✓ Connected (under 2s)
# ✓ Tools discovered: 25
```

## Registered tool names in Hermes

All tools prefixed with `mcp_Roblox_Studio_`. Example:
- `mcp_Roblox_Studio_execute_luau`
- `mcp_Roblox_Studio_script_read`
- `mcp_Roblox_Studio_start_stop_play`

## Multiple Instances

A single MCP client can connect to multiple running Studio instances. Use:
1. `list_roblox_studios` → get instance IDs
2. `set_active_studio <id>` → switch target
