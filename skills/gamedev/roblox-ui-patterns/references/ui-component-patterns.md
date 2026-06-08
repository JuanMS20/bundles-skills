# UI Component Patterns — Roblox

Referencia de componentes UI comunes en juegos Roblox populares.
Estructuras verificadas, no pseudo-código.

---

## 1. ScreenGui — Organización Base

### Estructura recomendada

```
ScreenGui (Name="GameUI", ResetOnSpawn=false, IgnoreGuiInset=true)
├── HUD (Frame)              — SIEMPRE visible, no se oculta
│   ├── HealthBar
│   ├── CoinsDisplay
│   ├── LevelDisplay
│   └── HotBar
├── Overlays (Frame)         — Modales, popups, confirmation dialogs
│   └── (se crean dinámicamente)
├── Menus (Frame)            — Paneles que se abren/cierran
│   ├── Inventory
│   ├── Shop
│   ├── Settings
│   └── Shop
└── Notifications (Frame)    — Toast messages, alerts
    └── (se crean dinámicamente)
```

### Propiedades clave del ScreenGui

| Propiedad | Valor | Razón |
|-----------|-------|-------|
| `ResetOnSpawn` | `false` | No perder estado al respawnear |
| `IgnoreGuiInset` | `true` | No overlap con top bar de Roblox |
| `DisplayOrder` | 0-100 | HUD=0, Menus=10, Overlays=20, Notifications=30 |
| `ZIndexBehavior` | `Sibling` | ZIndex funciona entre hermanos |
| `ClipToDeviceSafeArea` | `true` | Recortar en notch/dynamic island |

---

## 2. Inventory UI

### Estructura (Pet Simulator 99 / Blox Fruits style)

```
InventoryPanel (Frame, AnchorPoint={0.5,0.5}, Position center, Size ~40%)
├── Header (Frame)
│   ├── Title (TextLabel "INVENTARIO")
│   ├── CloseButton (ImageButton, X icon, AnchorPoint={1,0})
│   └── TabBar (Frame, UIListLayout Horizontal)
│       ├── Tab "Mascotas" (TextButton, active=highlighted)
│       ├── Tab "Items"
│       └── Tab "Equipados"
├── SearchBar (TextBox, placeholder "Buscar...")
├── SortDropdown (TextButton "Ordenar: Rarity ▼")
├── ItemGrid (ScrollingFrame)
│   ├── UIGridLayout (CellSize based on aspect ratio)
│   ├── UIPadding (8px all sides)
│   └── ItemTemplate (Frame, Visible=false, template)
│       ├── ItemImage (ImageLabel)
│       ├── RarityBorder (UIStroke, color = tier color)
│       ├── ItemName (TextLabel)
│       ├── Quantity (TextLabel, bottom-right)
│       └── EquippedBadge (TextLabel "EQUIPADO", top-right)
└── Footer (Frame)
    ├── ItemCount (TextLabel "12/50 items")
    └── EquipButton (TextButton "Equipar")
```

### UIGridLayout para inventarios

```lua
local grid = Instance.new("UIGridLayout")
grid.CellSize = UDim2.new(0, 80, 0, 80)  -- Tamaño fijo por slot
grid.CellPadding = UDim2.new(0, 6, 0, 6)  -- 6px gap
grid.SortOrder = Enum.SortOrder.LayoutOrder
grid.FillDirection = Enum.FillDirection.Horizontal
grid.Parent = scrollingFrame

-- Para que ScrollingFrame crezca automáticamente:
scrollingFrame.AutomaticCanvasSize = Enum.AutomaticSize.Y
```

### Item slot — Tamaño responsive

```lua
-- Slot con aspect ratio cuadrado
local slot = Instance.new("Frame")
slot.Size = UDim2.new(0, 80, 0, 80)
slot.BackgroundColor3 = Color3.fromRGB(40, 40, 45)

local aspect = Instance.new("UIAspectRatioConstraint")
aspect.AspectRatio = 1  -- cuadrado
aspect.Parent = slot

-- Borde de rarity
local stroke = Instance.new("UIStroke")
stroke.Color = Color3.fromRGB(180, 180, 180)  -- Common
stroke.Thickness = 2
stroke.Parent = slot
```

