---
name: roblox-animations-vfx
description: "Animaciones (Animator, TweenService) y VFX (ParticleEmitter, Trail, Beam) para Roblox. APIs, patrones, performance y anti-patterns."
version: "1.0"
---

# Roblox Animaciones + VFX

Todo lo que necesitas para animar personajes, UI y crear efectos visuales.

Fuentes:
- https://devforum.roblox.com/t/deprecating-loadanimation-on-humanoid-and-animationcontroller/857129 (Roblox staff)
- https://create.roblox.com/docs/reference/engine/classes/Animator/LoadAnimation
- https://create.roblox.com/docs/effects/particle-emitters
- https://create.roblox.com/docs/reference/engine/enums/EasingStyle
- https://create.roblox.com/docs/reference/engine/classes/TweenService

---

## 1. SISTEMA DE ANIMACIONES

### 1.1 Animator (reemplaza Humanoid:LoadAnimation)

**`Humanoid:LoadAnimation()` esta DEPRECATED.** Usar `Animator:LoadAnimation()` directamente.

**Por que importa:** Si el cliente crea un Animator antes que el servidor, la replicacion se rompe silenciosamente. Las animaciones se ven localmente pero no se replican a otros jugadores.

```lua
-- MAL (deprecated, puede romper replicacion)
local track = humanoid:LoadAnimation(anim)

-- BIEN (recomendado)
local animator = humanoid:FindFirstChild("Animator")
    or humanoid:WaitForChild("Animator", 5)
if not animator then return end
local track = animator:LoadAnimation(anim)
```

**Setup correcto del Animator:**

```lua
-- SERVER (ServerScriptService) - crear Animator al spawn
game.Players.PlayerAdded:Connect(function(player)
    player.CharacterAdded:Connect(function(character)
        local humanoid = character:WaitForChild("Humanoid")
        -- Crear Animator en el servidor PRIMERO
        if not humanoid:FindFirstChild("Animator") then
            local animator = Instance.new("Animator")
            animator.Parent = humanoid
        end
    end)
end)
```

```lua
-- CLIENT (StarterPlayerScripts) - obtener Animator del servidor
local player = game.Players.LocalPlayer
local character = player.Character or player.CharacterAdded:Wait()
local humanoid = character:WaitForChild("Humanoid")
local animator = humanoid:WaitForChild("Animator", 5)
```

### 1.2 AnimationTrack - API completa

```lua
local anim = Instance.new("Animation")
anim.AnimationId = "rbxassetid://TU_ANIMATION_ID"

local track = animator:LoadAnimation(anim)

-- Propiedades utiles
track.Length      -- duracion en segundos
track.IsPlaying   -- boolean
track.Speed       -- velocidad actual
track.TimePosition -- posicion actual en segundos
track.Looped      -- boolean, si repite

-- Metodos principales
track:Play(fadeTime, weight, speed)
track:Stop(fadeTime)
track:AdjustSpeed(speed)
track:AdjustWeight(weight, fadeTime)

-- Events
track.Stopped:Connect(function() ... end)
track.DidLoop:Connect(function() ... end)
track.KeyframeReached:Connect(function(name) ... end)
track:GetMarkerReachedSignal("MarkerName"):Connect(function(param) ... end)
```

**Parametros de Play:**
- `fadeTime` (default 0.1): tiempo de transicion
- `weight` (default 1): peso de blending (0-1, para mezclar animaciones)
- `speed` (default 1): velocidad de reproduccion

### 1.3 Patrones de animacion

**Reproducir por X segundos y parar:**
```lua
track:Play()
task.delay(track.Length / track.Speed, function()
    if track.IsPlaying then
        track:Stop()
    end
end)
```

**Reproducir N loops:**
```lua
track.Looped = true
local loopsDone = 0
track.DidLoop:Connect(function()
    loopsDone += 1
    if loopsDone >= 3 then
        track:Stop()
    end
end)
track:Play()
```

**Blending de animaciones (pesos):**
```lua
-- Animacion base a peso bajo
walkTrack:Play(0.2, 0.3, 1)  -- fadeTime, weight 0.3, speed 1

-- Animacion superior a peso completo
waveTrack:Play(0.2, 1, 1)    -- weight 1 = full override del layer
```

