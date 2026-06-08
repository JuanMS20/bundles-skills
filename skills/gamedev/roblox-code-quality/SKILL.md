---
name: roblox-code-quality
description: "Anti-patterns, seguridad, performance y calidad de codigo Luau para Roblox. Memory leaks, deprecated APIs, RemoteEvent security, Instance.new, task library."
version: "1.0"
---

# Roblox Code Quality - Anti-Patterns y Buenas Practicas

Reglas y anti-patterns criticos para escribir codigo Luau profesional en Roblox.

Fuentes:
- https://github.com/Kampfkarren/kampfkarren-luau-guidelines (Kampfkarren, Roblox engineer)
- https://devforum.roblox.com/t/psa-dont-use-instancenew-with-parent-argument/30296 (zeuxcg, Roblox engineer)
- https://devforum.roblox.com/t/tips-on-avoiding-memory-leaks/3913103
- https://gmmarket.me/community/post/roblox-remoteevent-security-how-exploits-work-and-how-to-stop-them-never-trust-t
- https://luau.org/performance

---

## 1. REGLAS CRITICAS (Violaciones = bugs o exploits)

### R1. Instance.new SIN segundo argumento

**40x mas lento** si pasas parent como segundo argumento (verificado por zeuxcg, Roblox engineer).

```lua
-- MAL (40x mas lento - actualiza fisica por cada propiedad)
local part = Instance.new("Part", workspace)
part.Size = Vector3.new(10, 10, 1)
part.CFrame = CFrame.new(0, 5, 0)

-- BIEN (propiedades primero, parent al final)
local part = Instance.new("Part")
part.Size = Vector3.new(10, 10, 1)
part.CFrame = CFrame.new(0, 5, 0)
part.Anchored = true
part.Parent = workspace
```

**Razon:** Cuando Parent != nil, cada cambio de propiedad dispara actualizaciones de fisica, rendering y replicacion. Asignar Parent al final = 1 sola actualizacion.

**Orden correcto:**
1. `Instance.new()` sin parent
2. Asignar todas las propiedades
3. Asignar Parent
4. Conectar signals (events)

---

### R2. NUNCA confiar en el cliente (RemoteEvent Security)

Cada RemoteEvent es superficie de ataque. Exploiters usan RemoteSpy para ver y modificar todo.

```lua
-- MAL - el cliente envia el precio
BuyItem.OnServerEvent:Connect(function(player, itemName, price)
    player.Coins.Value -= price  -- EXPLOIT: puede enviar price=0
end)

-- BIEN - servidor deriva el precio
local PRICES = { Sword = 100, Shield = 150, Potion = 50 }

BuyItem.OnServerEvent:Connect(function(player, itemName)
    -- 1. Type check
    if type(itemName) ~= "string" then return end
    -- 2. Whitelist
    local price = PRICES[itemName]
    if not price then return end
    -- 3. Validacion de recursos
    local coins = player.leaderstats and player.leaderstats:FindFirstChild("Coins")
    if not coins or coins.Value < price then return end
    -- 4. Ejecutar
    coins.Value -= price
    giveItem(player, itemName)
end)
```

**Checklist de seguridad:**
- [ ] Validar TIPO de cada argumento (type() check)
- [ ] Validar contra WHITELIST (no blacklist)
- [ ] Servidor deriva valores sensibles (precios, dano, recompensas)
- [ ] Rate limiting por jugador (cooldown entre fires)
- [ ] Ownership check si el argumento es una Instance
- [ ] Nunca pasar Functions o Tables por RemoteEvent
- [ ] Limpiar datos de rate limiting en PlayerRemoving

**Rate limiting basico:**
```lua
local COOLDOWN = 0.5
local lastFired = {}

Event.OnServerEvent:Connect(function(player, ...)
    local now = os.clock()
    if lastFired[player] and (now - lastFired[player]) < COOLDOWN then
        return
    end
    lastFired[player] = now
    -- logica
end)

game.Players.PlayerRemoving:Connect(function(p)
    lastFired[p] = nil  -- cleanup memory
end)
```

---

### R3. Task Library (no usar globals deprecated)

