# Matemáticas Avanzadas para Game Dev

## Ecuaciones Diferenciales

### Spring (Harmonic Oscillator)

```
// Fuerza = -k * x - c * v
// k = stiffness, c = damping

// Euler explícito (inestable para k grandes):
// a = -k * x - c * v
// v += a * dt
// x += v * dt

// Verlet (más estable):
// x_new = 2*x - x_prev + (-k*x - c*(x-x_prev)/dt) * dt^2
// x_prev = x
// x = x_new

// Semi-implicit Euler (estable y simple):
// v += (-k * x - c * v) * dt
// x += v * dt

// Parámetros críticos:
// - Overdamped: c^2 > 4*k (no oscila, lento)
// - Underdamped: c^2 < 4*k (oscila, rápido)
// - Critically damped: c^2 = 4*k (rápido sin oscilar)

// Frecuencia natural:
// ω = sqrt(k)
// Periodo = 2*PI / ω

// Damping ratio:
// ζ = c / (2 * sqrt(k))
// ζ < 1: underdamped
// ζ = 1: critically damped
// ζ > 1: overdamped
```

### Pendulum

```
// θ'' = -(g/L) * sin(θ)

// Pequeños ángulos: sin(θ) ≈ θ
// θ'' = -(g/L) * θ
// Periodo = 2*PI * sqrt(L/g)

// Grandes ángulos: integrar numéricamente
// θ += ω * dt
// ω += -(g/L) * sin(θ) * dt

// Damping: añadir -c * ω
// Driving: añadir F * cos(ω_drive * t)
```

### Double Pendulum (Caótico)

```
// Dos pendulum acoplados
// No tiene solución analítica
// Integrar con Runge-Kutta 4

// Sistema de ecuaciones:
// θ1'' = f(θ1, θ2, ω1, ω2)
// θ2'' = g(θ1, θ2, ω1, ω2)

// Sensibilidad a condiciones iniciales:
// Cambio de 0.0001 en θ0 → trayectoria completamente diferente
```

### Orbital Mechanics

```
// Fuerza gravitacional: F = G * m1 * m2 / r^2
// Aceleración: a = F / m1 = G * m2 / r^2

// Integración:
// a = G * M / |r|^3 * r
// v += a * dt
// pos += v * dt

// Energía total:
// E = 0.5 * m * v^2 - G * M * m / r
// E < 0: órbita elíptica
// E = 0: parabólica
// E > 0: hiperbólica

// Velocity Verlet (más preciso para órbitas):
// v_half = v + 0.5 * a * dt
// pos += v_half * dt
// a_new = G * M / |pos|^3 * pos
// v = v_half + 0.5 * a_new * dt
```

### Runge-Kutta 4 (RK4)

```
// Integración numérica de ecuaciones diferenciales

// dy/dt = f(t, y)

// k1 = f(t, y)
// k2 = f(t + dt/2, y + dt*k1/2)
// k3 = f(t + dt/2, y + dt*k2/2)
// k4 = f(t + dt, y + dt*k3)

// y_new = y + dt/6 * (k1 + 2*k2 + 2*k3 + k4)

// Ventaja: error O(dt^4), mucho más preciso que Euler
// Desventaja: 4 evaluaciones de f por paso
```

## Optimización Numérica

### Gradient Descent

```
// Minimizar función f(x)

// x_new = x - learning_rate * gradient(f, x)

// Learning rate:
// - Muy grande: diverge
// - Muy pequeño: lento
// - Adaptive: Adam, RMSprop

// Momentum:
// v = β * v + (1-β) * gradient
// x = x - learning_rate * v

// Adam (Adaptive Moment Estimation):
// m = β1 * m + (1-β1) * g
// v = β2 * v + (1-β2) * g^2
// m_hat = m / (1-β1^t)
// v_hat = v / (1-β2^t)
// x = x - lr * m_hat / (sqrt(v_hat) + ε)
```

### Simulated Annealing

```
// Evitar mínimos locales

// 1. Iniciar con solución aleatoria
// 2. Generar vecino aleatorio
// 3. Si vecino es mejor: aceptar
// 4. Si vecino es peor: aceptar con probabilidad exp(-ΔE / T)
// 5. Reducir temperatura T *= cooling_rate
// 6. Repetir

// T inicial: grande (acepta casi todo)
// T final: pequeña (solo acepta mejoras)
// cooling_rate: 0.95-0.99

// Uso: balance de juego, optimización de layouts, placement
```

