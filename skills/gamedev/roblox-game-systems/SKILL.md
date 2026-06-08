---
name: roblox-game-systems
description: "Patrones de arquitectura para sistemas de juego Roblox: DataStore (2026 limits), leaderstats, inventario, mascotas, economia, comunicacion cliente-servidor, UnreliableRemoteEvent."
version: "1.0"
---

# Roblox Game Systems - Patrones de Arquitectura

Sistemas de juego comunes para simuladores, RPGs y juegos de mascotas.

Fuentes:
- https://gmmarket.me/community/post/roblox-datastore-in-2026-the-new-per-experience-limit-explained-migration-plan
- https://gmmarket.me/community/post/roblox-client-server-replication-best-practices-remoteevent-vs-remotefunction-vs
- https://devforum.roblox.com/t/setasync-vs-updateasync-which-one-should-i-use/433021
- https://devforum.roblox.com/t/what-do-you-guys-think-the-best-way-of-making-a-pet-movement-system-is/359581
- https://create.roblox.com/docs/scripting/events/remote

---

## 1. DATA STORE (Persistencia)

### 1.1 Cambios 2026: Per-Experience Limits

**Desde abril 2025, los limites son por EXPERIENCIA (no por servidor).** Todos los servers comparten un mismo budget.

**Modelo antiguo (per-server):**
```
Budget = 60 + (players * 10) req/min por servidor
```

**Modelo nuevo (per-experience):**
- Budget compartido entre TODOS los servers activos
- Spike de CCU = budget se agota mas rapido
- Cap de almacenamiento total por experiencia
- Nuevas herramientas: Data Stores Manager, Storage Notifications, Batch Processor

**Limites per-key (sin cambios):**
| Dimension | Valor |
|-----------|-------|
| Max valor por key | 4 MB |
| Lectura per-key | 25 MB/min |
| Escritura per-key | 4 MB/min |
| Retencion versiones | 30 dias |

### 1.2 UpdateAsync vs SetAsync

**Regla: Usar UpdateAsync para todo save de datos.**

```lua
-- BIEN - UpdateAsync es atomico, considera el valor previo
dataStore:UpdateAsync("player_" .. userId, function(oldData)
    oldData = oldData or {}  -- primera vez = nil
    oldData.coins = playerData.coins
    oldData.pets = playerData.pets
    oldData.savedAt = os.time()
    return oldData
end)

-- MAL - SetAsync es ciego, puede sobreescribir datos de otro server
dataStore:SetAsync("player_" .. userId, playerData)
```

**SetAsync solo cuando:** Necesitas forzar un overwrite (reset de datos, migracion).

### 1.3 Patron DataStoreWrapper con Dirty Flag

```lua
-- DataStoreWrapper ModuleScript
local DataStoreService = game:GetService("DataStoreService")

local USE_DATASTORE = false  -- false para desarrollo local
local SAVE_INTERVAL = 60     -- segundos entre autosave

local DataStoreWrapper = {}
DataStoreWrapper.__index = DataStoreWrapper

function DataStoreWrapper.new(storeName)
    local self = setmetatable({}, DataStoreWrapper)
    self.store = USE_DATASTORE and DataStoreService:GetDataStore(storeName) or nil
    self.cache = {}      -- [userId] = data
    self.dirty = {}      -- [userId] = true/false
    self.connections = {} -- cleanup
    return self
end

function DataStoreWrapper:Load(userId)
    if self.cache[userId] then
        return self.cache[userId]
    end

    local data = nil
    if self.store then
        local ok, result = pcall(function()
            return self.store:GetAsync("player_" .. userId)
        end)
        if ok then
            data = result
        else
            warn("DataStore load failed for", userId, result)
        end
    end

    data = data or self:GetDefault()
    self.cache[userId] = data
    self.dirty[userId] = false
    return data
end

function DataStoreWrapper:MarkDirty(userId)
    self.dirty[userId] = true
end

function DataStoreWrapper:Save(userId)
    if not self.store then return true end
    if not self.dirty[userId] then return true end

    local data = self.cache[userId]
    if not data then return false end

    local ok, err = pcall(function()
        self.store:UpdateAsync("player_" .. userId, function(oldData)
            -- Merge: no perder datos de otra sesion
            return data
        end)
    end)

    if ok then
        self.dirty[userId] = false
        return true
    else
        warn("DataStore save failed:", userId, err)
        return false
    end
end

function DataStoreWrapper:GetDefault()
    return {
        coins = 0,
        gems = 0,
        pets = {},       -- {id = {uid = "abc", tier = "Common"}}
        equippedPets = {},
        totalHatches = 0,
    }
end

function DataStoreWrapper:StartAutoSave(players)
    task.spawn(function()
        while true do
            task.wait(SAVE_INTERVAL)
            for _, player in ipairs(players:GetPlayers()) do
                if self.dirty[player.UserId] then
                    self:Save(player.UserId)
                end
            end
        end
    end)
end

function DataStoreWrapper:Remove(userId)
    self.cache[userId] = nil
    self.dirty[userId] = nil
end

return DataStoreWrapper
```

