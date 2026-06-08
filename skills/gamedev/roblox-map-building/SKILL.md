---
name: roblox-map-building
description: "Creacion de mapas y mundos en Roblox Studio via MCP. Terrain API, estructura Workspace, iluminacion, organizacion y patrones de layout para juegos."
version: "1.0"
---

# Roblox Map Building via MCP

Guia para construir mapas completos en Roblox Studio usando las herramientas MCP (execute_luau, search_game_tree, inspect_instance) + generate_mesh para assets 3D.

Fuentes:
- https://create.roblox.com/docs/parts/terrain
- https://devforum.roblox.com/t/ruskis-tutorial-5-how-to-design-an-open-world-map/3554962
- https://devforum.roblox.com/t/ruskis-tutorial-1-how-to-design-a-map-layout/277853
- https://devforum.roblox.com/t/gameboys-workspace-organization-guide/2716314
- https://create.roblox.com/docs/reference/engine/classes/Terrain

---

## 1. Workflow de Creacion de Mapas

### Fase 0: Planificacion (ANTES de codear)
Responder estas preguntas antes de tocar Studio:

| Pregunta | Consideraciones |
|----------|----------------|
| Genero? | Simulador = zonas abiertas con spawns. FPS = fluidez, pocos dead ends. Obby = lineal vertical |
| Tema? | Define paleta de colores, materiales terrain, estilo de builds |
| Tamanio? | Mapa compacto con zonas unicas > mapa masivo repetitivo |
| Player count? | Define ancho de caminos, tamanio de areas |
| Progresion? | Zonas bloqueadas por nivel vs exploracion libre |

**Regla de Ruski:** "A compact map full of unique areas > a massive map that feels repetitive"

### Fase 1: Blockout (estructura base)
1. Crear carpetas en Workspace para organizacion
2. Colocar zonas con primitivas (Parts de colores) como placeholder
3. Definir POIs (Points of Interest) y distancias
4. Verificar con search_game_tree la estructura

### Fase 2: Terrain
1. Generar terreno base con Terrain API
2. Aplicar materiales por zona (biomas)
3. Agregar agua si aplica
4. Tunar vegetacion (Grass, LeafyGrass + Decoration)

### Fase 3: Builds y Props
1. Usar generate_mesh para assets unicos (edificios, rocas, arboles)
2. Usar search_creator_store para assets de la comunidad
3. Reciclar meshes con rotacion/escala variada

### Fase 4: Iluminacion y Atmosfera
1. Configurar Lighting
2. Agregar post-proceso (Bloom, ColorCorrection, SunRays)
3. Atmosphere para niebla y profundidad

### Fase 5: Optimizacion
1. StreamingEnabled para mapas grandes
2. Agrupar en Models con ModelStreamingMode
3. Verificar PartCount con search_game_tree

---

## 2. Estructura de Workspace

### Estructura recomendada
```
Workspace/
  Terrain/                    -- automatico de Roblox
  Map/                        -- todo el mapa estatico
    Zone1_StartArea/
      Ground/
      Buildings/
      Props/
      SpawnPoints/
    Zone2_Forest/
      Ground/
      Trees/
      Props/
    Zone3_Mountain/
      Ground/
      Rocks/
      Props/
  MapAssets/                  -- assets clonados por scripts
    Trees/
    Rocks/
    Buildings/
  Effects/                    -- particulas, effects visuales
  Camera/                     -- camerabins si aplica
  SpawnLocation               -- spawn principal
```

### Crear estructura via MCP
```lua
-- Crear estructura de carpetas del mapa
local mapFolders = {"Map", "MapAssets", "Effects"}
for _, name in ipairs(mapFolders) do
    local folder = Instance.new("Folder")
    folder.Name = name
    folder.Parent = game.Workspace
end

-- Crear zonas dentro de Map
local zones = {"Zone1_StartArea", "Zone2_Forest", "Zone3_Mountain"}
for _, zoneName in ipairs(zones) do
    local zone = Instance.new("Folder")
    zone.Name = zoneName
    zone.Parent = game.Workspace.Map
    -- Sub-carpetas por zona
    for _, sub in ipairs({"Ground", "Buildings", "Props", "SpawnPoints"}) do
        local f = Instance.new("Folder")
        f.Name = sub
        f.Parent = zone
    end
end
```

