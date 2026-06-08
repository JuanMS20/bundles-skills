# TDD con Roblox Studio MCP

Adaptación de red-green-refactor para desarrollo Roblox Luau vía MCP,
donde no existe un test runner tradicional.

## Contexto

Roblox Lua se ejecuta dentro del motor Roblox — no hay `pytest`, `jest`,
ni ningún runner externo. La verificación es visual (Play mode) o mediante
inspección del árbol de instancias vía MCP.

## Workflow

### RED — Confirmar que NO existe

Usar `execute_luau` con `assert()` para verificar que el comportamiento
buscado todavía no está presente:

```lua
-- RED: Tool no debe existir aun
local tool = game:GetService("StarterPack"):FindFirstChild("Lightning Gun")
assert(tool == nil, "RED: Tool should NOT exist yet")
```

El return de `execute_luau` muestra el mensaje si el assert falla.
Si pasa, devuelve el mensaje de confirmación.

### GREEN — Código mínimo

Crear o modificar instancias mediante:

- **`execute_luau`** — para crear instancias, setear propiedades, o scripting
  general en el lado servidor
- **`multi_edit`** — para ediciones precisas en scripts existentes
- **`generate_mesh`** — para generar modelos 3D por IA (uso único)

Siempre crear lo estrictamente necesario para pasar el test actual.
No anticipar tests futuros.

### VERIFY — Confirmar que existe

Usar las herramientas de inspección del MCP:

```lua
-- Via execute_luau con asserts
local tool = game:GetService("StarterPack"):FindFirstChild("Lightning Gun")
assert(tool ~= nil, "Tool should exist")
assert(tool.ToolTip == "Lightning Gun", "ToolTip check")
```

O mediante:

- **`search_game_tree(path="...")`** — confirma que la instancia y sus
  hijos existen en el árbol
- **`inspect_instance(path="...")`** — muestra todas las propiedades de
  una instancia para verificar valores exactos
- **`script_read(target_file="...")`** — lee el contenido completo de un
  script para verificar lógica

### VERIFY Pitfall: El operador `#` no cuenta slots con nil

En Luau, `#{nil, nil, nil}` retorna **0**, no 3. Esto afecta
verificaciones de arrays que esperan N slots inicializados a nil:

