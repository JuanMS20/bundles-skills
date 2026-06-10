# Matrices y Transformaciones 3D

## Matrices básicas

### Matriz identidad (4x4)
```
| 1  0  0  0 |
| 0  1  0  0 |
| 0  0  1  0 |
| 0  0  0  1 |
```

### Matriz de traslación (T)
```
| 1  0  0  tx |
| 0  1  0  ty |
| 0  0  1  tz |
| 0  0  0  1  |
```

### Matriz de escala (S)
```
| sx  0   0   0 |
| 0   sy  0   0 |
| 0   0   sz  0 |
| 0   0   0   1 |
```

### Matriz de rotación (R) - eje X
```
| 1  0      0       0 |
| 0  cos(θ) -sin(θ) 0 |
| 0  sin(θ)  cos(θ) 0 |
| 0  0      0       1 |
```

### Matriz de rotación (R) - eje Y
```
| cos(θ)  0  sin(θ) 0 |
| 0       1  0       0 |
| -sin(θ) 0  cos(θ) 0 |
| 0       0  0       1 |
```

### Matriz de rotación (R) - eje Z
```
| cos(θ) -sin(θ) 0  0 |
| sin(θ)  cos(θ) 0  0 |
| 0       0      1  0 |
| 0       0      0  1 |
```

## Multiplicación de matrices

```
// A * B (column-major)
for i in 0..3:
  for j in 0..3:
    C[i][j] = A[i][0]*B[0][j] + A[i][1]*B[1][j] + A[i][2]*B[2][j] + A[i][3]*B[3][j]
```

**Orden importa:** A * B ≠ B * A
**Convención:** Column-major (OpenGL) vs Row-major (DirectX)

## Transformaciones compuestas

```
// M = T * R * S (escalar primero, rotar, trasladar)
// Aplicar a punto: P' = M * P

// En código (column-major):
M = T * R * S
P_h = (x, y, z, 1)  // Homogeneous coordinates
P'_h = M * P_h
P' = (P'_h.x, P'_h.y, P'_h.z)
```

## Cámara (LookAt)

```
// Cámara en eye, mirando a target, con up vector
forward = normalize(target - eye)
right = normalize(cross(forward, up))
up_new = cross(right, forward)

// View matrix
View = | right.x    right.y    right.z   -dot(right, eye)   |
       | up_new.x   up_new.y   up_new.z  -dot(up_new, eye)  |
       | -forward.x -forward.y -forward.z dot(forward, eye)  |
       | 0          0          0          1                   |
```

## Proyección perspectiva

```
// FOV = field of view (vertical), aspect = width/height
// near, far = clipping planes

f = 1 / tan(FOV / 2)

Projection = | f/aspect  0   0                    0                    |
             | 0         f   0                    0                    |
             | 0         0   (far+near)/(near-far) (2*far*near)/(near-far) |
             | 0         0  -1                    0                    |
```

## Proyección ortográfica

```
// left, right, bottom, top, near, far
Projection = | 2/(right-left)  0              0               -(right+left)/(right-left) |
             | 0               2/(top-bottom) 0               -(top+bottom)/(top-bottom) |
             | 0               0              -2/(far-near)    -(far+near)/(far-near)      |
             | 0               0              0                1                          |
```

## Quaterniones

```
// Rotación de θ alrededor de eje (x, y, z)
// q = (w, x, y, z)
w = cos(θ/2)
x = sin(θ/2) * axis.x
y = sin(θ/2) * axis.y
z = sin(θ/2) * axis.z

// Normalizar
length = sqrt(w^2 + x^2 + y^2 + z^2)
q = q / length

// Quaternion a matriz 3x3
| 1-2y²-2z²   2xy-2zw     2xz+2yw    |
| 2xy+2zw     1-2x²-2z²   2yz-2xw    |
| 2xz-2yw     2yz+2xw     1-2x²-2y²  |

// Multiplicación de quaternions (composición de rotaciones)
// q1 * q2 = rotar por q2 primero, luego q1
q.w = q1.w*q2.w - q1.x*q2.x - q1.y*q2.y - q1.z*q2.z
q.x = q1.w*q2.x + q1.x*q2.w + q1.y*q2.z - q1.z*q2.y
q.y = q1.w*q2.y - q1.x*q2.z + q1.y*q2.w + q1.z*q2.x
q.z = q1.w*q2.z + q1.x*q2.y - q1.y*q2.x + q1.z*q2.w

// Rotar vector v por quaternion q
// v' = q * v_q * q^-1
// donde v_q = (0, v.x, v.y, v.z)
// q^-1 = (w, -x, -y, -z) / |q|²
```

**Ventajas de quaternions sobre matrices:**
- No suffer gimbal lock
- Interpolación sencilla (slerp)
- Más eficiente para rotación pura

## Slerp (Spherical Linear Interpolation)

