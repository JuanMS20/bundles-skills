---
name: roblox-npc-ai
description: "NPC AI en Roblox: PathfindingService, FSM (Finite State Machine), deteccion de jugadores, patrullaje, persecucion, combate. Usa cuando necesites NPCs que se muevan, persigan, patrullen o reaccionen al jugador. Resuelve 'el NPC se queda trabado', 'el pathfinding no funciona', o 'el comportamiento es caotico'."
version: "1.0"
---

# Roblox NPC AI — Pathfinding y FSM

Sistemas para NPCs con comportamiento inteligente: navegacion con PathfindingService y logica de estados con FSM.

Fuentes:
- https://create.roblox.com/docs/reference/engine/classes/PathfindingService.md
- https://create.roblox.com/docs/reference/engine/classes/Path.md
- https://mattqdev.github.io/blog/how-to-build-finite-state-machine-in-luau-roblox-npc
- https://create.roblox.com/docs/en-us/characters/pathfinding

---

## 1. PATHFINDINGSERVICE — API oficial

### CreatePath: parametros del agente

```lua
local PFS = game:GetService("PathfindingService")

local path = PFS:CreatePath({
    AgentRadius = 2,      -- espacio horizontal minimo (default: 2)
    AgentHeight = 5,      -- espacio vertical minimo (default: 5)
    AgentCanJump = true,  -- puede saltar (default: true)
    AgentCanClimb = false, -- puede trepar TrussParts (default: false)
    WaypointSpacing = 4,  -- distancia entre waypoints (default: 4)
    Costs = {             -- costo por material/modificador
        Water = 20,       -- evitar agua
        Lava = math.huge  -- nunca pasar por lava
    }
})
```

### ComputeAsync + GetWaypoints

```lua
path:ComputeAsync(startPosition, endPosition)

if path.Status == Enum.PathStatus.Success then
    local waypoints = path:GetWaypoints()
    for i, waypoint in ipairs(waypoints) do
        print(waypoint.Position, waypoint.Action)
        -- Action: Enum.PathWaypointAction.Walk o .Jump
    end
else
    warn("No path found:", path.Status)
end
```

### Path.Blocked — manejo de caminos bloqueados

```lua
path.Blocked:Connect(function(blockedWaypointIndex)
    -- Recalcular el path si se bloquea adelante del NPC
    if blockedWaypointIndex >= currentWaypointIndex then
        recalculatePath()
    end
end)

path.Unblocked:Connect(function(unblockedWaypointIndex)
    -- Opcional: retomar path original
end)
```

### Deprecated APIs (NO usar)

- `ComputeRawPathAsync` → usar `FindPathAsync` o `CreatePath` + `ComputeAsync`
- `ComputeSmoothPathAsync` → usar `CreatePath` + `ComputeAsync`
- `EmptyCutoff` → legacy, no tiene efecto

---

## 2. FSM — Finite State Machine

El patron correcto para NPC behavior. Evita spaghetti if/else.

### Modulo StateMachine (ReplicatedStorage/Shared/StateMachine.lua)

```lua
--!strict
export type StateHandler = {
    onEnter: ((self: StateMachine, prevState: string?) -> ())?,
    onUpdate: ((self: StateMachine, dt: number) -> ())?,
    onExit: ((self: StateMachine, nextState: string?) -> ())?,
}

export type StateMachine = {
    _states: {[string]: StateHandler},
    _current: string?,
    _previous: string?,
    addState: (self: StateMachine, name: string, handler: StateHandler) -> (),
    transition: (self: StateMachine, newState: string) -> (),
    update: (self: StateMachine, dt: number) -> (),
    getState: (self: StateMachine) -> string?,
    getPrevious: (self: StateMachine) -> string?,
}

local StateMachine = {}
StateMachine.__index = StateMachine

function StateMachine.new(): StateMachine
    return setmetatable({
        _states = {},
        _current = nil,
        _previous = nil,
    }, StateMachine) :: StateMachine
end

function StateMachine:addState(name: string, handler: StateHandler)
    self._states[name] = handler
end

function StateMachine:transition(newState: string)
    assert(self._states[newState], `Unknown state: {newState}`)
    if self._current == newState then return end

    local current = self._states[self._current or ""]
    if current and current.onExit then current.onExit(self, newState) end

    self._previous = self._current
    self._current = newState

    local next = self._states[newState]
    if next and next.onEnter then next.onEnter(self, self._previous) end
end

function StateMachine:update(dt: number)
    local handler = self._states[self._current or ""]
    if handler and handler.onUpdate then handler.onUpdate(self, dt) end
end

function StateMachine:getState(): string?
    return self._current
end

function StateMachine:getPrevious(): string?
    return self._previous
end

return StateMachine
```

### Flujo de estados tipico

