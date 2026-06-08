---
name: roblox-camera-systems
description: "Camara en Roblox: manipulacion, cutscenes, tweening, FOV, zoom, spectate, modos de camara. Usa cuando necesites intro cutscene, camara cinematica, spectate mode, shake, zoom dinamico, o cualquier control de camara mas alla del default. Resuelve 'la camara se ve mal' o 'necesito una cinematica'."
version: "1.0"
---

# Roblox Camera Systems — Manipulacion, Cutscenes y Efectos

Control de camara mas alla del comportamiento default: cutscenes, transiciones, efectos visuales, y patrones de camara comunes.

Fuentes:
- https://create.roblox.com/docs/reference/engine/classes/Camera.md
- https://create.roblox.com/docs/reference/engine/classes/Workspace (CurrentCamera)
- https://devforum.roblox.com/t/how-do-you-make-a-cutscene-w-tweening/224739

---

## 1. CORE: API de Camera

### Propiedades principales

```lua
local camera = workspace.CurrentCamera

-- Posicion y orientacion
camera.CFrame                    -- CFrame actual (posicion + rotacion)
camera.Focus                     -- Punto de atencion (afecta LOD, iluminacion)

-- Modo de camara
camera.CameraType = Enum.CameraType.Custom      -- default (sigue personaje)
camera.CameraType = Enum.CameraType.Scriptable   -- control manual total
camera.CameraType = Enum.CameraType.Fixed        -- fija en una posicion
camera.CameraType = Enum.CameraType.Watch        -- mira al CameraSubject

-- Seguimiento
camera.CameraSubject = humanoid   -- que objeto sigue la camara
camera.CameraSubject = basePart   -- seguir un Part en vez de Humanoid

-- FOV
camera.FieldOfView = 70           -- default 70, rango 1-120
camera.DiagonalFieldOfView        -- FOV diagonal
```

### Metodos utiles

```lua
-- Conversion mundo ↔ pantalla
local screenPos, onScreen = camera:WorldToScreenPoint(worldPos)
local screenPos, onScreen = camera:WorldToViewportPoint(worldPos)
local ray = camera:ScreenPointToRay(x, y, depth)
local ray = camera:ViewportPointToRay(x, y, depth)

-- Raycast de oclusion
local blockingParts = camera:GetPartsObscuringTarget(castPoints, ignoreList)

-- CFrame real (incluye VR head tracking)
local realCFrame = camera:GetRenderCFrame()

-- Zoom para encajar un modelo
camera:ZoomToExtents(modelCFrame, modelSize)

-- Roll (obsoleto pero disponible)
camera:SetRoll(math.rad(20))     -- inclinacion en radianes
local roll = camera:GetRoll()    -- en radianes
```

### Propiedades deprecated (NO usar)

| Deprecated | Reemplazo |
|---|---|
| `CoordinateFrame` | `CFrame` |
| `focus` | `Focus` |
| `:Interpolate()` | `TweenService:Create()` |
| `:PanUnits()` | Manipular CFrame directamente |
| `:TiltUnits()` | Manipular CFrame directamente |
| `:GetPanSpeed()` | Broken, no usar |
| `:GetTiltSpeed()` | Broken, no usar |

---

## 2. CUTSCENE BASICA CON TWEEN

### Setup: waypoints en Workspace

```
Workspace/
  CameraPoints/        -- Folder con Parts como waypoints
    Point1             -- Part (Position = start)
    Point2             -- Part (Position = interes)
    Point3             -- Part (Position = end)
```

### Cutscene secuencial (LocalScript)

