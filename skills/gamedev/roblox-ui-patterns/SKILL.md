---
name: roblox-ui-patterns
description: "Convenciones UI Roblox - tamanios, espaciados, colores, layouts y patrones. Valores reales extraidos de guias oficiales."
version: "1.0"
---

# Roblox UI Design Patterns

Convenciones extraidas de:
- Guia oficial Roblox "UI Design Starter Guide" (devforum.roblox.com/t/ui-design-starter-guide/53461)
- Guia oficial Roblox "Designing UI - Tips and Best Practices" (devforum.roblox.com/t/designing-ui-tips-and-best-practices/3074034)
- Comunidad Roblox DevForum

## REGLA DE ORO

**Usar Scale como primario, Offset solo para espaciados fijos pequenos.** Los juegos top (Pet Simulator 99, Blox Fruits, Brookhaven) usan Scale + UIAspectRatioConstraint para responsive.

---

## 1. Sizing - Scale vs Offset

| Elemento | Estrategia | Ejemplo UDim2 |
|----------|-----------|---------------|
| Paneles principales | Scale | {0.4, 0}, {0.6, 0} |
| Botones | Scale + AspectConstraint | {0.15, 0}, {0.08, 0} + UIAspectRatioConstraint(1.8) |
| Padding/bordes | Offset pequeno | {0, 8} a {0, 16} |
| Texto tamanio | FontSize fijo | TextSize = 14 a 18 labels, 20+ titulos |
| Corner radius | Scale o Offset | UDim.new(0, 8) para botones, UDim.new(0, 12) paneles |

### SizeConstraint (propiedad clave)
- RelativeXX: ambos ejes escalan al ancho (barras horizontales)
- RelativeYY: ambos ejes escalan al alto (sidebars, ScrollingFrames verticales)
- RelativeXY (default): normal

---

## 2. Layouts y Espaciado

### Valores tipicos de Padding (UIPadding)
```
Top/Bottom: 8-16px offset
Left/Right: 8-16px offset
```

### UIGridLayout (Inventarios, grids de items)
```
CellSize = UDim2.new(0.9, 0, 0.9, 0)
CellPadding = UDim2.new(0.02, 0, 0.02, 0)
SortOrder = Enum.SortOrder.LayoutOrder
```

### UIListLayout (Botones verticales, menus)
```
Padding = UDim.new(0, 6)
SortOrder = Enum.SortOrder.LayoutOrder
HorizontalAlignment = Center
```

### Espaciado estandar entre elementos
- Botones en misma fila: 4-8px gap
- Secciones de UI: 12-16px separacion
- Margen del borde de pantalla: 10-20px (via Scale: 0.02 a 0.05)
- Top bar obstruction: 58px offset (UI oficial de Roblox tapa zona superior)

---

## 3. AnchorPoint + Position

| Posicion | AnchorPoint | Position |
|----------|-------------|----------|
| Centro exacto | {0.5, 0.5} | {0.5, 0}, {0.5, 0} |
| Abajo-centro | {0.5, 1} | {0.5, 0}, {1, 0} |
| Top-derecha | {1, 0} | {1, 0}, {0, 0} |
| Bottom-derecha | {1, 1} | {1, 0}, {1, 0} |
| Top-izquierda | {0, 0} | {0, 0}, {0, 0} |

**Tip:** Siempre usar Scale para Position + AnchorPoint. Nunca Offset para posicion.

---

## 4. Colores y Temas

### Dark Theme (estandar en juegos top)
```
Background panel:    Color3.fromRGB(30, 30, 30)   -- #1E1E1E
Panel inner:         Color3.fromRGB(40, 40, 45)    -- #28282D
Button normal:       Color3.fromRGB(55, 55, 65)    -- #373741
Button hover:        Color3.fromRGB(70, 70, 85)    -- #464655
Button active:       Color3.fromRGB(80, 130, 230)  -- #5082E6 (azul accion)
Button danger:       Color3.fromRGB(220, 70, 70)   -- #DC4646
Button success:      Color3.fromRGB(80, 180, 80)   -- #50B450
Text primary:        Color3.fromRGB(255, 255, 255) -- blanco
Text secondary:      Color3.fromRGB(180, 180, 180) -- gris claro
Border subtle:       Color3.fromRGB(60, 60, 70)    -- #3C3C46
```