---

## 3. Terrain API (Verificado - docs oficiales)

### Metodos principales

#### FillBlock - Rellenar bloque rectangular
```lua
local terrain = game.Workspace.Terrain
terrain:FillBlock(
    CFrame.new(0, -10, 0),     -- posicion y orientacion
    Vector3.new(100, 4, 100),  -- tamanio en studs
    Enum.Material.Grass        -- material
)
```

#### FillBall - Rellenar esfera
```lua
terrain:FillBall(
    Vector3.new(0, 10, 0),  -- centro
    30,                      -- radio en studs
    Enum.Material.Rock       -- material
)
```

#### FillCylinder - Rellenar cilindro
```lua
terrain:FillCylinder(
    CFrame.new(0, 5, 0),     -- posicion y orientacion
    20,                       -- altura
    10,                       -- radio
    Enum.Material.Sand        -- material
)
```

#### FillWedge - Rellenar cuña/rampa
```lua
terrain:FillWedge(
    CFrame.new(0, 0, 0),     -- posicion
    Vector3.new(20, 10, 20), -- tamanio
    Enum.Material.Slate       -- material
)
```

#### FillRegion - Rellenar region completa
```lua
local region = Region3.new(
    Vector3.new(-50, -10, -50),  -- min
    Vector3.new(50, 0, 50)       -- max
)
terrain:FillRegion(region, 4, Enum.Material.Grass)  -- 4 = resolucion voxel
```

#### WriteVoxels - Control preciso por voxel
```lua
local region = Region3.new(
    Vector3.new(0, 0, 0),
    Vector3.new(20, 20, 20)
):ExpandToGrid(4)

local materials = {
    { -- X
        { -- Y
            Enum.Material.Grass,  -- Z
            Enum.Material.Grass,
        },
        {Enum.Material.Rock, Enum.Material.Rock},
    },
}
local occupancy = {
    {
        {1, 1},
        {1, 1},
    },
}

terrain:WriteVoxels(region, 4, materials, occupancy)
```

#### ReadVoxels - Leer terreno existente
```lua
local region = Region3.new(
    Vector3.new(0, 0, 0),
    Vector3.new(20, 20, 20)
):ExpandToGrid(4)

local materials, occupancy = terrain:ReadVoxels(region, 4)
local size = materials.Size
for x = 1, size.X do
    for y = 1, size.Y do
        for z = 1, size.Z do
            print(x, y, z, materials[x][y][z], occupancy[x][y][z])
        end
    end
end
```

#### ReplaceMaterial - Cambiar material en region
```lua
local region = Region3.new(Vector3.new(-50, 0, -50), Vector3.new(50, 20, 50))
terrain:ReplaceMaterial(region, 4, Enum.Material.Grass, Enum.Material.Sand)
```

### Materiales disponibles (23 + Air)
```
Piedra: Basalt, Cobblestone, Concrete, Glacier, Ice, Limestone, Rock, Salt, Sandstone, Slate
Tierra: Ground, Mud, Sand, Snow
Vegetacion: Grass, LeafyGrass
Urbano: Asphalt, Brick, Pavement, WoodPlanks
Lava: CrackedLava
Agua: Water
Vacio: Air
```

### Agua - Propiedades
```lua
local terrain = game.Workspace.Terrain
terrain.WaterColor = Color3.fromRGB(0, 100, 200)
terrain.WaterReflectance = 0.4
terrain.WaterTransparency = 0.3
terrain.WaterWaveSize = 0.3
terrain.WaterWaveSpeed = 30
```

### Vegetacion animada (pasto con movimiento)
```lua
local terrain = game.Workspace.Terrain
terrain.Decoration = true
terrain.GrassLength = 0.5  -- 0.1 a 1.0
```