### 1.4 Session Locking (basico)

Problema: Dos servers cargan los mismos datos, ambos modifican, el ultimo en guardar gana.

```lua
-- Solucion simple: guardar lastSessionId
-- Al cargar, verificar que no hay sesion activa
local SESSION_ID = game.JobId .. "_" .. tostring(os.time())

function DataStoreWrapper:LoadWithLock(userId)
    local data = self:Load(userId)
    
    if data._sessionLock and data._sessionLock ~= "" then
        -- Otra sesion tiene los datos
        -- Opcion 1: esperar y reintentar
        -- Opcion 2: forzar (steal session)
        warn("Session locked by:", data._sessionLock)
    end
    
    data._sessionLock = SESSION_ID
    self:MarkDirty(userId)
    return data
end

function DataStoreWrapper:SaveAndRelease(userId)
    local data = self.cache[userId]
    if data then
        data._sessionLock = ""
    end
    self:Save(userId)
end
```

**Nota:** Para produccion seria, usar ProfileService o ProfileStore que manejan todo esto automaticamente.

### 1.5 OnClose (save antes de apagar)

```lua
-- En ServerScriptService
game:BindToClose(function()
    for _, player in ipairs(game.Players:GetPlayers()) do
        dataStore:Save(player.UserId)
    end
    -- Dar tiempo a que terminen los saves
    task.wait(3)
end)
```

---

## 2. LEADERSTATS

```lua
-- ServerScriptService/LeaderstatsHandler
local Players = game:GetService("Players")

Players.PlayerAdded:Connect(function(player)
    local leaderstats = Instance.new("Folder")
    leaderstats.Name = "leaderstats"
    leaderstats.Parent = player

    local coins = Instance.new("IntValue")
    coins.Name = "Coins"
    coins.Value = 0
    coins.Parent = leaderstats

    local gems = Instance.new("IntValue")
    gems.Name = "Gems"     -- "Gems" no muestra coma en leaderboard
    gems.Value = 0
    gems.Parent = leaderstats
end)
```

**Tipos de Value para leaderstats:**
| Tipo | Display | Uso |
|------|---------|-----|
| IntValue | Numero entero | Coins, Level, Kills |
| NumberValue | Decimal | KDR, velocidad |
| StringValue | Texto | Rank, titulo |
| BoolValue | Check/empty | VIP status |

**Regla:** El folder DEBE llamarse "leaderstats" exactamente. Los valores dentro se muestran en el tab automaticamente.

### 2.2 Leaderstats para tiempos (timer/speedrun)

Para juegos con timer, el leaderboard debe ordenar por mejor tiempo. El truco:
almacenar tiempo como **IntValue en centésimas de segundo** (12050 = 02:00.50).

```lua
-- LeaderstatsHandler (Script)
local function onPlayerAdded(player)
    local leaderstats = Instance.new("Folder")
    leaderstats.Name = "leaderstats"
    leaderstats.Parent = player

    local bestTime = Instance.new("IntValue")
    bestTime.Name = "Best Time"
    bestTime.Value = 0  -- 0 = sin run completada
    bestTime.Parent = leaderstats
end

-- Al ganar (escuchar BindableEvent "VictoryTime"):
victoryTimeEvent.Event:Connect(function(player, elapsedSeconds)
    local centiseconds = math.floor(elapsedSeconds * 100)
    local bestTime = player.leaderstats:FindFirstChild("Best Time")
    if bestTime then
        if bestTime.Value == 0 or centiseconds < bestTime.Value then
            bestTime.Value = centiseconds
        end
    end
end)

-- Formato para display (en el client o donde sea):
local function formatTime(centiseconds)
    local mins = math.floor(centiseconds / 6000)
    local secs = math.floor((centiseconds % 6000) / 100)
    local cen = centiseconds % 100
    return string.format("%02d:%02d.%02d", mins, secs, cen)
end
```

