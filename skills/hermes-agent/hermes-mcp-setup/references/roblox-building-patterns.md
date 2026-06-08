# Roblox Building Patterns via MCP

## General Build Order

When building a Roblox system from scratch with MCP tools, follow this sequence.
Each step depends on the previous one — jumping ahead forces rework.

```
1. Explore        → search_game_tree    (understand current state)
2. Parts/Worlds   → execute_luau        (create workspace instances)
3. Infra layer    → execute_luau + multi_edit  (RemoteEvents, ModuleScripts, folders)
4. Server logic   → multi_edit          (Script in ServerScriptService or inside Tool)
5. Client logic   → execute_luau + multi_edit  (ScreenGui + LocalScript or LocalScript inside Tool)
6. Verify         → search_game_tree + inspect_instance + script_read
```

## Step Details

### 1. Explore — `search_game_tree`
- Start with `path="Workspace"`, `path="StarterGui"`, `path="ServerScriptService"`, `path="ReplicatedStorage"`, `path="StarterPack"`
- Set `max_depth=3` for overview, `max_depth=5` for detail
- Use `inspect_instance(path="...")` for specific parts (check Size, Position, Color, Anchored)
- Check if the place is fresh or has existing content

### 2. Create workspace objects — `execute_luau`
- Use a single `execute_luau` call to create all parts in a Folder under workspace
- Create folder first (`Instance.new("Folder")`), parent all parts to it
- Each part: set Name, Size, Position, Color, Anchored, Material, Parent
- Add decals: BillboardGui with TextLabel for floating names, neon SpawnPoint markers
- Keep positions spread out (80+ studs apart for separate "worlds")

**Modern Roblox catch**: `BorderSize` is **deprecated**. Use `UIStroke` instead.
- ❌ `part.BorderSize = 0` — error in modern Roblox
- ✅ `Instance.new("UIStroke")` with `.Thickness` and `.Color`

### 3. Create infrastructure — `execute_luau` + `multi_edit`
- Use `execute_luau` to create empty instances:
  - `RemoteEvent` in ReplicatedStorage (for client↔server communication)
  - `ModuleScript` in ReplicatedStorage (for shared data)
- Use `multi_edit` with `className="ModuleScript"` and first edit having `old_string=""` to fill content
- ModuleScript structure: return a table with typed data (Color3.fromRGB, Vector3.new, etc.)

### 4. Server scripts — `multi_edit`
- `className="Script"`, path under `ServerScriptService` (for GUI/teleport systems) OR inside the `Tool` (for weapons)
- Pattern: WaitForChild everything, connect to RemoteEvent.OnServerEvent
- Handler receives `(player, ...args)` from client
- Teleport: find `character.HumanoidRootPart`, set `.CFrame = CFrame.new(position)`
- Weapon: connect to `Tool.Activated`, do raycast, apply damage, fire RemoteEvent to clients for visuals

### 5. Client logic — `execute_luau` + `multi_edit`
- For GUIs: ScreenGui → Frames → Labels in StarterGui
- For weapons: LocalScript inside the Tool (connects to RemoteEvent.OnClientEvent for visual feedback)
- See weapon patterns below for beam + sound + particle visual effects

### 6. Verify — `search_game_tree` + `inspect_instance` + `script_read`
- Run `search_game_tree` on each service to confirm instances exist
- Run `script_read` on every script to verify content was written correctly
- Check for Lua syntax errors (string escaping, function calls)

## Modern GUI Patterns

Styling for clean, modern Roblox GUIs:

| Element | Recipe |
|---------|--------|
| **Dark card** | BackgroundColor3=Color3(22,22,30), UICorner(16), UIStroke(50,50,70) |
| **Floating button** | UDim2(1,-80, 1,-80) for bottom-right, UICorner(30) for circle |
| **World buttons** | Frame 72px tall, 10px corner, color strip on left (5px wide), hover lightens bg |
| **Overlay** | Full-screen Frame, BackgroundTransparency=0.55, TextButton for click-to-close |
| **Animations** | TweenService: size expand from 0, scale bounce on hover, fade on close |
| **Scroll list** | ScrollingFrame with UIListLayout, padding 10, AutomaticCanvasSize=Y |