### Tier/Rarity Colors (convencion coleccionables)
```
Common:    Color3.fromRGB(180, 180, 180)  -- gris
Uncommon:  Color3.fromRGB(85, 255, 85)    -- verde
Rare:      Color3.fromRGB(85, 170, 255)   -- azul
Epic:      Color3.fromRGB(170, 85, 255)   -- morado
Legendary: Color3.fromRGB(255, 170, 0)    -- naranja/dorado
Mythic:    Color3.fromRGB(255, 85, 85)    -- rojo
Secret:    Color3.fromRGB(255, 255, 85)   -- amarillo brillante
Exclusive: Color3.fromRGB(255, 200, 50)   -- dorado
```

---

## 5. UICorner (Bordes Redondeados)

```
Botones:    CornerRadius = UDim.new(0, 8)   -- 8px (suave)
Paneles:    CornerRadius = UDim.new(0, 12)  -- 12px (mas redondeado)
Cards/items: CornerRadius = UDim.new(0, 6)  -- 6px (sutil)
Pills/tags: CornerRadius = UDim.new(1, 0)   -- Fully round
```

**Importante:** Si usas Scale para CornerRadius, usa UDim.new(0.15, 0) a UDim.new(0.25, 0).

---

## 6. Tipografia

### Fonts recomendados
```
Titulos/Headers:    Enum.Font.GothamBold o Enum.Font.GothamBlack
Body/Labels:        Enum.Font.Gotham o Enum.Font.GothamMedium
Botones:            Enum.Font.GothamBold
Numeros/Stats:      Enum.Font.GothamBold
Small text:         Enum.Font.Gotham
```

### Tamanios
```
Titulo de panel:    TextSize = 20-24
Titulo de seccion:  TextSize = 16-18
Body text:          TextSize = 14
Small labels:       TextSize = 12
Button text:        TextSize = 14-16
```

### TextStroke (borde de texto)
```
TextStrokeColor3 = Color3.fromRGB(0, 0, 0)
TextStrokeTransparency = 0.5  -- sombra sutil
```

**Evitar** TextScaled en botones (tamanios inconsistentes). Mejor fijar TextSize.

---

## 7. Patrones de Layout por Componente

### HUD Bottom (botones de accion)
```
Container: AnchorPoint={0.5,1}, Position={0.5,0},{1,0}, Size={0.5,0},{0.12,0}
Layout: UIListLayout(Horizontal, Padding=4px)
Botones: Size={0.3,0},{0.9,0} dentro del container
ZIndex: DisplayOrder alto para estar encima
```

### Panel lateral (Inventario, Shop)
```
Container: Size={0.35,0},{0.75,0}, Position esquina, AnchorPoint correspondiente
Header: Size={1,0},{0.08,0} con titulo
Body: ScrollingFrame con UIGridLayout
Close button: AnchorPoint={1,0}, Position={1,0},{0,0}
Background: semi-transparente Color3.fromRGB(0,0,0), BackgroundTransparency=0.3
```

### Modal/Popup
```
Backdrop: Size={1,0},{1,0}, BackgroundTransparency=0.5, ZIndex alto
Panel: AnchorPoint={0.5,0.5}, Position={0.5,0},{0.5,0}, Size={0.5,0},{0.5,0}
Header + Body + Footer layout vertical con UIListLayout
```

### Equip Slots (barra de pets equipados)
```
Container: Size={0.3,0},{0.08,0}, AnchorPoint={0.5,0}, Position={0.5,0},{0.02,0}
Slots horizontales: UIListLayout(Horizontal, Padding=4px)
Cada slot: UIAspectRatioConstraint(1) + borde de tier color
Slot vacio: fondo oscuro con "?" o icono placeholder
```

### Egg/Shop Buttons
```
Grid de huevos: UIGridLayout
Cada egg button: UIAspectRatioConstraint(1) + ImageLabel del huevo
Precio: TextLabel abajo del huevo, TextSize=12, dorado
Boton de compra: debajo, BackgroundColor azul accion
```

---

## 8. Responsive Checklist

- [ ] Todo usa Scale para Size y Position (salvo paddings pequenos)
- [ ] UIAspectRatioConstraint en elementos que deben mantener proporcion
- [ ] AnchorPoint seteado correctamente (no calcular offsets manualmente)
- [ ] Probar con Device Emulator (minimo: iPhone + iPad)
- [ ] ScrollingFrame con AutomaticCanvasSize
- [ ] TextScaled OFF en botones, TextSize fijo
- [ ] ScreenGui.IgnoreGuiInset = true (evita overlap con top bar)
- [ ] Considerar zona segura: no poner UI critica en bordes extremos

---

## 9. Anti-Patterns