**Animation events (markers):**
```lua
-- Definir markers en el Animation Editor
-- Leerlos en codigo:
track:GetMarkerReachedSignal("Hit"):Connect(function()
    -- ejecutar logica en el frame exacto del golpe
    dealDamage()
end)
```

---

## 2. TWEENSERVICE

### 2.1 TweenInfo.new() - parametros

```lua
local tweenInfo = TweenInfo.new(
    time,              -- duracion en segundos (default 1)
    easingStyle,       -- Enum.EasingStyle (default Quad)
    easingDirection,   -- Enum.EasingDirection (default InOut)
    repeatCount,       -- numero de repeticiones extra (default 0, -1 = infinito)
    reverses,          -- si va y vuelve (default false)
    delayTime          -- delay antes de iniciar (default 0)
)
```

### 2.2 EasingStyles (de suave a brusco)

| Style | Valor | Comportamiento | Uso tipico |
|-------|-------|---------------|------------|
| **Linear** | 0 | Velocidad constante | Movimiento mecanico, loops |
| **Sine** | 1 | Suave (sinusoide) | UI basico, transiciones suaves |
| **Quad** | 3 | Un poco mas brusco | Estandar general |
| **Cubic** | 10 | Medio-brusco | Bounces, impactos |
| **Quart** | 4 | Brusco | Slides rapidos |
| **Quint** | 5 | Mas brusco | Entradas dramaticas |
| **Exponential** | 8 | El mas brusco (curva exp) | Snap, impacto |
| **Back** | 2 | Sobrepasa y vuelve | Efecto "spring", botones |
| **Bounce** | 6 | Rebota al llegar | Impacto, colisiones |
| **Elastic** | 7 | Como banda elastica | Efectos juguetones |
| **Circular** | 9 | Aceleracion subita, desaceleracion gradual | Movimientos naturales |

**EasingDirections:**
- `In` - efecto al inicio
- `Out` - efecto al final (el mas comun para UI)
- `InOut` - efecto al inicio y final

### 2.3 Patrones de Tween

**Tween basico:**
```lua
local TweenService = game:GetService("TweenService")

local tweenInfo = TweenInfo.new(0.5, Enum.EasingStyle.Back, Enum.EasingDirection.Out)
local tween = TweenService:Create(object, tweenInfo, {
    Position = UDim2.new(0.5, 0, 0.5, 0),
    BackgroundTransparency = 0
})
tween:Play()
tween.Completed:Wait()  -- esperar a que termine (bloquea)
```

**Tween con callback:**
```lua
local function tweenAsync(object, properties, duration, style, direction)
    local tweenInfo = TweenInfo.new(
        duration or 0.3,
        style or Enum.EasingStyle.Quad,
        direction or Enum.EasingDirection.Out
    )
    local tween = TweenService:Create(object, tweenInfo, properties)
    tween:Play()
    return tween
end

-- Uso
local t = tweenAsync(frame, {Position = UDim2.new(0, 0, 0, 0)}, 0.4)
t.Completed:Connect(function()
    print("Animacion terminada")
end)
```

**Cancelar tween previo antes de crear nuevo:**
```lua
-- TweenService sobreescribe tweens que modifican la misma propiedad
-- No hay que cancelar manualmente - el viejo se cancela solo
local tween1 = TweenService:Create(part, info1, {Position = goal1})
tween1:Play()

-- Esto cancela tween1 automaticamente
local tween2 = TweenService:Create(part, info2, {Position = goal2})
tween2:Play()
```

**Tween reversa (ida y vuelta):**
```lua
local info = TweenInfo.new(0.3, Enum.EasingStyle.Quad, Enum.EasingDirection.Out, 0, true)
local tween = TweenService:Create(frame, info, {Position = goalPos})
tween:Play()
-- Hace ida y vuelta automaticamente
```

### 2.4 Tween para UI - Patrones comunes

**Slide in desde arriba:**
```lua
-- Posicion inicial: arriba fuera de pantalla
frame.Position = UDim2.new(0.5, 0, -1, 0)
local tween = TweenService:Create(frame, TweenInfo.new(0.4, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {
    Position = UDim2.new(0.5, 0, 0.5, 0)
})
tween:Play()
```