**Por qué IntValue y no NumberValue:** IntValue permite sorting correcto en el
leaderboard nativo de Roblox (menor = mejor para tiempos). NumberValue tiene
precision issues con floats.

---

## 3. SISTEMA DE MASCOTAS (Pet System)

### 3.1 Data Model

```lua
-- Un jugador tiene:
{
    pets = {
        -- Cada pet es un entry con unique ID
        { uid = "pet_001", id = "cat", tier = "Common" },
        { uid = "pet_002", id = "dragon", tier = "Mythic" },
    },
    equippedPets = {
        -- Indices o UIDs de pets equipados
        "pet_001", "pet_002"
    },
    maxEquipped = 3,
}
```

### 3.2 Pet Config (ModuleScript)

```lua
local PetConfig = {
    -- [petId] = { name, tier, power, rarity }
    cat = { name = "Cat", tier = "Common", power = 1, rarity = 0.40 },
    dog = { name = "Dog", tier = "Common", power = 2, rarity = 0.30 },
    rabbit = { name = "Rabbit", tier = "Common", power = 3, rarity = 0.15 },
    fox = { name = "Fox", tier = "Rare", power = 5, rarity = 0.08 },
    wolf = { name = "Wolf", tier = "Rare", power = 8, rarity = 0.04 },
    bear = { name = "Bear", tier = "Epic", power = 15, rarity = 0.02 },
    dragon = { name = "Dragon", tier = "Epic", power = 25, rarity = 0.008 },
    phoenix = { name = "Phoenix", tier = "Mythic", power = 50, rarity = 0.0015 },
    unicorn = { name = "Unicorn", tier = "Mythic", power = 100, rarity = 0.0005 },
}

return PetConfig
```

### 3.3 Pet Following (Proxy Part Method - recomendado)

El metodo mas robusto: proxy part + AlignPosition/AlignOrientation.

```lua
-- Client-side: crear proxy parts para cada pet equipado
local function spawnPetProxy(player, petData, slotIndex)
    local character = player.Character
    if not character then return nil end
    local rootPart = character:FindFirstChild("HumanoidRootPart")
    if not rootPart then return nil end

    -- Proxy part (invisible, no collide)
    local proxy = Instance.new("Part")
    proxy.Name = "PetProxy_" .. petData.uid
    proxy.Size = Vector3.new(1, 1, 1)
    proxy.Transparency = 1
    proxy.CanCollide = false
    proxy.Anchored = false
    proxy.Parent = workspace.Pets

    -- Attachment en proxy para AlignPosition
    local att0 = Instance.new("Attachment")
    att0.Parent = proxy

    -- Attachment en HumanoidRootPart como target
    local targetAtt = Instance.new("Attachment")
    targetAtt.Name = "PetSlot_" .. slotIndex
    targetAtt.Parent = rootPart

    -- AlignPosition: mueve el proxy hacia el target
    local alignPos = Instance.new("AlignPosition")
    alignPos.Attachment0 = att0
    alignPos.Attachment1 = targetAtt
    alignPos.Mode = Enum.PositionAlignmentMode.TwoAttachment
    alignPos.AlignType = Enum.AlignType.PrimaryAxisParallel
    alignPos.Responsiveness = 10  -- mayor = mas rapido sigue
    alignPos.MaxVelocity = 30
    alignPos.MaxForce = 10000
    alignPos.Parent = proxy

    -- AlignOrientation: rota el proxy
    local alignOri = Instance.new("AlignOrientation")
    alignOri.Attachment0 = att0
    alignOri.Attachment1 = targetAtt
    alignOri.Mode = Enum.OrientationAlignmentMode.TwoAttachment
    alignOri.Responsiveness = 15
    alignOri.MaxTorque = 10000
    alignOri.Parent = proxy

    -- Visual: mesh/model del pet (weld al proxy)
    local petModel = createPetModel(petData)
    local weld = Instance.new("WeldConstraint")
    weld.Part0 = proxy
    weld.Part1 = petModel.PrimaryPart
    weld.Parent = proxy
    petModel.Parent = proxy

    -- Network ownership al jugador
    proxy:SetNetworkOwner(player)

    return proxy
end
```

