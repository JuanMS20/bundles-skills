---
name: roblox-visual-design
description: "Diseno visual Roblox: materiales, colores, iluminacion, coherencia estetica. Usa cuando el juego 'se ve raro', las texturas no convencen, o necesitas que las plataformas/edificios/props luzcan profesionales. Cubre SmoothPlastic low-poly, PBR realista, MaterialVariant, paletas por tema, y reglas de combinacion material+color."
version: "1.0"
---

# Roblox Visual Design — Materiales, Colores y Coherencia

Reglas y patrones para que tu juego se vea profesional, no amateur. Resuelve el "se ve raro" que sientes cuando Platform + Material + Color no combinan.

Fuentes:
- https://devforum.roblox.com/t/what-material-and-colors-should-i-use-to-create-low-poly-models/905822
- https://devforum.roblox.com/t/how-to-create-a-low-poly-lookvibe-using-roblox-studio-blocks/278566
- https://devforum.roblox.com/t/guide-to-texturesmaterials/1658926
- https://devforum.roblox.com/t/full-in-depth-tutorial-on-how-to-use-pbr-materials-to-create-realistic-objects-in-roblox/1574778
- https://devforum.roblox.com/t/full-release-surfaceappearance-tinting/3129960
- https://create.roblox.com/docs/parts/materials
- https://roblox.fandom.com/wiki/Class:MaterialVariant

---

## 1. PRIMERO: Elige tu ESTILO VISUAL

Antes de tocar materiales, decidir el estilo. Cada estilo tiene reglas distintas.

| Estilo | Material principal | Iluminacion | Ejemplos Roblox |
|--------|-------------------|-------------|-----------------|
| **Low-poly cartoon** | SmoothPlastic | Brightness alta, colores vibrantes | Pet Simulator, Blox Fruits |
| **Stylized semi-real** | Plastico + PBR selectivo | Future lighting, Atmosphere | Deepwoken, Arcane Odyssey |
| **Realista** | SurfaceAppearance PBR | Future + HDR, ColorCorrection | Veil of the Unknown, FRISING |
| **Retro/blocky** | Plastic, Neon | Flat, ClockTime fijo | Classic Roblox,obbys basicos |
| **Dark/horror** | Slate, Concrete, Neon accents | Brillo bajo, niebla densa | Doors, Apeirophobia |

**Regla:** NO mezclar estilos. Si eliges low-poly, TODO es SmoothPlastic. Si eliges realista, TODO tiene PBR. Mezclar es el #1 causa de "se ve raro".

---

## 2. LOW-POLY CARTOON (El mas comun en Roblox)

### Regla fundamental
> SmoothPlastic + colores vibrantes + buena iluminacion = profesional.
> Cualquier otro material en low-poly = se ve "raro" o "gratis".

### Paletas de color por tema

**Nature / Forest:**
```
Pasto:       SmoothPlastic, Color3.fromRGB(85, 170, 85)   o (120, 200, 80)
Tierra:      SmoothPlastic, Color3.fromRGB(139, 90, 43)   o (160, 110, 60)
Troncos:     SmoothPlastic, Color3.fromRGB(101, 67, 33)   o (120, 80, 40)
Follaje:     SmoothPlastic, Color3.fromRGB(34, 139, 34)   o (50, 160, 50)
Cielo:       SmoothPlastic, Color3.fromRGB(135, 206, 235)
Agua:        SmoothPlastic, Color3.fromRGB(64, 164, 223)
Flores:      SmoothPlastic, Color3.fromRGB(255, 100, 150) / (255, 220, 50)
Rocas:       SmoothPlastic, Color3.fromRGB(140, 140, 140) o (170, 160, 150)
```

**Sky / Obby / Platforms:**
```
Plataforma:  SmoothPlastic, Color3.fromRGB(100, 200, 255)  (azul cielo)
Acento:      SmoothPlastic, Color3.fromRGB(255, 220, 50)   (dorado)
Killbrick:   SmoothPlastic, Color3.fromRGB(220, 50, 50)    (rojo)
Checkpoint:  Neon,         Color3.fromRGB(50, 255, 50)     (verde neon)
Spawn:       SmoothPlastic, Color3.fromRGB(120, 200, 80)   (verde pasto)
Background:  SmoothPlastic, Color3.fromRGB(200, 230, 255)  (azul claro)
```

