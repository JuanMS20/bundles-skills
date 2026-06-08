---
name: judge-performance-budget
description: "Mide performance real con números — multi-plataforma. Web: Lighthouse, bundle, FCP/LCP. Juegos: FPS, frame time, draw calls. Móvil: cold start, battery. CLI: startup time. Load testing básico. Use when: 'es rápido?', performance check, 'tarda en cargar', juzgar performance, 'optimiza'."
---

# JUDGE PERFORMANCE BUDGET — Números o excusas?

## Principio: "Se siente rápido" no es métrica.

La IA no entiende performance. Importa `moment.js` completo para
formatear una fecha. Pone imágenes de 4MB. Hace fetch síncronos.
Tu trabajo es MEDIR y poner números sobre la mesa.

## FASE 0 — Detectar plataforma

Antes de medir, saber QUÉ medir:
- **Web**: package.json con React/Vue/Svelte/Next, index.html
- **Juego**: Canvas, WebGL, Unity, Godot, game loop visible
- **Móvil**: React Native, Flutter, Swift, Kotlin, APK/IPA
- **CLI**: script con argparse/click/commander, entrada por terminal
- **Desktop**: Electron, Tauri, Qt, .NET, exe/AppImage
- **Backend/API**: servidor HTTP, endpoints REST/GraphQL

Si hay múltiples (ej: web app + API backend), evaluar ambas.

## Budgets Universales (TODAS las plataformas)

| Métrica | Budget Máximo | Herramienta |
|---------|---------------|-------------|
| Memory usage | < 150MB crecimiento | `ps`, Task Manager, Activity Monitor |
| Startup time | < 2s (first interaction) | Timer desde launch |
| API response time (p95) | < 500ms | Logs / APM / curl timing |
| Sin memory leaks | Crecimiento < 10MB en 5 min de uso | Memory profiler |

## Budgets Web

| Métrica | Budget Máximo | Herramienta |
|---------|---------------|-------------|
| First Contentful Paint | < 1.8s | Lighthouse |
| Largest Contentful Paint | < 2.5s | Lighthouse |
| Time to Interactive | < 3.8s | Lighthouse |
| Total Bundle JS | < 500KB gzip | `npx vite-bundle-visualizer` |
| Imágenes above-the-fold | < 200KB cada una | Lighthouse |
| Main thread blocking | < 200ms tareas largas | Lighthouse |

### Verificación Web

```bash
# Bundle analysis
npx vite-bundle-visualizer   # o @next/bundle-analyzer / webpack-bundle-analyzer

# Lighthouse
npx lighthouse http://localhost:3000 --output=json
```

- [ ] Librerías gigantes importadas completas? (lodash, moment)
- [ ] Tree-shaking funcionando? (no imports de `*`)
- [ ] El vendor chunk es > 300KB?
- [ ] Performance score > 80
- [ ] Long tasks > 50ms?
- [ ] Forced synchronous layout?
- [ ] Memory leaks? (DevTools → Memory → Heap snapshots)

## Budgets Juegos

| Métrica | Budget Máximo | Herramienta |
|---------|---------------|-------------|
| FPS | >= 60 (>= 30 móvil) | Stats del engine / DevTools |
| Frame time | < 16.67ms (60 FPS) | `performance.now()` / engine profiler |
| Draw calls / frame | < 200 (2D) / < 3000 (3D) | Engine profiler |
| Load time (nivel/escena) | < 3s | Timer |
| Input lag | < 100ms | Manual / profiler |

- [ ] FPS estable? (no drops recurrentes)
- [ ] Memory crece al jugar múltiples rondas? (leak)
- [ ] Hay stuttering en momentos de alta acción?
- [ ] El game loop tiene allocaciones por frame? (GC pressure)

## Budgets Móvil

| Métrica | Budget Máximo | Herramienta |
|---------|---------------|-------------|
| Cold start | < 2s | Instruments (iOS) / Profiler (Android) |
| Memory pico | < 200MB | OS profiler |
| Battery drain (10 min) | < 5% | Manual / OS metrics |
| APK/IPA size | < 50MB | `ls -lh` del paquete |

## Budgets CLI

| Métrica | Budget Máximo | Herramienta |
|---------|---------------|-------------|
| Startup time (`--help`) | < 500ms | `time miapp --help` |
| Output streaming | No buffer todo en memoria | Probar con dataset grande |
| Memory | < 100MB | `ps` / Activity Monitor |

## Budgets Desktop

| Métrica | Budget Máximo | Herramienta |
|---------|---------------|-------------|
| Startup | < 2s | Timer |
| IPC latency (Electron/Tauri) | < 100ms | Profiler |
| Memory | < 300MB | Task Manager / Activity Monitor |

## Performance bajo Carga

"Escalable" requiere saber qué pasa con muchos usuarios, no solo uno.
Aplica a: web con backend, APIs, multiplayer games, cualquier servicio con red.