**Fade in/out:**
```lua
-- Fade in
local tween = TweenService:Create(frame, TweenInfo.new(0.3), {
    BackgroundTransparency = 0,
    GroupTransparency = 0  -- si es CanvasGroup
})

-- Fade out + destruir
local tween = TweenService:Create(frame, TweenInfo.new(0.3), {
    BackgroundTransparency = 1
})
tween:Play()
tween.Completed:Connect(function()
    frame:Destroy()
end)
```

**Scale pop (boton presionado):**
```lua
local info = TweenInfo.new(0.15, Enum.EasingStyle.Back, Enum.EasingDirection.Out, 0, true)
local shrink = TweenService:Create(button, info, {Size = UDim2.new(0.9, 0, 0.9, 0)})
-- Recordar: AnchorPoint = (0.5, 0.5) para que escale desde centro
shrink:Play()
```

---

## 3. PARTICLE EMITTERS (VFX)

### 3.1 Setup basico

```lua
-- Particulas en un Part
local emitter = Instance.new("ParticleEmitter")
emitter.Parent = part  -- o attachment

-- Particulas en un punto especifico (Attachment)
local attachment = Instance.new("Attachment")
attachment.Position = Vector3.new(0, 2, 0)
attachment.Parent = part

local emitter = Instance.new("ParticleEmitter")
emitter.Parent = attachment
```

### 3.2 Propiedades clave

| Propiedad | Tipo | Que hace |
|-----------|------|----------|
| `Texture` | string (asset ID) | Imagen de la particula |
| `Color` | ColorSequence | Color durante lifetime |
| `Size` | NumberSequence | Tamano durante lifetime |
| `Transparency` | NumberSequence | Opacidad durante lifetime |
| `Lifetime` | NumberRange | Segundos que vive cada particula |
| `Rate` | number | Particulas por segundo |
| `Speed` | NumberRange | Velocidad en studs/seg |
| `SpreadAngle` | Vector2 | Angulo de dispersion (X, Y) |
| `LightEmission` | number (0-1) | 0=normal, 1=additive (glow) |
| `EmissionDirection` | Enum.NormalId | Direccion de emision |
| `RotSpeed` | NumberRange | Velocidad de rotacion |
| `Acceleration` | Vector3 | Gravedad/fuerza adicional |
| `Drag` | number (0-1) | Resistencia al aire |
| `WindAffectsDrag` | boolean | Si responde al viento global |

**Shape:**
| Propiedad | Valores | Efecto |
|-----------|---------|--------|
| `Shape` | Box, Sphere, Cylinder, Disc | Forma del volumen de emision |
| `ShapeStyle` | Volume, Surface | Dentro o solo superficie |
| `ShapeInOut` | Inward, Outward, InAndOut | Direccion dentro/fuera |

**NumberSequence y ColorSequence:**
```lua
-- NumberSequence: tamano/transparencia sobre lifetime
-- keypoints = {time=0..1, value, envelop}
emitter.Size = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0),     -- nace tamano 0
    NumberSequenceKeypoint.new(0.3, 2),   -- crece a 2
    NumberSequenceKeypoint.new(1, 0),     -- muere tamano 0
})

-- ColorSequence: color sobre lifetime
emitter.Color = ColorSequence.new({
    ColorSequenceKeypoint.new(0, Color3.fromRGB(255, 100, 0)),  -- nace naranja
    ColorSequenceKeypoint.new(0.5, Color3.fromRGB(255, 255, 0)), -- amarillo
    ColorSequenceKeypoint.new(1, Color3.fromRGB(255, 0, 0)),    -- muere rojo
})
```

### 3.3 Presets de VFX