## Debugging Roblox Scripts via In-Game Instrumentation

When MCP tools don't work during Play mode, the only feedback loop is **inside the game itself**. Use visible GUI elements to surface script state.

### Technique: DebugLabel + pcall

```lua
-- 1. Add a TextLabel to the ScreenGui (in edit mode via execute_luau)
local debugLabel = Instance.new("TextLabel")
debugLabel.Name = "DebugLabel"
debugLabel.Size = UDim2.new(0, 400, 0, 60)
debugLabel.Position = UDim2.new(0, 10, 0, 10)
debugLabel.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
debugLabel.BackgroundTransparency = 0.3
debugLabel.TextColor3 = Color3.fromRGB(255, 200, 100)
debugLabel.Text = "🔧 Iniciando..."
debugLabel.TextSize = 14
debugLabel.Font = Enum.Font.GothamBold
debugLabel.TextXAlignment = Enum.TextXAlignment.Left
debugLabel.ZIndex = 100
debugLabel.Parent = gui

-- 2. In the LocalScript, wrap everything in pcall + update label
local function debug(msg)
    if debugLabel then debugLabel.Text = msg end
    print(msg)
end

local ok, err = pcall(function()
    debug("🔧 Cargando RemoteEvent...")
    -- ...rest of logic...
    debug("✅ Sistema listo")
end)

if not ok then
    debugLabel.TextColor3 = Color3.fromRGB(255, 80, 80)
    debugLabel.Text = "❌ ERROR: " .. tostring(err)
    warn(err)
end
```

### Common failure patterns this catches

| Symptom | Likely cause | DebugLabel shows |
|---------|-------------|------------------|
| Button does nothing | Script crashes before event connection | ❌ ERROR with traceback |
| Button does nothing | Script hangs on WaitForChild | Stuck at same debug message |
| Menu opens but empty | Clone from Template fails | ❌ ERROR: attempt to index nil |
| GUI doesn't render | execute_luau children lost after Play/Stop | ScreenGui exists but empty |

### Feedback loop for Play-mode-only bugs

```
1. Edit mode: instrument script with DebugLabel + pcall
2. Start Play  → user reads DebugLabel → tells agent text
3. Stop Play   → agent fixes → goto 1
```

## TDD-Style Development Workflow for Roblox

When building Roblox systems via MCP, use an adapted RED→GREEN→VERIFY loop since there's no traditional test runner:

```
RED:    execute_luau                → confirm behavior does NOT exist yet
GREEN:  execute_luau / multi_edit   → create minimal implementation
VERIFY: inspect_instance + search_game_tree → confirm all properties/setup
PLAY:   start_stop_play             → human visual check in game
```

### RED Phase (assert absence)

```lua
-- Confirm tool doesn't exist before creating it
local starterPack = game:GetService("StarterPack")
local tool = starterPack:FindFirstChild("Lightning Gun")
print("Tool exists:", tool ~= nil)      -- should print false
return tool ~= nil                       -- returns false → RED
```

### GREEN Phase (create minimum)

One `execute_luau` call to create all instances for this step. Set every relevant property. If the call returns an error, fix and retry before moving to VERIFY.

### VERIFY Phase (check through MCP, not asserts)

**Do NOT use `assert()` inside `execute_luau`** for property checks — asserts that fail cause `execute_luau` to return "[error]" without printing the comparison values, making debugging harder. Instead:

