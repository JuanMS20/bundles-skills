---
name: roblox-studio-development
description: Patterns for building Roblox game systems via MCP — TDD adaptation, weapon architecture, pet/collection systems, module extraction, and tool-specific editing workflows. Use when building or modifying Roblox weapons, tools, GUIs, pet simulators, collection loops, or teleport systems.
---

# Roblox Studio Development via MCP

## ⚠ Prerequisite: Read Official Documentation First

**LLMs hallucinate Roblox APIs they've never seen.** Before writing any code, you MUST read the official Roblox Engine API docs for the classes involved.

### How to fetch docs

**Method 1 — `web_extract` (recommended, works without Studio):**
```
web_extract(urls=["https://create.roblox.com/docs/reference/engine/classes/<ClassName>.md"])
```

**Method 2 — `mcp_Roblox_Studio_http_get` (only when Studio is open):**
Supports `query` parameter to search within the doc.
⚠ Requires Studio running + connected. If Studio is closed, use Method 1.

### Class-to-docs mapping

| What you're building | Classes to read |
|---|---|
| **Gamepass** | `MarketplaceService.md`, `GamePassService.md` |
| **Weapon / Tool** | `Tool.md`, `Beam.md`, `Attachment.md` |
| **Shop GUI** | `ScreenGui.md`, `Frame.md`, `ImageButton.md`, `TweenService.md` |
| **Pet / Collection system** | `DataStoreService.md`, `RemoteEvent.md`, `TweenService.md`, `Players.md` |
| **Character effects** | `Humanoid.md`, `Players.md` |

### Pitfall: Verify before claiming tool capability

Always test with a real URL before telling the user a tool works. `http_get` requires Studio open — if it fails, fall back to `web_extract` silently. Do not assume a tool works in all states.

### Why this matters

Without fresh docs, the LLM generates hallucinated APIs:
- `PromptPurchase` instead of `PromptGamePassPurchase`
- Missing `PromptGamePassPurchaseFinished` event handler
- Wrong parameter signatures
- Deprecated APIs (`GamePassService:PlayerHasPass` vs `MarketplaceService:UserOwnsGamePassAsync`)

### Fallback: Direct web search

If the class isn't in the reference engine docs:
```
web_search(query="site:create.roblox.com/docs/reference/engine <topic>")
```

---

## TDD Workflow Adaptation

When building Roblox systems via MCP (no traditional test runner), the RED→GREEN→REFACTOR loop maps to:

```
RED:    execute_luau with return value → confirm behavior absent
GREEN:  execute_luau (instances) or multi_edit (scripts) → create minimal implementation
VERIFY: inspect_instance + search_game_tree + script_read → confirm structure
PLAY:   start_stop_play → human checks result, stop, verify console for errors
```

### RED: Assert absence via return values

Use `return` (not `print`) for verification — `print()` output is NOT captured by `execute_luau`'s result.

```lua
-- RED: confirm tool does NOT exist
local tool = game:GetService("StarterPack"):FindFirstChild("Lightning Gun")
return tool == nil    -- "true" → RED confirmed
```

The return value of `execute_luau` is the ONLY guaranteed output. `print()` doesn't appear in the console or result.

### GREEN: Create via instances

```lua
-- Single execute_luau call to create all instances for this step
local tool = Instance.new("Tool")
tool.Name = "Lightning Gun"
-- ... set all properties ...
tool.Parent = game:GetService("StarterPack")

local handle = Instance.new("Part")
handle.Name = "Handle"
-- ... set properties ...
handle.Parent = tool
return true
```

### VERIFY: Prefer inspect_instance over assert

**Do NOT use `assert()` inside `execute_luau`** — failed asserts return "[error]" with no detail. Instead:

```lua
-- BAD: assert(error) → "[error]" with no values
assert(handle.Color == Color3.fromRGB(0, 200, 255), "color wrong")

-- GOOD: MCP inspect tools → shows all properties as strings, no FP precision issues
-- Call: inspect_instance(path="StarterPack.Lightning Gun.Handle")
```

**Prefer `inspect_instance` + `search_game_tree`** over `execute_luau` for verification because:
- No floating-point precision issues (values shown as readable strings)
- Shows ALL properties in one call
- Works even when `execute_luau` has execution limits

### PLAY: The only way to verify visual behavior

```lua
mcp_Roblox_Studio_start_stop_play(is_start=true)
```

After stopping Play, the MCP server may be temporarily unreachable (30-60s). Wait for auto-retry. Check console for errors via `get_console_output`.

**⚠ Edit-mode tools (`execute_luau`, `search_game_tree`, `inspect_instance`, `script_read`, `multi_edit`) do NOT work during Play mode.** Only `get_console_output` and `start_stop_play` function in Play. All TDD RED/GREEN/VERIFY steps must happen in Edit mode.

**Scripts created via `multi_edit` DO auto-execute in Play mode.** No manual pasting needed. Only scripts created via `execute_luau` (Instance.new + .Source) may fail to auto-execute — always prefer `multi_edit`.

**⚠ CRITICAL: `execute_luau` code is EPHEMERAL.** Tweens, event connections, Heartbeat loops, and any runtime behavior created via `execute_luau` **VANISH on Play**. They run once in edit mode but don't persist. Any logic that needs to work during gameplay (moving platforms, timers, kill bricks, physics) MUST live in a real Script/LocalScript created via `multi_edit`. This is the #1 cause of "it works in VERIFY but not when I play" bugs. Use `execute_luau` only for structural setup (creating Parts, setting properties) — never for runtime behavior.

---

## Weapon Architecture

```
StarterPack.<ToolName> (Tool)
├── Handle (MeshPart)               ← model from generate_mesh or Parts
├── Script                          ← server: Activated → raycast → damage
└── LocalScript                     ← client: beam + sound + particles

ReplicatedStorage
├── <EventName> (RemoteEvent)       ← dual-role: client→FireServer(aim) + server→FireClient(hitPos)
└── <ConfigModule> (ModuleScript)   ← shared constants
```