### NOTA CRITICA sobre WriteVoxels/ReadVoxels
- La grilla voxel es de **4x4x4 studs** (no 1x1x1)
- Las coordenadas del Region3 deben alinearse a multiplos de 4
- Usar `Region3:ExpandToGrid(4)` para alinear automaticamente
- Los arrays son 1-indexed (no 0-indexed como en C)
- FillBlock/FillBall son MAS RAPIDOS que WriteVoxels para formas simples

---

## 4. Patrones de Layout por Tipo de Juego

### Simulador (Pet Simulator style)
```
Zona central: Spawn + Shop + Egg Area
Zona circular exterior: Areas de farmeo separadas por bioma
Progression: Zonas concentricas, inner=basico, outer=dificil
Distancia entre zonas: ~40 segundos de caminata
```

### Layout recomendado para Pet Simulator
```
                    [Zone3_Mountain]
                         |
            [Zone2_Forest]---[Zone2_Lake]
                  \        /
                   [Zone1_StartArea]
                  /        \
           [EggShop]    [CoinShop]

- Centro: Spawn point + NPCs
- Radio interior (~100 studs): Zona 1 (basico, Common pets)
- Radio medio (~250 studs): Zona 2 (Rare pets)
- Radio exterior (~400 studs): Zona 3 (Epic/Mythic pets)
```

### Obby / Platformer Vertical (Sky Dash style)
```
Spawn al nivel del mar (y=0)
Dificultad ascendente: fácil → kill bricks → moving platforms → gauntlet
Victory zone en la cima
```

**⚠ CONSTRAINTS DE JUMP PHYSICS (VERIFICADO EN SESIÓN REAL):**
- Roblox jump height: ~7.2 studs (con Humanoid.JumpPower default de 50)
- Roblox jump distance horizontal: ~12 studs (a velocidad de camata 16 studs/seg)
- **Vertical gap SEGURO (top plataforma A → bottom plataforma B): MÁXIMO 5 studs**
- **Horizontal gap SEGURO (borde a borde): MÁXIMO 12 studs**
- Si necesitas subir más de 5 studs, agregar plataforma intermedia
- Estos valores son conservadores — usar 3-4 studs vertical para saltos "fáciles"
- **NUNCA asumir cuánto salta el jugador — SIEMPRE calcular el gap real entre superficies**

Layout (con gaps realistas — máximo 3 studs vertical por paso):
```
y=62  [Section5_VictoryPeak]     — plataforma final + victory pad
y=44  [Section4_TheGauntlet]      — máxima dificultad, plataformas estrechas
y=32  [Section3_MovingPlatforms]  — plataformas en movimiento
y=17  [Section2_KillBrickAlley]   — kill bricks entre plataformas
y=5   [Section1_EasyJumps]        — saltos básicos, ascendente
y=0   [Section0_SpawnIsland]      — SpawnLocation + plataforma grass
```

### Moving Platforms (Anchored + Heartbeat pattern)

**⚠ CRITICAL: TweenService en Parts Anchored NO arrastra al jugador automáticamente.**
Se necesita un Heartbeat loop que aplique el delta de movimiento a los jugadores encima.

**⚠ CRITICAL: BodyPosition/BodyGyro están DEPRECATED y causan jitter/bugs.**
No usar BodyPosition para moving platforms — el comportamiento es impredecible.

**Solución verificada: Part Anchored + CFrame Tween + Heartbeat player tracking.**

