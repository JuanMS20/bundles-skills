---
name: math-consultant
description: |
  Consultor matemático para desarrolladores. Revisa cálculos, proporciona fórmulas,
  y detecta errores en la lógica numérica de tu código.
  
  Use cuando:
  - Necesites verificar fórmulas de física, geometría, o probabilidad
  - Quieras calcular distancias, ángulos, colisiones, trayectorias, rotaciones
  - Necesites diseñar probabilidades (loot tables, spawn rates, randomness)
  - Tu código tenga cálculos que "casi funcionan" pero no sabes por qué
  - Trabajes con matrices, transformaciones 3D, pathfinding, o generación procedural
  - Necesites optimizar parámetros, balancear juegos, o analizar datos
  
  Domains cubiertos: física, geometría, probabilidad, matrices 3D, pathfinding,
  interpolación, generación procedural, ecuaciones diferenciales, optimización,
  teoría de juegos, spatial hashing, estadística avanzada.
  
  No es un solver simbólico (no resuelve ecuaciones complejas de forma algebraica).
  Es un revisor de cálculos que detecta errores comunes y proporciona fórmulas verificadas.
---

# Math Consultant — Consultor Matemático

## Principio

"Tienes un cálculo en tu código. ¿Está bien? ¿Qué estás omitiendo? ¿Hay una fórmula más simple?"

## Domains Cubiertos

| Domain | Qué revisa | Fórmulas disponibles |
|---|---|---|
| Física | Salto, movimiento, colisiones, fricción, gravedad | 40+ en physics-formulas.md |
| Geometría | Vectores, distancias, ángulos, raycasting, rotaciones | 60+ en geometry-formulas.md |
| Probabilidad | Loot tables, spawn rates, distribuciones, randomness | 30+ en probability-formulas.md |
| Matrices 3D | Transformaciones, cámaras, quaternions, proyecciones | 40+ en matrices-transformations.md |
| Pathfinding | A*, Dijkstra, BFS, navmesh, steering, flow fields | 50+ en pathfinding.md |
| Interpolación | Easing, Bézier, splines, animation curves | 40+ en interpolation-procedural.md |
| Procedural | Perlin noise, fractals, L-systems, terrain | 30+ en interpolation-procedural.md |
| Ecuaciones dif. | Springs, pendulums, órbitas, integración numérica | 20+ en advanced-math.md |
| Optimización | Gradient descent, simulated annealing, genetic | 15+ en advanced-math.md |
| Teoría de juegos | Minimax, MCTS, expectiminimax | 15+ en advanced-math.md |
| Spatial hashing | Grid, quadtree, octree, R-tree | 20+ en advanced-math.md |
| Estadística | Regresión, Bayes, Markov, A/B testing | 25+ en advanced-math.md |

## Patrón de uso

1. El usuario proporciona código con cálculos (o describe el problema)
2. El consultor identifica el dominio (física, geometría, probabilidad, matrices, pathfinding, etc.)
3. Revisa la fórmula contra referencias conocidas
4. Detecta errores: unidades mal, fórmulas incompletas, edge cases
5. Proporciona corrección o fórmula alternativa
6. Verifica con `anti-hallucination` que la fórmula sea real

---

## Física de Movimiento

### Salto / Jump Kinematics

**Fórmula base (salto simétrico):**
```
velocidad_inicial = sqrt(2 * gravedad * altura)
tiempo_pico = velocidad_inicial / gravedad
```

**Salto asimétrico (subida más lenta que caída):**
```
velocidad_inicial = (-2 * altura) / tiempo_pico
gravedad_subida = (2 * altura) / tiempo_pico^2
gravedad_caida = (2 * altura) / tiempo_caida^2
velocidad_horizontal = distancia / (tiempo_pico + tiempo_caida)
```

**Error común:** Usar gravedad constante para subida y caída. La mayoría de los juegos usan gravedad asimétrica para mejor control de aterrizaje.

**Verificación:** Si el jugador no alcanza la plataforma, revisar:
1. ¿La velocidad horizontal se aplica durante todo el salto?
2. ¿La gravedad de caída es mayor que la de subida?
3. ¿El `delta` se multiplica correctamente en cada frame?

### Movimiento con aceleración