**Fuego:**
```lua
local fire = Instance.new("ParticleEmitter")
fire.Texture = "rbxassetid://363518812"  -- fire texture comun
fire.Color = ColorSequence.new({
    ColorSequenceKeypoint.new(0, Color3.fromRGB(255, 200, 50)),
    ColorSequenceKeypoint.new(0.5, Color3.fromRGB(255, 100, 0)),
    ColorSequenceKeypoint.new(1, Color3.fromRGB(180, 0, 0)),
})
fire.Size = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0),
    NumberSequenceKeypoint.new(0.2, 3),
    NumberSequenceKeypoint.new(1, 0.5),
})
fire.Transparency = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0.2),
    NumberSequenceKeypoint.new(0.8, 0.5),
    NumberSequenceKeypoint.new(1, 1),
})
fire.Lifetime = NumberRange.new(0.5, 1.5)
fire.Rate = 40
fire.Speed = NumberRange.new(3, 6)
fire.SpreadAngle = Vector2.new(20, 20)
fire.LightEmission = 0.8
fire.Acceleration = Vector3.new(0, 8, 0)  -- sube
fire.EmissionDirection = Enum.NormalId.Top
```

**Humo:**
```lua
local smoke = Instance.new("ParticleEmitter")
smoke.Texture = "rbxassetid://363518812"
smoke.Color = ColorSequence.new(Color3.fromRGB(150, 150, 150), Color3.fromRGB(80, 80, 80))
smoke.Size = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 1),
    NumberSequenceKeypoint.new(1, 4),
})
smoke.Transparency = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0.3),
    NumberSequenceKeypoint.new(1, 1),
})
smoke.Lifetime = NumberRange.new(2, 4)
smoke.Rate = 15
smoke.Speed = NumberRange.new(1, 3)
smoke.SpreadAngle = Vector2.new(30, 30)
smoke.Acceleration = Vector3.new(0, 3, 0)
```

**Sparkles/destellos:**
```lua
local sparkles = Instance.new("ParticleEmitter")
sparkles.Texture = "rbxassetid://363278836"  -- sparkle
sparkles.Color = ColorSequence.new(Color3.fromRGB(255, 255, 200))
sparkles.Size = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0),
    NumberSequenceKeypoint.new(0.5, 0.3),
    NumberSequenceKeypoint.new(1, 0),
})
sparkles.Transparency = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0),
    NumberSequenceKeypoint.new(1, 1),
})
sparkles.Lifetime = NumberRange.new(0.3, 0.8)
sparkles.Rate = 30
sparkles.Speed = NumberRange.new(2, 5)
sparkles.SpreadAngle = Vector2.new(180, 180)
sparkles.LightEmission = 1
sparkles.RotSpeed = NumberRange.new(-180, 180)
```

**Aura (anillo alrededor de mascota/personaje):**
```lua
local aura = Instance.new("ParticleEmitter")
aura.Texture = "rbxassetid://363278836"
aura.Color = ColorSequence.new(tierColor)  -- color segun rareza
aura.Size = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0.5),
    NumberSequenceKeypoint.new(0.5, 1.5),
    NumberSequenceKeypoint.new(1, 0),
})
aura.Transparency = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0.5),
    NumberSequenceKeypoint.new(1, 1),
})
aura.Lifetime = NumberRange.new(0.8, 1.5)
aura.Rate = 20
aura.Speed = NumberRange.new(0.5, 1.5)
aura.SpreadAngle = Vector2.new(180, 180)
aura.LightEmission = 0.7
```

### 3.4 Control programatico

```lua
-- Encender/apagar particulas
emitter.Rate = 0        -- "apagar" (particulas activas siguen)
emitter.Enabled = false  -- desactivar completamente

-- Burst de particulas (explosion instantanea)
emitter.Rate = 0         -- no emitir continuamente
emitter:Emit(50)         -- emitir 50 de golpe

-- Limpiar particulas existentes
emitter:Clear()
```

---

## 4. TRAIL (estela)

Trail dibuja una textura entre dos Attachments mientras se mueven.

```lua
local att0 = Instance.new("Attachment")
att0.Position = Vector3.new(0, 0, -1.5)
att0.Parent = part

local att1 = Instance.new("Attachment")
att1.Position = Vector3.new(0, 0, 1.5)
att1.Parent = part

local trail = Instance.new("Trail")
trail.Attachment0 = att0
trail.Attachment1 = att1
trail.Lifetime = 1.0
trail.MinLength = 0.1
trail.FaceCamera = true
trail.LightEmission = 0.5
trail.TextureMode = Enum.TextureMode.Stretch
trail.Texture = "rbxassetid://..."  -- opcional
trail.Color = ColorSequence.new(Color3.fromRGB(255, 255, 255))
trail.Transparency = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 0),
    NumberSequenceKeypoint.new(1, 1),
})
trail.WidthScale = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 1),
    NumberSequenceKeypoint.new(1, 0),
})
trail.Parent = part
```