```lua
-- Patrón VERIFICADO en Sky Dash (Issue 005):
-- 1. Crear Part Anchored, tweenear su CFrame
-- 2. Touched/TouchEnded para trackear jugadores arriba
-- 3. Heartbeat: calcular delta CFrame y aplicar a HumanoidRootPart de jugadores

-- DEBE ser un Script real en ServerScriptService (NO execute_luau)
-- execute_luau es ephemeral — los tweens desaparecen al dar Play

local platform = Instance.new("Part")
platform.Anchored = true
platform.CanCollide = true
platform.Size = Vector3.new(8, 1, 8)

-- Tween directo del CFrame (infinite loop, reverses)
local tweenInfo = TweenInfo.new(3.5, Enum.EasingStyle.Linear,
    Enum.EasingDirection.InOut, -1, true, 0.8)
local tween = TweenService:Create(platform, tweenInfo, {
    CFrame = CFrame.new(targetPos)
})
tween:Play()

-- Player tracking (en Heartbeat):
local lastCFrame = platform.CFrame
RunService.Heartbeat:Connect(function()
    local currentCFrame = platform.CFrame
    local delta = currentCFrame:ToObjectSpace(lastCFrame)
    for player, rootPart in pairs(playersOnPlatform) do
        -- Verify player still near platform surface
        local hDist = Vector3.new(
            rootPart.Position.X - currentCFrame.X, 0,
            rootPart.Position.Z - currentCFrame.Z).Magnitude
        if hDist < 6 then
            rootPart.CFrame = delta:ToObjectSpace(rootPart.CFrame)
        end
    end
    lastCFrame = currentCFrame
end)
```

**Pitfalls verificados:**
- BodyPosition/BodyGyro: deprecated, causa jitter, NO usar
- execute_luau tweens: desaparecen al dar Play, DEBE ser Script real
- Plataformas cada 10 studs: no dejan espacio para gaps significativos.
  Para moving platforms funcionen, el gap total debe ser >20 studs sin
  plataformas intermedias (solo entry + exit estáticas)
- SetNetworkOwner(nil) solo aplica a Parts Unanchored — irrelevante aquí
- TouchEnded puede disparar prematuramente — siempre verificar distancia
  en el Heartbeat antes de aplicar delta

**Patrón de construcción via execute_luau** (función helper — evita sparse tables):
```lua
-- Helper para crear plataformas — usar función directa, NO sparse tables
local function mkP(name, sx, sy, sz, px, py, pz, mat, r, g, b, parent)
    local p = Instance.new("Part")
    p.Name = name
    p.Size = Vector3.new(sx, sy, sz)
    p.CFrame = CFrame.new(px, py, pz)
    p.Anchored = true
    p.Material = mat
    p.Color = Color3.fromRGB(r, g, b)
    p.CanCollide = true
    p.CastShadow = true
    p.Parent = parent
    return p
end

-- Posiciones explícitas por plataforma (no random, no fórmulas)
-- VERIFICAR: cada gap vertical <= 5 studs, horizontal <= 12 studs
mkP("Platform_1", 30, 2, 30, 0, 1, 0, Enum.Material.Grass, 85, 170, 85, folder)
mkP("Platform_1", 8, 1, 8,  8, 5, 0, Enum.Material.Grass, 85, 170, 85, folder)
-- gap: top(1+1=2) → bot(5-0.5=4.5) = 2.5 studs vertical ✓
```

**⚠ Pitfall: Jump distances**. NUNCA poner platforms con gaps > 5 studs vertical.
El jump height default de Roblox es ~7.2 studs. Un gap de 18 studs entre secciones
es IMPOSIBLE de saltar. Siempre calcular: `gapY = bottomB - topA`. Si > 5, agregar
plataforma intermedia. Verificado con bug real (tuve que reconstruir todo el mapa).

**⚠ Pitfall: Sparse tables**. Usar `table.insert` + `ipairs`, NO
`t[1]=x` — las sparse numeric keys causan Folders duplicados y bugs
de iteración. Verificado con 3 intentos fallidos en sesión real.

**⚠ Pitfall: Folders duplicados**. Siempre hacer `Destroy()` del Map completo
antes de recrear. Si un `execute_luau` falla a medias, los folders creados antes
del error QUEDAN en Workspace. Verificar con `search_game_tree` post-creación.