```lua
local TweenService = game:GetService("TweenService")
local Players = game:GetService("Players")
local camera = workspace.CurrentCamera

local cameraPoints = workspace:WaitForChild("CameraPoints")
local player = Players.LocalPlayer

local function playCutscene()
    -- Tomar control de la camara
    camera.CameraType = Enum.CameraType.Scriptable

    local waypoints = {
        {part = cameraPoints.Point1, duration = 3, style = Enum.EasingStyle.Quad},
        {part = cameraPoints.Point2, duration = 5, style = Enum.EasingStyle.Sine},
        {part = cameraPoints.Point3, duration = 2, style = Enum.EasingStyle.Quad},
    }

    -- Posicionar camara en primer punto
    camera.CFrame = CFrame.lookAt(
        waypoints[1].part.Position,
        waypoints[2].part.Position
    )

    for i, wp in ipairs(waypoints) do
        local nextPoint = waypoints[i + 1]
        if not nextPoint then break end

        local targetCFrame = CFrame.lookAt(wp.part.Position, nextPoint.part.Position)

        local tween = TweenService:Create(camera,
            TweenInfo.new(wp.duration, wp.style, Enum.EasingDirection.Out),
            {CFrame = targetCFrame}
        )
        tween:Play()
        tween.Completed:Wait()
    end

    -- Restaurar camara al personaje
    camera.CameraType = Enum.CameraType.Custom
    local character = player.Character or player.CharacterAdded:Wait()
    local humanoid = character:FindFirstChildWhichIsA("Humanoid")
    if humanoid then
        camera.CameraSubject = humanoid
    end
end

playCutscene()
```

### Cutscene con Focus (mejor calidad visual)

```lua
-- Tween tanto CFrame como Focus para mejor LOD e iluminacion
local tween = TweenService:Create(camera,
    TweenInfo.new(4, Enum.EasingStyle.Cubic, Enum.EasingDirection.Out),
    {
        CFrame = CFrame.lookAt(cameraPos, lookAtPos),
        Focus = CFrame.new(lookAtPos)  -- Focus siempre apunta al punto de interes
    }
)
tween:Play()
```

---

## 3. EFECTOS DE CAMARA

### Camera shake (explosion, impacto)

```lua
-- LocalScript
local RunService = game:GetService("RunService")
local camera = workspace.CurrentCamera
local TweenService = game:GetService("TweenService")

local shakeIntensity = 0
local shakeDecay = 8  -- que tan rapido se reduce

local function startShake(intensity)
    shakeIntensity = math.max(shakeIntensity, intensity)
end

local shakeConnection = nil
shakeConnection = RunService.RenderStepped:Connect(function(dt)
    if shakeIntensity > 0.01 then
        local offsetX = (math.random() - 0.5) * 2 * shakeIntensity
        local offsetY = (math.random() - 0.5) * 2 * shakeIntensity
        camera.CFrame = camera.CFrame * CFrame.new(offsetX, offsetY, 0)
        shakeIntensity = shakeIntensity * math.exp(-shakeDecay * dt)
    end
end)

-- Uso: startShake(0.5) para shake suave, startShake(2) para fuerte
```

### FOV zoom (sniper scope, sprint)

```lua
-- Zoom in (sniper scope)
local function zoomIn()
    camera.FieldOfView = 30  -- default 70
end

-- Zoom out (sprint effect)
local function sprintFOV()
    local tween = TweenService:Create(camera,
        TweenInfo.new(0.3, Enum.EasingStyle.Quad),
        {FieldOfView = 85}
    )
    tween:Play()
end

-- Reset
local function resetFOV()
    local tween = TweenService:Create(camera,
        TweenInfo.new(0.3, Enum.EasingStyle.Quad),
        {FieldOfView = 70}
    )
    tween:Play()
end
```

### Camara orbitando un punto

```lua
-- LocalScript con RunService
local RunService = game:GetService("RunService")
local camera = workspace.CurrentCamera
camera.CameraType = Enum.CameraType.Scriptable

local orbitCenter = Vector3.new(0, 5, 0)
local orbitRadius = 30
local orbitSpeed = 0.3  -- radianes por segundo
local orbitHeight = 15
local angle = 0

local connection
connection = RunService.RenderStepped:Connect(function(dt)
    angle = angle + orbitSpeed * dt

    local x = math.cos(angle) * orbitRadius
    local z = math.sin(angle) * orbitRadius

    local camPos = orbitCenter + Vector3.new(x, orbitHeight, z)
    camera.CFrame = CFrame.lookAt(camPos, orbitCenter)
    camera.Focus = CFrame.new(orbitCenter)
end)

-- Para detener: connection:Disconnect()
```

---

## 4. SPECTATE MODE

