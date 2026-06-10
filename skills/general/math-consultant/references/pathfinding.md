# Pathfinding y Navegación

## A* (A-Star)

```
// Pseudocódigo
open_set = PriorityQueue()  // Ordenado por f = g + h
open_set.add(start, priority=0)
came_from = {}  // Para reconstruir path
g_score = {start: 0}
f_score = {start: heuristic(start, goal)}

while open_set not empty:
  current = open_set.pop()  // Menor f_score
  if current == goal:
    return reconstruct_path(came_from, current)
  
  for neighbor in neighbors(current):
    tentative_g = g_score[current] + cost(current, neighbor)
    if tentative_g < g_score.get(neighbor, inf):
      came_from[neighbor] = current
      g_score[neighbor] = tentative_g
      f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
      if neighbor not in open_set:
        open_set.add(neighbor, priority=f_score[neighbor])

return failure  // No path encontrado
```

### Heurísticas

```
// Manhattan (grid sin diagonales)
h = abs(x1 - x2) + abs(y1 - y2)

// Euclidean (grid con diagonales o espacio libre)
h = sqrt((x1-x2)^2 + (y1-y2)^2)

// Chebyshev (grid con 8 direcciones)
h = max(abs(x1-x2), abs(y1-y2))

// Diagonal distance (8-dir con costo diferente)
h = max(abs(x1-x2), abs(y1-y2)) * D + min(abs(x1-x2), abs(y1-y2)) * D2
// D = costo diagonal, D2 = costo ortogonal

// Octile (variante de Chebyshev con pesos)
h = (abs(dx) + abs(dy)) + (sqrt(2) - 2) * min(abs(dx), abs(dy))
```

### Admissibility

```
// Heurística admissible: nunca sobreestima el costo real
// Si h es admissible, A* encuentra el camino óptimo

// Manhattan es admissible si solo movimientos ortogonales
// Euclidean es admissible para movimiento libre

// Si h(n) = 0 para todo n, A* = Dijkstra (garantiza óptimo pero lento)
// Si h(n) = costo real, A* = greedy (rápido pero no óptimo)
// Balance: h(n) <= costo real, pero lo más cercano posible
```

### Weighted A* (más rápido, menos óptimo)

```
// Multiplicar heurística por ε > 1
// f = g + ε * h
// ε = 1.2: 20% más rápido, camino 20% peor
// ε = 2.0: mucho más rápido, camino peor
```

### Jump Point Search (JPS) - optimización de A* en grids

```
// Sólo para grids uniformes
// En lugar de revisar cada vecino, "salta" hasta puntos relevantes

// Si no hay obstáculos, JPS = 10x más rápido que A*
// Si hay muchos obstáculos, beneficio menor

// Implementación: identificar "jump points" donde la dirección cambia
// o hay vecinos forzados
```

## Dijkstra

```
// A* con h(n) = 0
// Explora en todas las direcciones, garantiza camino más corto

// Use cuando:
// - No hay heurística clara
// - Necesitás todos los caminos desde un punto (flood fill)
// - El grafo es pequeño

// Pseudocódigo idéntico a A* pero f = g (sin heurística)
```

## BFS (Breadth-First Search)

```
// Dijkstra con costo uniforme (todo pesa 1)
// Cola FIFO, no priority queue

queue = [start]
visited = {start}
came_from = {start: None}

while queue:
  current = queue.pop(0)
  if current == goal:
    return reconstruct_path(came_from, current)
  
  for neighbor in neighbors(current):
    if neighbor not in visited:
      visited.add(neighbor)
      came_from[neighbor] = current
      queue.append(neighbor)

return failure
```

**Cuándo usar:**
- Grids sin costos diferentes
- Necesitás el camino con menos pasos
- Explorar conectividad

## DFS (Depth-First Search)

```
// LIFO, usa stack
// No garantiza camino óptimo
// Puede quedarse atrapado en ciclos

// Use cuando:
// - Explorar laberintos (backtracking)
// - No necesitás el camino más corto
// - Búsqueda topológica

stack = [start]
visited = {start}
came_from = {start: None}

while stack:
  current = stack.pop()
  if current == goal:
    return reconstruct_path(came_from, current)
  
  for neighbor in neighbors(current):
    if neighbor not in visited:
      visited.add(neighbor)
      came_from[neighbor] = current
      stack.append(neighbor)
```