**Patrón verificado — SIEMPRE seguir este orden:**
1. LEER posiciones reales de plataformas con `execute_luau` (Position.X/Y/Z)
2. CALCULAR puntos intermedios o posiciones relativas
3. CREAR elementos en las coordenadas calculadas
4. VERIFICAR espacialmente que cada elemento está donde debe estar
(ej: `dist < 15` studs de su plataforma de referencia)

Este patrón evitó el bug de KillBricks fuera de lugar (Issue 002) y posicionó
correctamente los Checkpoints (Issue 003) en el primer intento.

**⚠ Pitfall: FindFirstChild para elementos que DEBEN existir**. Si un Script depende
de que exista un Folder/Part en Workspace, usar `WaitForChild("name", timeout)` en vez
de `FindFirstChild`. FindFirstChild retorna nil silenciosamente si el elemento no existe
aún (race condition de carga). Verificado con setupKillBricks() que fallaba sin Map.

**Iluminación recomendada**: ClockTime=14-17.5, Atmosphere con Haze=2
para profundidad vertical, Bloom+ColorCorrection para polish.

### Regla de los 40 segundos
Los POIs (Points of Interest) deben estar a ~40 segundos de viaje entre si.
- A velocidad de caminata Roblox (~16 studs/seg): ~640 studs
- Corriendo (~24 studs/seg): ~960 studs

### Triangle Rule
Desde cualquier punto, el jugador debe ver al menos 3 POIs para elegir hacia donde ir.
Esto crea interes y evoca exploracion.

---

## 5. Iluminacion y Atmosfera

### Lighting basico (via execute_luau)
```lua
local lighting = game:GetService("Lighting")

-- Ambiente base
lighting.Ambient = Color3.fromRGB(127, 127, 127)
lighting.OutdoorAmbient = Color3.fromRGB(127, 127, 127)
lighting.Brightness = 2
lighting.ClockTime = 14  -- 2pm = dia soleado
lighting.GeographicLatitude = 41.77

-- Niebla
lighting.FogStart = 0
lighting.FogEnd = 1000
lighting.FogColor = Color3.fromRGB(192, 192, 192)
```

### Atmosphere (reemplaza Fog si existe)
```lua
local atmo = Instance.new("Atmosphere")
atmo.Parent = game:GetService("Lighting")
atmo.Density = 0.3           -- 0=claro, 1=niebla densa
atmo.Offset = 0.25           -- color horizon vs sky
atmo.Color = Color3.fromRGB(170, 190, 220)
atmo.Decay = Color3.fromRGB(120, 140, 200)
atmo.Glare = 0.5             -- brillo del sol
atmo.Haze = 2                -- distanciamiento atmosferico
```

### Post-proceso
```lua
local lighting = game:GetService("Lighting")

-- Bloom (resplandor)
local bloom = Instance.new("BloomEffect")
bloom.Intensity = 0.5
bloom.Size = 24
bloom.Threshold = 1.5
bloom.Parent = lighting

-- SunRays (rayos de sol)
local sunRays = Instance.new("SunRaysEffect")
sunRays.Intensity = 0.1
sunRays.Spread = 0.5
sunRays.Parent = lighting

-- ColorCorrection (ajuste color global)
local cc = Instance.new("ColorCorrectionEffect")
cc.Brightness = 0.05
cc.Contrast = 0.1
cc.Saturation = 0.1
cc.TintColor = Color3.fromRGB(255, 245, 230)  -- calido
cc.Parent = lighting
```

### Presets de iluminacion por tema
```
Fantasy:    Brightness=2.5, ClockTime=10, FogEnd=800, Tint calido, Bloom medio
Horror:     Brightness=0.8, ClockTime=21, FogEnd=200, Fog negro, Atmosphere densa
Sci-Fi:     Brightness=1.5, ClockTime=0,  Tint azul, Bloom alto, FogEnd=600
Simulator:  Brightness=2.0, ClockTime=14, FogEnd=1000, Sin fog, Bloom bajo
Noche:      Brightness=0.5, ClockTime=22, OutdoorAmbient dark, FogEnd=300
```

