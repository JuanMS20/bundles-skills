# Interpolación Avanzada y Generación Procedural

## Easing Functions

### Linear
```
f(t) = t
```

### Ease In

```
// Quadratic
f(t) = t^2

// Cubic
f(t) = t^3

// Quartic
f(t) = t^4

// Quintic
f(t) = t^5

// Exponential
f(t) = 2^(10*(t-1))

// Circular
f(t) = 1 - sqrt(1 - t^2)

// Back (overshoot)
f(t) = t^2 * ((overshoot + 1) * t - overshoot)
// overshoot = 1.70158 (default)

// Elastic
f(t) = -(2^(10*(t-1))) * sin((t-1.1) * 5 * PI / 1.1)

// Bounce
f(t) = 1 - bounce(1 - t)
// donde bounce es una serie de parabolas
```

### Ease Out

```
// General: f(t) = 1 - ease_in(1 - t)

// Quadratic
f(t) = 1 - (1-t)^2

// Cubic
f(t) = 1 - (1-t)^3

// Exponential
f(t) = 1 - 2^(-10*t)

// Elastic
f(t) = 2^(-10*t) * sin((t-0.1) * 5 * PI / 0.1) + 1
```

### Ease In-Out

```
// General: f(t) = t < 0.5 ? ease_in(2*t)/2 : 1 - ease_in(2-2*t)/2

// Quadratic
f(t) = t < 0.5 ? 2*t^2 : 1 - 2*(1-t)^2

// Cubic
f(t) = t < 0.5 ? 4*t^3 : 1 - 4*(1-t)^3

// Sinusoidal
f(t) = -0.5 * (cos(PI*t) - 1)
```

## Bézier Curves

### Quadratic Bézier (3 puntos de control)

```
B(t) = (1-t)^2 * P0 + 2*(1-t)*t * P1 + t^2 * P2

// Derivada (velocidad)
B'(t) = 2*(1-t)*(P1 - P0) + 2*t*(P2 - P1)

// Curvatura
B''(t) = 2*(P2 - 2*P1 + P0)
```

### Cubic Bézier (4 puntos de control)

```
B(t) = (1-t)^3 * P0 + 3*(1-t)^2*t * P1 + 3*(1-t)*t^2 * P2 + t^3 * P3

// Derivada
B'(t) = 3*(1-t)^2*(P1-P0) + 6*(1-t)*t*(P2-P1) + 3*t^2*(P3-P2)

// Segunda derivada
B''(t) = 6*(1-t)*(P2 - 2*P1 + P0) + 6*t*(P3 - 2*P2 + P1)
```

### Bézier de grado N

```
// Bézier de n+1 puntos de control
B(t) = sum( i=0..n, C(n,i) * (1-t)^(n-i) * t^i * Pi )
// C(n,i) = n! / (i! * (n-i)!)

// De Casteljau's algorithm (estable numéricamente)
// 1. Crear tabla de puntos
// 2. Para cada nivel, interpolar entre puntos adyacentes
// 3. El punto final es el resultado
```

### Bézier through points (Interpolación)

```
// Dado n puntos, encontrar control points para que la curva pase por ellos

// Para cubic Bézier:
// P0 = punto 0
// P1 = punto 0 + tangent_in * (1/3)
// P2 = punto 1 - tangent_out * (1/3)
// P3 = punto 1

// Tangentes:
// tangent_in = (punto[i+1] - punto[i-1]) * tension
// tangent_out = (punto[i+2] - punto[i]) * tension
// tension = 0.5 (default)
```

## Splines

### Catmull-Rom Spline

```
// Interpola entre puntos P0, P1, P2, P3
// Pasa por P1 y P2
// T = 0.5 (tension)

// Para t en [0, 1]:
// P(t) = 0.5 * [
//   (2*P1) +
//   (-P0 + P2) * t +
//   (2*P0 - 5*P1 + 4*P2 - P3) * t^2 +
//   (-P0 + 3*P1 - 3*P2 + P3) * t^3
// ]

// Tangente en P1:
// T = 0.5 * (P2 - P0)
```

### B-Spline

```
// No pasa por los puntos de control (aproxima)
// Más suave que Catmull-Rom

// Grado 3 (cubic), uniforme:
// Nósos = [0, 0, 0, 0, 1, 2, 3, 4, 4, 4, 4]
// Bases = funciones de blending

// P(t) = sum( N_i,k(t) * P_i )
// N_i,k = basis function de grado k

// Ventaja: local control (mover un punto afecta solo vecinos)
// Desventaja: no pasa por los puntos
```

### Hermite Spline

```
// Interpola entre puntos con tangentes especificadas

// P(t) = (2t^3 - 3t^2 + 1) * P0 +
//        (t^3 - 2t^2 + t) * T0 +
//        (-2t^3 + 3t^2) * P1 +
//        (t^3 - t^2) * T1

// T0 = tangente en P0, T1 = tangente en P1
// T0 = 0.5 * (P1 - P_{-1})
// T1 = 0.5 * (P2 - P0)
```

## NURBS (Non-Uniform Rational B-Spline)

