# Pet Simulator Core Loop — Architecture Reference

Session-derived reference for building Pet Simulator-style collection/hatching systems in Roblox via MCP.

## Domain Model

| Concept | Definition |
|---------|-----------|
| **Pet** | Collectible entity. Belongs to a rarity tier. Has a multiplier (future-use field). |
| **Egg** | Container that yields Pets via Weighted RNG. Each Egg defines weights per tier. |
| **Hatching** | The act of opening an Egg → RNG roll → Pet result. |
| **Tier** | Rarity level: Common > Rare > Epic > Mythic. |
| **Stack** | Inventory storage: `{ [petId: string]: number }` — duplicates stack by count. |
| **Equip** | Assign a Pet to an active slot (max 3). Does NOT consume from stack. Requires count >= 1. |
| **Auto-Hatch** | Client-side toggle loop that fires HatchEgg every ~2s. |

## Data Model (Roblox DataModel)

```
ReplicatedStorage/
├── PetData          (ModuleScript) — Global pet pool, keyed by string ID
├── EggData          (ModuleScript) — Egg definitions with weights per tier
├── RNGUtil          (ModuleScript) — Generic weightedRandom(items, weights)
└── [PetRemotes/     (Folder, created at runtime by PetManager)]
    ├── HatchEgg         (RemoteEvent) — Client→Server: eggId
    ├── PetHatched       (RemoteEvent) — Server→Client: petId, eggId
    ├── EquipPet         (RemoteEvent) — Client→Server: petId, slotIndex
    ├── UnequipPet       (RemoteEvent) — Client→Server: slotIndex
    ├── GetPlayerData    (RemoteEvent) — Client→Server: fetch initial data
    └── DataUpdate       (RemoteEvent) — Server→Client: full inventory sync

ServerScriptService/
├── DataStoreWrapper  (ModuleScript) — loadData/saveData with USE_DATASTORE flag
└── PetManager        (Script) — RNG, inventory, validation, auto-save

StarterPlayer/StarterPlayerScripts/
└── HatchController   (LocalScript) — UI creation, auto-hatch, animations, equip/inventory
```

## Key Patterns

### PetData — Global Pool with String Keys

PetData uses `{ [string]: Pet }` (string keys). **Luau `for _, v in t` iterates ALL key-value pairs** (not just array indices) — Luau extension over standard Lua 5.1.

```lua
-- ReplicatedStorage.PetData
local PetData = {
    _pets = {
        cat = { id = "cat", name = "Gato", tier = "Common", multiplier = 1.0 },
        dog = { id = "dog", name = "Perro", tier = "Common", multiplier = 1.2 },
        wolf = { id = "wolf", name = "Lobo", tier = "Rare", multiplier = 2.5 },
        unicorn = { id = "unicorn", name = "Unicornio", tier = "Mythic", multiplier = 25.0 },
    },
}
function PetData.getPet(id) return PetData._pets[id] end
function PetData.getPetsByTier(tier)
    local result = {}
    for _, pet in PetData._pets do  -- ✓ iterates ALL entries (string keys included)
        if pet.tier == tier then table.insert(result, pet) end
    end
    return result
end
return PetData
```

### RNGUtil — Generic Weighted Random

```lua
local RNGUtil = {}
function RNGUtil.weightedRandom(items, weights)
    assert(#items > 0); assert(#items == #weights)
    local total = 0; for _, w in weights do total += w end
    local roll = math.random() * total
    for i, item in items do
        roll -= weights[i]
        if roll <= 0 then return item end
    end
    return items[#items]
end
return RNGUtil
```

### Server Hatching (PetManager)

```lua
-- Step 1: Pick tier via weighted RNG from egg weights
local tierNames, tierWeights = {}, {}
for tier, weight in egg.weights do
    table.insert(tierNames, tier); table.insert(tierWeights, weight)
end
local selectedTier = RNGUtil.weightedRandom(tierNames, tierWeights)

-- Step 2: Pick pet within tier (equal weight)
local petsInTier = PetData.getPetsByTier(selectedTier)
local equalWeights = table.create(#petsInTier, 1)
for i = 1, #petsInTier do equalWeights[i] = 1 end
local selectedPet = RNGUtil.weightedRandom(petsInTier, equalWeights)

-- Step 3: Add to inventory (stack)
data.inventory[selectedPet.id] = (data.inventory[selectedPet.id] or 0) + 1

-- Step 4: Fire result + async save
events.PetHatched:FireClient(player, selectedPet.id, eggId)
task.spawn(function() DataStoreWrapper.saveData(player, data) end)
```

