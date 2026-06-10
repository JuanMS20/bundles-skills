# Fórmulas de Física para Game Dev

## Kinemática 2D/3D

### Movimiento uniformemente acelerado

```
v = v0 + a * t
s = s0 + v0 * t + 0.5 * a * t^2
v^2 = v0^2 + 2 * a * (s - s0)
```

### Salto (proyectil)

**Velocidad inicial para alcanzar altura H:**
```
v0 = sqrt(2 * g * H)          // Simétrico
v0 = (-2 * H) / t_peak         // Asimétrico
```

**Gravedad para alcanzar altura H en tiempo t_peak:**
```
g = (2 * H) / t_peak^2
```

**Alcance horizontal (R) con ángulo θ:**
```
R = (v0^2 * sin(2θ)) / g
```

**Altura máxima (H) con ángulo θ:**
```
H = (v0^2 * sin^2(θ)) / (2 * g)
```

### Movimiento circular

```
// Posición en círculo de radio r, ángulo θ (rad)
x = cx + r * cos(θ)
y = cy + r * sin(θ)

// Velocidad angular -> velocidad lineal
v = ω * r
```

### Fricción

```
// Fricción cinética
f_friction = -μ * N * normalize(v)
// donde N = fuerza normal (mg en superficie plana)
// μ = coeficiente de fricción

// Aplicada a velocidad
v_new = v + f_friction * delta
if |v_new| < threshold:
  v_new = 0  // Detenerse
```

### Impulso y colisión elástica

```
// Velocidades después de colisión 1D (masas m1, m2)
v1' = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
v2' = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)

// Coeficiente de restitución (e):
// e = 1 -> elástica perfecta
// e = 0 -> inelástica perfecta
// e = 0.5 -> semi-elástica
v1' = (v1 * (m1 - e*m2) + v2 * m2 * (1 + e)) / (m1 + m2)
```

## Euler Integration (Frame-based)

```
// Cada frame:
velocity += acceleration * delta
position += velocity * delta

// Problema: error acumulativo en delta grandes
// Solución: Verlet integration para mayor precisión
```

## Verlet Integration

```
// Más preciso para órbitas y oscilaciones
position_new = 2 * position - position_prev + acceleration * delta^2
position_prev = position
position = position_new
```

## Fuerzas comunes

| Fuerza | Fórmula | Notas |
|---|---|---|
| Gravedad | `F = m * g` | `g = 9.8 m/s²` o `g = 500 px/s²` |
| Resorte (Hooke) | `F = -k * (x - x0)` | `k` = rigidez, `x0` = posición de reposo |
| Amortiguamiento | `F = -c * v` | `c` = coeficiente de damping |
| Gravedad planetaria | `F = G * m1 * m2 / r^2` | `G = 6.67e-11` |
| Arrastre (drag) | `F = -0.5 * ρ * v^2 * Cd * A * normalize(v)` | ρ=densidad, Cd=coeficiente, A=área |