```lua
-- MAL (deprecated, menos preciso, mas overhead)
wait(1)
spawn(function() ... end)
delay(2, function() ... end)

-- BIEN (task library - moderno, preciso, mejor rendimiento)
task.wait(1)
task.spawn(function() ... end)
task.delay(2, function() ... end)
task.defer(function() ... end)  -- ejecuta en siguiente resumption point
```

| Deprecated | Reemplazo | Nota |
|-----------|-----------|------|
| `wait(n)` | `task.wait(n)` | Mas preciso, no throttled |
| `spawn(fn)` | `task.spawn(fn)` | Ejecuta inmediatamente |
| `delay(n, fn)` | `task.delay(n, fn)` | Mas confiable |
| N/A | `task.defer(fn)` | Nuevo - deferred execution |

---

### R4. Memory Leaks - Disconnect y Cleanup

**Regla:** Todo connection debe guardarse y desconectarse cuando ya no se necesita.

```lua
-- MAL - connection leak
local function onPlayerAdded(player)
    player.CharacterAdded:Connect(function(character)
        -- si el player se va, esta conexion sigue vivo
        character.Humanoid.Died:Connect(function()
            print(player.Name .. " died")
        end)
    end)
end

-- BIEN - cleanup en PlayerRemoving
local connections = {}

game.Players.PlayerAdded:Connect(function(player)
    connections[player] = {}
    
    local conn = player.CharacterAdded:Connect(function(character)
        -- logica
    end)
    table.insert(connections[player], conn)
end)

game.Players.PlayerRemoving:Connect(function(player)
    if connections[player] then
        for _, conn in ipairs(connections[player]) do
            conn:Disconnect()
        end
        connections[player] = nil
    end
end)
```

**Patron alternativo con Destroy:**
```lua
-- Si creas objetos que listen a events, destruirlos limpia todo
local folder = Instance.new("Folder")
folder.Name = "PlayerData_" .. player.UserId
folder.Parent = game.ServerStorage

-- Al cleanup:
folder:Destroy()  -- destruye folder + todos sus descendants y connections
```

**Fuentes de memory leak comunes:**
- Event connections no desconectados (.Changed, .Touched, RenderStepped)
- Tables con referencias a players que ya se fueron
- Timers/loops infinitos sin mecanismo de stop
- Tween completed connections en loops
-- Objetos destruidos pero con closures que los referencian

---

### R5. WaitForChild - Usar con timeout

```lua
-- MAL - puede colgar el script para siempre
local remote = replicatedStorage:WaitForChild("MyRemote")

-- BIEN - timeout explicito
local remote = replicatedStorage:FindFirstChild("MyRemote")
if not remote then
    warn("MyRemote not found")
    return
end

-- O con timeout (5 segundos)
local remote = replicatedStorage:WaitForChild("MyRemote", 5)
if not remote then
    warn("MyRemote timeout")
    return
end
```

**Reglas de WaitForChild:**
- En Server Scripts: generalmente seguro (servidor carga todo primero)
- En LocalScripts: PELIGROSO - StreamingEnabled puede causar infinite yield
- Preferir FindFirstChild + verificacion en LocalScripts
- Si usas WaitForChild en LocalScript, SIEMPRE con timeout
- No anidar WaitForChild dentro de event handlers (precarga antes)

---

## 2. PERFORMANCE

### RunService - elegir el evento correcto

| Event | Cuando se ejecuta | Uso correcto |
|-------|-------------------|--------------|
| `RenderStepped` | Antes del render frame | Solo UI visual (camara, GUI) |
| `Stepped` | Antes de simulacion fisica | Input processing, UI |
| `Heartbeat` | Despues de simulacion fisica | Raycasts, calculos de posicion, combat |

```lua
-- MAL - RenderStepped para logica de juego
RunService.RenderStepped:Connect(function(dt)
    checkEnemyPositions()  -- NO, esto es logica de juego
end)

-- BIEN - Heartbeat para logica de juego
RunService.Heartbeat:Connect(function(dt)
    checkEnemyPositions()
end)
```

**Nunca hacer operaciones pesadas en RenderStepped.** Solo UI/camera.

