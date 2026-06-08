---
name: roblox-sound-design
description: "Audio y sonido en Roblox: SoundService, SoundGroups, audio espacial, SFX, musica ambiental, transiciones con TweenService. Usa cuando necesites agregar efectos de sonido, musica de fondo, audio posicional, o control de volumen por categorias. Resuelve 'el juego se siente vacio' o 'los sonidos se escuchan mal'."
version: "1.0"
---

# Roblox Sound Design — Audio, SFX y Musica

Reglas y patrones para que tu juego suene profesional. El audio es el 50% de la experiencia — sin sonido, todo se siente "barato" o "incompleto".

Fuentes:
- https://create.roblox.com/docs/reference/engine/classes/Sound.md
- https://create.roblox.com/docs/reference/engine/classes/SoundService.md
- https://create.roblox.com/docs/reference/engine/classes/SoundGroup.md
- https://devforum.roblox.com/t/creating-immersive-environmental-audio-on-roblox/ (Inspire 2025)
- https://gamedevacademy.org/roblox-sound-service-tutorial-complete-guide

---

## 1. CORE: Objeto Sound

### Tipos de sonido por ubicacion

```lua
-- SONIDO 3D (posicional): parentear a BasePart o Attachment
local sound3D = Instance.new("Sound")
sound3D.SoundId = "rbxassetid://123456789"
sound3D.Parent = part  -- o attachment
-- Volumen depende de distancia al listener (camara por defecto)
-- Tiene efecto Doppler

-- SONIDO GLOBAL (no posicional): parentear a cualquier otra cosa
local sound2D = Instance.new("Sound")
sound2D.SoundId = "rbxassetid://123456789"
sound2D.Parent = script  -- o SoundService, StarterGui, etc.
-- Mismo volumen en toda la experiencia
-- Ideal para: musica de fondo, GUI clicks, notificaciones
```

### API completa del objeto Sound

```lua
local s = Instance.new("Sound")
s.SoundId = "rbxassetid://123456789"   -- ID del asset de audio
s.Volume = 0.5                          -- 0 a 10, default 0.5
s.PlaybackSpeed = 1                     -- velocidad/pitch, default 1
s.Looped = false                        -- repetir al terminar
s.Playing = false                       -- toggle playback (replica)
s.TimePosition = 0                      -- posicion actual en segundos
s.PlayOnRemove = false                  -- sonar al destruir

-- Audio espacial (solo sonidos 3D)
s.RollOffMinDistance = 10               -- distancia min sin atenuacion (studs)
s.RollOffMaxDistance = 100              -- distancia max audible (studs)
s.RollOffMode = Enum.RollOffMode.InverseTapered  -- como baja el volumen

-- PlaybackRegions (avanzado)
s.PlaybackRegionsEnabled = true
s.PlaybackRegion = NumberRange.new(5, 30)    -- rango de reproduccion
s.LoopRegion = NumberRange.new(10, 25)       -- rango de loop dentro del playback

-- Metodos
s:Play()       -- inicia desde TimePosition, resetea a 0
s:Stop()       -- detiene y resetea TimePosition a 0
s:Pause()      -- pausa sin resetear TimePosition
s:Resume()     -- continua desde donde se pauso

-- Propiedades read-only
s.IsPlaying    -- true si esta reproduciendo
s.IsLoaded     -- true si el audio cargo
s.TimeLength   -- duracion total en segundos
s.PlaybackLoudness  -- amplitud actual (0-1000)

-- Eventos
s.Ended:Connect(function(soundId) end)         -- termino de reproducir (NO para Looped)
s.DidLoop:Connect(function(soundId, count) end) -- veces que ha loopeado
s.Loaded:Connect(function(soundId) end)         -- audio termino de cargar
s.Played:Connect(function(soundId) end)         -- se llamo :Play()
s.Stopped:Connect(function(soundId) end)        -- se llamo :Stop()
```

### RollOffMode — como se desvanece el sonido 3D

| Modo | Comportamiento | Uso |
|------|---------------|-----|
| `Inverse` | Mas realista, decaimiento suave | General |
| `InverseTapered` | Default. Suave cerca, rapido lejos | Recomendado para la mayoria |
| `Linear` | Lineal entre Min y Max | Control preciso pero poco realista |
| `LinearSquared` | Lineal al cuadrado | Transicion mas abrupta |

**Regla:** Usar `InverseTapered` (default) para la mayoria de casos. Solo cambiar si necesitas control preciso del fade.