## Navmesh (Navigation Mesh)

```
// Grafo de polígonos (triángulos o convexos) en lugar de grid

// Pasos:
1. Generar navmesh desde la geometría del nivel
2. Construir grafo: cada polígono = nodo, bordes compartidos = aristas
3. A* sobre el grafo de polígonos
4. String pulling (Funnel algorithm) para suavizar el camino

// Ventajas:
// - Caminos más naturales (no grid-based)
// - Menos nodos que un grid fino
// - Más rápido para espacios grandes

// Desventajas:
// - Más complejo de implementar
// - Requiere regeneración cuando el nivel cambia
```

## Funnel Algorithm (String Pulling)

```
// Suavizar camino de polígonos en línea recta

// Input: secuencia de polígonos del navmesh
// Output: secuencia de waypoints

left_apex = right_apex = portal_start
path = [portal_start]

for each portal (left, right) in sequence:
  // Update left and right funnel
  if left is inside left_apex:
    left_apex = left
  if right is inside right_apex:
    right_apex = right
  
  // Check if apex crosses
  if left_apex crosses right_apex:
    add apex to path
    reset funnel

add goal to path
```

## Flow Fields

```
// Para multitudes (crowd simulation)
// Calcular un campo de direcciones desde el goal

// 1. Dijkstra desde goal: cada celda guarda distancia al goal
// 2. Para cada celda, dirección = gradiente de distancia (hacia el goal)
// 3. Los agentes siguen el campo

// Ventajas:
// - Miles de agentes sin recalcular path individual
// - Natural crowd avoidance

// Desventajas:
// - Costoso recalcular si el goal cambia
// - Ocupa memoria
```

## Potential Fields

```
// Campo potencial: atractores (goal) + repulsores (obstáculos)

// Atractor: potencial decrece con la distancia al goal
// Repulsor: potencial crece cerca de obstáculos

// Fuerza en cada punto = -gradiente(potencial)
// Movimiento = follow fuerza

// Problema: mínimos locales (atrapado en un "valle")
// Solución: combinar con A* o añadir ruido
```

## RRT (Rapidly-Exploring Random Tree)

```
// Para pathfinding en espacios de alta dimensionalidad
// Ej: brazos robóticos, evasión de obstáculos complejos

// 1. Iniciar árbol en start
// 2. Random sample en el espacio
// 3. Encontrar nodo más cercano en el árbol
// 4. Extender hacia el sample
// 5. Si no hay colisión, agregar al árbol
// 6. Repetir hasta conectar con goal

// RRT* (variante): optimiza el camino encontrado
```

## Path smoothing

```
// Después de A*, suavizar el camino

// 1. Raycast entre waypoints
//    Si waypoint[i] a waypoint[i+2] es visible (sin obstáculos):
//    Eliminar waypoint[i+1]

// 2. Catmull-Rom spline: pasar por todos los puntos con tangente continua

// 3. Bézier curve: suavizar esquinas

// 4. Rounding radius: en cada esquina, añadir arco de radio r
```

## Steering Behaviors

```
// Comportamientos de navegación para agentes

// Seek: ir hacia un target
desired = normalize(target - position) * max_speed
steering = desired - velocity

// Flee: huir de un target
desired = normalize(position - target) * max_speed
steering = desired - velocity

// Arrive: llegar suavemente al target
// desired speed = max_speed si distancia > slowing_radius
// desired speed = max_speed * (distance / slowing_radius) si distancia < slowing_radius

// Pursuit: perseguir un target en movimiento
// Estimar posición futura: target_pos + target_velocity * prediction_time
// Seek a la posición futura

// Evade: huir de un perseguidor en movimiento
// Estimar posición futura del perseguidor
// Flee de esa posición

// Wander: caminar aleatoriamente
// Añadir un pequeño vector aleatorio al steering

// Obstacle avoidance: evitar obstáculos
// Castear rayos hacia adelante, si detectan colisión, steer perpendicular

// Path following: seguir un camino
// Buscar punto más cercano en el path
// Seek al siguiente punto en el path

// Separation: mantener distancia con otros agentes
// Flee de la dirección promedio de los vecinos cercanos

// Cohesion: mantenerse cerca del grupo
// Seek al centro de masa de los vecinos

// Alignment: alinearse con la dirección del grupo
// Steering = dirección promedio de los vecinos - velocity

// Flocking: combinación de Separation + Cohesion + Alignment
```

