# Default Animation Suppression for Roblox Tools

## The Problem

When a Tool is activated, Roblox's default character Animate script (built into CoreScripts) plays a "toolnone" animation. This causes the character's torso and head to jerk/punch on every click. For ranged weapons, this looks comically wrong.

## Failed Approach: `toolanim` StringValue

```lua
-- ❌ Does NOT work in modern Roblox (2024+)
local anim = Instance.new("StringValue")
anim.Name = "toolanim"
anim.Value = ""
anim.Parent = tool
```

Modern Roblox CoreScripts do not check for `toolanim`. This approach is from the 2010s era.

## Working Approach: `mouse.Button1Down`

### LocalScript (inside Tool)

```lua
local tool = script.Parent
local repStorage = game:GetService("ReplicatedStorage")
local GunConfig = require(repStorage:WaitForChild("GunConfig"))
local event = repStorage:WaitForChild(GunConfig.RemoteEventName)

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

### Server Script (inside Tool)

```lua
local repStorage = game:GetService("ReplicatedStorage")
local GunConfig = require(repStorage:WaitForChild("GunConfig"))
local event = repStorage:WaitForChild(GunConfig.RemoteEventName)

event.OnServerEvent:Connect(function(player, targetPosition)
    -- ... raycast, damage, etc ...
    event:FireClient(player, hitPosition, direction)
end)
```

## Why This Works

| Event | Triggers Animate script? | Use |
|---|---|---|
| `Tool.Activated` | ✅ Yes — plays punch animation | ❌ Avoid for ranged weapons |
| `mouse.Button1Down` | ❌ No — Animate script ignores mouse events | ✅ Use for ranged weapons |

The default Animate script specifically listens for `Tool.Activated`. By using `mouse.Button1Down` to trigger the server event, the Animate script never fires and the character stands completely still while shooting.

## Cleanup

Always disconnect the `Button1Down` connection on `Tool.Unequipped` to prevent orphaned listeners from stacking across equip/unequip cycles.