### Paginación (si >50 items)

```lua
-- Opción 1: ScrollingFrame con AutomaticCanvasSize (recomendado)
scrollingFrame.AutomaticCanvasSize = Enum.AutomaticSize.Y
scrollingFrame.ScrollBarThickness = 6

-- Opción 2: Botones de página (si hay muchos items)
-- PageLabel: "Página 1 de 5"
-- PrevButton / NextButton debajo del grid
```

---

## 3. Shop UI

### Estructura (Gamepass / DevProduct shop)

```
ShopPanel (Frame, AnchorPoint center, Size ~50%)
├── Header
│   ├── Title (TextLabel "TIENDA")
│   ├── CurrencyDisplay (TextLabel with coin icon + amount)
│   └── CloseButton
├── TabBar (UIListLayout Horizontal)
│   ├── Tab "Popular"
│   ├── Tab "Ofertas"
│   ├── Tab "VIP"
│   └── Tab "Cosméticos"
├── ItemGrid (ScrollingFrame + UIGridLayout)
│   └── ShopItemTemplate (Frame)
│       ├── ItemImage (ImageLabel, aspect 1:1)
│       ├── ItemName (TextLabel)
│       ├── PriceTag (Frame)
│       │   ├── CoinIcon (ImageLabel)
│       │   └── PriceText (TextLabel, bold, green)
│       ├── OriginalPrice (TextLabel, tachado, si hay descuento)
│       ├── BuyButton (TextButton "COMPRAR")
│       └── OwnedBadge (TextLabel "Ya lo tienes", si comprado)
└── Footer
    ├── TermsLabel (TextLabel "Las compras son finales")
    └── PromoCodeButton (TextButton "Código de promoción")
```

### Botón de compra — Patrón

```lua
local buyBtn = Instance.new("TextButton")
buyBtn.Size = UDim2.new(0.8, 0, 0, 36)
buyBtn.Position = UDim2.new(0.1, 0, 1, -44)  -- Pegado abajo
buyBtn.BackgroundColor3 = Color3.fromRGB(80, 180, 80)  -- Verde éxito
buyBtn.Text = "COMPRAR - 100 Robux"
buyBtn.Font = Enum.Font.GothamBold
buyBtn.TextSize = 14
buyBtn.TextColor3 = Color3.new(1, 1, 1)

-- Corners
local corner = Instance.new("UICorner")
corner.CornerRadius = UDim.new(0, 8)
corner.Parent = buyBtn

-- Padding para que el texto no toque bordes
local pad = Instance.new("UIPadding")
pad.PaddingLeft = UDim.new(0, 8)
pad.PaddingRight = UDim.new(0, 8)
pad.Parent = buyBtn
```

### States del botón de compra

```lua
-- Estados: Normal → Hover → Pressed → Loading → Success/Error
local states = {
    normal = { Color3.fromRGB(80, 180, 80), "COMPRAR" },
    hover = { Color3.fromRGB(100, 200, 100), "COMPRAR" },
    pressed = { Color3.fromRGB(60, 150, 60), "COMPRANDO..." },
    owned = { Color3.fromRGB(80, 80, 90), "YA LO TIENES" },
    error = { Color3.fromRGB(220, 70, 70), "ERROR" },
}
```

---

## 4. Settings UI

### Estructura (patrón oficial Roblox)

```
SettingsPanel (Frame, center, Size ~50%, AspectRatio ~2.5)
├── Header
│   ├── Title (TextLabel "AJUSTES")
│   └── CloseButton (ImageButton, X icon)
├── SettingsList (ScrollingFrame + UIListLayout)
│   ├── AudioSection (Frame)
│   │   ├── SectionTitle (TextLabel "AUDIO")
│   │   ├── MusicSlider (Frame + UIDragDetector)
│   │   │   ├── Icon (ImageLabel, music note)
│   │   │   ├── SliderTrack (Frame, bg oscuro + UICorner)
│   │   │   │   ├── Fill (Frame, color de acento)
│   │   │   │   └── Handle (Frame, circular, drag)
│   │   │   └── ValueLabel (TextLabel "80%")
│   │   ├── SFXSlider (Frame + UIDragDetector)
│   │   └── VoiceChatSlider (Frame + UIDragDetector)
│   ├── GraphicsSection (Frame)
│   │   ├── SectionTitle (TextLabel "GRÁFICOS")
│   │   ├── QualityDropdown (TextButton)
│   │   └── FullscreenToggle (TextButton)
│   ├── GameplaySection (Frame)
│   │   ├── SectionTitle (TextLabel "JUGABILIDAD")
│   │   ├── CameraShakeToggle (TextButton toggle)
│   │   ├── DamageNumbersToggle (TextButton toggle)
│   │   └── MusicAutoPlayToggle (TextButton toggle)
│   └── ControlsSection (Frame)
│       ├── SectionTitle (TextLabel "CONTROLES")
│       └── Keybinds (Frame with key remapping)
```

