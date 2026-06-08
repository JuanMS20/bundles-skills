# Moon Jump Gamepass — Implementation Reference

## Context

Built for Place2 in `pistola-game-roblox`, a shooter with a Lightning Gun. Gamepass adds higher jumps (JumpPower 50 → 125) for 39 Robux, purchased via a Shop GUI.

## Architecture

```
StarterGui
└── MoonJumpShopGUI (ScreenGui + LocalScript)

ServerScriptService
└── MoonJumpManager (Script)

ReplicatedStorage
├── GamepassConfig (ModuleScript)
└── ShopRemote (RemoteEvent)
```

## GamepassConfig

```lua
-- ReplicatedStorage.GamepassConfig
local GamepassConfig = {
    MoonJump = {
        Id = 0,                      -- ← UPDATE THIS after publishing in Creator Dashboard
        Name = "Moon Jump",
        Price = 39,
        Description = "¡Salta como en la luna! Saltos extra-altos.",
        JumpPowerMultiplier = 2.5,    -- 50 → 125
    }
}
return GamepassConfig
```

## MoonJumpManager (ServerScriptService)

```lua
local Players = game:GetService("Players")
local MarketplaceService = game:GetService("MarketplaceService")
local RepStorage = game:GetService("ReplicatedStorage")
local GamepassConfig = require(RepStorage:WaitForChild("GamepassConfig"))
local shopRemote = RepStorage:WaitForChild("ShopRemote")

local MOON_JUMP_ID = GamepassConfig.MoonJump.Id
local BASE_JUMP = 50
local BOOSTED_JUMP = BASE_JUMP * GamepassConfig.MoonJump.JumpPowerMultiplier

local function applyGamepass(character, player)
    local humanoid = character:FindFirstChildWhichIsA("Humanoid")
    if not humanoid then return end

    local success, owns = pcall(function()
        return MarketplaceService:UserOwnsGamePassAsync(player, MOON_JUMP_ID)
    end)

    humanoid.JumpPower = (success and owns) and BOOSTED_JUMP or BASE_JUMP
end

-- Re-apply when client reports a purchase (via ShopRemote)
shopRemote.OnServerEvent:Connect(function(player)
    local character = player.Character
    if character then
        task.wait(0.1)
        applyGamepass(character, player)
    end
end)

Players.PlayerAdded:Connect(function(player)
    player.CharacterAdded:Connect(function(char)
        applyGamepass(char, player)
    end)
    if player.Character then
        applyGamepass(player.Character, player)
    end
end)
```

## Shop GUI (StarterGui — LocalScript)

```lua
local Players = game:GetService("Players")
local MarketplaceService = game:GetService("MarketplaceService")
local player = Players.LocalPlayer
local GamepassConfig = require(game:GetService("ReplicatedStorage"):WaitForChild("GamepassConfig"))

local screenGui = script.Parent
local moonJump = GamepassConfig.MoonJump
local shopRemote = game:GetService("ReplicatedStorage"):WaitForChild("ShopRemote")

-- Build UI elements
local shopButton = Instance.new("ImageButton")  -- bottom-right, semi-transparent
local shopPanel = Instance.new("Frame")          -- centered card UI
local overlay = Instance.new("Frame")            -- full-screen dim overlay
-- ... build full UI hierarchy ...

-- Wire up
shopButton.MouseButton1Click:Connect(function()
    shopPanel.Visible = not shopPanel.Visible
    overlay.Visible = shopPanel.Visible
end)

shopPanel.CloseButton.MouseButton1Click:Connect(function()
    shopPanel.Visible = false
    overlay.Visible = false
end)

shopPanel.BuyButton.MouseButton1Click:Connect(function()
    MarketplaceService:PromptGamePassPurchase(moonJump.Id)
end)

-- Handle purchase result
MarketplaceService.PromptGamePassPurchaseFinished:Connect(function(plr, id, purchased)
    if plr == player and id == moonJump.Id and purchased then
        -- Notify server to re-apply JumpPower immediately
        shopRemote:FireServer()
        -- Show notification
        local notification = Instance.new("TextLabel")
        notification.Text = "¡Compra exitosa! Ahora saltas como en la luna."
        notification.Parent = screenGui
        task.delay(3, function() notification:Destroy() end)
    end
end)
```

## Creator Dashboard Setup

To publish the gamepass (after testing):

1. Open **Game Settings** in Roblox Studio → **Passes** tab
2. Create a new Pass with name: "Moon Jump"
3. Set description: "¡Salta como en la luna!"
4. Upload icon (optional: use generate_mesh for a moon icon or use a built-in texture)
5. Note the **Pass ID** shown in the tab
6. Update `GamepassConfig.MoonJump.Id` with this ID
7. In Creator Dashboard → **Monetization** → **Passes**, set price to **39 Robux**
8. Republish the game

## Testing

### Without publishing (no real gamepass ID):

The server won't find `UserOwnsGamePassAsync` and JumpPower stays at 50. To test the full flow, either:
- **Option A**: Publish a dev copy with a free pass (0 Robux)
- **Option B**: Add a test bypass in `MoonJumpManager` (remove before shipping):

```lua
-- TEMP: TEST MODE ONLY — grants moon jump to everyone
local MOON_JUMP_TEST = true

local function applyGamepass(character, player)
    local humanoid = character:FindFirstChildWhichIsA("Humanoid")
    if not humanoid then return end
    humanoid.JumpPower = MOON_JUMP_TEST and BOOSTED_JUMP or BASE_JUMP
end
```

### Test checklist

- [ ] Shop button visible on screen at game start
- [ ] Click shop button → panel appears with overlay
- [ ] Moon Jump card shows name + price 39 Robux
- [ ] Click COMPRAR → Roblox purchase prompt appears
- [ ] Close shop with X button → panel disappears
- [ ] Click overlay → panel closes
- [ ] Without gamepass: JumpPower = 50 (normal jump)
- [ ] With gamepass: JumpPower = 125 (moon jump)
- [ ] Effect persists through respawns (CharacterAdded)
- [ ] Lightning Gun still works (no regression)

## Related

- Main skill: `roblox-studio-development` section "Gamepass / Monetization Systems"
- API: `MarketplaceService:UserOwnsGamePassAsync(player, gamepassId)` — returns boolean
- API: `MarketplaceService:PromptGamePassPurchase(gamepassId)` — client-side native UI
- API: `MarketplaceService.PromptGamePassPurchaseFinished(player, gamepassId, wasPurchased)` — client event
- API: `Humanoid.JumpPower` — controls jump height (default 50, max 150-200 range)