```lua
-- BAD: assert fails silently with no detail
assert(handle.Color == Color3.fromRGB(0, 200, 255), "color wrong")

-- GOOD: print values, then return true/false
print("Expected R:", 0/255, "Got R:", handle.Color.R)
print("Expected G:", 200/255, "Got G:", handle.Color.G)
print("Expected B:", 255/255, "Got B:", handle.Color.B)
local colorOk = math.abs(handle.Color.R - 0/255) < 0.01
    and math.abs(handle.Color.G - 200/255) < 0.01
    and math.abs(handle.Color.B - 255/255) < 0.01
print("Color match:", colorOk)
return colorOk
```

**Prefer `inspect_instance` + `search_game_tree`** over `execute_luau` for property verification:
- `inspect_instance(path="StarterPack.Lightning Gun")` shows ALL properties in one call
- `search_game_tree(path="StarterPack")` confirms the existence hierarchy
- These work even if `execute_luau` has execution limits
- No floating-point comparison issues (values shown as strings)

### Color comparison pitfall

`Color3.fromRGB(0, 200, 255)` internally stores floats: `Color3(0/255, 200/255, 255/255)` = `Color3(0, 0.7843137..., 1.0)`. When Roblox stores the color from `BrickColor` or material defaults, the stored RGB floats may differ at the 7th decimal place from what `fromRGB` computes. Direct `==` comparison can fail. Two fixes:

1. **Use `inspect_instance`** — it shows the stored Color string like `"0.0156..., 0.6862..., 0.9254..."` — verify visually.
2. **In Lua**: compare each channel with a tolerance (`math.abs(a - b) < 0.01`).

### PLAY Phase

```lua
mcp_Roblox_Studio_start_stop_play(is_start=true)
```

Only use this for **human visual verification**. MCP connectivity is unreliable during Play mode:
- `execute_luau` returns "Target is not reachable"
- `screen_capture` also fails
- `search_game_tree` and `inspect_instance` sometimes work, sometimes don't

After stopping Play mode, the MCP server may become **temporarily unreachable** with "MCP server 'Roblox_Studio' is unreachable after 3 consecutive failures. Auto-retry available in ~56s." Wait for auto-retry or ask the user to verify the Assistant plugin is active in Studio.

**Workflow rule**: Do ALL building and verification in Edit mode. Start Play only for the human to see the result. If you need to verify after Play: stop Play, wait for MCP reconnection, then inspect.

## Play Mode Limitations

Several MCP tools **stop working** once the game is started (Play mode) or return "Target is not reachable":

| Tool | Works in Edit? | Works in Play? | Alternative |
|------|---------------|----------------|-------------|
| `execute_luau` | ✅ | ❌ | Write logic, stop Play, verify statically |
| `screen_capture` | ✅ | ❌ | N/A — no visual verification possible while playing |
| `multi_edit` | ✅ | ❌ | Must stop Play first |
| `script_read` | ✅ | ❌ | Must stop Play first |
| `search_game_tree` | ✅ | ⚠️ | Sometimes works, sometimes "Target is not reachable" |
| `inspect_instance` | ✅ | ⚠️ | Same as search_game_tree |
| `get_console_output` | ✅ | ⚠️ | Shows Studio theme errors but NOT `print()` output from running scripts during Play |
| `generate_mesh` | ✅ | ❌ | Must be in Edit mode |

**Post-Play MCP disconnection**: After `start_stop_play(is_start=false)`, the MCP server often becomes unreachable for 30-60 seconds while Studio resets. The system auto-retries. Do not retry manually — wait for the auto-retry timer or ask the user to confirm the Assistant MCP plugin reconnected.

Also note: instances created via `execute_luau` (but NOT via `multi_edit`) can be lost after a Play/Stop cycle. Scripts written with `multi_edit` survive. If you created parts with `execute_luau` and they disappear after Play, recreate them.

## Weapon / Tool Development Patterns

Building an equipable weapon (gun, sword) from scratch follows a different architecture from GUI-focused systems.

### Research Phase — http_get for API docs

Before writing any code, look up the relevant Roblox Engine API docs:

| Class | Purpose | Key properties |
|-------|---------|----------------|
| `Tool` | Equipable weapon container | RequiresHandle, Activated event, Grip, Handle |
| `Beam` | Visual line between 2 points | Attachment0/1, Color, LightEmission, Width0/1, Texture, Transparency |
| `Attachment` | Position anchor for beams | CFrame, WorldPosition, Parent |
| `RemoteEvent` | Server↔Client bridge | OnServerEvent, FireClient |

**Pitfall**: There is NO built-in `Lightning` class in Roblox (returns 404). Lightning effects are created using `Beam` + `Attachment` + sparkle texture + additive blending (LightEmission=1).

### Tool Structure

A `Tool` in StarterPack becomes a weapon when structured as:

```
StarterPack.LightningGun (Tool)
├── Handle (MeshPart)           ← model generated via generate_mesh or built with Parts
├── Script                      ← server-side logic (Activated → raycast → damage)
└── LocalScript                 ← client-side visuals (beam, particles, sound)
ReplicatedStorage.LightningEvent (RemoteEvent)   ← bridge between Server Script and LocalScript
```

### Build Order for Weapons

```
1. Research APIs          → http_get (Tool, Beam, Attachment docs)
2. Create Tool            → execute_luau (Tool + Handle + grip config)
3. Generate model         → generate_mesh (AI creates weapon mesh, becomes Handle)
4. Create RemoteEvent     → execute_luau (placed in ReplicatedStorage)
5. Write Server Script    → multi_edit (Script inside Tool)
6. Write LocalScript      → multi_edit (LocalScript inside Tool)
7. Verify                 → inspect_instance + script_read
```

### Weapon Server Script Pattern

```lua
-- Script inside Tool (server-side)
local tool = script.Parent
local remoteEvent = game:ReplicatedStorage:WaitForChild("LightningEvent")
local random = Random.new()

tool.Activated:Connect(function()
    local character = tool.Parent
    if not character or not character:FindFirstChild("Humanoid") then return end
    local humanoid = character.Humanoid
    
    local handle = tool:FindFirstChild("Handle")
    local rootPart = character:FindFirstChild("HumanoidRootPart")
    if not handle or not rootPart then return end
    
    -- Direction from handle to where the player is aiming
    local direction = (humanoid.TargetPoint - handle.Position).Unit
    local maxRange = 200
    
    -- Raycast
    local params = RaycastParams.new()
    params.FilterType = Enum.RaycastFilterType.Blacklist
    params.FilterDescendantsInstances = {character}
    
    local result = workspace:Raycast(handle.Position, direction * maxRange, params)
    
    local hitPosition = result and result.Position or (handle.Position + direction * maxRange)
    local hitInstance = result and result.Instance
    
    -- Apply damage
    if hitInstance then
        local hitModel = hitInstance.Parent
        local hitHumanoid = hitModel and hitModel:FindFirstChild("Humanoid")
        if hitHumanoid then
            local damage = random:NextInteger(10, 30)
            hitHumanoid:TakeDamage(damage)
        end
    end
    
    -- Tell all clients to show visual effect
    remoteEvent:FireAllClients(hitPosition, direction)
end)
```

### Weapon LocalScript Pattern (Beam + Sound + Particles)