```
velocidad = velocidad_inicial + aceleracion * tiempo
posicion = posicion_inicial + velocidad_inicial * tiempo + 0.5 * aceleracion * tiempo^2
```

**Error común:** Usar `velocidad += aceleracion` sin multiplicar por `delta`. La aceleración es por segundo, no por frame.

### Colisión AABB (Axis-Aligned Bounding Box)

```
collision = (
  rect1.x < rect2.x + rect2.w &&
  rect1.x + rect1.w > rect2.x &&
  rect1.y < rect2.y + rect2.h &&
  rect1.y + rect1.h > rect2.y
)
```

**Error común:** Usar `<=` en lugar de `<`. Si los rectángulos se tocan exactamente en el borde, ¿es colisión? Depende del diseño.

### Distancia punto-círculo

```
distancia = sqrt((px - cx)^2 + (py - cy)^2)
collision = distancia <= radio
```

**Optimización:** Comparar distancia al cuadrado para evitar `sqrt`:
```
distancia_sq = (px - cx)^2 + (py - cy)^2
collision = distancia_sq <= radio^2
```

---

## Geometría y Vectores

### Distancia entre dos puntos

```
distancia = sqrt((x2 - x1)^2 + (y2 - y1)^2)
```

### Ángulo entre dos puntos

```
angulo = atan2(y2 - y1, x2 - x1)  // Resultado en radianes
```

**Error común:** Usar `atan` en lugar de `atan2`. `atan2` maneja correctamente los cuadrantes.

### Vector normalizado (dirección)

```
longitud = sqrt(vx^2 + vy^2)
vx_normal = vx / longitud
vy_normal = vy / longitud
```

**Error común:** No verificar `longitud == 0` antes de dividir. Si el vector es cero, el juego crashea.

### Producto punto (dot product)

```
dot = v1.x * v2.x + v1.y * v2.y
```

**Uso:** Determinar si dos vectores apuntan en la misma dirección:
- `dot > 0` → ángulo < 90° (misma dirección)
- `dot == 0` → perpendicular
- `dot < 0` → ángulo > 90° (direcciones opuestas)

### Producto cruz (cross product) en 2D

```
cross = v1.x * v2.y - v1.y * v2.x
```

**Uso:** Determinar si `v2` está a la izquierda o derecha de `v1`:
- `cross > 0` → v2 a la izquierda
- `cross < 0` → v2 a la derecha
- `cross == 0` → colineales

### Proyección de un punto sobre una línea

```
// Proyectar punto P sobre línea AB
t = ((P.x - A.x) * (B.x - A.x) + (P.y - A.y) * (B.y - A.y)) / ((B.x - A.x)^2 + (B.y - A.y)^2)
proyectado.x = A.x + t * (B.x - A.x)
proyectado.y = A.y + t * (B.y - A.y)
```

**Error común:** No clamp `t` entre 0 y 1. Si querés la proyección sobre el segmento (no la línea infinita), clamp `t`.

---

## Probabilidad y Aleatoriedad

### Loot table (weighted random)

```
// Items con pesos: sword=10, shield=5, potion=20, gold=65
total = sum(pesos)
r = random(0, total)
acumulado = 0
for item in items:
  acumulado += item.peso
  if r < acumulado:
    return item
```

**Error común:** Usar `r <= acumulado` en lugar de `r < acumulado`. El último item nunca se seleccionaría si `r == total`.

### Probabilidad independiente (no memoria)

```
// 30% de chance por evento, independiente
if random() < 0.30:
  drop_item()
```

**Error común:** Pensar que "30% significa que cada 3 eventos hay 1 drop". No. Pueden haber 10 eventos sin drop, o 3 drops seguidos.

### Probabilidad acumulada (pity system)

```
// Garantizar drop después de N intentos fallidos
intentos_fallidos += 1
chance = base_chance + (intentos_fallidos * incremento)
if random() < chance:
  drop_item()
  intentos_fallidos = 0
```

**Error común:** No resetear `intentos_fallidos` después del drop. El sistema se vuelve imposible de balancear.

### Distribución normal (Gaussian) para valores aleatorios