**Control:**
```lua
trail.Enabled = false  -- pausar
trail.Enabled = true   -- reanudar
trail:Clear()          -- limpiar estela existente
```

---

## 5. BEAM (rayo entre dos puntos)

Beam dibuja una textura entre dos Attachments (no necesita movimiento).

```lua
local att0 = Instance.new("Attachment")
att0.Parent = part1

local att1 = Instance.new("Attachment")
att1.Parent = part2

local beam = Instance.new("Beam")
beam.Attachment0 = att0
beam.Attachment1 = att1
beam.Texture = "rbxassetid://..."
beam.Color = ColorSequence.new(Color3.fromRGB(100, 200, 255))
beam.Transparency = NumberSequence.new(0)
beam.LightEmission = 1
beam.Width0 = 0.5  -- ancho en att0
beam.Width1 = 0.5  -- ancho en att1
beam.TextureSpeed = 1
beam.TextureLength = 1
beam.FaceCamera = true
beam.Segments = 10  -- mas = mas suave, mas costoso
beam.CurveSize0 = 0  -- curvatura cerca de att0
beam.CurveSize1 = 0  -- curvatura cerca de att1
beam.Parent = part1
```

**Zapping effect (rayo electrico):**
```lua
beam.Texture = "rbxassetid://148967956"  -- electric texture
beam.LightEmission = 1
beam.Segments = 8
beam.TextureSpeed = 5
beam.TextureLength = 2
-- Animar CurveSize0/1 con tween para movimiento
```

---

## 6. PERFORMANCE

### Particulas

| Regla | Limite | Razon |
|-------|--------|-------|
| Rate max | 400/seg (desktop), 100/seg (mobile) | Engine limit |
| Lifetime max | 20 segundos | Engine cap |
| Particulas simultaneas | <200 por emitter | Performance |
| Emitters activos | <20 por escena | Overdraw |
| Tamano particula | Lo menor posible | Fill-rate GPU |

**Tips de optimizacion:**
- Prefiere Rate alto + Size bajo sobre Rate bajo + Size alto
- Transparencia alta al inicio y final del lifetime (evita "pop in/out")
- Usa `LightEmission` cerca de 1 para textures oscuras (mejor efecto)
- Apaga emitters cuando no se vean (DistanceFromCamera check)
- Lifetime alto + Rate bajo = aura sostenida barata

### Tweens

- TweenService es eficiente - esta bien para UI y partes
- Para animaciones de personaje: usar AnimationTrack, NO tweens
- Para movimiento repetitivo continuo: preferir CFrame en Heartbeat sobre tween loops
- **⚠ EXCEPCIÓN: Moving Platforms** — TweenService con `reverses=true, repeatCount=-1` es correcto
  para el movimiento de la plataforma. Pero se necesita un SEPARATE Heartbeat loop para
  trackear jugadores y moverlos con la plataforma (delta CFrame). No confundir el tween
  de la plataforma con el tracking de jugadores — son dos sistemas independientes.
  Ver skill `roblox-map-building` → "Moving Platforms" para el patrón completo.
- Dos tweens sobre la misma propiedad: el segundo cancela el primero automaticamente
- `tween.Completed:Wait()` es valido pero cuidado con deadlocks

### Animations

- Crear Animator en servidor primero, siempre
- Usar `track.Stopped:Wait()` en vez de `task.wait(track.Length)` para saber cuando termina
- Limpiar tracks: `track:Stop()` + `track:Destroy()` cuando no se necesitan (aunque GC eventualmente lo hace)
- No reproducir mas de ~10 tracks simultaneos por personaje

---

## 7. ANTI-PATTERNS

### A1. Usar Humanoid:LoadAnimation
```lua
-- MAL (deprecated, replicacion rota)
local track = humanoid:LoadAnimation(anim)
-- BIEN
local animator = humanoid:WaitForChild("Animator", 5)
local track = animator:LoadAnimation(anim)
```