### DataStoreWrapper — Flag-Based Persistence

```lua
local USE_DATASTORE = true  -- false in dev, true published
local MOCK_DATA = { inventory = {}, equipped = { nil, nil, nil } }

function DataStoreWrapper.loadData(player)
    if not USE_DATASTORE then return deepCopy(MOCK_DATA) end
    local ok, data = pcall(function()
        return DataStoreService:GetDataStore("PetSim_v1"):GetAsync("PlayerData_" .. player.UserId)
    end)
    if ok and data then return data end
    return deepCopy(MOCK_DATA)
end

function DataStoreWrapper.saveData(player, data)
    if not USE_DATASTORE then return true end
    local ok, err = pcall(function()
        DataStoreService:GetDataStore("PetSim_v1"):SetAsync("PlayerData_" .. player.UserId, data)
    end)
    if not ok then warn("DataStore save failed:", err) end
    return ok
end
```

### ⚠ Save Safety — PlayerRemoving Must Be Synchronous

```lua
-- BAD: task.spawn may not execute before player leaves
Players.PlayerRemoving:Connect(function(player)
    task.spawn(function() DataStoreWrapper.saveData(player, data) end)  -- Might never run
end)

-- GOOD: sync save (pcall inside DataStoreWrapper won't block long)
Players.PlayerRemoving:Connect(function(player)
    DataStoreWrapper.saveData(player, data)
    playerData[player] = nil
end)
```

`task.spawn` defers to the next engine step — the player may be gone by then.

### ⚠ MCP: `multi_edit` Scripts DO Auto-Execute

Scripts created via `multi_edit` with `className="Script"/"LocalScript"/"ModuleScript"` DO auto-execute in Play mode. This was verified with the full Pet Sim stack (PetManager, DataStoreWrapper, HatchController). No manual pasting needed.

Only scripts created via `execute_luau` (Instance.new("Script") + .Source = ...) may fail to auto-execute. Always prefer `multi_edit` for script creation.

### ⚠ MCP: Edit Mode vs Play Mode Tools

| Tool | Edit Mode | Play Mode |
|------|-----------|-----------|
| `execute_luau` | ✅ | ❌ |
| `search_game_tree` | ✅ | ❌ |
| `inspect_instance` | ✅ | ❌ |
| `script_read` | ✅ | ❌ |
| `multi_edit` | ✅ | ❌ |
| `get_console_output` | ✅ | ✅ |
| `start_stop_play` | ✅ | ✅ |

**Implication**: TDD RED/GREEN/VERIFY steps must happen in Edit mode. Only INTEGRATION (Play) can verify runtime behavior via `get_console_output`.

### ⚠ Runtime-Created Remotes

PetRemotes folder is created at runtime by PetManager. It does NOT exist in Edit mode:
- `search_game_tree` and `inspect_instance` won't find it
- Client scripts must use `FindFirstChild` with retry loops, NOT `WaitForChild` (which blocks the entire LocalScript)

### ⚠ Multiple OnClientEvent Handlers

In Luau, connecting multiple handlers to the same `OnClientEvent` is valid — ALL handlers fire. This is useful (separate refresh logic for inventory + equip HUD) but can cause redundant operations if not intentional. Prefer consolidating into a single handler.

### Periodic Auto-Save (Safety Net)

```lua
task.spawn(function()
    while task.wait(60) do
        for player, data in playerData do
            DataStoreWrapper.saveData(player, data)
        end
    end
end)
```

Wrap in `task.spawn()` so it doesn't block event handler registration.

### Animation Queue — Generalized Sequential Processing

Multiple `PetHatched` events arrive faster than animations can play. Queue them. See `roblox-tdd-patterns` section 7 for the full pattern (queue + re-check guard).

### Centralized Auto-Hatch State

Mutually exclusive toggles (only one auto-hatch at a time). See `roblox-tdd-patterns` section 11 for the full centralized-state pattern.