---

## 2. PATRONES DE SONIDO

### Musica de fondo con crossfade

```lua
-- En SoundService o un LocalScript en StarterPlayerScripts
local TweenService = game:GetService("TweenService")

local currentMusic = Instance.new("Sound")
currentMusic.SoundId = "rbxassetid://MUSIC_ID"
currentMusic.Volume = 0.3
currentMusic.Looped = true
currentMusic.Parent = game.SoundService

local function ensureLoaded(sound)
    if not sound.IsLoaded then
        sound.Loaded:Wait()
    end
end

ensureLoaded(currentMusic)
currentMusic:Play()

local function crossfade(newSoundId, duration)
    local newMusic = Instance.new("Sound")
    newMusic.SoundId = "rbxassetid://" .. newSoundId
    newMusic.Volume = 0
    newMusic.Looped = true
    newMusic.Parent = game.SoundService

    ensureLoaded(newMusic)

    -- Fade out actual, fade in nuevo
    local fadeOut = TweenService:Create(currentMusic,
        TweenInfo.new(duration), {Volume = 0})
    local fadeIn = TweenService:Create(newMusic,
        TweenInfo.new(duration), {Volume = 0.3})

    fadeIn:Play()
    fadeOut:Play()
    newMusic:Play()

    fadeOut.Completed:Connect(function()
        currentMusic:Stop()
        currentMusic:Destroy()
        currentMusic = newMusic
    end)
end

-- Uso: crossfade("987654321", 2)  -- 2 segundos de transicion
```

### SFX de pasos (sonido en personaje)

```lua
-- LocalScript en StarterCharacterScripts
local Players = game:GetService("Players")
local player = Players.LocalPlayer
local character = script.Parent
local humanoid = character:WaitForChild("Humanoid")

local footstepSound = Instance.new("Sound")
footstepSound.SoundId = "rbxassetid://FOOTSTEP_ID"
footstepSound.Volume = 0.4
footstepSound.PlaybackSpeed = 1
footstepSound.Parent = character:WaitForChild("HumanoidRootPart")

local stepTimer = 0
local STEP_INTERVAL = 0.4  -- segundos entre pasos

humanoid.Running:Connect(function(speed)
    if speed > 1 then
        -- Ajustar velocidad de reproduccion segun velocidad de movimiento
        footstepSound.PlaybackSpeed = 0.8 + (speed / 30) * 0.6
    end
end)

game:GetService("RunService").Heartbeat:Connect(function(dt)
    local speed = humanoid.WalkSpeed
    local isMoving = humanoid.MoveDirection.Magnitude > 0

    if isMoving and speed > 1 then
        stepTimer = stepTimer + dt
        if stepTimer >= STEP_INTERVAL then
            footstepSound:Play()
            stepTimer = 0
        end
    else
        stepTimer = STEP_INTERVAL * 0.8  -- primer paso rapido al empezar a moverse
    end
end)
```

### Zona de audio ambiental (trigger area)

```lua
-- Script en una Part que funciona como zona
local zone = script.Parent
zone.Transparency = 1
zone.CanCollide = false
zone.Anchored = true

local ambientSound = Instance.new("Sound")
ambientSound.SoundId = "rbxassetid://AMBIENT_ID"
ambientSound.Volume = 0
ambientSound.Looped = true
ambientSound.RollOffMinDistance = 5
ambientSound.RollOffMaxDistance = 50
ambientSound.Parent = zone
ambientSound:Play()

local TweenService = game:GetService("TweenService")
local FADE_TIME = 1.5

zone.Touched:Connect(function(hit)
    local character = hit.Parent
    local humanoid = character:FindFirstChild("Humanoid")
    local player = game.Players:GetPlayerFromCharacter(character)
    if player and player.Name == game.Players.LocalPlayer.Name then
        TweenService:Create(ambientSound,
            TweenInfo.new(FADE_TIME), {Volume = 0.5}):Play()
    end
end)

-- Opcional: fade out al salir de la zona
```

### Sonido al coleccionar item