**Offset por slot (para multiples mascotas):**
```lua
local SLOT_OFFSETS = {
    Vector3.new(3, 2, 0),    -- derecha
    Vector3.new(-3, 2, 0),   -- izquierda
    Vector3.new(0, 3, -3),   -- atras
    Vector3.new(3, 2, -2),   -- detras derecha
    Vector3.new(-3, 2, -2),  -- detras izquierda
}

-- Mover target attachment al offset correspondiente
targetAtt.Position = SLOT_OFFSETS[slotIndex] or Vector3.new(0, 3, -3)
```

**BodyMovers DEPRECATED.** No usar BodyPosition/BodyGyro. Usar AlignPosition/AlignOrientation.

### 3.4 Hatch System (servidor)

```lua
-- Servidor: toda la logica de RNG y validacion en servidor
local function handleHatch(player, eggId)
    -- 1. Validar egg existe
    local eggConfig = EggConfig[eggId]
    if not eggConfig then return end

    -- 2. Validar puede pagar
    local coins = player.leaderstats:FindFirstChild("Coins")
    if not coins or coins.Value < eggConfig.price then return end

    -- 3. Cobrar
    coins.Value -= eggConfig.price

    -- 4. RNG (servidor)
    local petId = selectPetByWeight(eggConfig.pets)
    local petConfig = PetConfig[petId]

    -- 5. Generar UID unico
    local uid = "pet_" .. HttpService:GenerateGUID(false)

    -- 6. Guardar en inventario
    local data = dataStore:Load(player.UserId)
    table.insert(data.pets, {
        uid = uid,
        id = petId,
        tier = petConfig.tier,
    })
    data.totalHatches += 1
    dataStore:MarkDirty(player.UserId)

    -- 7. Notificar cliente
    HatchResult:FireClient(player, uid, petId, petConfig.tier)
end
```

---

## 4. COMUNICACION CLIENTE-SERVIDOR

### 4.1 Tabla de decision

| Situacion | Usar |
|-----------|------|
| Avisar al server algo paso (fire & forget) | `RemoteEvent` |
| Pedir un valor al server y esperar respuesta | `RemoteFunction` (solo client→server) |
| Datos高频, tolerantes a perdida (posicion, aim) | `UnreliableRemoteEvent` |
| Broadcast a todos | `RemoteEvent:FireAllClients()` |
| **NUNCA** server pide respuesta al client | ~~`RemoteFunction:InvokeClient()`~~ |

### 4.2 UnreliableRemoteEvent (nuevo, Marzo 2025)

Para datos que se envian cada frame donde no importa si se pierde un paquete.

```lua
-- Client: enviar direccion de aim cada frame
local AimEvent = ReplicatedStorage.Remotes.Character:WaitForChild("AimDirection")

RunService.RenderStepped:Connect(function()
    AimEvent:FireServer(workspace.CurrentCamera.CFrame.LookVector)
end)

-- Server: recibir, no importa si se pierden paquetes
AimEvent.OnServerEvent:Connect(function(player, lookVec)
    if typeof(lookVec) ~= "Vector3" then return end
    playerAimCache[player] = lookVec  -- overwrite, no acumular
end)
```

**Limites:**
- Max 1000 bytes por evento
- Sin garantia de orden
- No es mas rapido que RemoteEvent - beneficia en que DROPS packets bajo carga
- Buen caso: aim direction, VFX triggers, posicion NPCs
- Mal caso: monedas, XP, inventario, estado de juego

### 4.3 Organizacion de Remotes

```
ReplicatedStorage/
└── Remotes/
    ├── Combat/
    │   ├── RequestAttack (RemoteEvent)
    │   └── RequestBlock (RemoteEvent)
    ├── Shop/
    │   └── PurchaseItem (RemoteFunction)
    ├── Character/
    │   └── AimDirection (UnreliableRemoteEvent)
    ├── Pets/
    │   ├── HatchEgg (RemoteEvent)
    │   ├── EquipPet (RemoteEvent)
    │   └── UnequipPet (RemoteEvent)
    └── UI/
        ├── ShowNotification (RemoteEvent)
        └── UpdateHUD (RemoteEvent)
```