### Build Order

1. **Research APIs** — `http_get` on Tool, Beam, Attachment classes
2. **Tool + Handle** — `execute_luau` for Tool instance + placeholder Handle
3. **Weapon model** — `generate_mesh` → reparent mesh into Tool as Handle (see `generate_mesh` section)
4. **Adjust Grip** — After replacing Handle, tune `tool.Grip = CFrame.new(0, -0.3, 0.6)` so the weapon looks natural in hand (test in Play mode)
5. **Infra layer** — RemoteEvent + ModuleScript in ReplicatedStorage
6. **Server Script** — `multi_edit` inside Tool
7. **LocalScript** — `multi_edit` or full rewrite via `execute_luau`
8. **Suppress default animations** — Use `mouse.Button1Down` in LocalScript instead of `Tool.Activated` (see [Animation Suppression](./references/animation-suppression.md))
9. **Verify** — `inspect_instance` + `script_read` + Play mode test

### Suppress Default Character Animations

❗ **`toolanim` StringValue does NOT work in modern Roblox (2024+).** The Roblox default Animate script (built into CoreScripts) ignores it.

The correct fix is to use `mouse.Button1Down` instead of `Tool.Activated` in the LocalScript. See [Animation Suppression](./references/animation-suppression.md) for the full pattern.

---

## Module Extraction Pattern (GunConfig)

Extract shared constants into a ModuleScript in ReplicatedStorage. Both server and client scripts `require()` it. This prevents drift between sides and centralizes tuning.

### Structure

```lua
-- ReplicatedStorage.GunConfig
local GunConfig = {}

-- Event name (both scripts reference this, not a hardcoded string)
GunConfig.RemoteEventName = "LightningGunEvent"

-- Server constants
GunConfig.MaxRange = 200
GunConfig.DamageMin = 10
GunConfig.DamageMax = 30
GunConfig.Cooldown = 0.5

-- Client constants
GunConfig.BeamLifetime = 0.3
GunConfig.SoundId = "rbxasset://sounds/electronic_ping.wav"

-- Beam visual config (table of properties → data-driven)
GunConfig.Beam = {
    Width0 = 0.6,
    Width1 = 0.3,
    Texture = "rbxasset://textures/particles/sparkles_main.dds",
    TextureSpeed = 10,
    LightEmission = 1,
    FaceCamera = true,
    Color = {
        {time = 0, color = Color3.fromRGB(100, 200, 255)},
        {time = 0.5, color = Color3.fromRGB(200, 230, 255)},
        {time = 1, color = Color3.fromRGB(50, 150, 255)},
    },
    Transparency = {
        {time = 0, value = 0},
        {time = 0.7, value = 0},
        {time = 1, value = 1},
    },
}

return GunConfig
```

### Usage in Server Script

```lua
local GunConfig = require(repStorage:WaitForChild("GunConfig"))
local event = repStorage:WaitForChild(GunConfig.RemoteEventName)

-- Use constants everywhere
workspace:Raycast(origin, direction * GunConfig.MaxRange, params)
Random.new():NextInteger(GunConfig.DamageMin, GunConfig.DamageMax)
task.delay(GunConfig.Cooldown, function() ... end)
```

### Usage in LocalScript

```lua
local GunConfig = require(repStorage:WaitForChild("GunConfig"))

-- Beam properties from config
local beam = Instance.new("Beam")
beam.Color = ColorSequence.new(buildColorKeys(GunConfig.Beam.Color))
beam.Width0 = GunConfig.Beam.Width0
beam.TextureSpeed = GunConfig.Beam.TextureSpeed

-- Cleanup from config
DEBRIS:AddItem(beam, GunConfig.BeamLifetime)
```

### Benefits

- One place to tune: range, damage, cooldown, beam look, sound
- No hardcoded strings or magic numbers in scripts
- Adding a second weapon type is `local config = GunConfigs[weaponType]` instead of duplicating scripts

## Data-Driven Beam Functions (cfgOverride Pattern)

Extract `createLightning` and `createImpact` as generic functions that accept optional config overrides. When no override is passed, they fall back to `GunConfig.Beam`/`GunConfig.Impact` defaults.

```lua
-- Shared helpers: build sequences from config tables
local function buildColorSequence(colorConfig)
    local keys = {}
    for _, c in ipairs(colorConfig) do
        table.insert(keys, ColorSequenceKeypoint.new(c.time, c.color))
    end
    return ColorSequence.new(keys)
end

local function buildNumberSequence(transConfig)
    local keys = {}
    for _, t in ipairs(transConfig) do
        table.insert(keys, NumberSequenceKeypoint.new(t.time, t.value))
    end
    return NumberSequence.new(keys)
end

-- cfgOverride = nil → uses GunConfig.Beam defaults
local function createLightning(handle, hitPosition, cfgOverride)
    local cfg = cfgOverride or GunConfig.Beam

    local beam = Instance.new("Beam")
    beam.Color = buildColorSequence(cfg.Color)
    beam.Transparency = buildNumberSequence(cfg.Transparency)
    beam.Width0 = cfg.Width0
    beam.TextureSpeed = cfg.TextureSpeed
    -- ... all other Beam properties from cfg ...
    beam.Parent = handle

    DEBRIS:AddItem(beam, GunConfig.BeamLifetime)
    return beam
end

-- cfgOverride = nil → GunConfig.Impact defaults; beamCfg = nil → GunConfig.Beam
local function createImpact(position, cfgOverride, beamCfg)
    local cfg = cfgOverride or GunConfig.Impact
    local beamTexture = (beamCfg or GunConfig.Beam).Texture

    local emitter = Instance.new("ParticleEmitter")
    emitter.Texture = beamTexture
    emitter.Color = buildColorSequence(cfg.Color)
    -- ... all other ParticleEmitter properties from cfg ...
    return emitter
end
```