1. NO usar Offset para tamanios principales (se ve diferente en cada dispositivo)
2. NO usar TextScaled en botones (tamanios inconsistentes entre botones)
3. NO usar BackgroundTransparency=0 sin UICorner (rectangulos planos se ven amateur)
4. NO poner UI debajo de la top bar (58px) sin ScreenInsets configurado
5. NO hardcodear posiciones con Offset (se rompe en tablets/phones)
6. NO usar colores solidos sin padding (texto pegado al borde se ve mal)
7. NO mezclar Scale y Offset sin criterio (Scale base, Offset solo micro-ajustes)
8. NO usar `Completed:Connect` en tweens de botones — acumula listeners en cada click. Usar `Completed:Wait()` secuencial.
9. NO usar `WaitForChild` para referencias opcionales (HUD que puede no existir). Usar `FindFirstChild` + nil check.

---

## 11. Modal/Overlay Reset Pattern

### El problema
Victory screens, pause menus, modals — si el usuario puede clickear multiples veces,
los callbacks se acumulan. Resultado: pantallas que parpadean, dobles fires, estado corrupto.

### Solucion: Guard flag + sequential Wait

```lua
local isActive = false

-- Show (con guard)
someRemote.OnClientEvent:Connect(function()
    if isActive then return end
    isActive = true
    -- ... show UI, tween in ...
end)

-- Dismiss (con Wait secuencial, no Connect)
local function dismiss()
    local tween = TweenService:Create(overlay, TweenInfo.new(0.3), {
        BackgroundTransparency = 1
    })
    tween:Play()
    tween.Completed:Wait()  -- secuencial, no callback

    overlay.Visible = false
    isActive = false  -- reset al FINAL

    -- Restaurar referencias opcionales con FindFirstChild
    local hud = playerGui:FindFirstChild("HUD")
    if hud then hud.Enabled = true end
end

dismissBtn.MouseButton1Click:Connect(dismiss)
```

### Reglas
- `isActive` guard: prevenir doble-show
- `tween.Completed:Wait()`: bloquea hasta completar — no acumula callbacks
- Reset de flag DESPUES de que la animacion termine, no antes
- `FindFirstChild` para referencias que pueden no existir (HUD, otros guis)
- `ResetOnSpawn=false` en el ScreenGui para que sobreviva respawns

---

## 12. SurfaceGui Physical Leaderboard

Leaderboard fisico en el mundo del juego (no solo TAB). Usado en obbys, tycoons,
juegos de carrera. Los jugadores ven los mejores tiempos al spawnear.

### Estructura

```
Part (Anchored, CanCollide=false)
└── SurfaceGui (Face=Front, PixelsPerStud=20, ResetOnSpawn=false)
    └── MainFrame (fondo oscuro + UICorner)
        ├── Title (TextLabel "TOP RUNNERS")
        └── ScrollingFrame "Entries"
            ├── UIListLayout (SortOrder=LayoutOrder)
            ├── Frame "Sample" (Visible=false, template)
            │   ├── TextLabel "Rank" (#1, #2...)
            │   ├── TextLabel "PlayerName"
            │   └── TextLabel "Time"
            └── [Entry_1, Entry_2, ... clones of Sample at runtime]
```

### Script pattern (Script server-side, NO LocalScript)

Los Scripts server-side PUEDEN modificar SurfaceGui parented a Parts en Workspace.
El script clona el template `Sample` para cada entry, setea texto y colores.

```lua
-- En un Script en ServerScriptService
local scroll = board.SurfaceGui.MainFrame.Entries
local sample = scroll:WaitForChild("Sample")
local layout = scroll:WaitForChild("Layout")

local function updateLeaderboard()
    -- Limpiar entries previos (preservar Sample + Layout)
    for _, child in scroll:GetChildren() do
        if child.Name ~= "Sample" and child.Name ~= "Layout" then
            child:Destroy()
        end
    end

    -- Collectar + ordenar entries
    local entries = {} -- {name, centiseconds}
    table.sort(entries, function(a, b) return a.centiseconds < b.centiseconds end)

    -- Crear filas (top 5)
    for i = 1, math.min(#entries, 5) do
        local row = sample:Clone()
        row.Name = "Entry_" .. i
        row.Visible = true
        row.LayoutOrder = i
        row.Rank.Text = "#" .. i
        row.PlayerName.Text = entries[i].name
        row.Time.Text = formatTime(entries[i].centiseconds)
        row.Parent = scroll
    end

    -- "No runs yet" si no hay entries
    if #entries == 0 then
        local empty = sample:Clone()
        empty.Name = "Empty"
        empty.Visible = true
        empty.LayoutOrder = 1
        empty.Rank.Text = ""
        empty.PlayerName.Text = "No runs yet..."
        empty.Time.Text = ""
        empty.Parent = scroll
    end
end

-- Loop de actualizacion (cada 5s)
task.wait(3) -- delay inicial para que leaderstats se creen
updateLeaderboard()
while true do
    updateLeaderboard()
    task.wait(5)
end
```