```
// Interpolar entre dos quaternions q1 y q2
// t = 0 → q1, t = 1 → q2

dot = q1.x*q2.x + q1.y*q2.y + q1.z*q2.z + q1.w*q2.w

// Si dot < 0, invertir q2 para tomar el camino más corto
if dot < 0:
  q2 = -q2
  dot = -dot

// Clamp dot
if dot > 0.9995:
  // Lineal si son muy cercanos
  q = q1 + t*(q2 - q1)
  return normalize(q)

θ0 = acos(dot)
θ = θ0 * t
sinθ = sin(θ)
sinθ0 = sin(θ0)

s1 = cos(θ) - dot * sinθ / sinθ0
s2 = sinθ / sinθ0

q = q1*s1 + q2*s2
```

## Normal Matrix

```
// Para transformar normales correctamente (no usar la model matrix)
// Normal = (Model^-1)^T
// O si la model matrix solo tiene rotación y escala uniforme:
// Normal = Model (escalar primero, rotar, trasladar)

// Para escala no uniforme:
normalMatrix = transpose(inverse(modelMatrix))
normal_world = normalize(normalMatrix * normal_local)
```

## Error común: Escalar normales

```
// INCORRECTO: Transformar normal con model matrix
normal_world = modelMatrix * normal_local

// CORRECTO: Usar normal matrix
normal_world = normalize(transpose(inverse(modelMatrix)) * normal_local)
```

## Transformación de coordenadas (pipeline completo)

```
Local -> World -> View -> Clip -> NDC -> Screen

1. Local: coordenadas del modelo
2. World: modelMatrix * local
3. View: viewMatrix * world
4. Clip: projectionMatrix * view
5. NDC: clip.xyz / clip.w
6. Screen: (ndc.x * 0.5 + 0.5) * width, (ndc.y * 0.5 + 0.5) * height
```

## Billboard (sprite que mira a cámara)

```
// Extraer rotación de la view matrix y transponerla
billboardMatrix = |
  viewMatrix[0][0]  viewMatrix[1][0]  viewMatrix[2][0]  position.x |
  viewMatrix[0][1]  viewMatrix[1][1]  viewMatrix[2][1]  position.y |
  viewMatrix[0][2]  viewMatrix[1][2]  viewMatrix[2][2]  position.z |
  0                 0                 0                 1          |
```

## Raycasting desde mouse (screen → world)

```
// 1. Mouse (x, y) a NDC (-1 a 1)
ndc_x = (2.0 * mouse_x) / screen_width - 1.0
ndc_y = 1.0 - (2.0 * mouse_y) / screen_height

// 2. Ray en clip space
ray_clip = (ndc_x, ndc_y, -1.0, 1.0)

// 3. Ray en eye space
ray_eye = inverse(projection) * ray_clip
ray_eye = (ray_eye.x, ray_eye.y, -1.0, 0.0)

// 4. Ray en world space
ray_world = inverse(view) * ray_eye
ray_world = normalize(ray_world.xyz)

// 5. Ray: origin = camera_pos, direction = ray_world
```

## AABB en 3D

```
// Axis-Aligned Bounding Box
struct AABB {
  min: Vec3,
  max: Vec3
}

// Transformar AABB con matriz
// NO transformar min/max directamente
// Transformar los 8 vértices y recalcular min/max
vertices = [
  (min.x, min.y, min.z), (max.x, min.y, min.z),
  (min.x, max.y, min.z), (max.x, max.y, min.z),
  (min.x, min.y, max.z), (max.x, min.y, max.z),
  (min.x, max.y, max.z), (max.x, max.y, max.z)
]

transformed = []
for v in vertices:
  transformed.append(transform(v, matrix))

new_min = min(transformed)
new_max = max(transformed)
```

## Error común: Transformar AABB directamente

```
// INCORRECTO: AABB rotado no es AABB
new_min = M * min
new_max = M * max

// CORRECTO: Transformar vértices y recalcular
// O usar OBB (Oriented Bounding Box) si necesitás precisión
```

## Frustum culling

```
// Extraer 6 planos del frustum de la matriz View * Projection
// Para cada plano: ax + by + cz + d = 0
// Un objeto está fuera si está completamente detrás de un plano

// Test AABB vs frustum
for plane in frustum_planes:
  // Encontrar el vértice de la AABB más alejado del plano
  p = |
    plane.x > 0 ? max.x : min.x,
    plane.y > 0 ? max.y : min.y,
    plane.z > 0 ? max.z : min.z
  |
  if dot(plane, p) + plane.d < 0:
    return OUTSIDE

return INSIDE
```

## Screen-space bounding box

```
// Projectar AABB a screen space
// Devolver 2D rect para occlusion queries

min_screen = inf
max_screen = -inf
for v in aabb_vertices:
  world = model * v
  clip = projection * view * world
  ndc = clip.xyz / clip.w
  screen = (ndc.x * 0.5 + 0.5 * width, ndc.y * 0.5 + 0.5 * height)
  min_screen = min(min_screen, screen)
  max_screen = max(max_screen, screen)

return (min_screen, max_screen)
```