### Creating alternate beam types

```lua
-- Default blue beam
createLightning(handle, hitPosition)

-- Custom red beam for a different weapon
createLightning(handle, hitPosition, {
    Color = {{time = 0, color = Color3.new(1, 0, 0)}},
    Width0 = 2,
    TextureSpeed = 5,
})
```

This pattern lets you create N weapon types without duplicating `createLightning`/`createImpact`.

---

## Cooldown + Nil Guard Patterns

### Cooldown

```lua
local canFire = true
local event = repStorage:WaitForChild(GunConfig.RemoteEventName)

event.OnServerEvent:Connect(function(player, targetPosition)
    if not canFire then return end

    -- Nil checks BEFORE locking cooldown
    local character = player.Character
    if not character then return end
    local humanoid = character:FindFirstChild("Humanoid")
    if not humanoid then return end
    local handle = tool:FindFirstChild("Handle")
    if not handle then return end

    canFire = false  -- lock AFTER nil checks pass

    -- ... fire logic ...

    task.delay(GunConfig.Cooldown, function()
        canFire = true
    end)
end)
```

**Rule**: Set `canFire = false` AFTER all nil checks. If you set it before and a nil check returns early, the gun locks permanently.

### Nil guard on GetPlayerFromCharacter

```lua
local player = game:GetService("Players"):GetPlayerFromCharacter(character)
if player then
    event:FireClient(player, hitPosition, direction)
end
```

`GetPlayerFromCharacter` returns `nil` if the character died between Activated and FireClient. Calling `FireClient(nil, ...)` crashes.

---

## Script Editing: multi_edit vs execute_luau

### When to use each

| Method | Use for | Pitfall |
|--------|---------|---------|
| `multi_edit` | Small targeted edits (change a few lines) | `old_string` must match EXACTLY including tabs, quotes, and escaping — fails if whitespace differs |
| `execute_luau` with `.Source = ...` | Full script rewrites (change most of the file) | Must know the instance path; use `script_read` first to confirm Script/LocalScript exists |

### multi_edit escaping failures

`multi_edit` uses exact string matching. Tabs vs spaces, escaped quotes (`\"` in output but `"` in source), and multiline indentation differences cause `"old_string not found"`. When this happens:

1. Fall back to `execute_luau`, reading the script's `Script` reference
2. Rebuild the entire source string
3. Assign to `.Source` property

```lua
-- Fallback when multi_edit fails:
local tool = game:GetService("StarterPack"):FindFirstChild("Lightning Gun")
local script = tool:FindFirstChild("LightningGunClient")

script.Source = [[
    -- complete new source code here
    -- use [[ ]] literal strings to avoid escaping hell
]]

return "Done"
```

### Full-rewrite workflow (when multi_edit inserts at wrong nesting level)

**Gotcha**: When using `multi_edit` with `old_string` that matches a unique string but the insertion logic places new code at the wrong nesting level (e.g., inside a function body when you intended after it), the script gets corrupted.