---

## 6. Generacion de Assets con MCP

### generate_mesh - Crear mesh 3D con textura
Usar cuando necesitas un asset unico (edificio, roca, arbol, decoracion).

```
Prompt ejemplo: "cartoon style low poly tree with round green foliage and brown trunk"
Size: {5, 8, 5}  -- X, Y, Z en studs
MaxTriangles: 1000-5000 para props, 5000-15000 para buildings
```

Buenos prompts para mapas:
```
- "low poly cartoon house with chimney colorful" (edificio)
- "round cartoon rock boulder grey" (roca)
- "wooden fence segment low poly" (cerca)
- "cartoon style wooden sign post" (senal)
- "low poly cartoon treasure chest open" (cofre)
- "cartoon style egg nest with straw" (nido de huevos)
- "stone bridge arch low poly" (puente)
- "cartoon wooden cart with wheels" (carreta)
- "low poly cartoon crystal cluster glowing purple" (cristal)
- "cartoon style castle tower round" (torre)
```

### search_creator_store - Assets de la comunidad
Buscar por tipo: arboles, rocas, edificios, muebles, etc.
Usar insert_from_creator_store para colocarlos.

### Reciclaje de assets (optimizacion)
- Rotar meshes: CFrame.Angles(0, math.rad(45), 0)
- Escalar: Size * 0.8 o Size * 1.3
- Mismo arbol en 3 orientaciones = parece 3 arboles distintos
- Menos unique AssetIds = menos memoria

---

## 7. Colocacion de Objetos

### Colocar un Part basico
```lua
local part = Instance.new("Part")
part.Name = "Ground"
part.Size = Vector3.new(100, 1, 100)
part.Position = Vector3.new(0, -0.5, 0)
part.Anchored = true
part.Material = Enum.Material.Grass
part.Color = Color3.fromRGB(85, 170, 85)
part.Parent = game.Workspace.Map.Zone1_StartArea.Ground
```

### Colocar un SpawnPoint
```lua
local spawn = Instance.new("SpawnLocation")
spawn.Name = "Zone1_Spawn"
spawn.Size = Vector3.new(6, 1, 6)
spawn.Position = Vector3.new(0, 0.5, 0)
spawn.Anchored = true
spawn.Parent = game.Workspace.Map.Zone1_StartArea.SpawnPoints
```

### Colocar un Model (despues de generate_mesh)
```lua
-- El mesh se genera en Workspace, moverlo a la zona correcta
-- Verificar con search_game_tree donde se creo
-- Luego usar execute_luau para reposicionar:
local mesh = game.Workspace:FindFirstChild("GeneratedMesh")
if mesh then
    mesh.Name = "Tree_01"
    mesh:PivotTo(CFrame.new(50, 0, 30))
    mesh.Parent = game.Workspace.Map.Zone2_Forest.Trees
end
```

---

## 8. Generacion Procedural de Terrain con Ruido

### Terreno basico con variacion de altura
```lua
local terrain = game.Workspace.Terrain
local mapSize = 200  -- studs
local heightScale = 30

-- Funcion de ruido simple (usando math.noise)
for x = -mapSize/2, mapSize/2, 4 do
    for z = -mapSize/2, mapSize/2, 4 do
        local noise = math.noise(x / 80, z / 80)  -- escala del ruido
        local height = math.floor(noise * heightScale)

        local material = Enum.Material.Grass
        if height < -5 then
            material = Enum.Material.Sand
        elseif height > 15 then
            material = Enum.Material.Rock
        end

        terrain:FillBlock(
            CFrame.new(x, height, z),
            Vector3.new(4, 4, 4),
            material
        )
    end
end
```

### Agregar agua a nivel del mar
```lua
local terrain = game.Workspace.Terrain
local waterLevel = -5
local mapHalf = 100

terrain:FillBlock(
    CFrame.new(0, waterLevel, 0),
    Vector3.new(mapHalf * 2, 4, mapHalf * 2),
    Enum.Material.Water
)
```

