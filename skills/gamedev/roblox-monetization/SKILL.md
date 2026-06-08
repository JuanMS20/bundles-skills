---
name: roblox-monetization
description: "Estrategia y ejecución de monetización Roblox: pricing strategy, Game Passes, Developer Products, ProcessReceipt, Premium Payouts, A/B testing, estimación de revenue. Usa cuando digas 'configurar monetización', 'qué cobrar', 'game passes', 'developer products', 'process receipt', 'premium payouts', o necesites diseñar CÓMO gana dinero tu juego. Complementa roblox-studio-development (que tiene el código base de gamepass shop)."
---

# Roblox Monetization — Estrategia + Ejecución

Gana dinero sin arruinar la experiencia. Cada decisión de pricing se basa en datos, no en intuición.

---

## Quick start

Cuando el usuario diga "configura la monetización de mi juego":

```
1. Preguntar: ¿qué género es el juego? (determina modelo dominante)
2. Aplicar pricing framework (ver abajo)
3. Diseñar Game Passes + Developer Products
4. Implementar ProcessReceipt (server-side)
5. Estimar revenue con tabla DAU × ARPU
```

---

## 1. Pricing Framework

### Regla de oro
La monetización más efectiva en Roblox vende EXPRESIÓN/STATUS, no PODER. Los free players son tu producto (generan tráfico y engagement).

### Tiers de Game Passes

| Tier | Precio (Robux) | Precio real ($) | Tipo | Ejemplo |
|------|----------------|-----------------|------|---------|
| Entry | 10-50 | $0.03-0.14 | Micro-boost | +10% monedas, bag slot extra |
| Low | 100-300 | $0.29-0.86 | QoL | VIP básico, 2x monedas |
| Mid | 400-1000 | $1.14-2.86 | Status | VIP completo, exclusive pet |
| High | 1500-3000 | $4.29-8.57 | Premium | Mega bundle, exclusive zone |
| Whale | 5000+ | $14.29+ | Ultra | Founder pack, limited edition |

### Developer Products (consumibles)

| Tipo | Precio típico | Uso | Repeat? |
|------|---------------|-----|---------|
| Coins pack | 20-100 Robux | Monedas in-game | Sí |
| Booster | 50-200 Robux | 2x velocidad temporal | Sí |
| Gacha/Spin | 10-50 Robux | Ruleta de items | Sí (adicción) |
| Revive | 10-25 Robux | Volver a vida | Sí |

### Pricing psychology
- Números impares se perciben más baratos (99 Robux vs 100)
- Bundles deben ahorrar 20-30% vs comprar por separado
- Primer purchase debe ser < 50 Robux (convertir es el objetivo, no maximizar)
- Ofrecer "starter pack" con 70% descuento solo la primera vez

---

## 2. Game Passes — Qué crear

### Checklist mínimo viable (lanzar con esto)

```
[ ] VIP Pass (400-800 Robux) — 2x monedas, tag exclusivo, área VIP
[ ] Starter Pack (100-200 Robux) — monedas + item exclusivo, compra única
[ ] Extra Inventory/Slots (50-150 Robux) — slots de mascota/inventario
[ ] Cosmetic Exclusive (200-500 Robux) — aura, trail, effect visual
[ ] Speed/Convenience (100-300 Robux) — auto-collect, auto-hatch, speed boost
```

### Game Pass que NUNCA debes crear
- "Pay to win" directo (más daño que free players)
- Game pass que bloquea contenido base del juego
- Game pass sin beneficio visible inmediato
- Más de 10 game passes al inicio (confunde al jugador)

---

## 3. Developer Products — Cómo implementar

### Arquitectura

```
ServerScriptService/
└── MonetizationManager (Script)     ← ProcessReceipt + ownership checks

ReplicatedStorage/
├── ProductConfig (ModuleScript)     ← IDs, precios, efectos
└── Remotes/
    └── PurchaseComplete (RemoteEvent)  ← server→client notificación
```