### A2. Tween en RenderStepped
```lua
-- MAL - tweens ya se actualizan cada frame, doble trabajo
RunService.RenderStepped:Connect(function()
    TweenService:Create(part, info, goal):Play()
end)
-- BIEN - crear tween una vez, Play()
local tween = TweenService:Create(part, info, goal)
tween:Play()
```

### A3. Particulas sin transparency fade
```lua
-- MAL - particulas "popean" al aparecer/desaparecer
emitter.Transparency = NumberSequence.new(0)
-- BIEN - fade suave
emitter.Transparency = NumberSequence.new({
    NumberSequenceKeypoint.new(0, 1),     -- invisible al nacer
    NumberSequenceKeypoint.new(0.1, 0),   -- aparece
    NumberSequenceKeypoint.new(0.9, 0),   -- visible
    NumberSequenceKeypoint.new(1, 1),     -- invisible al morir
})
```

### A4. Crear Tween sin guardar referencia
```lua
-- MAL - no puedes cancelar o esperar
TweenService:Create(part, info, goal):Play()
-- BIEN - guardar referencia
local tween = TweenService:Create(part, info, goal)
tween:Play()
tween.Completed:Wait()
```

### A5. Trail sin MinLength
```lua
-- MAL - trail aparece incluso con movimiento minimo
trail.MinLength = 0
-- BIEN - solo aparece con movimiento significativo
trail.MinLength = 0.5
```

---

## 8. ADAPTIVE ANIMATION (Full Release, Abril 2026)

Sistema que permite **reutilizar una misma animacion en diferentes rig types** (R15, R6, custom rigs).

### Que es
- **HumanoidRigDescription (HRD)**: "traductor" que mapea joints de tu rig custom al sistema de animacion de Roblox
- **DynamicRigDescription (DRD)**: complemento del HRD para rigs dinamicos
- Una animacion R15 puede reproducirse en rigs custom y viceversa

### Como usarlo
1. En Studio, click en el icono "Adaptive Animation" en el toolbar
2. Seleccionar tu Avatar
3. Click "Create" — genera HRD/DRD instances automaticamente

### Nota importante
> Si mapeaste manualmente un joint a "Pelvis" durante la beta, actualizar a la nueva propiedad **Spine** via Properties window o Avatar Ribbon.

### Limitaciones
- Solo disponible via plugin de Studio (no es API programatica directa)
- La animacion debe haber sido creada con el Animation Editor

Fuente: https://devforum.roblox.com/t/full-release-adaptive-animation-use-one-animation-across-any-rig/4605672

---

## 9. STYLING TRANSITIONS (Studio Beta, Mayo 2026)

Sistema nativo para tweens de UI dentro del ecosistema Styling — **sin codigo**.

```lua
-- Se definen en Stylesheets, se aplican automaticamente
-- Transiciones declarativas: cuando cambia un estilo, se tweena
-- Funciona con Style Editor (no-code) o via Luau scripts
```

### Estado
- Studio Beta (no disponible in-experience aun)
- Se habilita en Beta Features > "Styling Transitions"

Fuente: https://devforum.roblox.com/t/studio-beta-styling-transitions/4646870

---

## Fuentes

- https://devforum.roblox.com/t/deprecating-loadanimation-on-humanoid-and-animationcontroller/857129
- https://create.roblox.com/docs/reference/engine/classes/Animator/LoadAnimation
- https://create.roblox.com/docs/reference/engine/classes/AnimationTrack
- https://create.roblox.com/docs/effects/particle-emitters
- https://create.roblox.com/docs/reference/engine/classes/Trail
- https://create.roblox.com/docs/effects/beams
- https://create.roblox.com/docs/reference/engine/classes/TweenService
- https://create.roblox.com/docs/reference/engine/enums/EasingStyle
- https://create.roblox.com/docs/reference/engine/datatypes/TweenInfo
- https://devforum.roblox.com/t/full-release-adaptive-animation-use-one-animation-across-any-rig/4605672
- https://devforum.roblox.com/t/studio-beta-styling-transitions/4646870