This happens most often with Luau `end` keyword ambiguity — if you match the `end` of a function to insert code after it, `multi_edit` may match the WRONG `end` (e.g., a nested if-block's `end`) and insert inside the function.

**Fix**: Replace the ENTIRE script content instead of patching. Read it first with `script_read`, then write the corrected full version:

```lua
-- After script_read confirms the current content:
local manager = game:GetService("ServerScriptService"):FindFirstChild("MoonJumpManager")
manager.Source = [[
-- complete rewritten source here
-- use [[ ]] literal strings to avoid escaping hell
]]
return "Full rewrite done"
```

This avoids the nesting ambiguity entirely.

```lua
-- 1. Read current script to confirm it exists
--    script_read(target_file="StarterPack.Lightning Gun.LightningGunClient")

-- 2. Build new source as a [[ ]] literal string
local newSource = [[
-- no escaping needed inside [[ ]]
local function foo()
    print("hello \"world\"")
end
]]

-- 3. Assign and verify
ls.Source = newSource
-- script_read() again to confirm
```

---

## MCP Connectivity Setup

### Enabling the built-in MCP

The MCP is built into Roblox Studio (2025+). No plugin installation needed.

1. Open **Assistant** in Studio (View → Assistant or Ctrl+Shift+A)
2. Click **…** → **Manage MCP Servers**
3. Toggle **ON** "Enable Studio as MCP server"
4. Optional: Quick connect → toggle your client on

### Hermes config (already correct for Windows)

```yaml
mcp_servers:
  Roblox_Studio:
    command: cmd.exe
    args:
    - /c
    - '%LOCALAPPDATA%\Roblox\mcp.bat'
    timeout: 60
```

### Old plugins causing interference

If MCP tools fail with "Target is not reachable" or "unreachable", old plugin files may be interfering. See [MCP Troubleshooting](./references/mcp-troubleshooting.md) for the full diagnostic path and fix.

**Quick fix**: Remove `MCPPlugin.rbxmx` and `MCPStudioPlugin.rbxm` from `%LOCALAPPDATA%\Roblox\Plugins\`, then restart Studio.

---

## Key Pitfalls

| Pitfall | Fix |
|---------|------|
| `execute_luau` with `print()` → output not captured | Use `return` values for verification |
| `execute_luau` with `assert()` → `"[error]"` no detail | Use `inspect_instance` + `search_game_tree` instead |
| Old MCP plugins interfere with built-in MCP | Remove `MCPPlugin.rbxmx`/`MCPStudioPlugin.rbxm` from `%LOCALAPPDATA%\Roblox\Plugins\` (see [MCP Troubleshooting](./references/mcp-troubleshooting.md)) |
| MCP "Target is not reachable" when tools fail | Toggle "Enable Studio as MCP server" OFF/ON in Assistant → Manage MCP Servers |
| `multi_edit` `old_string` not found (escaping mismatch) | Fall back to `execute_luau` `.Source = [[...]]` |
| `multi_edit` fails with long comment blocks in old_string | Comments with special chars (em-dashes, quotes, multiline) break matching. Rewrite entire script via `multi_edit` with `old_string` = full first/last lines instead of the comment block, or fall back to full rewrite via `execute_luau` `.Source` |
| Pet Sim: weighted RNG must roll tier THEN pet | Two-step roll: accumulate weights for tier, then random pick from candidates in that tier (see [Pet Simulator Core Loop](./references/pet-simulator-core-loop.md)) |
| Pet Sim: DataStore fails in Studio | Use wrapper with `USE_DATASTORE` flag — false = memory-only, true = real DataStore when published |
| `multi_edit` insertion lands at wrong nesting level (inside a function body instead of after it) | The match is correct but the insertion context is wrong. **Fix**: rewrite the entire script via `execute_luau .Source = [[...]]` instead of patching |
| Instances created by `execute_luau` lost after Play/Stop | Recreate after Play, or use `multi_edit` for scripts |
| `execute_luau` runtime behavior (tweens, Heartbeat, events) vanishes on Play | **Use `multi_edit` for all Scripts.** `execute_luau` is structural-only (Parts, properties). Runtime logic MUST be in real Scripts. |
| Cooldown lock if `canFire = false` set before nil checks | Set `canFire = false` AFTER all guard checks pass |
| `FireClient(nil, ...)` crash when character dies | Guard `GetPlayerFromCharacter` result |
| `humanoid.TargetPoint` aiming unreliable | Use LocalScript mouse hit → RemoteEvent (see animation-suppression.md) |
| `generate_mesh` result placed in Workspace | Must be manually reparented into the Tool as Handle |
| Instances created by `execute_luau` can lose Parent after cycles | Always assign `.Parent` explicitly |
| `WaitForChild` in UI-creating LocalScript blocks ALL UI creation | Never use blocking `WaitForChild` at top level of UI LocalScripts — move to `task.spawn` with retries |
| MCP-created Scripts/LocalScripts auto-execute in Play mode when created via `multi_edit` | Scripts created via `multi_edit` with `className="Script"`/`"LocalScript"`/`"ModuleScript"` DO auto-execute in Play mode. This was verified with PetManager (Script), DataStoreWrapper (ModuleScript), and HatchController (LocalScript) — all ran correctly without manual pasting. ⚠ Scripts created via `execute_luau` (Instance.new("Script") + .Source = ...) may NOT auto-execute — prefer `multi_edit` for all script creation. |
| `toolanim` StringValue ignored in modern Roblox | Use `mouse.Button1Down` instead of `Tool.Activated` in LocalScript (see animation-suppression.md) |
| Character face moves on every click (punch animation) | Same fix — `mouse.Button1Down` instead of `Tool.Activated` |
| Notification/UI toast frame `Visible = true` at startup | Set `Visible = false` on the instance. Only set `Visible = true` before animation begins, `Visible = false` after fade-out completes. Text renders even at off-screen positions if parent frame is visible. |
| `execute_luau`, `search_game_tree`, `screen_capture` don't work in Play mode | These MCP tools only work in Edit mode. In Play mode, the only diagnostic tool is `get_console_output`. Stop play first to resume Edit mode tools. |
| Not loading `roblox-ui-patterns` before creating UI | SIEMPRE cargar `roblox-ui-patterns` con `skill_view()` antes de escribir cualquier código de UI en Studio. La skill documenta patrones, espaciados, colores, anti-patterns y componentes (inventory, shop, settings, HUD, etc.). Improvisar sin ella causa errores como overlap de botones, uso incorrecto de Scale vs Offset, y layouts que no escalan. Aplica a TODO tipo de UI: inventario, tienda, ajustes, HUD, notificaciones, modales. |
| `game.Players.LocalPlayer` nil in edit mode | `LocalPlayer` only exists in Play mode. When creating UI via `execute_luau` in Edit mode, parent ScreenGui to `game.StarterGui` instead of `player:WaitForChild("PlayerGui")`. The UI will load into PlayerGui when Play starts. |
| `screen_capture` timeout in edit mode | `screen_capture` can hang/timeout (60s) in edit mode. **Workaround**: start Play → take screenshot → stop Play. Play mode screenshots work reliably. |
| Helper functions not shared between `execute_luau` calls | Each `execute_luau` invocation is a fresh Luau state — no shared variables, functions, or closures. If you need helper functions (e.g. `cf()`, `bt()`, `lbl()` for UI creation), **redefine them in every call** that uses them. |
| Chaining `execute_luau` for complex construction | For large UIs or structures, split into multiple `execute_luau` calls. Each call can reference instances from prior calls via `WaitForChild`. Pattern: Part 1 creates ScreenGui + MainFrame + helpers, Part 2 adds section A, Part 3 adds section B, etc. Each part redefines helpers and does `game.StarterGui:WaitForChild("BloxUI"):WaitForChild("Main")` to resume. |
| MCP returns "Target is not reachable" after Play/Stop cycle | After stopping Play, MCP may take 5-10s to reconnect. If it persists: toggle "Enable Studio as MCP server" OFF/ON in Assistant settings. No need to restart Studio. |
| Multiple `OnClientEvent:Connect()` on same event | Valid in Luau — ALL handlers fire. Useful but can create redundancy if not careful. Prefer single handler per event unless intentional (e.g., separate UI refresh logic). |
| RemoteEvents/Folders created at runtime by server script | Don't exist in Edit mode — `search_game_tree` and `inspect_instance` won't find them. Client scripts must use `FindFirstChild` with retries, not `WaitForChild` (which blocks UI creation). |
| Verify scripts assert on runtime-only instances | Scripts that create BindableEvents/RemoteEvents at runtime don't have those instances in edit mode. **VERIFY must check SOURCE CODE** (string patterns like `src:find("BindableEvent")`) instead of searching the tree. Only verify tree structure for instances created via `execute_luau` or `multi_edit` in edit mode. |
| Sparse numeric tables cause duplicate instances | `t[1]=x; t[2]=y` creates sparse arrays that misbehave with `ipairs`. Use `table.insert(t, x)` + `ipairs` for all instance arrays. Sparse keys left empty Folders after partial failures. |
| Failed `execute_luau` leaves orphaned instances | When a GREEN attempt crashes halfway, instances created before the error persist. Must explicitly `Destroy()` before retrying — search_game_tree to find orphans, then cleanup execute_luau. |
| `execute_luau` `.Source` rewrite breaks auto-execution silently | If you rewrite a Script/LocalScript via `execute_luau` assigning `.Source = [[...]]`, the script may STOP auto-executing in Play mode — even though the Source property looks correct via `script_read`. **Recovery**: (1) delete the broken script via `execute_luau` (`script:Destroy()`), (2) recreate with `multi_edit` + `className` which DOES auto-execute. **Do NOT** try `multi_edit` old_string on the corrupted content — it won't match because `execute_luau` changed the Source. |
| `multi_edit` fails when path exists as Folder, not Script | When creating a new script with `multi_edit`, if the target path already exists as a Folder (not a Script), you get "Object at path is not a script type. Found: Folder". **Fix**: delete the orphan Folder first via `execute_luau` (`folder:Destroy()`), then retry `multi_edit` with `className`. |
| Console output stale across Play/Stop cycles | `get_console_output` may show messages from a previous Play session and never show new ones, even with `clear=true`. The Output panel in Studio itself may show fresh errors. **Workaround**: rely on visual verification (screen_capture + vision_analyze) + `search_game_tree` to confirm instances exist, rather than depending solely on console output for Play-mode diagnosis. |
| Build large games incrementally via MCP, not all-at-once | A complete game (mining sim with 5 zones, 8 tools, 12 pets, 5 eggs, 5+ UI panels, DataStore, monetization) is too large for a single session. **Pattern**: (1) create config ModuleScripts first, (2) server script with multi_edit, (3) minimal client test script with multi_edit, (4) verify Play works, (5) expand client incrementally. Never write the full 1000+ line client in one shot. See [references/game-architecture-patterns.md](references/game-architecture-patterns.md) for full reference. |

## Default Animation Suppression

### The problem

When a Tool is activated via `Tool.Activated`, Roblox's default character Animate script plays a "punch" animation that moves the character's torso and head on every click. For a ranged weapon, this looks wrong.

### Two failed approaches (don't use these)

**1. `toolanim` StringValue** (doesn't work in modern Roblox)

```lua
-- ❌ Does NOT suppress the animation
local toolanim = Instance.new("StringValue")
toolanim.Name = "toolanim"
toolanim.Value = ""
toolanim.Parent = tool
```

This approach is documented in old Roblox tutorials but the modern default Animate script (built into CoreScripts) ignores it. The punch animation plays regardless.

**2. The `toolanim` with "Slash"/"Lunge"** (replaces punch with sword animation, still moves)

```lua
-- ❌ Still moves the character, just differently
toolanim.Value = "Slash"
```

### The fix: Use `mouse.Button1Down` instead of `Tool.Activated`

The default Animate script only reacts to `Tool.Activated`. If the client sends fire requests via `mouse.Button1Down` directly, the Animate script never fires and the character stands still.

```lua
-- ✅ LocalScript: use mouse.Button1Down — NO Tool.Activated on client
tool.Equipped:Connect(function(mouse)
    local connection
    connection = mouse.Button1Down:Connect(function()
        if mouse and mouse.Hit then
            event:FireServer(mouse.Hit.Position)
        end
    end)

    tool.Unequipped:Connect(function()
        if connection then
            connection:Disconnect()
            connection = nil
        end
    end)
end)
```

**Why this works**: `mouse.Button1Down` fires on any left-click. `Tool.Activated` fires on left-click AND triggers the Animate script. By using `mouse.Button1Down`, we keep the functionality and lose the animation.

### Server-side: Use `OnServerEvent` (no `Activated`)

Since the client now uses `mouse.Button1Down` → `FireServer`, the server must listen to `OnServerEvent` instead of `Tool.Activated`.

```lua
-- Server Script: receive via OnServerEvent (NO Activated handler!)
event.OnServerEvent:Connect(function(player, targetPosition)
    if not canFire then return end
    
    local character = player.Character
    if not character then return end
    
    local handle = tool:FindFirstChild("Handle")
    if not handle then return end
    
    canFire = false
    
    local origin = handle.Position
    local direction = (targetPosition - origin).Unit
    
    local result = workspace:Raycast(origin, direction * GunConfig.MaxRange, params)
    -- On hit: apply damage via Humanoid:TakeDamage()
    -- Then FireClient back to show beam + sound + particles at hit position
    
    event:FireClient(player, hitPosition, direction)
    
    task.delay(GunConfig.Cooldown, function()
        canFire = true
    end)
end)
```

---

## Gamepass / Monetization Systems

Gamepasses let players purchase permanent upgrades via Robux. The architecture follows a server-authoritative ownership check → apply effect pattern.

### Architecture

```
StarterGui
└── MoonJumpShopGUI (ScreenGui + LocalScript)   ← Shop UI + purchase prompt

ServerScriptService
└── MoonJumpManager (Script)                     ← Ownership check + apply effect

ReplicatedStorage
├── GamepassConfig (ModuleScript)                 ← Shared config: ID, price, multiplier
└── ShopRemote (RemoteEvent)                     ← Client→Server purchase notification
```

### GamepassConfig — Central Configuration

```lua
-- ReplicatedStorage.GamepassConfig
local GamepassConfig = {
    MoonJump = {
        Id = 0,                      -- Set after publishing in Creator Dashboard
        Name = "Moon Jump",
        Price = 39,                   -- In Robux
        Description = "¡Salta como en la luna! Saltos extra-altos.",
        JumpPowerMultiplier = 2.5,    -- Base JumpPower 50 → 125
    }
}
return GamepassConfig
```

### MoonJumpManager — Server: Verify Ownership + Apply Effect

```lua
-- ServerScriptService.MoonJumpManager
local Players = game:GetService("Players")
local MarketplaceService = game:GetService("MarketplaceService")
local GamepassConfig = require(game:GetService("ReplicatedStorage"):WaitForChild("GamepassConfig"))

local MOON_JUMP_ID = GamepassConfig.MoonJump.Id
local BASE_JUMP_POWER = 50
local BOOSTED_JUMP_POWER = BASE_JUMP_POWER * GamepassConfig.MoonJump.JumpPowerMultiplier

local function applyMoonJump(character, player)
    local humanoid = character:FindFirstChildWhichIsA("Humanoid")
    if not humanoid then return end

    local success, owns = pcall(function()
        return MarketplaceService:UserOwnsGamePassAsync(player, MOON_JUMP_ID)
    end)

    if success and owns then
        humanoid.JumpPower = BOOSTED_JUMP_POWER
    else
        humanoid.JumpPower = BASE_JUMP_POWER
    end
end

Players.PlayerAdded:Connect(function(player)
    -- Apply on initial spawn
    player.CharacterAdded:Connect(function(character)
        applyMoonJump(character, player)
    end)
    -- If character already exists
    if player.Character then
        applyMoonJump(player.Character, player)
    end
end)
```

**Key points**:
- `UserOwnsGamePassAsync` is wrapped in `pcall` because it can fail (rate limits, network errors)
- Use `CharacterAdded` to handle respawns — effect persists across deaths
- If ownership check fails, default to NO gamepass (secure: don't grant free effect)
- The `ShopRemote` event lets the server re-apply JumpPower immediately after purchase confirmation

### MoonJumpShopGUI — Shop UI Pattern

```lua
-- StarterGui.MoonJumpShopGUI (LocalScript inside a ScreenGui)
local Players = game:GetService("Players")
local MarketplaceService = game:GetService("MarketplaceService")
local player = Players.LocalPlayer
local GamepassConfig = require(game:GetService("ReplicatedStorage"):WaitForChild("GamepassConfig"))

local screenGui = script.Parent

-- Floating shop button (always visible)
local shopButton = Instance.new("ImageButton")
shopButton.Size = UDim2.new(0, 48, 0, 48)
shopButton.Position = UDim2.new(1, -64, 1, -64)
shopButton.BackgroundColor3 = Color3.fromRGB(26, 26, 46)
shopButton.Image = "rbxasset://textures/ui/.../icons/places.png"  -- placeholder
shopButton.Parent = screenGui

-- Shop panel (hidden by default)
local shopPanel = Instance.new("Frame")
-- ... build a Frame with overlay, card, purchase button, etc.
shopPanel.Visible = false
shopPanel.Parent = screenGui

-- Purchase handler
shopPanel.PurchaseButton.MouseButton1Click:Connect(function()
    MarketplaceService:PromptGamePassPurchase(GamepassConfig.MoonJump.Id)
end)

-- Close button
shopPanel.CloseButton.MouseButton1Click:Connect(function()
    shopPanel.Visible = false
end)

-- Toggle UI
shopButton.MouseButton1Click:Connect(function()
    shopPanel.Visible = not shopPanel.Visible
end)
```

**Shop panel structure**:
1. **Overlay**: Full-screen black with 60% transparency (click to close)
2. **Card**: Centered 400×500px, dark background (#1a1a2e), rounded corners
3. **Title**: "TIENDA" / "SHOP", white bold
4. **Product tile**: 350×180px showing icon, name, description, price (39 Robux icon + text), COMPRAR button
5. **Close button**: X in top-right corner
6. **Notification**: Toast-style "¡Compra exitosa!" with 3s fade out on `PromptGamePassPurchaseFinished`

### Purchase flow

```
Player clicks COMPRAR
  → MarketplaceService:PromptGamePassPurchase(gamepassId)
    → Roblox native purchase UI (handles everything: balance check, confirmation, payment)
  → On client: PromptGamePassPurchaseFinished(player, gamepassId, wasPurchased)
    → If wasPurchased: show notification, fire ShopRemote to server
  → On server: CharacterAdded fires → re-check UserOwnsGamePassAsync → JumpPower = 125
```

### Key Pitfalls

| Pitfall | Fix |
|---------|------|
| `UserOwnsGamePassAsync` fails silently | Wrap in `pcall`; assume NOT owned on failure |
| Gamepass ID is 0 before publishing | Keep `Id = 0` as placeholder; update in GamepassConfig when published |
| Effect lost on respawn | Re-apply in `CharacterAdded` (not just `PlayerAdded`) |
| Stale ownership cache | Roblox's API caches for ~5 min; call every `CharacterAdded` for fresh check. Fallback: `pcall` + defaults |
| `PromptGamePassPurchase` opens automatically if not owned | That's expected behavior — Roblox handles the native popup |
| Shop panel overlapping gameplay | Add `Overlay` with background click to close; keep `shopButton` small and semi-transparent |
| Floating button covering game UI | Use a low ZIndex or position in bottom-right corner with transparency |

### Flow comparison: Server-authoritative vs Client

| Aspect | Server-authoritative (recommended) | Client-only |
|--------|-----------------------------------|-------------|
| Ownership check | `UserOwnsGamePassAsync` on server | `UserOwnsGamePassAsync` on client (exploitable) |
| Effect application | Server sets `Humanoid.JumpPower` | Client adds force (bypassable) |
| Verification timing | Every `CharacterAdded` + on purchase notify | One-time at join |
| Security | ✅ Exploit-resistant | ❌ Player can spoof |

**Always keep ownership verification and effect application on the server.**

## Known Issues

## Pet Simulator / Collection Systems

For building Pet Simulator-style collection, hatching, and inventory systems, see [Pet Simulator Core Loop](./references/pet-simulator-core-loop.md).

Key patterns in the reference:
- **PetData + EggData** with weighted RNG (roll tier → roll pet within tier)
- **Stack inventory** with equip that doesn't consume
- **DataStore wrapper** with `USE_DATASTORE` flag
- ⚠ **Save on PlayerRemoving must be synchronous** — never use `task.spawn` for leave saves
- **Auto-save loop** (task.spawn + wait 60s safety net)
- **SetAttribute for UI slot indices** — avoid connection stacking in refresh functions
- **DataUpdate sync event** — server broadcasts full state, client refreshes HUD components
- **Luau `for _, v in t` iterates all entries** (string keys included) — Luau extension over Lua 5.1

Key patterns covered:
- **EggData + PetData** ModuleScripts with weighted RNG (roll tier → roll pet within tier)
- **Stack inventory** (`{ [petId]: count }`) with equip slots that don't consume
- **DataStore wrapper** with `USE_DATASTORE` flag for Studio → Published transition
- **Auto-Hatch** client loop with `task.wait(2)` delay
- **Hatching animation** phases via TweenService on ImageLabels (shake → break → reveal)
- **RemoteEvent architecture** for hatching, equipping, and data sync

---

## UI Debugging: LocalScript programmatic GUI not visible

When a LocalScript creates UI via `Instance.new()` in `player:WaitForChild("PlayerGui")` and the UI doesn't appear in Play mode, follow this diagnostic chain:

### Step 1: Verify PlayerGui works

Create a minimal test ScreenGui in **StarterGui** (not via LocalScript). **This must be temporary — remove it after diagnosis.**

```lua
-- Execute this in Edit mode using execute_luau:
local sg = Instance.new("ScreenGui")
sg.Name = "DebugTest"
sg.ResetOnSpawn = false
local frame = Instance.new("Frame")
frame.Size = UDim2.new(0.5, 0, 0, 80)
frame.Position = UDim2.new(0.25, 0, 0, 0)
frame.BackgroundColor3 = Color3.fromRGB(255, 0, 0) -- bright red
frame.BorderSizePixel = 0
frame.Parent = sg
local label = Instance.new("TextLabel")
label.Size = UDim2.new(1, 0, 1, 0)
label.BackgroundTransparency = 1
label.Text = "DEBUG UI - VISIBLE?"
label.TextScaled = true
label.TextColor3 = Color3.fromRGB(255, 255, 255)
label.Font = Enum.Font.GothamBold
label.Parent = frame
sg.Parent = game:GetService("StarterGui")
```

- If the test GUI **IS visible** → PlayerGui works; the problem is in the LocalScript
- If the test GUI is **NOT visible** → PlayerGui or ScreenGui rendering is broken

**⚠ After confirming, immediately destroy the test GUI:**
```lua
-- Execute in Edit mode:
game:GetService("StarterGui"):FindFirstChild("DebugTest"):Destroy()
```

### Step 2: Find blocking `WaitForChild` calls

`WaitForChild` in a LocalScript is **synchronous and blocking**. If the waited-for instance never appears (or appears slowly), **the entire script freezes** and no UI gets created.

**Common blocker**: `ReplicatedStorage:WaitForChild("Remotes"):WaitForChild("PetRemotes")` when the Remotes folder is created at runtime by a different script.

**Fix**: Separate UI creation from remote wiring:

```lua
-- BAD: blocks UI creation
local remotes = ReplicatedStorage:WaitForChild("Remotes"):WaitForChild("PetRemotes")

-- GOOD: create UI first, wire remotes async
-- (Bottom of script or in a task.spawn)

-- 1. Create all UI (frames, buttons, labels) FIRST
-- 2. Then in a background thread, try to find remotes with retries:
task.spawn(function()
    local maxRetries = 5
    local retryDelay = 1
    local petRemotes
    
    for attempt = 1, maxRetries do
        local remotesFolder = ReplicatedStorage:FindFirstChild("Remotes")
        if remotesFolder then
            petRemotes = remotesFolder:FindFirstChild("PetRemotes")
        end
        if petRemotes then break end
        task.wait(retryDelay)
    end
    
    if not petRemotes then
        warn("Could not find PetRemotes after retries")
        return
    end
    
    -- Wire events, load data, etc.
end)
```

### Step 3: Add nil guards to remote calls

Since remote variables (`hatchEgg`, `equipPet`, etc.) start as `nil` and are assigned asynchronously, protect every `FireServer`/`FireClient` call:

```lua
btn.MouseButton1Click:Connect(function()
    if hatchEgg then  -- nil guard
        hatchEgg:FireServer(eggId)
    end
end)
```

### Step 4: Add user-visible connection status

When remote variables start as `nil` and are set asynchronously, buttons that silently check `if remote then` give no feedback. Add a status label so the user knows what's happening:

```lua
-- During UI creation:
local status = Instance.new("TextLabel")
status.Size = UDim2.new(0, 300, 0, 30)
status.Position = UDim2.new(0.5, -150, 0, 80)
status.BackgroundTransparency = 1
status.Text = "Conectando..."
status.TextColor3 = Color3.fromRGB(255, 200, 50)  -- yellow = loading
status.TextScaled = true
status.Font = Enum.Font.GothamBold
status.Parent = gui

-- In async connection task:
task.spawn(function()
    for attempt = 1, 5 do
        local r = RS:FindFirstChild("Remotes")
        local pr = r and r:FindFirstChild("PetRemotes")
        if pr then
            hatchEgg = pr:FindFirstChild("HatchEgg")
            if hatchEgg then
                connected = true
                status.Text = "Listo!"
                status.TextColor3 = Color3.fromRGB(100, 200, 100)  -- green = ready
                task.delay(2, function() status.Visible = false end)
                break
            end
        end
        status.Text = "Conectando... (" .. attempt .. "/5)"
        task.wait(1)
    end
    if not connected then
        status.Text = "Error de conexion"
        status.TextColor3 = Color3.fromRGB(255, 50, 50)  -- red = error
    end
end)
```

**Color convention**: Yellow = loading/connecting, Green = ready, Red = error.

**Button feedback**: When a button is clicked but remotes aren't ready, update the status label instead of doing nothing:

```lua
btn.MouseButton1Click:Connect(function()
    if not connected or not hatchEgg then
        status.Text = "Esperando conexion..."
        status.Visible = true
        return
    end
    hatchEgg:FireServer(eggId)
end)
```

### Step 5: Remove all debug/test elements before confirming ready

**⚠ User will notice and get angry if debug elements are left in the game.** Before telling the user a fix is ready:

```lua
-- Remove any test ScreenGui added to StarterGui
local sg = game:GetService("StarterGui"):FindFirstChild("DebugTest")
if sg then sg:Destroy() end

-- Remove any visual debug decorations (colored borders, debug text)
```

Always clean up temporary instances added during debugging.

### Step 6: UI positioning convention

**Primary game UI bars belong at the TOP of the screen** (Y offset close to 0), not at the bottom (Y offset near `1`). Users will angrily reject bottom-positioned game controls.

```lua
-- GOOD: Egg bar at top
bar.Position = UDim2.new(0, 0, 0, 0)  -- Y = 0 (top)

-- BAD: Egg bar at bottom
bar.Position = UDim2.new(0, 0, 1, -100)  -- Y = 1 - offset (bottom)
```

Bottom-of-screen UI should be reserved for HUD elements like equipped-pet slots or health bars, never primary action buttons.

### Step 7: Verify in Play mode

1. Press Play
2. Check if base UI frames are visible before clicking anything
3. Check the status label shows "Conectando..." → "Listo!" or "Error de conexion"
4. If UI is visible but buttons don't respond → the async remote wiring might not have completed yet
5. Check Output panel for `warn()` messages from the retry failure case

---

## Luau: `for _, v in t` behavior

**Key fact**: In Luau (Roblox), `for _, v in t` iterates ALL key-value pairs in a table, including string keys. This is a Luau extension over standard Lua 5.1 where the same syntax only iterates the array part (numeric indices).

```lua
local t = { cat = 1, dog = 2, rabbit = 3 }
local count = 0
for _, v in t do
    count += 1
end
-- count == 3 (Luau) vs count == 0 (Lua 5.1)
```

This means PetData-style static tables with string keys can be iterated directly:
```lua
local PetData = { _pets = { cat = {...}, dog = {...} } }
function PetData.getPetsByTier(tier)
    for _, pet in PetData._pets do  -- ✅ works in Luau
        -- ...
    end
end
```

---

## Architecture Summary
ReplicatedStorage: PetData + EggData (ModuleScripts) + PetRemotes (Folder of RemoteEvents)
ServerScriptService: PetManager (RNG + inventory + DataStore) + DataManager (orchestrator)
StarterGui: PetUI (ScreenGui with EggPanel, HatchAnim, InventoryPanel, EquipHUD)
StarterPlayerScripts: HatchController (LocalScript — auto-hatch + animations)
```

Build order: PetData → EggData → Remotes → PetManager → DataManager → PetUI → HatchController

### Known Issues

### `humanoid.TargetPoint` doesn't work for cursor-aligned aiming

In default Roblox places, `humanoid.TargetPoint` is unreliable or always returns the character's position rather than where the mouse points. This means `(humanoid.TargetPoint - handle.Position).Unit` does NOT point toward the cursor.

**Workaround**: Use a LocalScript to get the mouse hit position (via `Tool.Equipped` event) and send it to the server via RemoteEvent. Use `mouse.Button1Down` rather than `Tool.Activated` to avoid triggering default animations (see "Default Animation Suppression" above).

**This is the recommended pattern** for any weapon that needs cursor-aligned aiming.

### generate_mesh workflow

`generate_mesh` creates a model in Workspace with nested structure: `Model → world → body → body_geom (MeshPart)`. The MeshPart must be reparented into the Tool and the empty container deleted.

```lua
-- After generate_mesh returns:
local meshModel = workspace:FindFirstChild("<prompt text>")
local meshPart = meshModel:FindFirstChild("world"):FindFirstChild("body"):FindFirstChild("body_geom")

-- Rename and move
meshPart.Name = "Handle"
meshPart.Anchored = false
meshPart.CanCollide = false
meshPart.Parent = tool  -- The target Tool

-- Clean up empty container
meshModel:Destroy()

-- Delete old Handle if it exists
local oldHandle = tool:FindFirstChild("Handle")
if oldHandle then oldHandle:Destroy() end

-- Adjust Grip so the mesh looks right in hand
tool.Grip = CFrame.new(0, -0.3, 0.6)
```

**Grip tuning**: The default grip is `CFrame.new()`. A good starting point for a handgun is `CFrame.new(0, -0.3, 0.6)` — offset down (Y) to align with the hand and forward (Z) to position the barrel in front of the character. Test in Play mode and iterate. The Grip has 4 sub-properties: `GripPos` (position offset), `GripUp`, `GripRight`, `GripForward` (orientation).

The generated mesh has its own texture and color. You may want to adjust `MeshPart.Color` or set a `Material` after reparenting.