### ProductConfig ModuleScript

```lua
-- ReplicatedStorage.ProductConfig
local ProductConfig = {
    Products = {
        [123456789] = {  -- ← Reemplazar con tu Product ID real
            name = "1000 Coins",
            effect = "coins",
            amount = 1000,
        },
        [123456790] = {
            name = "2x Speed Boost",
            effect = "booster",
            duration = 300,  -- 5 minutos
            multiplier = 2,
        },
        [123456791] = {
            name = "Revive",
            effect = "revive",
        },
    },
    GamePasses = {
        VIP = 123456792,       -- ← Reemplazar con tu GamePass ID
        StarterPack = 123456793,
        ExtraSlots = 123456794,
    },
}

function ProductConfig.GetProduct(productId)
    return ProductConfig.Products[productId]
end

function ProductConfig.GetGamePass(passId)
    for name, id in pairs(ProductConfig.GamePasses) do
        if id == passId then return name end
    end
    return nil
end

return ProductConfig
```

### MonetizationManager — ProcessReceipt

```lua
-- ServerScriptService.MonetizationManager
local Players = game:GetService("Players")
local MarketplaceService = game:GetService("MarketplaceService")
local ProductConfig = require(game:GetService("ReplicatedStorage"):WaitForChild("ProductConfig"))

local PurchaseComplete = game:GetService("ReplicatedStorage"):WaitForChild("Remotes"):WaitForChild("PurchaseComplete")

-- ============================================================
-- PROCESS RECEIPT — El callback más importante de tu juego
-- Roblox llama esto DESPUÉS de que el jugador paga
-- Si no lo implementas, Roblox retiene el dinero y el jugador no recibe nada
-- ============================================================

MarketplaceService.ProcessReceipt = function(receiptInfo)
    local player = Players:GetPlayerByUserId(receiptInfo.PlayerId)
    if not player then
        -- Jugador se fue antes de que se procesara
        -- Importante: devolver NotProcessedYet para que Roblox reintente
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    local productId = receiptInfo.ProductId
    local product = ProductConfig.GetProduct(productId)

    if not product then
        warn("Unknown product:", productId)
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    -- Aplicar efecto según tipo
    local success = false

    if product.effect == "coins" then
        success = grantCoins(player, product.amount)

    elseif product.effect == "booster" then
        success = applyBooster(player, product.duration, product.multiplier)

    elseif product.effect == "revive" then
        success = revivePlayer(player)

    else
        warn("Unhandled product effect:", product.effect)
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end

    if success then
        -- Notificar al cliente para mostrar UI de confirmación
        PurchaseComplete:FireClient(player, product.name, product.effect)
        return Enum.ProductPurchaseDecision.PurchaseGranted
    else
        return Enum.ProductPurchaseDecision.NotProcessedYet
    end
end

-- ============================================================
-- GAMEPASS OWNERSHIP CHECK
-- Llamar en CharacterAdded + cuando el jugador compra
-- ============================================================

local function checkGamePasses(player, character)
    local humanoid = character:FindFirstChildWhichIsA("Humanoid")
    if not humanoid then return end

    for passName, passId in pairs(ProductConfig.GamePasses) do
        local success, owns = pcall(function()
            return MarketplaceService:UserOwnsGamePassAsync(player, passId)
        end)

        if success and owns then
            applyPassEffect(player, passName, humanoid)
        end
    end
end

local function applyPassEffect(player, passName, humanoid)
    if passName == "VIP" then
        -- 2x monedas, tag, etc.
        player:SetAttribute("VIP", true)
    elseif passName == "StarterPack" then
        -- Items iniciales
        player:SetAttribute("HasStarterPack", true)
    elseif passName == "ExtraSlots" then
        -- Slots extra
        player:SetAttribute("ExtraSlots", true)
    end
end

-- Conectar a PlayerAdded
Players.PlayerAdded:Connect(function(player)
    player.CharacterAdded:Connect(function(character)
        checkGamePasses(player, character)
    end)
end)

-- ============================================================
-- PROMPT PURCHASE (llamar desde UI/Shop)
-- ============================================================

-- Server-side: el cliente pide comprar, el servidor valida y promptea
local PromptPurchase = game:GetService("ReplicatedStorage"):WaitForChild("Remotes"):WaitForChild("PromptPurchase")

PromptPurchase.OnServerEvent:Connect(function(player, purchaseType, itemId)
    if purchaseType == "gamepass" then
        MarketplaceService:PromptGamePassPurchase(player, itemId)
    elseif purchaseType == "product" then
        MarketplaceService:PromptProductPurchase(player, itemId)
    end
end)

-- ============================================================
-- HELPER FUNCTIONS (reemplazar con tu lógica real)
-- ============================================================

local function grantCoins(player, amount)
    local coins = player.leaderstats and player.leaderstats:FindFirstChild("Coins")
    if not coins then return false end
    coins.Value += amount
    return true
end

local function applyBooster(player, duration, multiplier)
    player:SetAttribute("SpeedMultiplier", multiplier)
    task.delay(duration, function()
        if player.Parent then  -- aún en el juego
            player:SetAttribute("SpeedMultiplier", 1)
        end
    end)
    return true
end

local function revivePlayer(player)
    local character = player.Character
    if not character then return false end
    local humanoid = character:FindFirstChildWhichIsA("Humanoid")
    if not humanoid then return false end
    humanoid.Health = humanoid.MaxHealth
    return true
end
```