| Métrica | Budget | Herramienta |
|---------|--------|-------------|
| Concurrent users soportados | Definido y verificado | k6 / artillery / locust / wrk |
| p95 response time bajo carga | < 1000ms (100 usuarios) | k6 / artillery |
| Error rate bajo carga | < 1% | k6 / artillery |
| Max throughput | Medido y documentado | k6 / artillery |

```bash
# k6 (recomendado)
k6 run --vus 50 --duration 30s script.js

# Alternativa simple sin tools
seq 100 | xargs -P 10 -I {} curl -s -o /dev/null -w '%{time_total}\n' http://localhost:3000/api/health
```

**Load testing con Python via `execute_code` (sin instalar nada):**
Cuando no hay k6/artillery instalados y necesitas números rápido, Python stdlib es suficiente:

```python
import requests, time, concurrent.futures, statistics

URL = "https://app.example.com"

def fetch(url):
    start = time.time()
    try:
        resp = requests.get(url, timeout=10)
        return resp.status_code, time.time() - start
    except Exception:
        return 0, time.time() - start

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(fetch, URL) for _ in range(20)]
    results = [f.result() for f in futures]

latencies = [r[1] for r in results]
codes = [r[0] for r in results]
print(f"Success: {sum(1 for c in codes if c==200)}/20")
print(f"p50: {statistics.median(latencies)*1000:.0f}ms | p95: {sorted(latencies)[18]*1000:.0f}ms")
```

Produce p50, p95, error rate y success count en ~20 líneas. Suficiente para budgets de pre-lanzamiento (2-20 usuarios). Para production load testing real, usar k6.

- [ ] Se definió cuántos usuarios concurrentes debe soportar?
- [ ] Se probó bajo carga real?
- [ ] El p95 se mantiene bajo 1s con carga?
- [ ] No hay errores 5xx bajo carga?
- [ ] Hay rate limiting o backpressure configurado?

Si NO se puede ejecutar load testing (sin tools, sin entorno):
DECLARAR "Performance bajo carga: NO VERIFICADO". No asumir que escala.

## Patrones de RECHAZO (errores clásicos de IA)

### Web
```javascript
// ❌ Importar todo lodash
import _ from 'lodash';
// ✅ Importar solo lo necesario
import debounce from 'lodash/debounce';

// ❌ Imagen sin optimizar
<img src="/foto-4k.jpg" />
// ✅ Imagen optimizada con lazy loading
<img src="/foto-4k.webp" loading="lazy" width="800" height="600" />

// ❌ Re-render de todo el árbol
// ✅ Memoización donde aplica
const MemoChild = memo(ExpensiveChild);
```

### Juegos
```javascript
// ❌ Allocar objetos en el game loop (GC pressure)
function update() { particles.push(new Particle(x, y)); } // cada frame
// ✅ Object pooling
const pool = [];
function update() { const p = pool.pop() || new Particle(); p.reset(x, y); }

// ❌ DOM queries en cada frame
function render() { document.getElementById('score').textContent = score; }
// ✅ Cache referencias
const scoreEl = document.getElementById('score');
```

### Backend
```javascript
// ❌ N+1 queries
for (const user of users) { const posts = await db.query('SELECT * FROM posts WHERE user_id = ?', user.id); }
// ✅ Query batch
const posts = await db.query('SELECT * FROM posts WHERE user_id IN (?)', users.map(u => u.id));

// ❌ Devolver TODO sin paginar
// ✅ Paginar con LIMIT/OFFSET o cursor
```

## Formato de Veredicto

```
## VEREDICTO JUDGE PERFORMANCE BUDGET

### Plataforma: [Web / Juego / Móvil / CLI / Desktop / Backend]

### Estado: [OPTIMIZADO / NECESITA TRABAJO / CRÍTICO]

### Métricas Medidas:
| Métrica | Valor | Budget | Estado |
|---------|-------|--------|--------|
| ... | X | <Y | ✅/❌ |

### Performance bajo Carga:
- Verificado: [SÍ/NO] | p95: Xms | Error rate: X% | Concurrent: N

### Hallazgos:
1. [archivo] — [problema] — impacto: [ALTO/MEDIO/BAJO]

### Quick Wins (bajo esfuerzo, alto impacto):
1. [acción] — impacto estimado: X%

### Score General: [0-100]/100
```

## Reglas de Oro
- **NUNCA** apruebes si hay métricas críticas en rojo (definidas por plataforma)
- **NUNCA** apruebes si hay memory leaks detectados
- **NUNCA** apruebes si la app crashea bajo carga básica (10+ usuarios concurrentes)
- Si hay >3 métricas en rojo -> CRÍTICO. Performance es feature.
- Si NO mediste load testing -> declarar "escalabilidad NO VERIFICADA"