```
// B-Spline con pesos (racional)
// Permite cónicas exactas (círculos, elipses)

// P(t) = sum( N_i,k(t) * w_i * P_i ) / sum( N_i,k(t) * w_i )

// w_i = peso del punto de control
// w_i > 1: curva se acerca al punto
// w_i < 1: curva se aleja del punto
// w_i = 0: punto no afecta la curva
```

## Perlin Noise

```
// 2D Perlin Noise
function noise2D(x, y):
  // 1. Encontrar celda
  x0 = floor(x), y0 = floor(y)
  x1 = x0 + 1, y1 = y0 + 1
  
  // 2. Gradients (pseudo-random)
  g00 = gradient(x0, y0)
  g01 = gradient(x0, y1)
  g10 = gradient(x1, y0)
  g11 = gradient(x1, y1)
  
  // 3. Distances
  dx0 = x - x0, dy0 = y - y0
  dx1 = x - x1, dy1 = y - y0
  
  // 4. Dot products
  s = dot(g00, (dx0, dy0))
  t = dot(g10, (dx1, dy0))
  u = dot(g01, (dx0, dy1))
  v = dot(g11, (dx1, dy1))
  
  // 5. Interpolate
  sx = smoothstep(dx0)  // 3x^2 - 2x^3
  a = lerp(s, t, sx)
  b = lerp(u, v, sx)
  sy = smoothstep(dy0)
  return lerp(a, b, sy)

// Octaves: sumar noise a diferentes frecuencias
function fbm(x, y, octaves):
  value = 0
  amplitude = 1
  frequency = 1
  for i in 0..octaves:
    value += amplitude * noise2D(x * frequency, y * frequency)
    amplitude *= 0.5
    frequency *= 2
  return value
```

### Simplex Noise (optimización de Perlin)

```
// 2D: usa simplex grid (triángulos) en lugar de cuadrados
// 3D: usa tetraedros
// Más rápido, menos direcciones visibles

// 2D:
// 1. Transformar a skewed space
// 2. Encontrar simplex (triángulo)
// 3. Interpolar con gradientes

// Ventaja: O(n) en lugar de O(2^n)
// (2D: 3 puntos en lugar de 4)
```

### Voronoi Noise (Worley Noise)

```
// Basado en puntos aleatorios (feature points)
// Para cada punto, calcular distancia al feature point más cercano

function worley(x, y):
  // 1. Encontrar celda
  cell_x = floor(x), cell_y = floor(y)
  
  // 2. Buscar en vecindad 3x3
  min_dist = inf
  for dx in -1..1:
    for dy in -1..1:
      fp = random_point(cell_x + dx, cell_y + dy)
      dist = distance((x, y), fp)
      min_dist = min(min_dist, dist)
  
  return min_dist

// Variantes:
// F1: distancia al punto más cercano
// F2: distancia al segundo punto más cercano
// F2-F1: patrón celular
```

## Procedural Generation

### Terrain (Heightmap)

```
// 1. Generar heightmap con Perlin Noise / fbm
// 2. Aplicar erosión (thermal, hydraulic)
// 3. Colorear según altura (agua, arena, hierba, roca, nieve)

// Erosión térmica:
// Para cada celda:
//   if slope > threshold:
//     dif = slope - threshold
//     move = dif * erosion_rate * delta
//     height -= move
//     neighbor += move

// Erosión hídrica:
// 1. Simular lluvia
// 2. Calcular flujo (d8 o d-infinity)
// 3. Transportar sedimento
// 4. Depositar
```

### Fractals

```
// Mandelbrot set
// Para cada punto c:
//   z = 0
//   for n in 0..max_iter:
//     z = z^2 + c
//     if |z| > 2: break
//   color = n / max_iter

// Julia set
// Fijar c, variar z inicial

// Sierpinski triangle
// 1. Triángulo equilátero
// 2. Encontrar punto medio de cada lado
// 3. Conectar puntos medios (forma triángulo central)
// 4. Recursión en los 3 triángulos exteriores

// Koch snowflake
// 1. Línea
// 2. Dividir en 3
// 3. Reemplazar segmento medio con 2 lados de triángulo equilátero
// 4. Recursión
```

### L-Systems

```
// Gramática formal para plantas

// Símbolos:
// F: avanzar
// +: girar derecha
// -: girar izquierda
// [: guardar estado
// ]: restaurar estado

// Reglas:
// F -> F[+F]F[-F]F

// Iteración 0: F
// Iteración 1: F[+F]F[-F]F
// Iteración 2: F[+F]F[-F]F[+F[+F]F[-F]F]F[+F]F[-F]F[-F[+F]F[-F]F]F[+F]F[-F]F

// Interpretación:
// F: dibujar línea
// +/-: rotar ángulo
// [/]: push/pop stack (posición y ángulo)

// Parámetros:
// ángulo = 25.7°
// paso = 5
// iteraciones = 5
```

### Diamond-Square Algorithm