### Genetic Algorithms

```
// Población de soluciones, evolucionar

// 1. Iniciar población aleatoria
// 2. Evaluar fitness de cada individuo
// 3. Seleccionar padres (proporcional a fitness)
// 4. Crossover: combinar genes
// 5. Mutación: cambiar genes aleatoriamente
// 6. Reemplazar población
// 7. Repetir

// Representación:
// - Binaria: bits
// - Real: números
// - Permutación: orden
// - Árbol: expresiones

// Uso: generación de niveles, balance, NPC behavior
```

## Teoría de Juegos

### Minimax

```
// Árbol de decisiones, alternar jugadores

// Valor de nodo:
// Si es mi turno: max(valor de hijos)
// Si es turno del oponente: min(valor de hijos)

// Valor de hoja: evaluación del estado

// Pseudocódigo:
function minimax(node, depth, maximizing):
  if depth == 0 or node is terminal:
    return evaluate(node)
  
  if maximizing:
    value = -inf
    for child in node.children:
      value = max(value, minimax(child, depth-1, false))
    return value
  else:
    value = inf
    for child in node.children:
      value = min(value, minimax(child, depth-1, true))
    return value

// Alpha-Beta pruning:
// Si encontrás un valor mejor que el que ya tenés, podar
function minimax(node, depth, alpha, beta, maximizing):
  if depth == 0 or terminal:
    return evaluate(node)
  
  if maximizing:
    value = -inf
    for child in node.children:
      value = max(value, minimax(child, depth-1, alpha, beta, false))
      if value >= beta:
        break  // Beta cutoff
      alpha = max(alpha, value)
    return value
  else:
    value = inf
    for child in node.children:
      value = min(value, minimax(child, depth-1, alpha, beta, true))
      if value <= alpha:
        break  // Alpha cutoff
      beta = min(beta, value)
    return value
```

### Expectiminimax

```
// Minimax con nodos de azar (dados, cartas)

// Nodos:
// - Max: jugador (maximiza)
// - Min: oponente (minimiza)
// - Chance: azar (valor esperado)

// Valor de nodo chance:
// value = sum( probabilidad * valor_del_hijo )

// Pseudocódigo:
function expectiminimax(node, depth):
  if depth == 0 or terminal:
    return evaluate(node)
  
  if node.type == MAX:
    return max( expectiminimax(child, depth-1) for child in node.children )
  if node.type == MIN:
    return min( expectiminimax(child, depth-1) for child in node.children )
  if node.type == CHANCE:
    return sum( child.probability * expectiminimax(child, depth-1) for child in node.children )
```

### Monte Carlo Tree Search (MCTS)

```
// Para juegos con estado grande (Go, Chess, etc.)

// 4 pasos:
// 1. Selection: seleccionar nodo con UCB1
//    UCB1 = win_rate + C * sqrt(ln(parent_visits) / visits)
// 2. Expansion: agregar hijos no visitados
// 3. Simulation: jugar hasta el final con política aleatoria
// 4. Backpropagation: actualizar visitas y wins

// Repetir N veces
// Elegir movimiento con mayor win_rate

// Uso: AI de juegos de mesa, RTS, cualquier juego con estado grande
```

## Spatial Hashing

### Grid Spatial Hash

```
// Dividir el mundo en celdas
// Cada objeto se almacena en la celda donde está

// Celda de un punto:
cell_x = floor(x / cell_size)
cell_y = floor(y / cell_size)

// Insertar objeto:
grid[cell_x, cell_y].add(object)

// Buscar vecinos:
// Revisar 3x3 celdas alrededor de la celda actual
for dx in -1..1:
  for dy in -1..1:
    for obj in grid[cell_x + dx, cell_y + dy]:
      if distance(obj, query) < threshold:
        return obj

// Ventaja: O(1) inserción, O(k) búsqueda (k = promedio de objetos por celda)
// Desventaja: poco eficiente si los objetos son muy grandes
```

### Quadtree

