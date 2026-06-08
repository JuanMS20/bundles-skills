# Game Architecture Patterns — Full Simulator Reference

Session-derived reference for building a complete Roblox simulator game via MCP.

## Architecture (Server-Authoritative)

```
ReplicatedStorage/
├── GameName/ (Folder)
│   ├── CrystalData (ModuleScript)  — items/crystals config
│   ├── ZoneData (ModuleScript)     — zone definitions + unlock reqs
│   ├── ToolData (ModuleScript)     — tool/pickaxe tiers
│   ├── PetData (ModuleScript)      — pet definitions + egg prices
│   ├── GameConfig (ModuleScript)   — shared constants (XP curves, cooldowns)
│   ├── GamepassConfig (ModuleScript) — monetization IDs (placeholder until published)
│   └── RNGUtil (ModuleScript)      — weighted random helper
├── Remotes/ (Folder, created at runtime by server)

ServerScriptService/
├── DataStoreWrapper (ModuleScript) — persistence with USE_DATASTORE flag
├── GameServer (Script)             — all server logic: leaderstats, economy, events

StarterPlayer/StarterPlayerScripts/
└── GameClient (LocalScript)        — ALL client: world build, HUD, panels, input
```

## Build Order (Critical)

1. Config ModuleScripts → verify with inspect_instance
2. DataStoreWrapper in ServerScriptService
3. Server Script via multi_edit (all handlers)
4. MINIMAL client test (5 lines, print only) → verify Play auto-executes
5. Expand client incrementally, test after each addition

NEVER write 1000+ line LocalScript in one shot. Break into multi_edit expansions.

## Key Patterns

### Data Config ModuleScripts
- Use string keys: `{ [string]: {...} }`
- Luau iterates ALL entries: `for _, v in t do ... end`
- Functions: getItem(id), getItemsByZone(zone), getTierColor(tier)

### Client Script Structure
- Helper functions first (formatNumber, createCorner, createPadding)
- Event handlers (notifications, drops, hatch results)
- Core functions (teleportToZone, mineRock, updateHUD)
- UI builders (HUD, bottomBar, ShopPanel, PetsPanel, ZonesPanel)
- World builders (buildCrystalRock, buildZone, buildWorld)
- task.spawn at end: retry remotes → load modules → wire events → build → print

### Folder + ModuleScript Pattern
```lua
local cd = Instance.new("Folder", ReplicatedStorage)
cd.Name = "GameName"
local ms = Instance.new("ModuleScript", cd)
ms.Name = "CrystalData"
-- Then multi_edit to set Source
```

## Monetization
- GamePassConfig with id=0 placeholders (update after publish)
- ProcessReceipt on server
- UserOwnsGamePassAsync in pcall on CharacterAdded
- VIP (2x coins), Auto-Mine, Extra Slots, Double Rebirth
- DevProducts: coins, boosts, starter pack