**Sci-fi / Futurista:**
```
Metal:       SmoothPlastic, Color3.fromRGB(80, 80, 90)     (gris oscuro)
Panel:       SmoothPlastic, Color3.fromRGB(40, 40, 50)     (casi negro)
Acento:      Neon,         Color3.fromRGB(0, 200, 255)     (cyan neon)
Piso:        SmoothPlastic, Color3.fromRGB(50, 55, 65)
Energia:     Neon,         Color3.fromRGB(100, 50, 255)    (violeta)
Lineas:      Neon,         Color3.fromRGB(0, 255, 150)     (verde neon)
```

**Fantasy / Medieval:**
```
Piedra:      SmoothPlastic, Color3.fromRGB(160, 150, 140)
Madera:      SmoothPlastic, Color3.fromRGB(139, 90, 43)
Techo:      SmoothPlastic, Color3.fromRGB(120, 50, 30)
Dorado:      Neon,         Color3.fromRGB(255, 200, 50)
Magia:       Neon,         Color3.fromRGB(170, 85, 255)    (morado)
Bandera:     SmoothPlastic, Color3.fromRGB(180, 30, 30)    (rojo)
```

### Cuando usar Neon (unico material例外 en low-poly)
- Ventanas/vidrio: Neon + Color3.fromRGB(200, 230, 255) + Transparency 0.3
- Cristales magicos: Neon + color vibrante + Transparency 0.2
- Checkpoints/marcadores: Neon para que "brillen" y destaquen
- Ojos de personajes/monstruos: Neon blanco o rojo
- Lineas de energia/sci-fi: Neon como acento sobre SmoothPlastic oscuro

### Anti-patterns low-poly
- NO usar Grass, Sand, Rock, Wood materials en low-poly → se ven "sucios" al lado de SmoothPlastic
- NO usar Reflectance > 0 en low-poly → rompe el estilo flat
- NO usar transparencias parciales en plataformas (confuso para el jugador)
- NO mezclar Plastic (con textura) con SmoothPlastic → inconsistencia visual

---

## 3. PBR REALISTA (SurfaceAppearance)

Para juegos que quieren verse "reales". Requiere Future lighting.

### Requisitos
1. Lighting.Technology = `Future` (obligatorio para PBR)
2. MeshParts (no Parts — SurfaceAppearance solo funciona en MeshParts)
3. Publicar el juego (necesario para Asset Manager)

### SurfaceAppearance — mapa de propiedades

```lua
local sa = Instance.new("SurfaceAppearance")
sa.ColorMap = "rbxassetid://..."      -- textura base (obligatorio)
sa.NormalMap = "rbxassetid://..."     -- relieve/detalle (recomendado)
sa.RoughnessMap = "rbxassetid://..."  -- suavidad vs aspereza
sa.MetalnessMap = "rbxassetid://..."  -- que partes son metal
sa.Color = Color3.fromRGB(255,255,255) -- tint (full release, multiplicador)
sa.AlphaMode = Enum.AlphaMode.Overlay -- transparencia
sa.Parent = meshPart
```

### Tinting (Full Release)
```lua
-- Un solo ColorMap, multiples colores via tint
sa.Color = Color3.fromRGB(255, 200, 150)  -- multiplica con ColorMap
-- Tip: crear ColorMap en gris claro cerca de blanco = maxima flexibilidad de tint
```

### Resoluciones (maximo 1K en Roblox)
```
Props cercanos:   1024x1024 (1K)
Props medios:      512x512
Props lejanos:     256x256
UI/superficie:    1024x1024
```

### VRAM budget
- 1 SurfaceAppearance (4 textures 1K) = ~12MB VRAM
- Budget seguro: < 200MB total (aprox 15-16 assets PBR)
- Compartir ColorMap entre variantes con tint ahorra VRAM