```
// Generar terreno fractal

// 1. Iniciar 4 esquinas con valores aleatorios
// 2. Diamond step: valor del centro = promedio de esquinas + random
// 3. Square step: valor de los puntos medios = promedio de vecinos + random
// 4. Reducir rango del random
// 5. Recursión

// grid_size = 2^n + 1
// roughness = 0.5 (factor de decaimiento)

function diamond_square(grid, size, roughness):
  half = size / 2
  if half < 1: return
  
  // Diamond step
  for y in 0..grid_size-1, step=size:
    for x in 0..grid_size-1, step=size:
      avg = (grid[y][x] + grid[y][x+size] + grid[y+size][x] + grid[y+size][x+size]) / 4
      grid[y+half][x+half] = avg + random(-roughness, roughness)
  
  // Square step
  for y in 0..grid_size-1, step=half:
    for x in 0..grid_size-1, step=half:
      if grid[y][x] is empty:
        count = 0
        sum = 0
        for (nx, ny) in neighbors:
          if grid[ny][nx] is not empty:
            sum += grid[ny][nx]
            count += 1
        grid[y][x] = sum / count + random(-roughness, roughness)
  
  diamond_square(grid, half, roughness * 0.5)
```

### Poisson Disc Sampling

```
// Distribuir puntos uniformemente sin clustering

// 1. Iniciar con punto aleatorio
// 2. K = 30 intentos por punto
// 3. Para cada punto activo:
//    Generar punto aleatorio en anillo [r, 2r]
//    Si no hay vecinos más cerca de r:
//      Agregar punto
// 4. Repetir hasta no más puntos activos

// r = radio mínimo
// Ventaja: distribución natural, sin patrones regulares
// Uso: spawn points, muestreo, texturas

// Bridson's algorithm (más eficiente):
// 1. Grid de tamaño r/sqrt(2)
// 2. Cada celda puede tener 0 o 1 puntos
// 3. Para cada punto, buscar vecinos en 5x5 celdas
```

### Wave Function Collapse (WFC)

```
// Generar imágenes/texturas basado en un input

// 1. Analizar input: extraer patrones NxN
// 2. Para cada celda del output, mantener lista de posibles patrones
// 3. Elegir celda con menor entropía (menos opciones)
// 4. Colapsar: elegir un patrón al azar
// 5. Propagar: actualizar vecinos según restricciones
// 6. Repetir hasta que todo esté colapsado

// Si una celda tiene 0 opciones: backtrack o reiniciar
// Usa: generación de mapas, texturas, niveles
```

## Animation Curves

### Curve Editors

```
// Keyframes: puntos (tiempo, valor, tangente_in, tangente_out)
// Interpolación entre keyframes: Bézier, Hermite, o linear

// Tipos de tangente:
// - Auto: calculado automáticamente
// - Flat: tangente horizontal
// - Linear: tangente = pendiente entre keyframes
// - Fixed: tangente manual
// - Step: sin interpolación (cambio instantáneo)

// Easing curves:
// - In: aceleración
// - Out: desaceleración
// - In-Out: acelerar + desacelerar
// - Custom: curve editor
```

### Spline-based Animation

```
// Animación de objetos a lo largo de una curva
// Posición = curve(t)
// Orientación = tangent(t) o normal(t)

// Velocidad constante:
// Reparametrizar por longitud de arco
// t_new = arc_length(t) / total_length

// Banking: inclinación en curvas
// bank_angle = k * curvature
```

## Error común: Perlin noise con artefactos

```
// INCORRECTO: Usar solo 1 octava
// Resultado: demasiado suave

// CORRECTO: Usar múltiples octavas (fbm)
// 4-8 octavas es el sweet spot

// INCORRECTO: Gradients no normalizados
// Resultado: patrones visibles

// CORRECTO: Normalizar gradients
```

## Error común: Bézier con inflexiones

```
// INCORRECTO: Control points alineados
// P0=(0,0), P1=(1,1), P2=(2,2), P3=(3,3)
// Resultado: línea recta

// CORRECTO: Offset perpendicular
// P0=(0,0), P1=(0,1), P2=(2,1), P3=(2,0)
// Resultado: curva suave

// INCORRECTO: Loop en la curva
// Control points que se cruzan
// Resultado: self-intersection

// CORRECTO: Verificar monotonicidad
// Si x(t) y y(t) son monótonos, no hay loops
```

## Error común: Pathfinding sin smoothing

```
// INCORRECTO: Seguir waypoints exactos
// Resultado: movimiento robótico

// CORRECTO: Aplicar easing o Bézier
// Interpolar entre waypoints con curva

// INCORRECTO: Velocidad constante en path
// Resultado: aceleraciones bruscas

// CORRECTO: Reparametrizar por longitud
// Velocidad = constante, no t
```

## Error común: Terrain sin erosion

```
// INCORRECTO: Raw fbm
// Resultado: terreno "mullido", sin detalles

// CORRECTO: Aplicar erosión
// Thermal: suaviza picos
// Hydraulic: crea valles y ríos

// INCORRECTO: Altura = color directamente
// Resultado: transiciones bruscas

// CORRECTO: Usar gradientes
// Transición suave entre biomas
```