---

## 9. Optimizacion de Mapas

### StreamingEnabled (mapas grandes)
```lua
-- En execute_luau (solo funciona si no esta en Play mode)
game.Workspace.StreamingEnabled = true
game.Workspace.StreamingMinRadius = 64     -- studs minimos
game.Workspace.StreamingTargetRadius = 256  -- studs target
```

### Mesh Streaming (Opt-in Phase, Abril 2026)

Sistema que maneja LOD y memoria de meshes automaticamente basado en importancia de escena.

```lua
-- Habilitar en Workspace
game.Workspace.MeshStreamingAndImprovedLoDs = Enum.PropertyStatus.Enabled
```

- Genera LODs en cloud automaticamente
- Stream-in meshes detallados solo cuando estan cerca
- Default behavior en ~Julio 2026
- Recomendado habilitar AHORA para prepararse

Fuente: https://devforum.roblox.com/t/introducing-mesh-streaming-and-improved-cloud-lods-in-published-experiences-opt-in-phase/4601232

### Limits recomendados
```
Parts totales: < 5000 para buen rendimiento
Parts con collission: < 2000
Meshes unicos: < 500
Terrain voxels: robusto, pero evitar regiones de +1000 studs cubicos de WriteVoxels
Decals/Textures: < 200
PointLights: < 50
Particles emitters: < 30
```

### Tips de optimizacion
- Anchored = true en todo lo estatico (obligatorio)
- CanCollide = false en decoracion que no bloquea (arboles lejanos, techo)
- CastShadow = false en partes pequenas o lejanas
- Usar Models con PrimaryPart para agrupar
- Reciclar AssetIds (misma roca rotada = 2 rocas visuales, 1 asset)

---

## 10. Checklist de Verificacion via MCP

Despues de construir, verificar con:

```
[ ] search_game_tree(path="Workspace") — estructura correcta de carpetas
[ ] search_game_tree(instance_type="BasePart") — contar parts totales
[ ] search_game_tree(instance_type="SpawnLocation") — spawns colocados
[ ] inspect_instance(path="Workspace.Terrain") — terreno existe
[ ] execute_luau — contar parts: #game.Workspace:GetDescendants()
[ ] screen_capture — verificar visualmente el mapa
[ ] start_stop_play + get_console_output — errores en runtime
```

### Contar parts por tipo
```lua
local parts = 0
local meshes = 0
for _, obj in ipairs(game.Workspace:GetDescendants()) do
    if obj:IsA("BasePart") then parts = parts + 1 end
    if obj:IsA("MeshPart") then meshes = meshes + 1 end
end
print("Parts:", parts, "| Meshes:", meshes)
```

---

## 11. Anti-Patterns de Mapas

1. NO crear mapas sin planificacion previa (sketch/zonas primero)
2. NO dejar Parts sin Anchored (flotan o caen en runtime)
3. NO usar Parts individuales para suelo (usar Terrain)
4. NO hacer mapas simetricos perfectos (artificial, aburrido)
5. NO poner todo en la raiz de Workspace (usar carpetas)
6. NO crear dead ends sin proposito (frustrante para jugadores)
7. NO olvidar SpawnLocations (sin ellos players spawn random)
8. NO exceder 5000 parts sin StreamingEnabled
9. NO usar FogEnd < 100 sin proposito (corta visibilidad demasiado)
10. NO dejar Boundary invisible (si no se puede entrar, que no parezca que si)

---

## Fuentes

- https://create.roblox.com/docs/parts/terrain
- https://create.roblox.com/docs/reference/engine/classes/Terrain
- https://devforum.roblox.com/t/ruskis-tutorial-5-how-to-design-an-open-world-map/3554962
- https://devforum.roblox.com/t/ruskis-tutorial-1-how-to-design-a-map-layout/277853
- https://devforum.roblox.com/t/gameboys-workspace-organization-guide/2716314
- https://create.roblox.com/docs/reference/engine/classes/Atmosphere