### Sources de textures PBR gratuitas
- PolyHaven.com (CC0, 1K download)
- AmbientCG.com (CC0)
- ShareTextures.com (gratis)

### Anti-patterns PBR
- NO subir textures > 1K → Roblox las rechaza o crashea
- NO usar JPEG → siempre PNG (JPEG pierde datos en normal/roughness maps)
- NO usar PBR con ShadowMap lighting → Future es obligatorio
- NO poner SurfaceAppearance en Parts normales → solo MeshParts
- SurfaceAppearance.ColorMap NO se puede modificar en runtime (limitacion de Roblox)
- SurfaceAppearance.Color (tint) SI se puede modificar en runtime

---

## 4. MATERIALVARIANT (Materiales Custom via MCP)

### generate_material (MCP tool)

```python
# Uso via MCP:
generate_material(
    baseMaterial="Plastic",       # Material base del enum
    materialPattern="Regular",    # Regular u Organic
    materialId="MyGrass01",       # ID unico
    materialDescription="Bright green grass with subtle variation"
)
# Retorna: { baseMaterial, name }
# Para aplicar: part.Material = baseMaterial, part.MaterialVariant = name
```

### Aplicar MaterialVariant via Luau
```lua
-- Despues de generate_material retorna { baseMaterial="Plastic", name="MyGrass01" }
local part = Instance.new("Part")
part.Material = Enum.Material.Plastic     -- DEBE ser el baseMaterial
part.MaterialVariant = "MyGrass01"        -- nombre retornado por generate_material
part.Color = Color3.fromRGB(85, 170, 85)
part.Parent = workspace
```

### Patrones de uso
- `materialPattern="Regular"`: edificios, suelos, paredes, objetos geometricos
- `materialPattern="Organic"`: terreno, vegetacion, rocas, agua, nieve
- La descripcion (materialDescription) define la apariencia: ser especifico

### Descripciones efectivas para generate_material
```
MAL:  "grass"                                    → generico, resultado impredecible
BIEN: "bright cartoon grass with light streaks"   → especifico, mejor resultado
BIEN: "worn grey cobblestone with moss between"   → detallado
BIEN: "smooth white marble with subtle veins"     → preciso
BIEN: "red brick wall with white mortar lines"    → descriptivo
```

---

## 5. ILUMINACION — El multiplicador visual mas importante

Materiales perfectos con mala iluminacion = se ve mal. Iluminacion correcta + materiales simples = se ve bien.

### Iluminacion por estilo

**Low-poly cartoon:**
```lua
-- Setup rapido via execute_luau
local lighting = game:GetService("Lighting")
lighting.Brightness = 2.5
lighting.ClockTime = 14
lighting.Ambient = Color3.fromRGB(150, 150, 150)
lighting.OutdoorAmbient = Color3.fromRGB(150, 150, 150)
lighting.GlobalShadows = true

-- Atmosphere para depth
local atmo = Instance.new("Atmosphere")
atmo.Density = 0.25
atmo.Haze = 1.5
atmo.Parent = lighting

-- ColorCorrection para vibrancia
local cc = Instance.new("ColorCorrectionEffect")
cc.Saturation = 0.15          -- mas vibrante
cc.Brightness = 0.05
cc.Contrast = 0.1
cc.TintColor = Color3.fromRGB(255, 248, 235)  -- calido
cc.Parent = lighting

-- Bloom para glow suave
local bloom = Instance.new("BloomEffect")
bloom.Intensity = 0.4
bloom.Size = 20
bloom.Threshold = 1.8
bloom.Parent = lighting
```

**Realista PBR:**
```lua
lighting.Brightness = 3
lighting.ClockTime = 15.5
lighting.Technology = Enum.Technology.Future  -- OBLIGATORIO
lighting.Ambient = Color3.fromRGB(80, 80, 80)
lighting.EnvironmentDiffuseScale = 0.5
lighting.EnvironmentSpecularScale = 0.8
-- Atmosphere density bajo (0.15), Haze 0.5
-- Sin ColorCorrection al inicio, ajustar al gusto
```