**Convencion:** verbo-sustantivo (RequestAttack, PurchaseItem, HatchEgg).

---

## 5. ECONOMIA (Server-Authoritative)

```lua
-- Toda economia se maneja en servidor
local EconomyService = {}

function EconomyService.addCoins(player, amount)
    if typeof(amount) ~= "number" or amount <= 0 then return false end
    local coins = player.leaderstats:FindFirstChild("Coins")
    if not coins then return false end
    
    coins.Value += amount
    dataStore:MarkDirty(player.UserId)
    return true
end

function EconomyService.spendCoins(player, amount)
    if typeof(amount) ~= "number" or amount <= 0 then return false end
    local coins = player.leaderstats:FindFirstChild("Coins")
    if not coins or coins.Value < amount then return false end
    
    coins.Value -= amount
    dataStore:MarkDirty(player.UserId)
    return true
end

function EconomyService.getCoins(player)
    local coins = player.leaderstats:FindFirstChild("Coins")
    return coins and coins.Value or 0
end

return EconomyService
```

**Regla:** El cliente NUNCA dice cuanto cobrar. El servidor deriva el precio de su config interna.

---

## 6. ARQUITECTURA DE SCRIPTS

### 6.1 Single-Script Architecture (recomendado por Quenty)

```
ServerScriptService/
├── MainServer (Script)           -- requiere todos los modules
└── (nada mas)

ReplicatedStorage/
├── Modules/
│   ├── PetConfig (ModuleScript)
│   ├── EggConfig (ModuleScript)
│   ├── RNGUtil (ModuleScript)
│   ├── DataStoreWrapper (ModuleScript)
│   ├── PetManager (ModuleScript)
│   └── EconomyService (ModuleScript)
└── Remotes/                      -- RemoteEvents/Functions

StarterPlayerScripts/
├── MainClient (LocalScript)      -- requiere todos los client modules
```

### 6.2 Event Bus (BindableEvent interno)

```lua
-- Para comunicacion entre modulos DEL MISMO lado (server<->server)
local EventBus = {}
local events = {}

function EventBus:fire(eventName, ...)
    if events[eventName] then
        events[eventName]:Fire(...)
    end
end

function EventBus:on(eventName, callback)
    if not events[eventName] then
        events[eventName] = Instance.new("BindableEvent")
        events[eventName].Parent = script
    end
    return events[eventName].Event:Connect(callback)
end

return EventBus
```

### 6.2b Cross-Script Communication (BindableEvent + RemoteEvent)

Patron para cuando scripts independientes (no ModuleScripts) necesitan comunicarse.

```
Server Script A (producer) → BindableEvent → Server Script B (consumer)
Server Script B → RemoteEvent:FireClient → Client LocalScript
```

**Ejemplo real (Sky Dash timer):**
- `CheckpointHandler` detecta checkpoint activado → `BindableEvent("SectionUpdate"):Fire(player, sectionNum)`
- `GameManager` escucha `SectionUpdate.Event` → actualiza estado del jugador
- `GameManager` envía timer via `RemoteEvent("TimerUpdate"):FireClient(player, elapsed, section)`
- `HUDController` (LocalScript) escucha `OnClientEvent` → actualiza UI

**Creación del BindableEvent** (en el script consumidor, NO en execute_luau):
```lua
-- Al final de GameManager (el consumidor):
local sectionUpdater = Instance.new("BindableEvent")
sectionUpdater.Name = "SectionUpdate"
sectionUpdater.Parent = ReplicatedStorage:WaitForChild("Remotes")

sectionUpdater.Event:Connect(function(player, sectionNum)
    updatePlayerSection(player, sectionNum)
end)
```

**Fire desde el productor:**
```lua
-- En CheckpointHandler (el productor):
local remotes = game.ReplicatedStorage:FindFirstChild("Remotes")
if remotes then
    local sectionUpdate = remotes:FindFirstChild("SectionUpdate")
    if sectionUpdate then
        sectionUpdate:Fire(player, cpNum)
    end
end
```

**Por qué FindFirstChild (no WaitForChild) en el productor:** El BindableEvent solo existe despues de que el script consumidor corra en runtime. Si el productor usa `WaitForChild`, se cuelga si el consumidor todavia no creo el event. Con `FindFirstChild`, simplemente no envia si no existe todavia — y en el siguiente touch, ya estara disponible.