---

## 4. Premium Payouts — El ingreso oculto

### Qué son
Roblox te paga Robux por cada segundo que un **Premium subscriber** pasa en tu juego. No necesita comprar nada. Solo jugar.

### Datos clave
- Puede representar **20-40% del ingreso** en juegos de alto engagement
- Se basa en session length × retención
- Brookhaven gana MÁS por Premium Payouts que por ventas directas

### Cómo optimizar
1. **Maximizar session length**: daily quests, social features, progresión lenta
2. **Maximizar retención D1/D7**: eventos diarios, rewards por volver
3. **Social hooks**: tradeo, equipos, chat — el jugador se queda por los amigos
4. **No forzar compras**: los jugadores que disfrutan gastan más a largo plazo

### Métricas a monitorear
```
- Session length promedio (target: >10 min)
- Retención D1 (target: >30%)
- Retención D7 (target: >15%)
- % de sesiones con Premium subscribers
```

---

## 5. A/B Testing de Precios

### Framework

```
1. Elegir 1 game pass o product para testear
2. Crear 2 variantes de precio (ej: 200 vs 300 Robux)
3. Ejecutar 7+ días MÍNIMO
4. Necesitas 1000+ visitas por variante para datos válidos
5. Medir: conversion rate × precio = revenue por visitor
```

### Métricas clave

```
Revenue per visitor = (visitors × conversion_rate × price) / visitors

Ejemplo:
- Opción A: 200 Robux, 5% convierte → $0.29 × 0.05 = $0.014/visitor
- Opción B: 300 Robux, 3% convierte → $0.43 × 0.03 = $0.013/visitor

→ Opción A gana aunque sea más barata (mayor volumen)
```

### Qué testear primero
1. Starter pack price (mayor impacto — es la primera compra)
2. VIP price (mayor revenue por unidad)
3. Consumable price (mayor repeat purchase)

---

## 6. Estimación de Revenue

### Tabla de referencia

| DAU | ARPU/mes | Revenue/mes | Nivel |
|-----|----------|-------------|-------|
| 100 | $0.50 | $50 | Hobby |
| 500 | $1.00 | $500 | Side income |
| 1,000 | $1.50 | $1,500 | Part-time |
| 5,000 | $2.00 | $10,000 | Full-time |
| 20,000 | $3.00 | $60,000 | Studio |