```
IDLE ──(ve jugador)──> CHASE ──(en rango)──> ATTACK
  ^                        |  |                   |
  |    (pierde vista)      |  (vida < 30%)       |
  |                        v  v                   |
  └────────────────── SEARCH  RETREAT <───────────┘

PATROL ──(ve jugador)──> CHASE (misma rama)
```

---

## 3. NPC COMPLETO: Pathfinding + FSM

```lua
-- ServerScriptService/NPCController.lua (simplificado)
local PFS = game:GetService("PathfindingService")
local StateMachine = require(game.ReplicatedStorage.Shared.StateMachine)

local NPC = script.Parent  -- Model del NPC
local HUMANOID = NPC:WaitForChild("Humanoid")
local ROOT = NPC:WaitForChild("HumanoidRootPart")

-- Constantes
local DETECT_RANGE = 60
local ATTACK_RANGE = 15
local RETREAT_HP = 0.3
local PATROL_POINTS = {
    Vector3.new(0, 1, 0),
    Vector3.new(50, 1, 0),
    Vector3.new(50, 1, 50),
    Vector3.new(0, 1, 50),
}
local patrolIndex = 1

-- Contexto compartido entre estados
local ctx = {
    target = nil,
    lastKnownPos = nil,
    fsm = nil,
}

-- Helper: jugador mas cercano
local function getNearestPlayer()
    local nearest, minDist = nil, DETECT_RANGE
    for _, player in ipairs(game.Players:GetPlayers()) do
        local char = player.Character
        if char then
            local hrp = char:FindFirstChild("HumanoidRootPart")
            if hrp then
                local dist = (hrp.Position - ROOT.Position).Magnitude
                if dist < minDist then
                    nearest = player
                    minDist = dist
                end
            end
        end
    end
    return nearest, minDist
end

-- Helper: caminar a posicion via pathfinding
local function walkTo(pos)
    local path = PFS:CreatePath({AgentRadius = 2, AgentHeight = 5})
    path:ComputeAsync(ROOT.Position, pos)
    if path.Status ~= Enum.PathStatus.Success then return false end

    local waypoints = path:GetWaypoints()
    for _, wp in ipairs(waypoints) do
        if wp.Action == Enum.PathWaypointAction.Jump then
            HUMANOID.Jump = true
        end
        HUMANOID:MoveTo(wp.Position)
        HUMANOID.MoveToFinished:Wait()
    end
    return true
end

-- Crear FSM
local fsm = StateMachine.new()

-- IDLE
fsm:addState("Idle", {
    onEnter = function(self)
        HUMANOID.WalkSpeed = 8
    end,
    onUpdate = function(self, dt)
        local player, dist = getNearestPlayer()
        if player then
            ctx.target = player
            self:transition("Chase")
        end
    end,
})

-- PATROL
fsm:addState("Patrol", {
    onEnter = function(self)
        HUMANOID.WalkSpeed = 8
    end,
    onUpdate = function(self, dt)
        -- Detectar jugador
        local player = getNearestPlayer()
        if player then
            ctx.target = player
            self:transition("Chase")
            return
        end

        -- Mover al siguiente punto de patrulla
        local target = PATROL_POINTS[patrolIndex]
        local dist = (target - ROOT.Position).Magnitude
        if dist < 4 then
            patrolIndex = patrolIndex % #PATROL_POINTS + 1
        end
        HUMANOID:MoveTo(PATROL_POINTS[patrolIndex])
    end,
})

-- CHASE
fsm:addState("Chase", {
    onEnter = function(self)
        HUMANOID.WalkSpeed = 16
    end,
    onUpdate = function(self, dt)
        local char = ctx.target and ctx.target.Character
        if not char then self:transition("Search"); return end

        local hrp = char:FindFirstChild("HumanoidRootPart")
        if not hrp then self:transition("Search"); return end

        local dist = (hrp.Position - ROOT.Position).Magnitude

        -- Perdio vista
        if dist > DETECT_RANGE * 1.5 then
            ctx.lastKnownPos = hrp.Position
            self:transition("Search")
            return
        end

        -- En rango de ataque
        if dist <= ATTACK_RANGE then
            self:transition("Attack")
            return
        end

        -- Vida baja
        if HUMANOID.Health / HUMANOID.MaxHealth < RETREAT_HP then
            self:transition("Retreat")
            return
        end

        -- Perseguir
        ctx.lastKnownPos = hrp.Position
        walkTo(hrp.Position)
    end,
    onExit = function(self)
        HUMANOID.WalkSpeed = 8
    end,
})

-- SEARCH
fsm:addState("Search", {
    onEnter = function(self)
        HUMANOID.WalkSpeed = 10
    end,
    onUpdate = function(self, dt)
        -- Volvio a ver al jugador
        local player = getNearestPlayer()
        if player then
            ctx.target = player
            self:transition("Chase")
            return
        end

        -- Ir a ultima posicion conocida
        if ctx.lastKnownPos then
            walkTo(ctx.lastKnownPos)
            ctx.lastKnownPos = nil
            task.wait(3)  -- esperar en el lugar
        end

        self:transition("Patrol")
    end,
})

-- ATTACK
fsm:addState("Attack", {
    onEnter = function(self)
        HUMANOID.WalkSpeed = 4
    end,
    onUpdate = function(self, dt)
        local char = ctx.target and ctx.target.Character
        if not char then self:transition("Search"); return end

        local hrp = char:FindFirstChild("HumanoidRootPart")
        if not hrp then self:transition("Search"); return end

        local dist = (hrp.Position - ROOT.Position).Magnitude

        if dist > ATTACK_RANGE * 1.3 then
            self:transition("Chase")
            return
        end

        -- Logica de ataque aqui (damage, animacion, cooldown)
        -- Ejemplo: HACER DAMAGE cada 1.2s
    end,
})

-- RETREAT
fsm:addState("Retreat", {
    onEnter = function(self)
        HUMANOID.WalkSpeed = 20
    end,
    onUpdate = function(self, dt)
        -- Alejarse del jugador
        local char = ctx.target and ctx.target.Character
        if char and char:FindFirstChild("HumanoidRootPart") then
            local dir = (ROOT.Position - char.HumanoidRootPart.Position).Unit
            local fleeTo = ROOT.Position + dir * 30
            HUMANOID:MoveTo(fleeTo)
        end

        -- Si recupero vida o perdio al jugador
        if HUMANOID.Health / HUMANOID.MaxHealth > 0.5 then
            self:transition("Idle")
        end
    end,
})

-- Iniciar FSM
fsm:transition("Patrol")

-- Loop principal
game:GetService("RunService").Heartbeat:Connect(function(dt)
    fsm:update(dt)
end)
```