```lua
-- Script server-side, disparado por evento
local function playCollectSound(player, position)
    -- Crear sonido temporal en la posicion
    local sound = Instance.new("Sound")
    sound.SoundId = "rbxassetid://COLLECT_ID"
    sound.Volume = 0.6
    sound.Parent = workspace.Terrain  -- sonido global

    -- Para sonido 3D, parentear a una Part temporal en la posicion
    local tempPart = Instance.new("Part")
    tempPart.Position = position
    tempPart.Anchored = true
    tempPart.CanCollide = false
    tempPart.Transparency = 1
    tempPart.Parent = workspace

    sound.Parent = tempPart
    sound:Play()
    sound.Ended:Connect(function()
        tempPart:Destroy()
    end)
end
```

---

## 3. SOUNDGROUPS — Control por categorias

```lua
-- Configuracion de SoundGroups (Script en SoundService)
local SoundService = game:GetService("SoundService")

-- Crear grupos
local musicGroup = Instance.new("SoundGroup")
musicGroup.Name = "Music"
musicGroup.Volume = 0.3
musicGroup.Parent = SoundService

local sfxGroup = Instance.new("SoundGroup")
sfxGroup.Name = "SFX"
sfxGroup.Volume = 0.7
sfxGroup.Parent = SoundService

local ambientGroup = Instance.new("SoundGroup")
ambientGroup.Name = "Ambient"
ambientGroup.Volume = 0.4
ambientGroup.Parent = SoundService

-- Asignar un sonido a un grupo
local bgm = Instance.new("Sound")
bgm.SoundGroup = musicGroup  -- volumen controlado por el grupo
bgm.SoundId = "rbxassetid://MUSIC_ID"
bgm.Looped = true
bgm.Parent = SoundService

-- Ajustar volumen de toda una categoria
local TweenService = game:GetService("TweenService")
TweenService:Create(musicGroup,
    TweenInfo.new(1), {Volume = 0.1}):Play()  -- bajar musica
```

**Regla:** Siempre usar SoundGroups. Permite mute por categoria sin tocar cada Sound individualmente.

---

## 4. ANTI-PATTERNS

| Anti-pattern | Problema | Fix |
|---|---|---|
| Sonido 3D parentado a StarterGui/SoundService | Se escucha global, no posicional | Parentear a BasePart o Attachment |
| RollOffMaxDistance muy bajo | Sonido corta abruptamente | Minimo 50 studs para SFX, 100+ para ambiente |
| Sin `IsLoaded` check | Sonido no reproduce si no cargo | `if not s.IsLoaded then s.Loaded:Wait() end` |
| Volume > 1 en SFX | Distorision, especialmente con multiples sonidos | SFX: 0.3-0.8, Musica: 0.1-0.4, Ambient: 0.2-0.5 |
| Sin SoundGroups | No se puede mutear por categoria | Crear Music, SFX, Ambient groups |
| Musica con Volume 0.5+ | Apaga SFX y ambiente | Musica siempre mas baja que SFX |
| Usar :Play() en loop sin :Stop() | Sonidos se acumulan | Siempre :Stop() antes de :Play() en loops |
| Ignorar Ended event para cleanup | Memory leak de sonidos temporales | `sound.Ended:Wait(); sound:Destroy()` |
| Usar metodos lowercase (`:play()`) | Deprecated | Usar PascalCase (`:Play()`) siempre |
| `EmitterSize` (deprecated) | Usa API vieja | Usar `RollOffMinDistance` / `RollOffMaxDistance` |

---

## 5. CHECKLIST

```
[ ] Sonidos 3D parenteados a BasePart/Attachment (no a GUI/scripts)
[ ] Sonidos globales (musica) parenteados a SoundService o GUI
[ ] SoundGroups configurados: Music, SFX, Ambient
[ ] Volume hierarchy: SFX > Ambient > Musica
[ ] IsLoaded check antes de :Play() en sonidos criticos
[ ] RollOffMinDistance/MaxDistance configurados en sonidos 3D
[ ] Crossfade para transiciones de musica (no corte abrupto)
[ ] Cleanup de sonidos temporales via Ended event
[ ] Sin metodos deprecated (lowercase, EmitterSize, MaxDistance)
[ ] Probar en playtest: verificar que suena posicionalmente correcto
```

---

## Fuentes

- https://create.roblox.com/docs/reference/engine/classes/Sound.md
- https://create.roblox.com/docs/reference/engine/classes/SoundService.md
- https://create.roblox.com/docs/reference/engine/classes/SoundGroup.md
- https://devforum.roblox.com/t/creating-immersive-environmental-audio-on-roblox/ (Inspire 2025)
- https://gamedevacademy.org/roblox-sound-service-tutorial-complete-guide