### Slider Widget (patrón oficial)

```lua
-- Estructura de un slider
local sliderFrame = Instance.new("Frame")
sliderFrame.Name = "MusicSlider"
sliderFrame.Size = UDim2.new(1, 0, 0, 40)
sliderFrame.BackgroundTransparency = 1

-- Track
local track = Instance.new("Frame")
track.Size = UDim2.new(0.7, 0, 0, 8)
track.Position = UDim2.new(0.25, 0, 0.5, -4)
track.BackgroundColor3 = Color3.fromRGB(60, 60, 70)
track.Parent = sliderFrame

local trackCorner = Instance.new("UICorner")
trackCorner.CornerRadius = UDim.new(0.5, 0)
trackCorner.Parent = track

-- Fill
local fill = Instance.new("Frame")
fill.Size = UDim2.new(0.8, 0, 1, 0)  -- 80%
fill.BackgroundColor3 = Color3.fromRGB(80, 130, 230)
fill.Parent = track

local fillCorner = Instance.new("UICorner")
fillCorner.CornerRadius = UDim.new(0.5, 0)
fillCorner.Parent = fill

-- Handle (draggable)
local handle = Instance.new("TextButton")
handle.Size = UDim2.new(0, 20, 0, 20)
handle.Position = UDim2.new(0.8, -10, 0.5, -10)
handle.BackgroundColor3 = Color3.new(1, 1, 1)
handle.Text = ""
handle.Parent = track

local handleCorner = Instance.new("UICorner")
handleCorner.CornerRadius = UDim.new(0.5, 0)
handleCorner.Parent = handle

-- UIDragDetector (nuevo, 2025+)
local drag = Instance.new("UIDragDetector")
drag.DragStyle = Enum.UIDragDetectorStyle.Line
drag.ResponseStyle = Enum.UIDragDetectorResponseStyle.Scale
drag.BoundingUIObject = track
drag.Parent = handle
```

### Toggle Button (on/off)

```lua
local function createToggle(parent, name, defaultState)
    local frame = Instance.new("Frame")
    frame.Name = name
    frame.Size = UDim2.new(1, 0, 0, 36)
    frame.BackgroundTransparency = 1

    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(0.7, 0, 1, 0)
    label.Text = name
    label.TextColor3 = Color3.fromRGB(255, 255, 255)
    label.TextXAlignment = Enum.TextXAlignment.Left
    label.Font = Enum.Font.Gotham
    label.TextSize = 14
    label.BackgroundTransparency = 1
    label.Parent = frame

    local toggleBtn = Instance.new("TextButton")
    toggleBtn.Size = UDim2.new(0, 44, 0, 24)
    toggleBtn.Position = UDim2.new(1, -50, 0.5, -12)
    toggleBtn.BackgroundColor3 = defaultState
        and Color3.fromRGB(80, 180, 80)
        or Color3.fromRGB(80, 80, 90)
    toggleBtn.Text = ""
    toggleBtn.Parent = frame

    local toggleCorner = Instance.new("UICorner")
    toggleCorner.CornerRadius = UDim.new(0.5, 0)
    toggleCorner.Parent = toggleBtn

    local circle = Instance.new("Frame")
    circle.Size = UDim2.new(0, 18, 0, 18)
    circle.Position = defaultState
        and UDim2.new(1, -21, 0.5, -9)
        or UDim2.new(0, 3, 0.5, -9)
    circle.BackgroundColor3 = Color3.new(1, 1, 1)
    circle.Parent = toggleBtn

    local circleCorner = Instance.new("UICorner")
    circleCorner.CornerRadius = UDim.new(0.5, 0)
    circleCorner.Parent = circle

    local state = defaultState

    toggleBtn.MouseButton1Click:Connect(function()
        state = not state
        -- Tween position
        TweenService:Create(circle, TweenInfo.new(0.2), {
            Position = state
                and UDim2.new(1, -21, 0.5, -9)
                or UDim2.new(0, 3, 0.5, -9)
        }):Play()
        -- Tween color
        TweenService:Create(toggleBtn, TweenInfo.new(0.2), {
            BackgroundColor3 = state
                and Color3.fromRGB(80, 180, 80)
                or Color3.fromRGB(80, 80, 90)
        }):Play()
    end)

    frame.Parent = parent
    return frame, function() return state end
end
```