**Dark / Horror:**
```lua
lighting.Brightness = 0.5
lighting.ClockTime = 21
lighting.Ambient = Color3.fromRGB(30, 30, 40)
lighting.OutdoorAmbient = Color3.fromRGB(20, 20, 30)
lighting.FogEnd = 300
lighting.FogColor = Color3.fromRGB(15, 15, 20)

local atmo = Instance.new("Atmosphere")
atmo.Density = 0.6
atmo.Haze = 5
atmo.Parent = lighting
```

### Regla: Iluminacion primero, materiales despues
Si cambias materiales y nada mejora, el problema es la iluminacion, no los materiales. Verificar:
1. Brightness (2-3 para cartoon, 3+ para PBR)
2. ClockTime (14 para dia, 21 para noche)
3. Atmosphere (sin atmosphere = "plano", con = profundidad)
4. ColorCorrection (Saturation +0.1 a +0.2 = colores mas vivos)

---

## 6. REGLAS DE COHERENCIA VISUAL

### Regla 1: Un material dominante
```
Low-poly:    90% SmoothPlastic + 10% Neon (acentos)
Realista:    80% SurfaceAppearance PBR + 20% materiales base Roblox
Retro:       100% Plastic + colores solidos
```

### Regla 2: Maximo 3-5 colores por zona
```
Zona forest:   verde pasto, marron tronco, verde oscuro follaje, azul cielo
Zona desert:   arena, naranja acento, marron rocas
Zona ice:      blanco, azul claro, cyan acento
```
Mas de 5 colores = visual noise, se ve desordenado.

### Regla 3: Coherencia entre plataformas
Si las plataformas son el elemento principal del juego:
- MISMO material para todas (SmoothPlastic para low-poly)
- Variacion de COLOR, no de material (azul claro, azul medio, azul oscuro)
- Bordes consistentes: mismo estilo de edge en todas
- Tamano consistente: todas las plataformas mismo "peso visual"

### Regla 4: Jerarquia visual
```
Neon / brillante  → "importante, mirame" (checkpoints, items, peligros)
SmoothPlastic     → "normal, fondo" (plataformas, paredes, suelo)
Oscuro            → "decorativo, no interactivo" (fondo, cielo)
```

### Regla 5: CastShadow selectivo
```lua
-- SOLO en elementos donde las sombras agregan valor
part.CastShadow = true   -- plataformas principales, edificios
part.CastShadow = false  -- props chicos, decoracion lejana, particulas
```
Sombras en TODO = ruido visual y performance hit.

---

## 7. ANTI-PATTERNS (Lo que hace que "se vea rara")

| Anti-pattern | Por que se ve mal | Fix |
|---|---|---|
| Mezclar Grass material + SmoothPlastic en mismo mapa | Textura vs flat = clash | Elegir UNO. Low-poly = SmoothPlastic siempre |
| Plataformas de colores random sin paleta | Visual noise, amateur | Definir 3-5 colores, rotar entre ellos |
| Material Grass/Wood en plataformas de obby | Se ve "sucio" e inconsistente | SmoothPlastic + color solido |
| Sin iluminacion (default Studio) | Plano, sin profundidad | Minimo: Brightness=2, ClockTime=14, Atmosphere |
| Neon en todo | Distractante, pierde impacto | Neon SOLO para acentos (< 10% de la escena) |
| Reflectance > 0 en estilo low-poly | Rompe estetica flat | Reflectance = 0 siempre en low-poly |
| Transparency parcial en plataformas | Confusion para el jugador | Solidas o completamente invisibles |
| Colores pastel desaturados en juegos de accion | Sin energia | Subir saturation +0.15 en ColorCorrection |
| Cada plataforma material distinto | Sin coherencia | Mismo material, variar solo color |
| Sin post-proceso (bloom, CC) | "Se ve a Studio default" | Bloom bajo + ColorCorrection = polish inmediato |

---

## 8. PATRONES DE CREACION VIA MCP