---

## 4. PATHFINDINGMODIFIER — zonas especiales

```lua
-- Marcar zonas como "costosas" o "no pasables"
local modifier = Instance.new("PathfindingModifier")
modifier.ModifierId = "Lava"
modifier.Parent = lavaPart  -- la parte que contiene lava

-- En CreatePath:
local path = PFS:CreatePath({
    Costs = {
        Lava = math.huge,  -- nunca pasar
        Water = 20,        -- evitar pero permite
    }
})
```

### Casos comunes de Costs
```lua
Costs = {
    Water = 20,          -- evitar agua
    Mud = 10,            -- preferir no pasar
    Lava = math.huge,    -- NUNCA pasar
    Road = 0.5,          -- preferir caminos
    Shortcut = 0,        -- siempre usar si existe
}
```

---

## 5. ANTI-PATTERNS

| Anti-pattern | Problema | Fix |
|---|---|---|
| if/else anidados para estados | Spaghetti, imposible debuggear | FSM con transiciones explicitas |
| MoveTo sin pathfinding | NPC choca con paredes | PathfindingService:CreatePath + ComputeAsync |
| ComputeAsync en cada frame | Lag severo, COMPUTE ES YIELD | Llamar cada 0.5-1s, no cada frame |
| No manejar Path.Blocked | NPC se queda trabado | Reconectar evento Blocked y recalcular |
| Ignorar PathStatus.NoPath | NPC hace nada silenciosamente | Loggear/warn si Status ~= Success |
| Humanoid.WalkSpeed sin reset | Velocidad incorrecta entre estados | onExit resetea, onEnter configura |
| Estado " Chase" sin timeout | Persigue infinitamente | Distancia max + transicion a Search |
| walkTo sincronico en onUpdate | Bloquea el update loop | Usar coroutine o moveWaypoints async |

---

## 6. CHECKLIST

```
[ ] FSM con transiciones explicitas (no if/else)
[ ] PathfindingService:CreatePath con parametros correctos del agente
[ ] Path.Blocked conectado para recalcular camino
[ ] WalkSpeed configurado por estado (onEnter) y reseteado (onExit)
[ ] Deteccion de jugador con rango y verificacion de Character valido
[ ] Timeout/distancia max en Chase → transicion a Search
[ ] Computar path cada 0.5s+ (no cada frame)
[ ] Logica de ataque con cooldown (no damage cada frame)
[ ] PathfindingModifier en zonas especiales (agua, lava)
[ ] Probar NPC en playtest: patrulla, detecta, persigue, ataca, retreat
```

---

## Fuentes

- https://create.roblox.com/docs/reference/engine/classes/PathfindingService.md
- https://create.roblox.com/docs/reference/engine/classes/Path.md
- https://mattqdev.github.io/blog/how-to-build-finite-state-machine-in-luau-roblox-npc
- https://create.roblox.com/docs/en-us/characters/pathfinding