---

## 5. HUD — Barra Inferior de Acciones

### Estructura (Blox Fruits style)

```
HotBar (Frame, bottom-center, AnchorPoint={0.5,1})
├── UIListLayout (Horizontal, Padding=4px)
└── Slots (4-6 slots)
    └── Slot (Frame)
        ├── UIAspectRatioConstraint (1:1)
        ├── SlotBG (ImageLabel or Frame, bg oscuro)
        ├── ItemIcon (ImageLabel)
        ├── KeyBind (TextLabel "1", top-left, small)
        └── CooldownOverlay (Frame, semi-transparente, visible during cooldown)
```

### Crear hotbar dinámicamente

```lua
local function createHotBar(parent, slotCount)
    local bar = Instance.new("Frame")
    bar.Name = "HotBar"
    bar.Size = UDim2.new(0, slotCount * 52 + (slotCount - 1) * 4, 0, 52)
    bar.AnchorPoint = Vector2.new(0.5, 1)
    bar.Position = UDim2.new(0.5, 0, 1, -10)
    bar.BackgroundTransparency = 1

    local layout = Instance.new("UIListLayout")
    layout.FillDirection = Enum.FillDirection.Horizontal
    layout.Padding = UDim.new(0, 4)
    layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
    layout.Parent = bar

    for i = 1, slotCount do
        local slot = Instance.new("Frame")
        slot.Name = "Slot_" .. i
        slot.Size = UDim2.new(0, 52, 0, 52)
        slot.BackgroundColor3 = Color3.fromRGB(40, 40, 45)
        slot.LayoutOrder = i

        local corner = Instance.new("UICorner")
        corner.CornerRadius = UDim.new(0, 6)
        corner.Parent = slot

        local keyLabel = Instance.new("TextLabel")
        keyLabel.Size = UDim2.new(0, 16, 0, 16)
        keyLabel.Position = UDim2.new(0, 2, 0, 2)
        keyLabel.BackgroundTransparency = 1
        keyLabel.Text = tostring(i)
        keyLabel.TextColor3 = Color3.fromRGB(150, 150, 150)
        keyLabel.TextSize = 10
        keyLabel.Font = Enum.Font.GothamBold
        keyLabel.TextXAlignment = Enum.TextXAlignment.Left
        keyLabel.TextYAlignment = Enum.TextYAlignment.Top
        keyLabel.Parent = slot

        slot.Parent = bar
    end

    bar.Parent = parent
    return bar
end
```

---

## 6. Notifications / Toast Messages

### Estructura

```
NotificationContainer (Frame, top-right, AnchorPoint={1,0})
├── UIListLayout (Vertical, Padding=8px)
└── (Toast templates created dynamically)
```

### Toast pattern