### Rank colors (convencion)
```
#1 Gold:   Color3.fromRGB(255, 215, 0)
#2 Silver: Color3.fromRGB(192, 192, 192)
#3 Bronze: Color3.fromRGB(205, 127, 50)
#4+:       Color3.fromRGB(180, 180, 200) atenuando
```

### Debugging tips
- Agregar `print` en cada paso: "LeaderboardDisplay: Starting...",
  "LeaderboardDisplay: [player] Best Time = X", "Updated with N entries"
- El script corre solo en Play mode. En edit mode no se ven entries (correcto).
- Si el leaderboard esta vacio en Play: verificar que leaderstats se crearon
  ANTES del primer updateLeaderboard() (delay de 3s inicial).
- Race condition: LeaderstatsHandler y LeaderboardDisplay ambos usan
  `Players.PlayerAdded`. El leaderboard debe tolerar `FindFirstChild("leaderstats")`
  devolviendo nil en los primeros ciclos.

### Pitfalls
- **ResetOnSpawn=true**: la SurfaceGui se resetea al respawn y pierde entries dinamicas.
  Poner `ResetOnSpawn=false`. El Script recrea entries en su loop, pero es waste.
- **Face es relativa al Part, no al mundo**: `Enum.NormalId.Front` depende de la
  orientación del Part (`CFrame.LookVector`). Verificar antes con una captura visual
  o test rapido. Si no se ve, probar `Back`, `Right`, `Left` como alternativa.
- **CanvasSize default (800x600)**: con `PixelsPerStud` el canvas se calcula diferente.
  No confiar en el default — setear explicitamente si hay problemas de renderizado.
- **CanvasSize default (800x600)**: con PixelsPerStud, puede no coincidir con el
  tamano del Part. ScrollingFrame con `AutomaticCanvasSize=Y` lo maneja.
- **Sample.Visible=false**: siempre mantener el template invisible. Los clones
  se setean a `Visible=true`.

---

## 10. Snippets Reutilizables

### Helper: createButton
```lua
local function createButton(parent, props)
    local btn = Instance.new("TextButton")
    btn.Name = props.name or "Button"
    btn.Size = props.size or UDim2.new(0.15, 0, 0.08, 0)
    btn.Position = props.position or UDim2.new(0, 0, 0, 0)
    btn.AnchorPoint = props.anchorPoint or Vector2.new(0, 0)
    btn.BackgroundColor3 = props.color or Color3.fromRGB(55, 55, 65)
    btn.TextColor3 = Color3.fromRGB(255, 255, 255)
    btn.Text = props.text or ""
    btn.Font = Enum.Font.GothamBold
    btn.TextSize = props.textSize or 14
    btn.AutoButtonColor = true
    btn.Parent = parent

    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 8)
    corner.Parent = btn

    if props.padding then
        local pad = Instance.new("UIPadding")
        pad.PaddingLeft = UDim.new(0, props.padding)
        pad.PaddingRight = UDim.new(0, props.padding)
        pad.Parent = btn
    end

    return btn
end
```

### Helper: createPanel
```lua
local function createPanel(parent, props)
    local panel = Instance.new("Frame")
    panel.Name = props.name or "Panel"
    panel.Size = props.size or UDim2.new(0.35, 0, 0.75, 0)
    panel.Position = props.position or UDim2.new(0, 0, 0, 0)
    panel.AnchorPoint = props.anchorPoint or Vector2.new(0, 0)
    panel.BackgroundColor3 = props.color or Color3.fromRGB(30, 30, 30)
    panel.BackgroundTransparency = props.transparency or 0
    panel.BorderSizePixel = 0
    panel.Parent = parent

    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 12)
    corner.Parent = panel

    local pad = Instance.new("UIPadding")
    pad.PaddingTop = UDim.new(0, props.pad or 12)
    pad.PaddingBottom = UDim.new(0, props.pad or 12)
    pad.PaddingLeft = UDim.new(0, props.pad or 12)
    pad.PaddingRight = UDim.new(0, props.pad or 12)
    pad.Parent = panel

    return panel
end
```

---

## 8. NUEVAS CAPACIDADES UI 2026

### UIShadow (Studio Beta, Mayo 2026)