**⚠ Warning: execute_luau NO persiste en Play mode.** Todos los scripts de comunicacion
(BindableEvent setup, RemoteEvent handlers) DEBEN ser Scripts reales creados via
`multi_edit` en ServerScriptService/StarterGui. Código ejecutado via `execute_luau`
desaparece al dar Play.

### 6.3 Init pattern (ModuleScripts con init)

```lua
-- Modulos que necesitan setup:
local PetManager = {}

function PetManager:init(dataStore, remotes)
    self.dataStore = dataStore
    self.remotes = remotes
    -- conectar events, etc
end

function PetManager:equipPet(player, petUid)
    -- ...
end

return PetManager

-- En MainServer:
local PetManager = require(ReplicatedStorage.Modules.PetManager)
PetManager:init(dataStore, remotes)
```

---

## 7. ANTI-PATTERNS

### A1. Cliente envia precio
```lua
-- MAL
BuyEvent.OnServerEvent:Connect(function(player, item, price)
    coins.Value -= price  -- EXPLOIT: price=0
end)
-- BIEN: servidor busca precio en su config
```

### A2. DataStore en cada frame
```lua
-- MAL
coins.Changed:Connect(function()
    dataStore:Save(userId)  -- 60 writes/min por player
end)
-- BIEN: dirty flag + autosave cada 60 seg
```

### A3. SetAsync para player data
```lua
-- MAL: puede perder datos si otro server escribio
store:SetAsync(key, data)
-- BIEN: UpdateAsync considera valor previo
store:UpdateAsync(key, function(old) return data end)
```

### A4. invokeClient desde servidor
```lua
-- MAL: exploiter puede colgar el server forever
local result = RemoteFunc:InvokeClient(player, "getData")
-- BIEN: FireClient + cliente responde con otro FireServer
```

### A5. BodyPosition/BodyGyro para pets
```lua
-- MAL: deprecated
local bp = Instance.new("BodyPosition")
-- BIEN: AlignPosition + AlignOrientation
local ap = Instance.new("AlignPosition")
```

### A6. Script isolation — no shared state between Scripts

En Roblox, cada Script tiene su propio scope local. No hay forma de acceder
a variables/estado de otro Script directamente. Solo hay 3 mecanismos:

- **BindableEvent**: server↔server (un script fire, otro escucha)
- **RemoteEvent**: server↔client (FireClient / FireServer)
- **ModuleScript**: shared code (requiere `require()` de ambos lados)

Si Script A tiene `local playerState = {}` y Script B necesita leer/escribir
ese estado, la solución es:
1. Script A crea un BindableEvent y escucha comandos
2. Script B firea el BindableEvent con los parámetros necesarios
3. Script A maneja la lógica internamente

NUNCA intentar: `_G.playerState`, `shared.state`, o asumir que ModuleScripts
comparten referencias de tablas mutables (las tablas se copian al require).

Verificado en Sky Dash: VictoryHandler necesitaba detener el timer de GameManager
→ 3 BindableEvents (SectionUpdate, VictoryUpdate, PlayAgainReset). Para más
de 3-4 eventos, considerar consolidar en un único BindableEvent con comando
string: `bus:Fire("victory", player)` / `bus:Fire("reset", player)`.

### A7. Race condition — BindableEvents creados en runtime

Cuando dos Scripts crean/leen BindableEvents al inicio (top-level), hay race condition:

```lua
-- Script A (LeaderstatsHandler) crea VictoryTime:
local victoryTime = Instance.new("BindableEvent")
victoryTime.Name = "VictoryTime"
victoryTime.Parent = remotes

-- Script B (GameManager) busca VictoryTime dentro de un event handler:
victoryUpdater.Event:Connect(function(player)
    local victoryTime = remotes:FindFirstChild("VictoryTime")  -- OK: ya en runtime
    if victoryTime then victoryTime:Fire(player, elapsed) end
end)
```

**Regla:** Si Script B necesita el BindableEvent en un event handler (no en init),
usar `FindFirstChild` (no `WaitForChild`). El BindableEvent ya existirá cuando
el handler se dispare en runtime. Solo es race condition en init-time.