### Fórmula
```
Revenue = DAU × 30 días × ARPU
ARPU = (GamePass revenue + Product revenue + Premium Payouts) / DAU

Ejemplo real:
- 1,000 DAU
- 5% convierte en game pass de 400 Robux ($1.14)
- 10% compra consumible de 100 Robux ($0.29) × 2 veces/mes
- Premium Payouts: $0.50/usuario/mes

Revenue = (50 × $1.14) + (100 × $0.29 × 2) + (1000 × $0.50)
        = $57 + $58 + $500 = $615/mes
```

---

## 7. Documento de Monetización (template)

Cuando el usuario pida "diseña la monetización de mi juego":

```
# ESTRATEGIA DE MONETIZACIÓN — [Nombre del Juego]
Fecha: YYYY-MM-DD

## 1. Resumen Ejecutivo
- Modelo principal: [Game Passes / Developer Products / Mix]
- Revenue target mes 1: $___
- Revenue target mes 6: $___
- ARPU esperado: $___

## 2. Game Passes
| # | Nombre | Precio | Beneficio | Prioridad |
|---|--------|--------|-----------|-----------|
| 1 | VIP | 400 R$ | 2x monedas, tag, area VIP | ALTA |
| 2 | Starter Pack | 150 R$ | 500 monedas + item exclusivo | ALTA |
| 3 | Extra Slots | 100 R$ | +3 slots de mascota | MEDIA |
| 4 | [Custom] | ___ R$ | ___ | ___ |

## 3. Developer Products
| # | Nombre | Precio | Efecto | Consumible |
|---|--------|--------|--------|------------|
| 1 | 1000 Coins | 25 R$ | +1000 monedas | Sí |
| 2 | Speed Boost | 50 R$ | 2x velocidad 5 min | Sí |
| 3 | Revive | 15 R$ | Revivir en el acto | Sí |

## 4. Premium Payouts Strategy
- Session length target: >10 min
- Retención D1 target: >30%
- Mecánicas de engagement: [daily quests, social, trade]

## 5. Estimación de Revenue
| Escenario | DAU | ARPU | Revenue/mes |
|-----------|-----|------|-------------|
| Conservador | ___ | $___ | $___ |
| Realista | ___ | $___ | $___ |
| Optimista | ___ | $___ | $___ |

## 6. A/B Testing Plan
- Test 1: [what] — [when] — [metric]
- Test 2: [what] — [when] — [metric]

## 7. Anti-Patterns a Evitar
- [ ] No pay-to-win
- [ ] No bloquear contenido base
- [ ] No más de 10 game passes al inicio
- [ ] Primer purchase < 50 Robux
```

---

## Anti-patterns

- **Pay-to-win directo** → aliena free players, reduce retención a largo plazo
- **Más de 10 game passes** → confunde al jugador, diluye conversiones
- **No implementar ProcessReceipt** → Roblox retiene el dinero, jugador no recibe
- **Pricing sin datos** → A/B testea siempre, no adivines
- **Ignorar Premium Payouts** → puede ser 20-40% de tu ingreso
- **Starter pack caro** → el objetivo es CONVERTIR, no maximizar la primera compra
- **No verificar ownership en CharacterAdded** → el efecto del game pass se pierde al respawnear

---

## Relación con otras skills

- **roblox-market-research**: Usa ANTES de esta skill. Primero decide QUÉ construir, luego CÓMO monetizarlo.
- **roblox-studio-development**: Tiene el código base de Gamepass shop (MoonJump pattern). Esta skill agrega la capa de estrategia + ProcessReceipt + Premium Payouts.
- **roblox-game-systems**: Tiene el patrón EconomyService (server-authoritative). Esta skill lo complementa con la lógica de purchases.
- **roblox-ui-patterns**: Para diseñar la shop UI que se vea bien y convierta.
