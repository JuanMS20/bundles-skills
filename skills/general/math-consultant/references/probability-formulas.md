# Probabilidad y Aleatoriedad para Game Dev

## Distribuciones

### Uniforme
```
// random() devuelve [0, 1)
valor = min + (max - min) * random()
```

### Normal (Gaussiana)
```
// Box-Muller
u1 = random()
u2 = random()
z = sqrt(-2 * ln(u1)) * cos(2 * PI * u2)
valor = media + desviacion * z
```

### Triangular
```
// Valores concentrados entre min y max, pico en mode
// Rejection sampling simple
u = random()
v = random()
if u > v:
  swap(u, v)
valor = min + (max - min) * v
```

### Exponencial
```
// Más valores bajos, pocos altos
// λ = rate (inverso de media)
valor = -ln(1 - random()) / lambda
```

### Bernoulli (coin flip)
```
// P éxito, (1-P) fracaso
exito = random() < p
```

## Loot Tables

### Weighted Random
```
// Items con pesos relativos
function weighted_random(items):
  total = sum(item.weight for item in items)
  r = random() * total
  acumulado = 0
  for item in items:
    acumulado += item.weight
    if r < acumulado:
      return item
  return items[-1]  // fallback
```

**Error común:** Usar `r <= acumulado`. Usar `r < acumulado` para evitar que el último item nunca se seleccione si r == total.

### Probability Table (probabilidades absolutas)
```
// Items con probabilidades que suman 100%
function probability_table(items):
  r = random()
  acumulado = 0
  for item in items:
    acumulado += item.probability
    if r < acumulado:
      return item
```

### Nested Loot Table (tablas anidadas)
```
// Un drop puede ser otra tabla
function nested_loot(table):
  item = weighted_random(table)
  if item.subtable:
    return nested_loot(item.subtable)
  return item
```

### Pity System (garantía)
```
// Después de N intentos sin éxito, aumentar chance
class PitySystem:
  base_chance = 0.05
  pity_increment = 0.05
  max_pity = 20
  attempts = 0

  function roll():
    chance = base_chance + (attempts * pity_increment)
    if random() < chance:
      attempts = 0
      return success
    attempts += 1
    if attempts >= max_pity:
      attempts = 0
      return success  // Guaranteed
    return failure
```

**Error común:** No resetear `attempts` después del éxito. El sistema se vuelve imposible de balancear.

## Spawn Rates

### Constante (por segundo)
```
// Spawn rate: 2 enemigos por segundo
if random() < spawn_rate * delta:
  spawn()
```

### Con cooldown
```
// Evitar spawns masivos
if time_since_last_spawn >= min_cooldown:
  if random() < spawn_rate * delta:
    spawn()
    time_since_last_spawn = 0
```

### Variable (según distancia al jugador)
```
// Más enemigos cerca del jugador
spawn_rate = base_rate * (1 + proximity_factor / distance_to_player)
```

## Randomness Quality

### Perlin Noise (continuidad espacial)
```
// Para terreno, viento, movimiento orgánico
// Valores cercanos en espacio = valores cercanos en output
value = perlin(x, y)  // Ó octave-based noise
```

### Seeded Random (determinista)
```
// Mismo seed = misma secuencia
rng = seed_random(seed)
value = rng.next()
```

### Shuffle (Fisher-Yates)
```
// Barajar array sin bias
for i from n-1 down to 1:
  j = random_int(0, i)
  swap(array[i], array[j])
```

**Error común:** Usar `sort` con comparador random. Eso no produce una permutación uniforme.

## A/B Testing (balance)

### Two-proportion z-test
```
// ¿La versión A tiene mejor conversión que B?
p1 = conversions_A / visitors_A
p2 = conversions_B / visitors_B
p = (conversions_A + conversions_B) / (visitors_A + visitors_B)
se = sqrt(p * (1-p) * (1/visitors_A + 1/visitors_B))
z = (p1 - p2) / se

// z > 1.96 -> 95% significancia
// z > 2.58 -> 99% significancia
```

## RNG en Multiplayer

### Deterministic (client-side prediction)
```
// Seed compartido, misma secuencia
server_seed = hash(game_state)
client_seed = server_seed

// Ambos calculan el mismo resultado
if deterministic_roll(server_seed, entity_id) < 0.5:
  // Sincronizado
```

### Authoritative (server-side)
```
// Server genera, client recibe
result = server_rng.next()
client.apply(result)
```