Si Script B necesita el BindableEvent en init (top-level), usar `WaitForChild`.
Esto bloquea hasta que Script A lo cree.

### A8. State reset sin granularidad (muerte/respawn)

```lua
-- MAL: re-inicializar TODO el estado al respawnear
playerState[player] = {
    startTime = nil,
    running = false,
    section = 0,        -- BUG: pierde progreso del jugador
}

-- BIEN: separar estado que se resetea vs estado que persiste
local prevSection = playerState[player] and playerState[player].section or 0
playerState[player] = {
    startTime = nil,     -- resetea: timer vuelve a 0
    running = false,     -- resetea: debe moverse para iniciar
    section = prevSection, -- PRESERVA: progreso no se pierde al morir
}
```

**Regla:** Cuando `CharacterAdded` o `Died` re-inicializa estado per-player,
distinguir explícitamente qué campos se resetean y cuáles se preservan.
Categorías típicas:
- **Resetea al morir:** timer, combo, velocidad temporal, buffs
- **Preserva al morir:** checkpoint/sección, progreso, items permanentes, stats

### A7. Victory Zone Pattern (Touch → Stop Timer → UI → Reset)

Flujo completo para condición de victoria en juegos con timer:

```
1. VictoryZone (Part, CanCollide=false, Neon) → .Touched detecta jugador
2. VictoryHandler → BindableEvent("VictoryUpdate"):Fire(player)
3. GameManager → escucha VictoryUpdate, calcula finalElapsed, FireClient timer final, running=false
4. VictoryHandler → RemoteEvent("VictoryReached"):FireClient(player)
5. VictoryScreenController (LocalScript) → muestra overlay con tiempo, botón Play Again
6. Play Again → RemoteEvent("PlayAgain"):FireServer()
7. VictoryHandler → BindableEvent("PlayAgainReset"):Fire(player) + Health=0
8. GameManager → escucha PlayAgainReset, section=0, timer reset
```

**Reglas:**
- VictoryZone debe ser `CanCollide=false` (el jugador la atraviesa, no saltar sobre ella)
- `hasWon[player]` previene doble-fire del Touched
- GameManager calcula `finalElapsed` ANTES de poner `running=false`
- Play Again: matar personaje (`Health=0`) fuerza respawn en `RespawnLocation` (seteado a Section 0)
- VictoryScreen `ResetOnSpawn=false` — no se destruye al respawnear
- HUD se oculta durante victory, se re-muestra al Play Again

### A9. Leaderstats con Changed para save
```lua
-- MAL: save en cada cambio
coins.Changed:Connect(function() saveData() end)
-- BIEN: marcar dirty, autosave periodico
coins.Changed:Connect(function() dataStore:MarkDirty(userId) end)
```

---

## 8. CHARACTER CONTROLLER LIBRARY (Full Release, Abril 2026)

Reemplaza el Humanoid "black box" con una implementacion Luau transparente y extensible. Compuesto por **AvatarAbilities Library** + **ControllerManager**.

### Cambios clave vs Humanoid
- **Conservation of Momentum**: personajes mantienen momento lineal/angular al dejar el suelo (no mas CFrame math para platforms/vehicles)
- **Friction-Based Movement**: caminar respeta material properties (desliza en hielo, tracciona en goma)
- **Performance**: igual o 2x mas rapido que Humanoid en mediciones reales
- **Extensible**: habilidades futuras (Crouch, Sprint) sin esperar engine updates

### Como adoptar
1. Save/Publish tu experiencia
2. Avatar Settings -> Movement section -> Character Controller Library
3. Deseleccionar Abilities que no quieras

### Properties para restaurar "feel" legado
```
MaintainLinearMomentum
MaintainAngularMomentum
AirController
FrictionWeight
Friction
GroundController
StarterPlayer.BreakJointsOnDeath
Player.DevEnableMouseLock  -- Shift-Lock deshabilitado con CCL
```

### Limitaciones actuales
- R6 + Server Authority = **no playable**
- R6 tiene algunos bugs reportados
- Se activa via Avatar Settings (no aparece si solo R6 seleccionado — workaround: set R15, activar CCL, volver a R6)
- Mobile touch UI se actualizo — verificar que no overlap con custom UI (60px safe zone)