### SetAttribute — Avoid Connection Stacking on UI Buttons

When `refreshEquipHUD` is called repeatedly and connects events each time, connections stack. Instead, pre-connect once with `SetAttribute`:

```lua
-- During UI creation (once):
slotBtn:SetAttribute("slotIndex", i)
slotBtn.MouseButton1Click:Connect(function()
    unequipPet:FireServer(slotBtn:GetAttribute("slotIndex"))
end)

-- In refreshEquipHUD (called many times):
-- Only update visuals, DON'T reconnect events:
slot.button.Visible = petId ~= nil
slot.label.Text = petId and info.name or "Vacio"
```

### DataUpdate — Central Sync Event

Server sends full player data after every equip/unequip/hatch:

```lua
-- Server (after equip/unequip):
events.DataUpdate:FireClient(player, data)  -- { inventory, equipped }

-- Client:
dataUpdate.OnClientEvent:Connect(function(data)
    inventoryData = data
    refreshEquipHUD(data)
    if inventoryVisible then refreshInventory(data) end
end)
```

### Inventory Grid — Dynamic Cell Construction

Clear and rebuild from `data.inventory` on every open/update:

```lua
local function refreshInventory(data)
    -- Destroy old cells
    for _, child in invScrolling:GetChildren() do
        if child:IsA("Frame") then child:Destroy() end
    end
    -- Build cells from data.inventory
    for petId, count in data.inventory do
        local info = PetData.getPet(petId)
        if info then
            -- Cell: colored bg by tier, name, count, equip/equipped button
        end
    end
end
```

### Slot Allocation Strategy

```lua
-- Client: find first empty slot
for slotIdx = 1, 3 do
    if data.equipped[slotIdx] == nil then
        equipPet:FireServer(petId, slotIdx); break
    end
end

-- Server validations (PetManager EquipPet handler):
-- 1. slotIndex in [1, 3]
-- 2. player owns pet (data.inventory[petId] >= 1)
-- 3. pet NOT already in another slot (no duplicates across slots)
-- 4. assign data.equipped[slotIndex] = petId → DataUpdate → save
```

### Luau `for _, v in t` — Iterates All Entries

In Luau (modern Roblox), `for _, v in tableWithStringKeys` iterates all entries, not just the array part. You don't need `pairs()` for value iteration with this construct.

| Construct | Standard Lua | Luau (Roblox) |
|-----------|-------------|----------------|
| `for k, v in t` | Error (table not callable) | Iterates all k,v (like `pairs`) |
| `for _, v in t` | Error | Iterates all values |
| `for v in t` | Error | Array part only (like `ipairs`) |
| `for k, v in pairs(t)` | Works | Works |

## Design Decisions Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Pet identity | String ID | Readability > compactness |
| Inventory | Stack with count | Prevents bloat, standard Pet Sim |
| Equip consumes | No | Matches Pet Sim 99 |
| DataStore | Wrapper with flag | Studio memory-mode without setup |
| Multiplier field | Defined, not wired | Future-proof |
| Egg access | UI-only (no 3D) | Eliminates ProximityPrompt complexity |
| Hatching animation | 2D ImageLabels + TweenService | Simpler than ViewportFrame |
| Equipped pets | HUD-only (no 3D followers) | Avoids NPC replication + collision |
| Rarity pool | Global + weights per egg | One table edit to add pets |
| Auto-hatch | Client loop (2s delay) | Dies on disconnect |
| Save on leave | Synchronous (no task.spawn) | PlayerRemoving may not yield again |
| UI slot indices | SetAttribute | Avoids connection stacking |
| Script creation | `multi_edit` (not `execute_luau`) | Auto-executes in Play mode |
| Anim pause (auto-hatch) | 0.3s reduced | Faster feedback during continuous hatching |

## Class-to-Docs Mapping

| What you're building | Classes to read |
|---|---|
| DataStore wrapper | `DataStoreService.md` |
| RemoteEvent inventory | `RemoteEvent.md`, `RemoteFunction.md`, `Players.md` |
| Hatching animation | `TweenService.md` |
| UI panels | `ScreenGui.md`, `Frame.md`, `ImageButton.md`, `ImageLabel.md` |