```lua
-- LocalScript inside Tool (client-side)
local tool = script.Parent
local remoteEvent = game:ReplicatedStorage:WaitForChild("LightningEvent")

-- Preload sound (use a built-in Roblox sound, find the right SoundId)
local soundTemplate = Instance.new("Sound")
soundTemplate.SoundId = "rbxasset://sounds/...electric_zap..."
soundTemplate.Volume = 1

remoteEvent.OnClientEvent:Connect(function(hitPosition, direction)
    local character = tool.Parent
    if not character or not tool:FindFirstChild("Handle") then return end
    local handle = tool.Handle
    if not handle then return end
    
    -- Create attachments for the beam
    local att0 = Instance.new("Attachment")
    att0.Parent = handle
    att0.WorldPosition = handle.Position
    
    local att1 = Instance.new("Attachment")
    att1.Parent = workspace.Terrain
    att1.WorldPosition = hitPosition
    
    -- Create the lightning beam
    local beam = Instance.new("Beam")
    beam.Attachment0 = att0
    beam.Attachment1 = att1
    beam.Color = ColorSequence.new({
        ColorSequenceKeypoint.new(0, Color3.fromRGB(180, 220, 255)),  -- white-blue
        ColorSequenceKeypoint.new(1, Color3.fromRGB(0, 150, 255)),     -- blue
    })
    beam.LightEmission = 1          -- additive blending
    beam.LightInfluence = 0         -- not affected by environment light
    beam.FaceCamera = true
    beam.Width0 = 0.5
    beam.Width1 = 0.2
    beam.Transparency = NumberSequence.new({
        NumberSequenceKeypoint.new(0, 0),
        NumberSequenceKeypoint.new(0.8, 0),
        NumberSequenceKeypoint.new(1, 0.8),  -- fade out at end
    })
    beam.Texture = "rbxasset://textures/particles/sparkles_main.dds"
    beam.TextureMode = Enum.TextureMode.Wrap
    beam.TextureLength = 0.5
    beam.TextureSpeed = 3
    beam.Segments = 5
    beam.Parent = workspace
    
    -- Play sound (clone so multiple shots can overlap)
    local sfx = soundTemplate:Clone()
    sfx.Parent = handle
    sfx:Play()
    
    -- Destroy after animation completes
    task.delay(0.3, function()
        beam:Destroy()
        att0:Destroy()
        att1:Destroy()
        if sfx then sfx:Destroy() end
    end)
end)
```

**Cleanup rule**: Beams + Attachments + Sound clones must be destroyed after ~0.3-0.5s. Each shot spawns new instances — without cleanup they accumulate forever.

### Mesh Generation for Weapon Handles

Use `generate_mesh` to create the weapon model by AI:

```
generate_mesh(textPrompt="sci-fi lightning pistol with glowing blue barrel", size={x=2, y=1.5, z=0.8})
```

#### generate_mesh Output Structure

The tool returns `{"tag":"Assistant-MeshGen-<uuid>"}` — this is NOT a direct instance reference. The actual mesh appears in Workspace as a **Model** named after the full prompt text. The internal structure is:

```
Workspace.<prompt text> (Model)
  └── world (Model)
        └── body (Model)
              └── body_geom (MeshPart)    ← the actual weapon mesh
```