```lua
local function showToast(parent, message, toastType)
    local colors = {
        success = { bg = Color3.fromRGB(40, 80, 40), border = Color3.fromRGB(80, 180, 80), icon = "✓" },
        warning = { bg = Color3.fromRGB(80, 70, 30), border = Color3.fromRGB(220, 180, 50), icon = "⚠" },
        error = { bg = Color3.fromRGB(80, 30, 30), border = Color3.fromRGB(220, 70, 70), icon = "✕" },
        info = { bg = Color3.fromRGB(30, 50, 80), border = Color3.fromRGB(80, 130, 230), icon = "ℹ" },
    }
    local c = colors[toastType] or colors.info

    local toast = Instance.new("Frame")
    toast.Size = UDim2.new(0, 280, 0, 48)
    toast.BackgroundColor3 = c.bg
    toast.AnchorPoint = Vector2.new(1, 0)
    toast.Position = UDim2.new(1, 0, 0, 0)

    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 8)
    corner.Parent = toast

    local stroke = Instance.new("UIStroke")
    stroke.Color = c.border
    stroke.Thickness = 2
    stroke.Parent = toast

    local icon = Instance.new("TextLabel")
    icon.Size = UDim2.new(0, 32, 1, 0)
    icon.BackgroundTransparency = 1
    icon.Text = c.icon
    icon.TextColor3 = c.border
    icon.TextSize = 18
    icon.Font = Enum.Font.GothamBold
    icon.Parent = toast

    local msg = Instance.new("TextLabel")
    msg.Size = UDim2.new(1, -40, 1, 0)
    msg.Position = UDim2.new(0, 36, 0, 0)
    msg.BackgroundTransparency = 1
    msg.Text = message
    msg.TextColor3 = Color3.fromRGB(255, 255, 255)
    msg.TextSize = 13
    msg.Font = Enum.Font.Gotham
    msg.TextXAlignment = Enum.TextXAlignment.Left
    msg.TextWrapped = true
    msg.Parent = toast

    toast.Parent = parent

    -- Auto-dismiss después de 3 segundos
    task.delay(3, function()
        local tween = TweenService:Create(toast, TweenInfo.new(0.3), {
            BackgroundTransparency = 1,
        })
        tween:Play()
        tween.Completed:Wait()
        toast:Destroy()
    end)

    return toast
end
```

---

## 7. Modal / Popup / Confirmation Dialog

### Estructura

```
Overlay (Frame, full screen, BackgroundTransparency=0.5, ZIndex=100)
└── Dialog (Frame, center, AnchorPoint={0.5,0.5})
    ├── UIAspectRatioConstraint (~2.0)
    ├── UISizeConstraint (MinSize=300, MaxSize=600)
    ├── UICorner (12px)
    ├── Header (TextLabel, title)
    ├── Body (TextLabel, message)
    └── Footer (Frame, UIListLayout Horizontal)
        ├── CancelButton (TextButton "Cancelar")
        └── ConfirmButton (TextButton "Confirmar")
```

### Pattern con guard flag (anti-spam)

```lua
local isDialogOpen = false

local function showDialog(title, message, onConfirm)
    if isDialogOpen then return end
    isDialogOpen = true

    -- Crear overlay + dialog
    local overlay = createOverlay()  -- full-screen backdrop
    local dialog = createDialog(overlay, title, message)

    -- Botones
    dialog.Footer.CancelButton.MouseButton1Click:Connect(function()
        closeDialog(overlay)
        isDialogOpen = false
    end)

    dialog.Footer.ConfirmButton.MouseButton1Click:Connect(function()
        closeDialog(overlay)
        isDialogOpen = false
        if onConfirm then onConfirm() end
    end)
end

local function closeDialog(overlay)
    local tween = TweenService:Create(overlay, TweenInfo.new(0.25), {
        BackgroundTransparency = 1,
    })
    tween:Play()
    tween.Completed:Wait()  -- Sequential, NO .Connect
    overlay:Destroy()
end
```

---

## 8. Pet/Collection Display (ViewportFrame)

### Para mostrar 3D pets/items en UI

```
PetCard (Frame)
├── UICorner (8px)
├── UIStroke (tier color)
├── ViewportFrame (background transparente)
│   ├── WorldModel
│   │   └── PetModel (cloned from ReplicatedStorage)
│   └── Camera (positioned to frame pet)
├── RarityLabel (TextLabel, top, tier color bg)
├── PetName (TextLabel, bottom)
└── LevelBadge (TextLabel, top-right)
```

### Setup de ViewportFrame