```
// Box-Muller transform
u1 = random()
u2 = random()
z = sqrt(-2 * ln(u1)) * cos(2 * PI * u2)
valor = media + desviacion * z
```

**Uso:** Generar valores que se concentren alrededor de una media (ej: daño de arma, stats de enemigos).

### Spawn rate con cooldown

```
// Evitar spawns masivos en frames cortos
if tiempo_desde_ultimo_spawn >= cooldown_minimo:
  if random() < chance_por_segundo * delta:
    spawn()
    tiempo_desde_ultimo_spawn = 0
```

**Error común:** Usar `chance_por_frame` en lugar de `chance_por_segundo * delta`. El spawn rate depende del FPS.

---

## Verificación de cálculos

### Checklist de revisión

| Problema | ¿Qué revisar? |
|---|---|
| Salto no alcanza | ¿Gravedad asimétrica? ¿Velocidad horizontal constante? ¿Delta correcto? |
| Colisión falla | ¿AABB usa < o <=? ¿Punto-círculo compara distancia^2 o distancia? |
| Movimiento errático | ¿Velocidad se multiplica por delta? ¿Unidades consistentes? |
| Randomness raro | ¿Probabilidad es por frame o por segundo? ¿Hay memoria? ¿Pity system? |
| Vectores rotos | ¿Normalización verifica longitud cero? ¿Ángulo usa atan2? |

### Unidades

Siempre verificar consistencia:
- Píxeles vs metros vs tiles
- Segundos vs frames vs milisegundos
- Grados vs radianes
- Velocidad por frame vs velocidad por segundo

**Error clásico:** `gravedad = 9.8` (m/s²) pero `delta` está en frames. Si el juego corre a 60fps, `gravedad_real = 9.8 / 60` por frame.

---

## Pitfalls

### Inventar fórmulas
Nunca derivar una fórmula de física desde cero sin verificar. Siempre comparar con una fuente conocida (references) o calcular con valores de prueba.

### Ignorar delta
Toda operación por frame debe multiplicarse por `delta`. `posicion += velocidad * delta`. Sin delta, la física depende del FPS.

### Usar floats para dinero/contadores
Nunca usar `float` para valores que deben ser exactos (dinero, contadores de items). Usar `int` o `decimal`.

### Asumir física realista para juegos
Los juegos NO usan física realista. Usan "física arcade" que se siente bien, no que es correcta físicamente.

- Gravedad en juegos de plataforma es ~5-10x la real para que el salto sea snappy
- Fricción es exagerada para evitar que el personaje deslice eternamente
- Colisiones usan AABB simplificado en lugar de mesh exacto
- "Coyote time" permite saltar 100ms después de dejar el suelo
- "Jump buffering" acepta input de salto 100ms antes de tocar el suelo

**Regla:** Si el usuario dice "mi salto no se siente bien", NO calcular con g=9.8 m/s². Preguntar: "¿Qué tan 'floaty' o 'snappy' querés que sea?" y ajustar la gravedad artísticamente. Las fórmulas de la skill son la base matemática; los valores de los parámetros son decisiones de diseño.

### Ignorar el contexto del motor
Unity usa `FixedUpdate` con `Time.fixedDeltaTime`. Godot usa `_physics_process` con `delta`. Asegurar que la fórmula coincida con el ciclo de física del motor.

---

## References

- [references/physics-formulas.md](references/physics-formulas.md) — Física: cinemática, salto, colisiones, movimiento
- [references/geometry-formulas.md](references/geometry-formulas.md) — Geometría: vectores, distancias, ángulos, raycasting
- [references/probability-formulas.md](references/probability-formulas.md) — Probabilidad: loot tables, spawn rates, randomness
- [references/matrices-transformations.md](references/matrices-transformations.md) — Matrices 3D: transformaciones, cámaras, quaternions, proyecciones
- [references/pathfinding.md](references/pathfinding.md) — Pathfinding: A*, Dijkstra, BFS, navmesh, steering, flow fields
- [references/interpolation-procedural.md](references/interpolation-procedural.md) — Interpolación: easing, Bézier, splines; Procedural: Perlin noise, fractals, L-systems
- [references/advanced-math.md](references/advanced-math.md) — Ecuaciones diferenciales, optimización, teoría de juegos, spatial hashing, estadística