```lua
-- BAD: asume que `#` cuenta slots vacíos
local data = { equipped = { nil, nil, nil } }
assert(#data.equipped == 3, "expected 3 slots")
-- → ¡Falla! # retorna 0

-- GOOD: verificar cada slot individualmente
assert(data.equipped[1] == nil)
assert(data.equipped[2] == nil)
assert(data.equipped[3] == nil)
```

**Cuándo aparece**: inventario con N slots vacíos, arrays con placeholders
nil que planeas llenar después. Siempre verificar slot por slot o con un
contador manual en vez de `#`.

### Pitfall: `for _, v in t` itera TODAS las keys en Luau

A diferencia de Lua estándar donde `for v in t` usa `ipairs` (solo
índices numéricos), **en Luau itera sobre todas las key-value pairs**,
incluyendo keys string:

```lua
local t = { a = 1, b = 2, c = 3 }
local count = 0
for _, v in t do  -- Funciona en Luau, a diferencia de Lua estándar
	count += 1     -- count = 3 (a, b, c)
end
```

Esto hace que código como `for _, pet in PetData._pets do` funcione
correctamente con diccionarios string-keyed. No necesitas `pairs()`.

### GREEN Pitfall: Estado huérfano entre intentos fallidos

Cuando un `execute_luau` falla a mitad de ejecución (parse error, nil
reference, etc.), las instancias creadas **antes** del punto de fallo
quedan en el DataModel. El siguiente intento puede crear duplicados
o conflictos con estos huérfanos.

**Síntomas**: Folders duplicados (uno vacío, uno con hijos), Parts en
posiciones incorrectas, asserts que pasan pero la estructura está mal.

**Protocolo de cleanup**:
1. Antes de reintentar, ejecutar `search_game_tree` para detectar orphans
2. `execute_luau` con `Destroy()` explícito de todo lo creado:
   ```lua
   local map = workspace:FindFirstChild("Map")
   if map then map:Destroy() end
   -- Repeat for any Lighting effects, etc.
   ```
3. Re-ejecutar el GREEN desde cero

**Regla**: Si un GREEN falló, SIEMPRE cleanup antes de reintentar.
Nunca asumir estado limpio después de un error.

### GREEN Pitfall: Errores al crear scripts via execute_luau

Cuando usas `execute_luau` para crear Scripts/LocalScripts/ModuleScripts,
el código que escribes en `Source` puede tener bugs que solo aparecen
en runtime. **El `execute_luau` no valida el código dentro de `Source`.**

SIEMPRE verificar con `script_read` después de crear, y probar en Play
mode. Bugs comunes:

- Referencia incorrecta a instancias (ej: `remotesFolder.Parent = remotesFolder`
  en vez de `petRemotes.Parent = remotesFolder`)
- Variables capturadas en closures que se vuelven stale
- Nombres mal escritos en `WaitForChild`

### INTEGRATION TEST — Play mode

1. `start_stop_play(is_start=true)` — inicia el juego
2. Esperar ~2-3 segundos a que cargue
3. `start_stop_play(is_start=false)` — detiene el juego
4. `get_console_output()` — revisar errores de script en la consola

**Limitación importante:** durante Play mode, varias herramientas MCP no
están disponibles: `execute_luau`, `screen_capture`, `search_game_tree`,
`inspect_instance`, `mouse_input`. Solo se puede detener el juego con
`start_stop_play` y ver la consola con `get_console_output`.

**Otra limitación:** `get_console_output()` puede no mostrar `print()` o
`warn()` de nuestros scripts. Solo los errores rojos (runtime errors)
aparecen con certeza. Usa `warn()` para debugging (más visible que
`print()` pero tampoco garantizado en todas las sesiones).

## Pipeline completo por issue

```
1. PLAN: behaviors a verificar (lista numerada, aprobación del usuario)
2. RED:  execute_luau con assert → falla (confirma que no existe)
3. GREEN: código mínimo (execute_luau / multi_edit)
4. VERIFY: inspección (execute_luau / search / inspect / script_read)
5. INTEGRATION: Play mode → check console errors
6. Repetir para cada behavior
```

## Patrones de Roblox MCP descubiertos

### Cola de animación con race condition

Cuando encolas animaciones en respuesta a RemoteEvents, puede ocurrir una
race condition si un evento llega entre la salida del `while #queue > 0`
y el `isAnimating = false`. **Solución: re-check guard:**

```lua
local function processQueue()
	if isAnimating then return end
	isAnimating = true
	
	while #animQueue > 0 do
		-- reproducir animación (síncrona con :Wait())
	end
	
	isAnimating = false
	-- ⚠️ Guard: items que llegaron durante la última animación
	if #animQueue > 0 then
		processQueue()
	end
end
```

### Estado centralizado vs closures por botón (Auto-Hatch)

Cuando múltiples botones compiten por un recurso único (ej: solo un
auto-hatch activo a la vez), **NO uses closures per-botón con estado
local**:

```lua
-- ❌ MAL: closure + variable local por botón
for _, def in eggDefs do
	local autoActive = false  -- stale cuando otro botón lo overridea
	autoBtn.MouseButton1Click:Connect(function()
		autoActive = not autoActive  -- bug: visual y lógica desincronizados
	end)
end

-- ✅ BIEN: estado centralizado
local autoState = { activeEggId = nil, buttons = {} }
local function deactivateAuto()
	if autoState.activeEggId then
		local btn = autoState.buttons[autoState.activeEggId]
		btn.BackgroundColor3 = GRAY  -- reset visual
		autoState.activeEggId = nil
	end
end
```

### PlayerRemoving: save síncrono, no task.spawn

Cuando un jugador abandona el juego, `PlayerRemoving` tiene una ventana
limitada para guardar. **NO uses `task.spawn`**:

```lua
-- ❌ MAL: puede no ejecutarse antes de que el jugador se vaya
Players.PlayerRemoving:Connect(function(player)
	task.spawn(function()
		DataStoreWrapper.saveData(player, data)
	end)
end)

-- ✅ BIEN: síncrono
Players.PlayerRemoving:Connect(function(player)
	DataStoreWrapper.saveData(player, data)
	playerData[player] = nil
end)
```

### UI invisible por colores oscuros

Los colores como `Color3.fromRGB(20, 20, 25)` con transparencia 0.3 son
casi invisibles contra el skybox de Studio. **Siempre empezar con colores
brillantes para debug** y oscurecer después:

```lua
-- DEBUG: colores brillantes + bordes
frame.BackgroundColor3 = Color3.fromRGB(255, 0, 0)   -- rojo brillante
frame.BorderSizePixel = 2
frame.BorderColor3 = Color3.fromRGB(0, 255, 0)       -- borde verde

-- PRODUCCIÓN: oscurecer
frame.BackgroundColor3 = Color3.fromRGB(30, 30, 35)
frame.BorderSizePixel = 0
```

### Debug: ScreenGui de prueba en StarterGui

Cuando la UI no se ve, crea un ScreenGui mínimo directamente en
StarterGui (desde execute_luau en Edit mode) para descartar problemas de
PlayerGui o renderizado:

```lua
local sg = Instance.new("ScreenGui")
sg.Name = "DebugTest"
sg.ResetOnSpawn = false
sg.Parent = game:GetService("StarterGui")

local frame = Instance.new("Frame")
frame.Size = UDim2.new(0.5, 0, 0, 80)
frame.BackgroundColor3 = Color3.fromRGB(255, 0, 0)
frame.Parent = sg
```

Si este frame rojo se ve en Play mode, el problema está en tu script
cliente (HatchController/LocalScript). Si no se ve, el problema es de
infraestructura (PlayerGui, script execution, etc).

**⚠ CRITICAL: Limpia el debug GUI después de confirmar.**
Los artifacts de diagnóstico NO deben quedarse en el proyecto:
```lua
-- Ejecuta en Edit mode cuando termines:
local d = game:GetService("StarterGui"):FindFirstChild("DebugTest")
if d then d:Destroy() end
```

## Referencias

- `execute_luau` no captura `print()` en `get_console_output()` — los
  prints internos se pierden. Usar `return` para obtener output.
- Los sonidos built-in de Roblox están en `rbxasset://sounds/*.wav`.
  Preferir `electronic_ping.wav`, `click.wav`, `powerup.wav` (existen
  con seguridad).
- Para beams/texturas, usar la textura built-in de sparkles:
  `rbxasset://textures/particles/sparkles_main.dds`
- Luau `for v in t` itera todas las key-value pairs (no solo array).
  Verificado: string keys sí se recorren.
