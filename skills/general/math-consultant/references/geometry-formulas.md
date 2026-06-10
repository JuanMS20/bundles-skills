# Fórmulas de Geometría para Game Dev

## Coordenadas

### Conversión polar -> cartesiano
```
x = r * cos(θ)
y = r * sin(θ)
```

### Conversión cartesiano -> polar
```
r = sqrt(x^2 + y^2)
θ = atan2(y, x)
```

## Vectores

### Operaciones básicas
```
// Suma
v = (v1.x + v2.x, v1.y + v2.y)

// Escalar
v = (v.x * s, v.y * s)

// Longitud (magnitud)
|v| = sqrt(v.x^2 + v.y^2)

// Normalizado
v_norm = v / |v|   (verificar |v| != 0)

// Distancia entre dos vectores
|v1 - v2| = sqrt((v1.x - v2.x)^2 + (v1.y - v2.y)^2)
```

### Producto punto (Dot Product)
```
dot = v1.x * v2.x + v1.y * v2.y
// o en 3D:
dot = v1.x * v2.x + v1.y * v2.y + v1.z * v2.z
```

**Interpretaciones:**
- `dot = |v1| * |v2| * cos(θ)` → ángulo entre vectores
- `dot > 0` → ángulo < 90° (misma dirección)
- `dot = 0` → perpendicular
- `dot < 0` → ángulo > 90° (opuestos)
- `dot = |v1| * |v2|` → paralelos, mismo sentido
- `dot = -|v1| * |v2|` → paralelos, sentido opuesto

**Uso:** Ángulo, proyección, facing, iluminación, sorting por profundidad.

### Producto cruz (Cross Product) en 2D
```
cross = v1.x * v2.y - v1.y * v2.x
```

**Interpretación:**
- `cross > 0` → v2 está a la izquierda de v1
- `cross < 0` → v2 está a la derecha de v1
- `cross = 0` → colineales
- `|cross| = |v1| * |v2| * sin(θ)` → área del paralelogramo

**Uso:** Determinar sentido de giro, área, orientación, colinealidad.

### Proyección de vector
```
// Proyección de v1 sobre v2
scalar = dot(v1, v2) / dot(v2, v2)
proj = (v2.x * scalar, v2.y * scalar)
```

## Colisiones

### AABB (Axis-Aligned Bounding Box)
```
overlap = (
  a.x < b.x + b.w &&
  a.x + a.w > b.x &&
  a.y < b.y + b.h &&
  a.y + a.h > b.y
)
```

**Penetración:**
```
overlap_x = min(a.x + a.w, b.x + b.w) - max(a.x, b.x)
overlap_y = min(a.y + a.h, b.y + b.h) - max(a.y, b.y)
```

### Círculo vs Círculo
```
dist_sq = (c1.x - c2.x)^2 + (c1.y - c2.y)^2
collision = dist_sq <= (c1.r + c2.r)^2
```

**Penetración:**
```
dist = sqrt(dist_sq)
penetration = (c1.r + c2.r) - dist
normal = (c2.x - c1.x, c2.y - c1.y) / dist
```

### Punto en Círculo
```
dist_sq = (px - cx)^2 + (py - cy)^2
inside = dist_sq <= r^2
```

### Punto en Rectángulo
```
inside = (
  px >= rect.x &&
  px < rect.x + rect.w &&
  py >= rect.y &&
  py < rect.y + rect.h
)
```

### Punto en Triángulo (barycentric)
```
// P en triángulo ABC?
// Áreas con signo
Area = 0.5 * cross(B - A, C - A)
Area1 = 0.5 * cross(B - P, C - P)
Area2 = 0.5 * cross(C - P, A - P)
Area3 = 0.5 * cross(A - P, B - P)

inside = (abs(Area1 + Area2 + Area3 - Area) < epsilon)
```

### Línea vs Círculo
```
// Distancia del centro al segmento AB
AP = P - A
AB = B - A
t = dot(AP, AB) / dot(AB, AB)
t = clamp(t, 0, 1)
closest = A + AB * t
dist_sq = |P - closest|^2
intersect = dist_sq <= r^2
```

### Raycasting (rayo vs segmento)
```
// Rayo: P + t * D, t >= 0
// Segmento: A + u * (B - A), u en [0, 1]
// Resolver:
// P.x + t * D.x = A.x + u * (B.x - A.x)
// P.y + t * D.y = A.y + u * (B.y - A.y)

// Sistema 2x2:
denom = D.x * (A.y - B.y) - D.y * (A.x - B.x)
if denom == 0: // Paralelos
  return false

t = ((A.x - P.x) * (A.y - B.y) - (A.y - P.y) * (A.x - B.x)) / denom
u = ((A.x - P.x) * D.y - (A.y - P.y) * D.x) / denom

intersect = (t >= 0 && u >= 0 && u <= 1)
hit_point = P + D * t
```

## Rotaciones

### Rotar punto alrededor de origen
```
x' = x * cos(θ) - y * sin(θ)
y' = x * sin(θ) + y * cos(θ)
```

### Rotar punto alrededor de centro arbitrario
```
dx = x - cx
dy = y - cy
x' = cx + dx * cos(θ) - dy * sin(θ)
y' = cy + dx * sin(θ) + dy * cos(θ)
```

### Ángulo entre dos direcciones
```
// signed ángulo (más corto)
cross = v1.x * v2.y - v1.y * v2.x
dot = v1.x * v2.x + v1.y * v2.y
angle = atan2(cross, dot)
```

### Interpolación lineal (Lerp)
```
lerp(a, b, t) = a + (b - a) * t
// t = 0 -> a, t = 1 -> b
```

### Interpolación esférica (Slerp) para vectores
```
// Para vectores unitarios
angle = acos(dot(v1, v2))
slerp = (sin((1-t)*angle) / sin(angle)) * v1 + (sin(t*angle) / sin(angle)) * v2
```

## Triángulos

### Área
```
// Coordinates
area = 0.5 * abs((x1(y2 - y3) + x2(y3 - y1) + x3(y1 - y2)))

// Vectors
area = 0.5 * |cross(B - A, C - A)|
```

### Centroid (centro de masa)
```
cx = (x1 + x2 + x3) / 3
cy = (y1 + y2 + y3) / 3
```

### Circumcenter (centro del círculo circunscrito)
```
d = 2 * (x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2))
ux = ((x1^2 + y1^2)*(y2 - y3) + (x2^2 + y2^2)*(y3 - y1) + (x3^2 + y3^2)*(y1 - y2)) / d
uy = ((x1^2 + y1^2)*(x3 - x2) + (x2^2 + y2^2)*(x1 - x3) + (x3^2 + y3^2)*(x2 - x1)) / d
```