### Plataformas de obby (low-poly cartoon)
```lua
local function mkPlatform(name, size, pos, color)
    local p = Instance.new("Part")
    p.Name = name
    p.Size = size
    p.CFrame = CFrame.new(pos)
    p.Anchored = true
    p.Material = Enum.Material.SmoothPlastic  -- SIEMPRE en low-poly
    p.Color = color
    p.CastShadow = true
    p.CanCollide = true
    p.Reflectance = 0        -- 0 en low-poly
    p.TopSurface = Enum.SurfaceType.Smooth
    p.BottomSurface = Enum.SurfaceType.Smooth
    p.Parent = workspace.Map
    return p
end

-- Rotar entre 3-4 colores de la paleta
local platformColors = {
    Color3.fromRGB(100, 200, 255),  -- azul cielo
    Color3.fromRGB(130, 210, 255),  -- azul claro
    Color3.fromRGB(80, 190, 240),   -- azul medio
    Color3.fromRGB(110, 205, 250),  -- azul suave
}

mkPlatform("P1", Vector3.new(8,1,8), Vector3.new(0,1,0), platformColors[1])
mkPlatform("P2", Vector3.new(8,1,8), Vector3.new(8,5,0), platformColors[2])
```

### Edificio estilizado (low-poly)
```lua
-- Pared
local wall = Instance.new("Part")
wall.Material = Enum.Material.SmoothPlastic
wall.Color = Color3.fromRGB(230, 220, 200)  -- crema

-- Techo
local roof = Instance.new("Part")
roof.Material = Enum.Material.SmoothPlastic
roof.Color = Color3.fromRGB(180, 60, 40)    -- terracota

-- Ventanas (unico uso de Neon en low-poly)
local window = Instance.new("Part")
window.Material = Enum.Material.Neon
window.Color = Color3.fromRGB(200, 230, 255)
window.Transparency = 0.15
```

### Aplicar generate_material + crear parte
```lua
-- 1. Llamar generate_material via MCP:
--    generate_material(baseMaterial="Plastic", materialPattern="Organic",
--                      materialId="MossyRock", materialDescription="grey rock with green moss patches")
-- 2. Aplicar resultado:
local rock = Instance.new("Part")
rock.Material = Enum.Material.Plastic     -- baseMaterial retornado
rock.MaterialVariant = "MossyRock"        -- name retornado
rock.Color = Color3.fromRGB(130, 130, 120)
rock.Parent = workspace.Map
```

---

## 9. CHECKLIST DE VERIFICACION VISUAL

Despues de construir, verificar:

```
[ ] Todas las plataformas usan el MISMO material (ej: SmoothPlastic)
[ ] Colores rotan dentro de una paleta de 3-5 colores definidos
[ ] Neon solo en acentos (checkpoints, items, peligros) — < 10% de la escena
[ ] Reflectance = 0 en todo (excepto estilo realista)
[ ] Iluminacion configurada: Brightness, ClockTime, Atmosphere, ColorCorrection, Bloom
[ ] CastShadow true solo en elementos principales
[ ] Sin mezcla de estilos (todo low-poly O todo PBR, no ambos)
[ ] Probar con screen_capture — verificar que no hay "visual noise"
[ ] Start_stop_play + verificar que la iluminacion se ve bien en runtime
[ ] Comparar con screenshots de juegos profesionales del mismo genero
```

---

## Fuentes

- https://devforum.roblox.com/t/what-material-and-colors-should-i-use-to-create-low-poly-models/905822
- https://devforum.roblox.com/t/how-to-create-a-low-poly-lookvibe-using-roblox-studio-blocks/278566
- https://devforum.roblox.com/t/guide-to-texturesmaterials/1658926
- https://devforum.roblox.com/t/full-in-depth-tutorial-on-how-to-use-pbr-materials-to-create-realistic-objects-in-roblox/1574778
- https://devforum.roblox.com/t/full-release-surfaceappearance-tinting/3129960
- https://create.roblox.com/docs/parts/materials
- https://roblox.fandom.com/wiki/Class:MaterialVariant
- https://roblox.fandom.com/wiki/Class:SurfaceAppearance
