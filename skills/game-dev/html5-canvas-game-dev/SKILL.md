---
name: html5-canvas-game-dev
description: "Build single-file HTML5 Canvas games with physics, rendering, collision detection, and game state management. Covers spec-first workflow, simulation-first physics validation, collision response design, and power tuning. Use when building browser games, canvas games, physics simulations, or interactive HTML5 demos."
tags: [game-dev, html5, canvas, physics, single-file]
---

# HTML5 Canvas Game Development

## Workflow Obligatorio: Simular ANTES de Codear

**NUNCA escribas código de juego sin validar los parámetros primero.**

1. Definir constantes de física (gravedad, velocidad, potencia, fricción)
2. **Simular trayectorias en Python/JS fuera del juego** — verificar que el proyectil alcanza los objetivos
3. Ajustar parámetros hasta que la simulación confirme viabilidad
4. SOLO THEN implementar en el canvas

```
WRONG:  Escribir juego → probar en browser → "no llega" → reescribir
RIGHT:  Simular física → ajustar params → verificar → implementar → probar en browser
```

**Señal de alarma**: Si el usuario puede preguntar "¿esto funciona?", no verificaste lo suficiente.

## Arquitectura de Juego Single-File

### Estructura mínima
```
HTML: canvas element + viewport meta
CSS: canvas centrado, sin scroll, cursor apropiado
JS:
  1. Constantes (W, H, GROUND, GRAVITY, etc.)
  2. Configuración de niveles/entidades (DATA-DRIVEN)
  3. Estado del juego (let state, level, score, etc.)
  4. Input handling (mouse + touch, passive:false)
  5. Física/update loop
  6. Rendering (draw functions)
  7. Game loop (requestAnimationFrame)
```

### Patrón de niveles data-driven
```javascript
const LEVELS = [
  { birds: ['red','red','yellow'],
    pigs: [{x:790,y:380,r:20,hp:2}],
    blocks: [{x:700,y:430,w:40,h:120,hp:3}] },
  // ...
];
function loadLevel(idx) {
  // Deep copy from LEVELS — never mutate the config
  blocks = LEVELS[idx].blocks.map(b => ({...b, maxHp:b.hp}));
}
```

### Cola de entidades (patrón anti-duplicación)
**Pitfall**: Si la entidad "activa" y la "pendiente" se dibujan desde la misma lista, se duplica visualmente.

```javascript
// WRONG — dibuja la entidad activa DOS veces (en su posición + en la cola)
for (let i=0; i<queue.length; i++) drawEntity(queue[i]);

// RIGHT — separar activa de pendiente
const qStart = isActive ? 1 : 0; // skip la que está en uso
for (let i=qStart; i<queue.length; i++) {
  const gx = computedPosition(queue.length - i); // calcular posición dinámica
  drawEntity(queue[i]);
}
```

**Regla**: Las posiciones de la cola se calculan en render, NO se almacenan en los objetos.

### Canvas rendering verification
Los browsers headless a veces muestran pantalla negra. Verificar que el script ejecutó:
```javascript
// En consola del browser:
document.getElementById('c').width + 'x' + document.getElementById('c').height
// Si dice "300x150" → script NO ejecutó (default canvas size)
// Si dice "1200x600" (o el tamaño configurado) → OK
```

### Touch input
```javascript
canvas.addEventListener('touchstart', handler, {passive: false});
canvas.addEventListener('touchmove', handler, {passive: false});
canvas.addEventListener('touchend', handler, {passive: false});
// SIEMPRE {passive: false} para poder prevenir default
```

### Canvas rotate para sprites con dirección
```javascript
function drawEntity(x, y, angle) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  // Dibujar todo relativo a (0,0)
  ctx.restore();
}
// Ángulo de dirección de movimiento:
const angle = Math.atan2(entity.vy, entity.vx);
```

## Simulation-First Workflow (from game-physics-simulation)

**Core principle**: Simulate before you implement. A 5-minute Python script saves hours of broken gameplay.