### Roadmap
- Strafe Ability (reemplaza Shift-Lock)
- Crouch y Sprint abilities
- Nuevos touch buttons default

Fuente: https://devforum.roblox.com/t/full-release-the-future-of-character-movement-character-controller-library/4565267

---

## 9. DATASTORE RTBF AUTOMATIZADO (Beta, Abril 2026)

Procesamiento automatico de solicitudes "Right To Be Forgotten" (RTBF).

### Como funciona
1. Definir deletion templates que mapean data stores/keys a usuarios
2. Roblox procesa automaticamente las solicitudes RTBF usando esos templates
3. Elimina la necesidad de procesar manualmente cada solicitud

### Data Store Storage Limits (Live, Abril 2026)
- Limits per-experience (no per-server)
- Escalan con lifetime users de la experiencia
- Solo ~30 experiencias de 55M estan sobre el limite
- Data Store Manager disponible para medir uso

Fuente: https://devforum.roblox.com/t/beta-introducing-automated-rtbf-processing-for-data-stores/4568086

---

## 10. MESH STREAMING (Opt-in Phase, Abril 2026)

Sistema de streaming de meshes con LOD mejorado.

```lua
-- Habilitar en Workspace
Workspace.MeshStreamingAndImprovedLoDs = Enum.PropertyStatus.Enabled
```

- Genera LODs en cloud automaticamente
- Stream meshes basado en importancia de escena
- Default behavior en ~Julio 2026
- Reemplaza Texture Streaming que ya estaba activo

Fuente: https://devforum.roblox.com/t/introducing-mesh-streaming-and-improved-cloud-lods-in-published-experiences-opt-in-phase/4601232

---

## 11. LUAU NEW TYPE SOLVER (General Release, Enero 2026)

El nuevo type solver de Luau ahora es default para nocheck y non-strict mode.

### Accion requerida
- Si usabas el New Type Solver en strict mode via Studio Beta:
  - Set `Workspace.UseNewLuauTypeSolver` de Default a Enabled
  - El Studio Beta feature se elimino el 7 de Enero 2026
- El viejo type inference engine sigue disponible durante 2026

Fuente: https://devforum.roblox.com/t/general-release-luau%E2%80%99s-new-type-solver/4084991

---

## 12. STUDIO MCP + PLAYTEST AGENT (Studio Beta, Abril 2026)

### Studio MCP Server
- Studio ahora tiene MCP server built-in
- Creadores pueden usar API keys con LLMs externos (Google, Anthropic, OpenAI)
- 44% del top 1000 creadores ya usa AI tools via MCP

### Playtest Agent
- Subagente de Assistant que spawnea un character de test
- Ejecuta escenarios de gameplay en contexto propio
- Se habilita en Beta Features > "Playtest Agent"

Fuente: https://devforum.roblox.com/t/studio-beta-studio-assistant-mcp-playtest-agent/4566767

---

## 13. APIS DEPRECATED 2026

| API | Estado | Migracion |
|-----|--------|-----------|
| Legacy Game Pass web APIs | Deprecated Abril 23, 2026 | Migrar a Open Cloud APIs |
| Legacy Developer Product APIs | Deprecated Abril 23, 2026 | Migrar a Open Cloud APIs |
| PlayerOwnsAsset | Breaking change pendiente | Migrar a Economy API |
| Perspective API (moderation) | EOL Diciembre 31, 2026 | Migrar a Roblox moderation native |
| Old Type Solver | Disponible durante 2026 | Migrar a New Type Solver |

Fuente: https://devforum.roblox.com/t/upcoming-breaking-change-to-playerownsasset-and-inventory-web-apis/4226591

---

## Fuentes

- https://gmmarket.me/community/post/roblox-datastore-in-2026-the-new-per-experience-limit-explained-migration-plan
- https://gmmarket.me/community/post/roblox-client-server-replication-best-practices-remoteevent-vs-remotefunction-vs
- https://devforum.roblox.com/t/setasync-vs-updateasync-which-one-should-i-use/433021
- https://devforum.roblox.com/t/what-do-you-guys-think-the-best-way-of-making-a-pet-movement-system-is/359581
- https://devforum.roblox.com/t/are-bodymovers-still-supported/188345
- https://devforum.roblox.com/t/how-do-you-architect-a-single-script-architecture/1550226
- https://create.roblox.com/docs/scripting/events/remote