```lua
-- LocalScript en StarterPlayerScripts
local Players = game:GetService("Players")
local camera = workspace.CurrentCamera
local TweenService = game:GetService("TweenService")

local spectating = nil

local function spectatePlayer(targetPlayer)
    local character = targetPlayer.Character
    if not character then return end

    local humanoid = character:FindFirstChildWhichIsA("Humanoid")
    if not humanoid then return end

    camera.CameraSubject = humanoid
    spectating = targetPlayer
end

local function stopSpectate()
    local player = Players.LocalPlayer
    local character = player.Character
    if character then
        local humanoid = character:FindFirstChildWhichIsA("Humanoid")
        if humanoid then
            camera.CameraSubject = humanoid
        end
    end
    spectating = nil
end

-- Ciclar entre jugadores (ejemplo con tecla)
local UserInputService = game:GetService("UserInputService")
UserInputService.InputBegan:Connect(function(input, processed)
    if processed then return end
    if input.KeyCode == Enum.KeyCode.Right then
        local allPlayers = Players:GetPlayers()
        local currentIndex = table.find(allPlayers, spectating) or 0
        local nextIndex = (currentIndex % #allPlayers) + 1
        spectatePlayer(allPlayers[nextIndex])
    elseif input.KeyCode == Enum.KeyCode.Left then
        stopSpectate()
    end
end)
```

---

## 5. PATRONES POR GENERO

### Top-down / Isometrico

```lua
camera.CameraType = Enum.CameraType.Scriptable
local player = Players.LocalPlayer

RunService.RenderStepped:Connect(function()
    local char = player.Character
    if char and char:FindFirstChild("HumanoidRootPart") then
        local pos = char.HumanoidRootPart.Position
        camera.CFrame = CFrame.lookAt(
            pos + Vector3.new(0, 40, 30),  -- arriba y atras
            pos                              -- mirando al personaje
        )
        camera.Focus = CFrame.new(pos)
    end
end)
```

### Side-scroller (2.5D)

```lua
camera.CameraType = Enum.CameraType.Scriptable
RunService.RenderStepped:Connect(function()
    local char = player.Character
    if char and char:FindFirstChild("HumanoidRootPart") then
        local pos = char.HumanoidRootPart.Position
        camera.CFrame = CFrame.lookAt(
            Vector3.new(pos.X, pos.Y + 5, pos.Z + 20),  -- fijo en Z
            pos
        )
    end
end)
```

---

## 6. ANTI-PATTERNS

| Anti-pattern | Problema | Fix |
|---|---|---|
| No restaurar CameraType despues de cutscene | Camara trabada en Scriptable | Siempre restaurar a Custom + CameraSubject |
| Usar `CoordinateFrame` | Deprecated | Usar `CFrame` |
| Usar `:Interpolate()` | Deprecated, menos control | TweenService:Create() |
| Modificar CFrame en Scriptable sin Focus | LOD e iluminacion incorrecta | Siempre setear Focus junto con CFrame |
| Camera shake sin decay | Shake infinito | math.exp(-decay * dt) para reducir |
| FOV > 100 o < 20 | Desorientante para el jugador | Rango seguro: 30-90 |
| Cutscene sin poder saltar | Jugador atrapado | Agregar skip con input o timer |
| Tween a CFrame sin lookAt | Camara mira al vacio | CFrame.lookAt(pos, lookAt) siempre |

---

## 7. CHECKLIST

```
[ ] CameraType = Scriptable ANTES de modificar CFrame
[ ] CameraType = Custom + CameraSubject restaurado DESPUES
[ ] Focus seteado junto con CFrame para LOD/iluminacion
[ ] TweenService para transiciones suaves (no :Interpolate)
[ ] Camera shake con decay (no infinito)
[ ] FOV en rango 30-90 (default 70)
[ ] Sin APIs deprecated (CoordinateFrame, Interpolate, PanUnits)
[ ] Cutscene con opcion de skip
[ ] Probar en playtest: transiciones fluidas, no hay frame drops
[ ] Verificar que camara funciona en mobile (touch controls)
```

---

## Fuentes

- https://create.roblox.com/docs/reference/engine/classes/Camera.md
- https://create.roblox.com/docs/reference/engine/classes/Workspace.md (CurrentCamera)
- https://devforum.roblox.com/t/how-do-you-make-a-cutscene-w-tweening/224739
- https://create.roblox.com/docs/en-us/workspace/camera