Nueva instancia nativa para drop shadows 2D. Reemplaza workarounds con ImageLabel.

```lua
local uiShadow = Instance.new("UIShadow")
uiShadow.BlurRadius = UDim.new(0, 30)
uiShadow.Color = Color3.new(0, 0, 0)
uiShadow.Transparency = 0.5
uiShadow.Offset = UDim2.new(0, 10, 0, 10)
uiShadow.Spread = UDim.new(0, 0)
uiShadow.Parent = parentFrame
```

Propiedades:
- `BlurRadius`: cantidad de blur
- `Color`: color de la sombra
- `Transparency`: opacidad (0=solido, 1=invisible)
- `Offset`: posicion relativa
- `Spread`: expansion

**Limitaciones:**
- No soportado en Path2D
- En TextLabel/TextButton/TextBox: sombra aplica al rectangulo, NO al texto
- Multiples UIShadow por instancia permitidos
- Studio Beta — no disponible in-experience hasta Client Release

### Individual UICorner Rounding (Studio Beta, Mayo 2026)

UICorner ahora permite radio diferente por esquina:

```lua
local uiCorner = Instance.new("UICorner")
uiCorner.CornerRadius = UDim.new(0, 0)  -- reset todas a 0
uiCorner.TopLeftRadius = UDim.new(0, 12)
uiCorner.TopRightRadius = UDim.new(0, 12)
uiCorner.BottomLeftRadius = UDim.new(0, 0)
uiCorner.BottomRightRadius = UDim.new(0, 0)
uiCorner.Parent = frame
```

**Notas:**
- `CornerRadius` existente sigue funcionando como alias (setea todas)
- Cambiar `CornerRadius` sobreescribe las 4 propiedades individuales
- Use cases: speech bubbles, tab headers, cards con solo top-rounded

### StyleQuery (Full Release, 2026)

Sistema para UI responsive que se adapta a constraints de layout y settings globales sin codigo. Parte del ecosistema UI Styling.

Fuente: https://devforum.roblox.com/t/studio-beta-new-ui-capabilities-shadows-individual-corners/4636263

---

## Fuentes

- https://devforum.roblox.com/t/ui-design-starter-guide/53461
- https://devforum.roblox.com/t/designing-ui-tips-and-best-practices/3074034
- https://create.roblox.com/docs/ui
- https://create.roblox.com/docs/tutorials/use-case-tutorials/ui/interactive-ui
- https://www.gameuidatabase.com/ (referencia general de UI en games)

---

## Componentes y Patrones de UI por Tipo

Para patrones detallados de componentes específicos, ver [references/ui-component-patterns.md](references/ui-component-patterns.md).

### Resumen rápido de componentes

| Componente | Referencia | Ejemplo de uso |
|-----------|-----------|----------------|
| **Inventory UI** | [ref §2](references/ui-component-patterns.md#2-inventory-ui) | Pet Simulator, Blox Fruits, coleccionables |
| **Shop UI** | [ref §3](references/ui-component-patterns.md#3-shop-ui) | Gamepass shop, DevProduct shop, tienda de ítems |
| **Settings UI** | [ref §4](references/ui-component-patterns.md#4-settings-ui) | Volume sliders, toggles, keybinds |
| **HUD / HotBar** | [ref §5](references/ui-component-patterns.md#5-hud--barra-inferior-de-acciones) | Barras de acción, slots de equipamiento |
| **Notifications** | [ref §6](references/ui-component-patterns.md#6-notifications--toast-messages) | Toast messages, alerts, confirmaciones |
| **Modal / Popup** | [ref §7](references/ui-component-patterns.md#7-modal--popup--confirmation-dialog) | Confirmaciones, diálogos de warning |
| **Pet Display** | [ref §8](references/ui-component-patterns.md#8-petcollection-display-viewportframe) | ViewportFrame para 3D pets/items |
| **Tab System** | [ref §9](references/ui-component-patterns.md#9-tab-system) | Navegación entre páginas de un panel |
| **Quick Ref** | [ref §10](references/ui-component-patterns.md#10-quick-reference--valores-comunes) | Tamaños, colores, valores típicos |

### ScreenGui Organization (resumen)

```
ScreenGui (ResetOnSpawn=false, IgnoreGuiInset=true, DisplayOrder based)
├── HUD (DisplayOrder=0)       — siempre visible
├── Menus (DisplayOrder=10)    — se abren/cierran
├── Overlays (DisplayOrder=20) — modales, popups
└── Notifications (DisplayOrder=30) — toast, alerts
```