## Grid-based pathfinding

```
// Representaciones de grid

// 2D array: 0 = walkable, 1 = obstacle
grid = [[0, 0, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0]]

// Bitmask: cada celda = bits (walkable, swimmable, flyable, etc.)
// Tile costs: cada celda = costo de pasar (montaña = 3, camino = 1)

// Diagonal movement:
// - Costo: 1.4 (sqrt(2)) o 2
// - Chequear: si hay obstáculos en ambos vecinos ortogonales, no permitir diagonal
// ("cutting corners")
```

## Hierarchical Pathfinding

```
// Para mapas grandes

// 1. Cluster: dividir el mapa en clusters
// 2. Abstract graph: un nodo por cluster, aristas entre clusters adyacentes
// 3. A* en el abstract graph: encontrar clusters de inicio a goal
// 4. A* en cada cluster: encontrar camino detallado

// Ventaja: A* en 1000x1000 grid = 1M nodos
//         Hierarchical: 10 clusters = 10 nodos + 10 paths de 100 nodos
```

## Error común: No considerar tamaño del agente

```
// INCORRECTO: Pathfind con grid de 1x1 celdas
// Si el agente ocupa 2x2 celdas, puede quedar atascado

// CORRECTO:
// 1. Erode obstacles: expandir obstáculos por radio del agente
// 2. O: pathfind en grid de 2x2 celdas
// 3. O: usar clearance values (distancia al obstáculo más cercano)
```

## Error común: Pathfinding en cada frame

```
// INCORRECTO: Recalcular A* cada frame
// 60fps * 100 enemigos = 6000 A* por segundo

// CORRECTO:
// 1. Recalcular cada N frames o solo cuando el goal cambia
// 2. Replanificar parcialmente (si el path se bloquea, recalcular desde ahí)
// 3. Usar flow fields para multitudes
// 4. Usar steering behaviors para micro-correcciones
```

## Error común: Ignorar movimiento diagonal

```
// INCORRECTO: Solo 4 direcciones
// Camino largo: (0,0) → (0,1) → (0,2) → (1,2) → (2,2)
// = 5 pasos

// CORRECTO: 8 direcciones
// (0,0) → (1,1) → (2,2)
// = 2 pasos (sqrt(2) * 2 ≈ 2.8)
// Más corto y natural

// Pero: si hay obstáculos en (0,1) y (1,0), no permitir (1,1)
```

## Pathfinding con restricciones

```
// Tamaño del agente
// 2x2: expandir obstáculos por 1 celda

// Altura del agente
// Si el agente es 2x2x3, no puede pasar por pasillos de 2x2x2

// Terrain types
// Agua: solo nadadores
// Montaña: solo montañeros
// Puente: todo el mundo

// One-way: puente que se derrumba después de pasar

// Dynamic obstacles: otros agentes, puertas temporales
// Solución: recalcular, steering, o reservation tables
```

## Reservation Tables

```
// Para múltiples agentes en el mismo espacio

// Grid 4D: x, y, time, agent_id
// Cada celda (x, y, t) = reservado por agente A

// Al pathfind:
// 1. Reservar celdas (x, y, t) para cada paso
// 2. Si otra reserva conflictúa, esperar o desviar

// Ventaja: no colisiones, rutas optimizadas
// Desventaja: costoso, requiere sincronización
```

## Reciprocal Velocity Obstacles (RVO)

```
// Para evitar colisiones entre agentes en movimiento

// Cada agente calcula velocidad que evite colisiones con otros
// Considerando que los otros también evitan

// Velocidad nueva = velocidad preferida + ajuste para evitar colisiones
// Recíproco: cada agente asume que el otro también coopera

// Implementación: ORCA (Optimal Reciprocal Collision Avoidance)
```