### Operaciones costosas a evitar en loops

```lua
-- EVITAR en loops frecuentes:
Instance.new()           -- crear instancias por frame
:GetChildren()           -- crea nueva table cada vez
:GetDescendants()        -- peor aun
:FindFirstChild()        -- rapido pero no en loops de 1000+
table.insert()           -- usa # para arrays simples
string.format()          -- usa concatenacion si es simple
```

### Pre-calcular fuera de loops

```lua
-- MAL
for i = 1, 1000 do
    local pos = Vector3.new(i * 4, 0, 0)
    local cf = CFrame.new(pos)
    -- ...
end

-- BIEN - precalcular constantes
local STEP = 4
for i = 1, 1000 do
    local cf = CFrame.new(i * STEP, 0, 0)
    -- ...
end
```

### Anchored = true en todo lo estatico

```lua
-- Cualquier Part que no deba moverse:
part.Anchored = true
part.CanCollide = true  -- solo si necesita collision
part.CanQuery = false   -- si no necesita raycasts
part.CanTouch = false   -- si no necesita Touched events
```

---

## 3. PATRONES DE CODIGO

### ModuleScript pattern (Kampfkarren)

```lua
-- BIEN - nombre claro, retorna al final
local PetManager = {}

function PetManager.getPet(id)
    -- ...
end

return PetManager

-- MAL - return inline
return {
    getPet = function(id) ... end
}
```

### Type annotations (Luau strict)

```lua
--!strict

type Pet = {
    id: string,
    name: string,
    tier: string,
}

local function getPet(id: string): Pet?
    -- ...
end

-- Preferir string enums
type Tier = "Common" | "Rare" | "Epic" | "Mythic"
```

### Early return sobre nesting

```lua
-- MAL
function processPurchase(player, item)
    if item then
        if canAfford(player, item) then
            if hasInventorySpace(player) then
                -- logica 4 niveles de indentacion
            end
        end
    end
end

-- BIEN
function processPurchase(player, item)
    if not item then return end
    if not canAfford(player, item) then return end
    if not hasInventorySpace(player) then return end
    -- logica a nivel base
end
```

### Preferir FindFirstChild sobre WaitForChild para estado

```lua
-- Para cosas que PUEDEN no existir:
local tool = player.Backpack:FindFirstChild("Sword")

-- Para cosas que DEBEN existir (server, al inicio):
local replicatedStorage = game:GetService("ReplicatedStorage")
local remotes = replicatedStorage:WaitForChild("Remotes", 10)
```

---

## 4. ANTI-PATTERNS COMUNES

### A1. Debounce con wait()

```lua
-- MAL
local debouncing = false
button.MouseButton1Click:Connect(function()
    if debouncing then return end
    debouncing = true
    wait(1)
    debouncing = false
end)

-- BIEN
local lastClick = 0
button.MouseButton1Click:Connect(function()
    local now = os.clock()
    if now - lastClick < 1 then return end
    lastClick = now
    -- logica
end)
```

### A2. Touched sin debounce

```lua
-- MAL - se dispara multiples veces por frame
part.Touched:Connect(function(hit)
    givePoints(player)
end)

-- BIEN
local touched = false
part.Touched:Connect(function(hit)
    if touched then return end
    touched = true
    givePoints(player)
    task.delay(0.5, function()
        touched = false
    end)
end)
```

### A3. String concatenation en loops

```lua
-- MAL - crea strings intermedios
local result = ""
for i = 1, 1000 do
    result = result .. tostring(i) .. ","
end

-- BIEN - table.concat
local parts = {}
for i = 1, 1000 do
    parts[i] = tostring(i)
end
local result = table.concat(parts, ",")
```

### A4. Parent = nil en vez de Destroy

```lua
-- MAL - no limpia connections internos
part.Parent = nil

-- BIEN - limpia todo
part:Destroy()
```

### A5. Global variables

```lua
-- MAL
myVariable = 42  -- global, accesible desde cualquier script

-- BIEN
local myVariable = 42  -- local al scope
```

### A6. Crear instancias dentro de loops frecuentes