### "Can It Work?" Questions
For each game mechanic, ask:
- Can the projectile reach the target? (range verification)
- Can the player survive this encounter? (difficulty verification)
- Is there a valid strategy to win? (solvability verification)
- Are multiple strategies viable? (gameplay depth)

### Simulation Steps
1. **Extract physics constants** — list every physical constant and formula before writing game code
2. **Define verification questions** — what must be true for the game to be playable?
3. **Write a simulation script** — deterministic, frame-by-frame, matching the game's actual update loop
4. **Iterate on design, not code** — if simulation shows the mechanic doesn't work, adjust constants/positions, NOT game code
5. **THEN implement** — only write game code after simulation confirms solvability

See `references/simulation-template.md` for a complete brute-force simulation template.

### Anti-Pattern: Code-First-Then-Hope
```
WRONG: Write game → Open in browser → "looks good" → Ship
RIGHT: Design mechanics → Simulate → Fix design → Implement → Verify
```

## Collision Response Design

The collision response determines if the game feels right:

| Response | When to use | Feel |
|----------|-------------|------|
| Bounce (reverse velocity) | Bumper-style, pinball | Frustrating if targets are far |
| Slow down (reduce magnitude) | Plow-through, destruction | Satisfying, realistic |
| Stop | Heavy objects, walls | Safe default |

**Pitfall**: Bouncing backward (multiply by negative) makes it nearly impossible to reach behind the first obstacle. For destruction games, use `velocity *= 0.5` (same direction, reduced speed).

## Power Tuning Formula

For projectile games, calculate max range analytically:
```
max_velocity = MAX_STRETCH * POWER
range ≈ vx * (1 - DRAG^frames) / (1 - DRAG)
```
Then verify with simulation that max range >= distance to farthest target + margin.

**Pitfall**: Air drag (multiplicative per-frame) reduces range more than expected. At DRAG=0.999 over 50 frames, range is ~5% less than drag-free. At DRAG=0.99, range drops ~40%.

## Pitfalls

### 1. Patch de optimización corrompe archivos HTML
Usar `patch` para "eliminar líneas en blanco" o "comprimir" puede borrar tags de cierre (`</script></body></html>`) si el diff no es preciso.
**Fix**: Nunca optimizar archivos HTML/JS con patches ciegos. Releer el archivo completo antes de cualquier edit.

### 2. Física no verificada = juego no superable
El error más común: diseñar niveles sin simular si los proyectiles alcanzan los objetivos.
**Fix**: Siempre simular trayectorias con las constantes exactas del juego ANTES de crear niveles.

### 3. Colisión AABB asimétrica
```javascript
// WRONG — solo detecta colisión por un lado
return a.x < b.x + b.w && a.x + a.r > b.x && a.y < b.y + b.h && a.y + a.r > b.y;

// Better — circle vs rect más preciso
const cx = Math.max(b.x, Math.min(a.x, b.x + b.w));
const cy = Math.max(b.y, Math.min(a.y, b.y + b.h));
return Math.hypot(a.x - cx, a.y - cy) < a.r;
```
Para juegos casuales, AABB simple funciona. Pero si hay problemas de colisión fantasma, usar circle-rect.

### 4. let/const top-level no accesibles desde browser console
Variables declaradas con `let`/`const` en `<script>` top-level no se agregan a `window`. No se pueden leer desde DevTools console.
**Fix**: Para debugging, exizar manualmente al window o usar `var` temporal.

### 5. Rotación de sprites
Los rasgos faciales (ojos, cejas, pico) deben dibujarse relativos a (0,0) dentro de save/translate/rotate, NO con coordenadas absolutas.

## Checklist de verificación post-implementación

```
[ ] Física simulada y verificada (el proyectil alcanza el objetivo)
[ ] Canvas dimensions correctas (no 300x150 default)
[ ] Sin errores en console
[ ] Input funciona (mouse + touch)
[ ] Cola de entidades sin duplicación
[ ] Rotación de sprites funciona durante movimiento
[ ] Estados del juego (ready → aiming → flying → won/lost) transicionan correctamente
[ ] Niveles se cargan correctamente (tipos preservados)
```