```lua
local function setupViewport(viewportFrame, modelTemplate)
    -- Clonar modelo
    local model = modelTemplate:Clone()
    model.Parent = viewportFrame.WorldModel

    -- Calcular bounds
    local cf, size = model:GetBoundingBox()
    local maxSize = math.max(size.X, size.Y, size.Z)

    -- Posicionar cámara
    local camera = Instance.new("Camera")
    camera.Parent = viewportFrame
    viewportFrame.CurrentCamera = camera

    local distance = maxSize * 2
    camera.CFrame = cf * CFrame.new(0, maxSize * 0.2, distance)
    camera.CFrame = CFrame.lookAt(camera.CFrame.Position, cf.Position)

    return model
end
```

---

## 9. Tab System

### Patrón de tabs reutilizable

```lua
local function createTabSystem(tabBar, pages)
    local activeTab = nil

    for tabName, pageFrame in pairs(pages) do
        local tab = Instance.new("TextButton")
        tab.Name = tabName
        tab.Size = UDim2.new(0, 100, 1, 0)
        tab.BackgroundColor3 = Color3.fromRGB(55, 55, 65)
        tab.Text = tabName
        tab.Font = Enum.Font.GothamBold
        tab.TextSize = 12
        tab.TextColor3 = Color3.fromRGB(180, 180, 180)
        tab.Parent = tabBar

        local corner = Instance.new("UICorner")
        corner.CornerRadius = UDim.new(0, 6)
        corner.Parent = tab

        tab.MouseButton1Click:Connect(function()
            -- Hide all pages
            for _, page in pairs(pages) do
                page.Visible = false
            end
            -- Deactivate all tabs
            for _, t in ipairs(tabBar:GetChildren()) do
                if t:IsA("TextButton") then
                    TweenService:Create(t, TweenInfo.new(0.15), {
                        BackgroundColor3 = Color3.fromRGB(55, 55, 65),
                        TextColor3 = Color3.fromRGB(180, 180, 180),
                    }):Play()
                end
            end
            -- Activate this tab
            pageFrame.Visible = true
            TweenService:Create(tab, TweenInfo.new(0.15), {
                BackgroundColor3 = Color3.fromRGB(80, 130, 230),
                TextColor3 = Color3.new(1, 1, 1),
            }):Play()
            activeTab = tabName
        end)
    end

    -- Auto-select first tab
    local firstTab = tabBar:FindFirstChildWhichIsA("TextButton")
    if firstTab then firstTab:Fire("MouseButton1Click") end
end
```

---

## 10. Quick Reference — Valores Comunes

### Tamaños típicos de componentes

| Componente | Size (Scale) | Notas |
|-----------|-------------|-------|
| Panel principal (inventory/shop) | 40-50% width, 60-80% height | Center anchor |
| Panel settings | 50% width, 60% height | AspectRatio ~2.5 |
| Header de panel | 100% width, 8-10% height | Top of panel |
| Botón de acción | 15-20% width, 6-8% height | + UIAspectRatioConstraint |
| Tab button | Variable width, 100% height tab bar | Horizontal list |
| Hotbar slot | 52x52px (offset) | Bottom-center |
| Toast notification | 280px width, 48px height | Top-right, auto-dismiss |
| Slider track | 70% width, 8px height | Centered in row |
| Toggle switch | 44x24px (offset) | Right-aligned in row |

### Colores por contexto

| Contexto | Color | RGB |
|----------|-------|-----|
| Comprar/Comprar ahora | Verde éxito | (80, 180, 80) |
| Cancelar/Cerrar | Rojo peligro | (220, 70, 70) |
| Seleccionado/Activo | Azul acento | (80, 130, 230) |
| Deshabilitado | Gris oscuro | (80, 80, 90) |
| Advertencia | Amarillo | (220, 180, 50) |
| Texto primario | Blanco | (255, 255, 255) |
| Texto secundario | Gris claro | (180, 180, 180) |

---

## Fuentes

- https://create.roblox.com/docs/ui
- https://create.roblox.com/docs/tutorials/use-case-tutorials/ui/interactive-ui
- https://devforum.roblox.com/t/designing-ui-tips-and-best-practices/3074034
- https://devforum.roblox.com/t/specific-details-about-ui-scaling-best-practices/3888004
- https://devforum.roblox.com/t/ui-design-starter-guide/53461