```
// División recursiva del espacio

// Nodo:
// - bounds: rectángulo
// - objects: lista de objetos
// - children: 4 nodos (NW, NE, SW, SE)
// - capacity: máximo de objetos antes de dividir

// Insertar:
// 1. Si objeto está fuera de bounds: ignorar o guardar en root
// 2. Si nodo es hoja y objects < capacity: agregar
// 3. Si nodo es hoja y objects >= capacity: dividir
// 4. Recursión en el hijo correspondiente

// Dividir:
// - Crear 4 hijos con bounds más pequeños
// - Redistribuir objetos entre hijos
// - Marcar nodo como no-hoja

// Buscar:
// 1. Si query no intersecta bounds: retornar
// 2. Si es hoja: revisar todos los objetos
// 3. Si no es hoja: recursión en hijos que intersectan

// Ventaja: adaptativo a densidad de objetos
// Desventaja: más complejo que grid
```

### Octree (3D)

```
// Igual que quadtree pero en 3D
// 8 hijos por nodo (dividir en 2 por cada eje)

// Uso: colisiones en 3D, culling, voxel engines
```

### R-tree

```
// Árbol balanceado para áreas rectangulares
// Cada nodo contiene MBR (Minimum Bounding Rectangle)

// Insertar:
// 1. Encontrar hoja con menor expansión de MBR
// 2. Si hoja está llena: split

// Split:
// - Linear split: elegir dos objetos más lejanos
// - Quadratic split: minimizar área total

// Buscar:
// - Recursión en nodos cuyo MBR intersecta la query

// Ventaja: eficiente para objetos de tamaño variable
// Desventaja: más complejo que quadtree
```

## Estadística Avanzada

### Regresión Lineal

```
// Ajustar y = mx + b a datos

// n = número de datos
// sum_x = sum(x_i)
// sum_y = sum(y_i)
// sum_xy = sum(x_i * y_i)
// sum_x2 = sum(x_i^2)

// m = (n*sum_xy - sum_x*sum_y) / (n*sum_x2 - sum_x^2)
// b = (sum_y - m*sum_x) / n

// R^2 (coeficiente de determinación):
// R^2 = 1 - (sum((y_i - y_pred)^2) / sum((y_i - y_mean)^2))
// R^2 = 1: perfecto
// R^2 = 0: sin correlación
// R^2 < 0: peor que promedio

// Error estándar:
// SE = sqrt(sum((y_i - y_pred)^2) / (n - 2))
```

### Correlación de Pearson

```
// r = cov(X, Y) / (std(X) * std(Y))
// r = [-1, 1]
// r = 1: correlación perfecta positiva
// r = -1: correlación perfecta negativa
// r = 0: sin correlación

// r = sum((x_i - x_mean)(y_i - y_mean)) / sqrt(sum((x_i-x_mean)^2) * sum((y_i-y_mean)^2))

// Uso: balance de juego (ej: ¿el tiempo de partida correlaciona con el score?)
```

### Inferencia Bayesiana

```
// P(H|D) = P(D|H) * P(H) / P(D)

// H = hipótesis
// D = datos
// P(H) = prior (creencia inicial)
// P(D|H) = likelihood (probabilidad de los datos dada la hipótesis)
// P(H|D) = posterior (creencia actualizada)

// Ejemplo: ¿Cuál es la probabilidad de que un jugador sea tóxico dado que flamea?
// P(tóxico|flamea) = P(flamea|tóxico) * P(tóxico) / P(flamea)

// P(flamea|tóxico) = 0.8 (80% de tóxicos flamean)
// P(tóxico) = 0.1 (10% de jugadores son tóxicos)
// P(flamea) = 0.15 (15% de jugadores flamean)
// P(tóxico|flamea) = 0.8 * 0.1 / 0.15 = 0.53

// Uso: matchmaking, detección de tóxicos, balance adaptativo
```

### Markov Chains

```
// Sistema de estados, probabilidades de transición

// Matriz de transición P:
// P[i][j] = probabilidad de ir de estado i a j
// Cada fila suma 1

// Estado después de n pasos:
// state_n = state_0 * P^n

// Estado estacionario:
// π = π * P
// (autovector de autovalor 1)

// Uso:
// - Progresión de niveles (estado = nivel, transición = éxito/fracaso)
// - Comportamiento de NPC (estado = acción, transición = probabilidad)
// - Loot progression (estado = tier, transición = drop)
```

### Hidden Markov Models (HMM)