Additional properties of `body_geom`:
- Has `MeshId` (rbxassetid://...) and `TextureID` (rbxassetid://...) — auto-generated by AI
- Default color is grey (`BrickColor "Medium stone grey"`)
- Default material is `Plastic`
- Size may differ from the `size` parameter you passed (it's a bounding box hint, not exact)

#### Reparenting into a Tool as Handle

`generate_mesh` places the model in Workspace. To use it as a Tool Handle:

1. **Find the MeshPart** using search_game_tree with `max_depth=5` on Workspace, or follow the path structure above.
2. **Rename** the MeshPart to `"Handle"`.
3. **Destroy** the old Handle Part (if replacing).
4. **Reparent** the MeshPart to the Tool: `meshPart.Parent = tool`.
5. **Set handle properties**: `meshPart.Anchored = false`, `meshPart.CanCollide = false`.
6. **Destroy** the empty AI-generated container Model in Workspace.
7. **Adjust Grip** on the Tool so the weapon sits naturally in hand.

**Important**: One `execute_luau` call can do all of steps 2-7. The container Model is only needed temporarily to hold the MeshPart — destroy it after reparenting to avoid cluttering Workspace.

#### Grip Adjustment

After the MeshPart is set as Handle, adjust `Tool.Grip` (a CFrame) to control hand position:

```lua
-- Simple positional offset (no rotation change)
tool.Grip = CFrame.new(0, -0.3, 0.6)

-- With rotation adjustment for angled weapons
tool.Grip = CFrame.new(0, -0.3, 0.6) * CFrame.Angles(0, math.rad(-45), 0)
```

- Positive Z = grip further forward (toward barrel direction)
- Negative Y = grip lower (below the weapon, for a natural hold)
- Default right-hand grip. Rotation adjusts the weapon angle in the character's hand.
- Fine-tune by: stop Play → adjust Grip → start Play → visually check → repeat.
- The MeshPart's `CFrame.Rotation` may have non-identity values from the AI generation, so experiment with different Grip rotations.

### Key Differences: Weapon vs GUI System

| Aspect | Teleport/GUI system | Weapon system |
|--------|-------------------|---------------|
| Primary container | ScreenGui (StarterGui) | Tool (StarterPack) |
| Server script location | ServerScriptService | Inside the Tool itself |
| Client script location | LocalScript in ScreenGui | LocalScript inside the Tool |
| Server↔Client bridge | RemoteEvent.OnServerEvent | RemoteEvent both ways: server fires AllClients for visuals |
| Execution trigger | Button click | Tool.Activated (mouse click while equipped) |
| Visual feedback | Screen elements (open/close) | World-space Beam + particles + sound |
| Data flow direction | Client→Server (request) | Server→AllClients (broadcast visuals) |
| Instance creation method | execute_luau for GUI children | multi_edit for scripts inside Tool |

### Weapon Gotchas

| Mistake | Fix |
|---------|-----|
| Using `Lightning` class (doesn't exist) | Use `Beam` + `Attachment` + sparkle texture instead |
| Forgetting to destroy Beam/Attachments per shot | Use `task.delay(0.3, cleanup)` — each shot creates new instances |
| Script in Tool but no Handle named exactly "Handle" | `RequiresHandle=true` requires a `BasePart` child named `Handle` |
| Putting Server Script in wrong container | Weapon script MUST be inside the Tool, not in ServerScriptService |
| Forgetting to blacklist the shooter's character in raycast | Character's own parts will block the ray — use `FilterDescendantsInstances = {character}` |
| RemoteEvent created with execute_luau lost after Play/Stop | RemoteEvent created via execute_luau survives Play/Stop (it's a service child, not GUI) |

## Common Luau GUI Patterns (Teleport System)

A teleport-with-menu system follows this structure:

**ReplicatedStorage**:
- `RemoteEvent` (e.g., "TeleportToWorld") — client fires, server handles
- `ModuleScript` (e.g., "WorldData") — shared data: names, colors, positions

**ServerScriptService**: Script connected to RemoteEvent.OnServerEvent
- Receives `(player, worldIndex)`, looks up position from WorldData
- Moves `character.HumanoidRootPart.CFrame = CFrame.new(position)`
- Guards: `CharacterAdded:Wait()` if no character, `WaitForChild("HumanoidRootPart", 5)` with nil check

**StarterGui**: ScreenGui with:
- Floating toggle button (bottom-right, circular, ◈ icon)
- Menu overlay (full-screen dark background + centered card)
- World buttons cloned from a hidden Template with color indicators
- LocalScript: TweenService for open/close animations, escape key to close
- Click flow: FireServer(worldIndex) → closeMenu()

| Mistake | Fix |
|---------|-----|
| Using `BorderSize = 0` on Frame/Part | Remove property, use `UIStroke` instead |
| `print("...%d..."):format(n)` — format called on print result | Wrap: `print(("...%d..."):format(n))` |
| Creating instance without setting Parent | Set `.Parent` after all other properties |
| Typo `Enum.Material.Neon` (missing dot) | Use `Enum.Material.Neon` |
| Typo `Enum.Material.SmoothPlastic` | Use `Enum.Material.SmoothPlastic` |
| Relying on `get_console_output` to see script `print()` during Play | Console doesn't show script outputs in Play mode — verify statically in Edit |
| Assuming execute_luau-created children survive Play/Stop cycle | They don't — you CANNOT rely on instances created via execute_luau; scripts via multi_edit DO survive |