```lua
-- MAL - crea Instancias cada frame
RunService.Heartbeat:Connect(function()
    local effect = Instance.new("Part")
    effect.Parent = workspace
    -- despues de un rato: cientos de parts
end)

-- BIEN - object pool o reutilizar
local effectPool = {}
local activeEffects = {}

local function getEffect()
    if #effectPool > 0 then
        return table.remove(effectPool)
    end
    return Instance.new("Part")
end

local function returnEffect(effect)
    effect.Parent = nil
    table.insert(effectPool, effect)
end
```

---

## 5. CHECKLIST DE CALIDAD

Antes de considerar un script "listo":

```
[ ] Instance.new sin segundo argumento (Parent al final)
[ ] task.wait/task.spawn en vez de wait/spawn
[ ] RemoteEvents validan tipo, whitelist, y ownership
[ ] Rate limiting en todos los Remotes del servidor
[ ] Connections almacenados y desconectados en cleanup
[ ] WaitForChild con timeout en LocalScripts
[ ] Anchored=true en Parts estaticos
[ ] Sin globals (todo local)
[ ] Early returns en vez de nesting profundo
[ ] Sin TextScaled en botones
[ ] Debounce en Touched y MouseButton1Click
[ ] Destroy() en vez de Parent = nil
[ ] PlayerRemoving limpia datos y connections del jugador
[ ] Comentarios explican POR QUE, no QUE
[ ] ModuleScripts retornan variable nombrada al final
```

---

## 6. HERRAMIENTAS DE CALIDAD

### Linting con selene
- https://github.com/Kampfkarren/selene
- Detecta: globals undefined, deprecated functions, unused variables
- Config: selene.toml con std = "roblox"

### Formato con StyLua
- https://github.com/JohnnyMorganz/StyLua
- Formato consistente automatico
- Integrable con CI/CD

### Type checking con luau LSP
- Activar `--!strict` en todos los scripts nuevos
- Para codebases existentes: activar global, agregar `--!nonstrict` a viejos, migrar gradualmente

---

## 7. NUEVO EN 2026 — TYPE SOLVER Y DEPRECATIONS

### New Type Solver (General Release, Enero 2026)
- Default ahora para nocheck y non-strict mode
- Si usabas strict mode via Studio Beta: set `Workspace.UseNewLuauTypeSolver = Enabled`
- El viejo solver sigue disponible durante 2026, pero sera removido
- `--!strict` mas preciso, mejores type refinements

### APIs Deprecated en 2026
| API | Fecha | Migracion |
|-----|-------|-----------|
| Legacy Game Pass web endpoints | Abril 23, 2026 | Open Cloud APIs |
| Legacy Developer Product web APIs | Abril 23, 2026 | Open Cloud APIs |
| PlayerOwnsAsset | Breaking change pendiente | Economy API |
| Old Type Solver | Finales 2026 | New Type Solver |

### Vector library (Luau runtime)
- Luau ahora tiene `vector` library built-in para construir y operar con el tipo nativo vector
- Fast-call optimization, constant folding en compiler
- `vector.create(x, y, z)`, `vector.magnitude(v)`, etc.

Fuente: https://devforum.roblox.com/t/general-release-luau%E2%80%99s-new-type-solver/4084991

---

## Fuentes

- https://github.com/Kampfkarren/kampfkarren-luau-guidelines
- https://devforum.roblox.com/t/psa-dont-use-instancenew-with-parent-argument/30296
- https://devforum.roblox.com/t/tips-on-avoiding-memory-leaks/3913103
- https://devforum.roblox.com/t/partial-usage-of-non-task-library-functions-on-the-roblox-client/3450748
- https://gmmarket.me/community/post/roblox-remoteevent-security-how-exploits-work-and-how-to-stop-them-never-trust-t
- https://luau.org/performance
- https://devforum.roblox.com/t/playercharacteradded-humanoiddied-etc-improperly-cleaned-up/3363908
- https://devforum.roblox.com/t/general-release-luau%E2%80%99s-new-type-solver/4084991
- https://devforum.roblox.com/t/upcoming-breaking-change-to-playerownsasset-and-inventory-web-apis/4226591