```
// Markov chain donde los estados no son observables

// Estados: S1, S2, ...
// Observaciones: O1, O2, ...
// Emission probabilities: P(Ot | St)

// Problemas:
// 1. Evaluación: P(O|model) -> Forward algorithm
// 2. Decodificación: secuencia de estados más probable -> Viterbi algorithm
// 3. Aprendizaje: estimar parámetros -> Baum-Welch

// Uso: reconocimiento de patrones de jugador, predicción de comportamiento
```

### A/B Testing (Test de hipótesis)

```
// Comparar dos versiones (A vs B)

// 1. Definir métrica (conversion rate, retention, etc.)
// 2. Dividir jugadores aleatoriamente
// 3. Medir métrica en cada grupo
// 4. Test estadístico

// Test de proporciones (z-test):
// p_A = conversions_A / n_A
// p_B = conversions_B / n_B
// p_pooled = (conversions_A + conversions_B) / (n_A + n_B)
// SE = sqrt(p_pooled * (1-p_pooled) * (1/n_A + 1/n_B))
// z = (p_A - p_B) / SE

// p-value:
// p < 0.05 -> significativo al 95%
// p < 0.01 -> significativo al 99%

// Tamaño de muestra:
// n = (Z_{α/2} + Z_β)^2 * (p_A*(1-p_A) + p_B*(1-p_B)) / (p_A - p_B)^2
```

### Confidence Intervals

```
// Intervalo de confianza para una proporción:
// CI = p ± Z * sqrt(p*(1-p)/n)

// Z para 95%: 1.96
// Z para 99%: 2.58

// Uso: "El win rate de este personaje es 52% ± 3% con 95% de confianza"
```

## Error común: Euler explícito inestable

```
// INCORRECTO: Euler explícito para springs
// v += a * dt
// x += v * dt
// Resultado: si dt > 2/sqrt(k), explota

// CORRECTO: Semi-implicit Euler o Verlet
// v += a * dt
// x += v * dt
// (más estable, aunque todavía tiene límite)

// CORRECTO: RK4 para precisión
// Pero: 4x más costoso

// Regla: dt < 1/(2*sqrt(k)) para Euler explícito
```

## Error común: Gradient descent sin momentum

```
// INCORRECTO: SGD puro
// x = x - lr * gradient
// Resultado: oscilaciones, lento

// CORRECTO: Adam o momentum
// v = β * v + (1-β) * gradient
// x = x - lr * v

// O: RMSprop
// cache = γ * cache + (1-γ) * gradient^2
// x = x - lr * gradient / sqrt(cache + ε)
```

## Error común: Minimax sin depth limit

```
// INCORRECTO: Minimax sin límite
// Resultado: explota recursivamente

// CORRECTO: Limitar depth
// depth = 5-10 para juegos rápidos
// depth = 20+ para juegos lentos

// CORRECTO: Iterative deepening
// depth = 1, 2, 3, ... hasta que se acabe el tiempo
// Usar el mejor resultado del último depth completado
```

## Error común: Quadtree sin límite de profundidad

```
// INCORRECTO: Dividir hasta que haya 1 objeto por nodo
// Resultado: árbol gigante, muchos nodos vacíos

// CORRECTO: Capacidad + profundidad máxima
// capacity = 10
// max_depth = 10

// CORRECTO: Si un objeto cruza máltiples celdas
// Guardarlo en el nodo padre o en todas las celdas que intersecta
```

## Error común: Spatial hash con tamaño de celda incorrecto

```
// INCORRECTO: celda = 1px
// Resultado: cada objeto en su propia celda, búsqueda O(n)

// INCORRECTO: celda = 1000px
// Resultado: todos los objetos en la misma celda, búsqueda O(n)

// CORRECTO: celda = 2 * tamaño promedio de objeto
// O: celda = tamaño del query más común
// Regla: la mayoría de las celdas debería tener 1-5 objetos
```

## Error común: Bayes sin prior actualizado

```
// INCORRECTO: Usar siempre el mismo prior
// P(tóxico) = 0.1
// Resultado: ignora la historia del jugador

// CORRECTO: Actualizar prior con cada observación
// P(tóxico|historial) = P(tóxico) * P(historial|tóxico) / P(historial)
// El prior se vuelve más preciso con más datos

// CORRECTO: Usar Beta distribution para prior flexible
// Beta(α, β) = prior sobre la probabilidad
// α = éxitos + 1, β = fracasos + 1
// Posterior = Beta(α + éxitos, β + fracasos)
```
