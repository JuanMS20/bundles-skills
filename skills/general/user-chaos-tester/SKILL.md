---
name: user-chaos-tester
description: "Testing como usuario torpe: explora, interactúa y verifica la app desde la perspectiva de alguien que NO conoce el sistema. Detecta flujos rotos, forms que aceptan basura, navegación confusa, y estados de error invisibles. Multi-plataforma: web, móvil, juegos, desktop, CLI. Use when: 'prueba como usuario', 'usuario torpe', 'chaos testing', 'exploratory testing', post-judge validation, 'qué pasa si hago X', o después de un pipeline dev-qa-judge para encontrar anomalías que los otros no detectaron."
tags: [testing, exploratory, chaos, ux, post-judge]
---

# User Chaos Tester

Testing desde la perspectiva de un usuario que no sabe cómo funciona el sistema. Los bundles anteriores (dev, qa, judge) revisan el código desde dentro. Este skill revisa la app desde **fuera**.

Funciona en cualquier plataforma: web, móvil, juegos, desktop, CLI. No asumas web.

## Cuándo usar

- **Post-judge:** Después de que el pipeline dev-qa-judge apruebe, como capa final
- **Antes de launch:** Cuando la app "funciona técnicamente" pero no se ha probado como usuario real
- **Post-regresión:** Después de cambios grandes para confirmar que nothing obvious broke

## FASE 0 — Levantamiento

1. Levantar la app (según plataforma: npm start, python app.py, expo start, steam, etc.)
2. Capturar URL/port/endpoint/ejecutable
3. Si NO se puede levantar → ABORT, documentar por qué

## FASE 1 — Detección de plataforma + Observación (5 min)

### Detectar plataforma
Identificar ANTES de interactuar — determina qué vectores de FASE 2 aplicar:
- **Web:** URLs, browser, DevTools disponible
- **Móvil:** app en dispositivo/emulador, gestures, rotación
- **Juego:** game loop, save states, controller input
- **Desktop:** ventanas, integración con OS
- **CLI:** terminal, stdin/stdout

### Observación visual
Sin tocar nada, solo mirar:
- ¿La UI se ve completa o hay elementos cortados/rotos?
- ¿Los botones tienen labels claros?
- ¿Los formularios tienen labels en los inputs?
- ¿Hay loading states visibles?
- ¿Los colores/textos son legibles?

**Output:** Lista de problemas visuales con capturas/screenshot.

### Paridad de funcionalidades entre plataformas (OBLIGATORIO si app multiplataforma)

Si la app corre en más de una plataforma (web desktop + web mobile, o web + móvil nativo, etc.), **DEBES** verificar que las funcionalidades existen en AMBAS. No basta con que "se vea bien".

**Proceso:**
1. En FASE 2, ejecuta los vectores en TODAS las plataformas detectadas
2. Compara qué controles/funcionalidades existen en cada una
3. Reporta como CRITICAL cualquier funcionalidad que exista en una plataforma pero no en otra

**Ejemplos comunes de desparidad:**
- Password toggle (ojo para ver contraseña) existe en desktop pero no en mobile
- Tooltips visibles en desktop pero no en touch
- Hover states que no existen en mobile (no hay hover en touch)
- Sidebar colapsable que se pierde en mobile sin alternativa
- Dropdowns que se comportan diferente (click vs tap)
- Forms con campos que se ocultan en mobile pero son necesarios
- Botones de acción que desaparecen en mobile (editar, borrar)

**Output de esta sub-fase:**
```
PARIDAD ENTRE PLATAFORMAS:
  Desktop: [lista de funcionalidades clave]
  Mobile:  [lista de funcionalidades clave]
  FALTAN EN MOBILE: [lista]
  FALTAN EN DESKTOP: [lista]
```

## FASE 2 — Interacción Caótica (15 min)

Simular un usuario que NO sabe qué hace. No es un atacante — es alguien confundido, apurado, o despistado.

Ejecutar los vectores UNIVERSALES (cualquier plataforma) y luego los ESPECÍFICOS de la plataforma detectada en FASE 1.

### 2.1 Universales — Autenticación
- Login con campos vacíos
- Login con credenciales inventadas
- "Olvidé contraseña" — ¿funciona el flujo?
- ¿Se puede acceder a funcionalidad sin estar logueado?

### 2.2 Universales — Entrada de datos
- Enviar forms vacíos o incompletos
- Strings con caracteres especiales: ñ, á, emoji, unicode
- Strings larguísimos (1000+ chars)
- Números negativos donde se esperan positivos
- Decimales donde se esperan enteros
- Fechas inválidas (30 de febrero, año 9999)

### 2.3 Universales — Confusión de usuario
Lo que un torpe de verdad hace — no ataques, errores genuinos:
- Click en el botón equivocado (botones pegados a otros)
- Abandonar un flujo a mitad (llenar form, no terminar, irse a otra pantalla)
- Hacer las cosas en orden incorrecto (ej: checkout sin items, editar registro inexistente)
- Escribir en el campo incorrecto (nombre en campo de email)
- Presionar Enter/submit cuando no debería
- Presionar "atrás"/cancelar cuando algo está cargando

### 2.4 Universales — Timing
- Click rápido múltiples veces en el mismo botón
- Submit form dos veces rápido
- Navegar Away mientras algo carga

### 2.5 Universales — Concurrencia y state pollution
- Abrir el mismo recurso en 2 instancias → editar ambos → guardar ambos
- Abrir edit en instancia 1, borrar el recurso en instancia 2, guardar en instancia 1
- Crear y borrar el mismo recurso simultáneamente

### 2.6 Universales — Copy-paste (involuntario)
- Pegar texto con formato desde Word/Excel (RTF/HTML embebido)
- Pegar caracteres RTL (árabe, hebreo) que invierten el orden del texto
- Pegar strings inmensos (10,000+ chars) del portapapeles
- Pegar datos de Excel con saltos de línea y tabs en campos simples

### 2.7 Web — Navegación y browser
- Botón "atrás" del navegador después de submit
- Recargar página a mitad de proceso
- Abrir la misma URL en múltiples tabs
- Cambiar la URL manualmente (forzar rutas inexistentes)
- Navegar a /admin, /debug, /api, /.env

### 2.8 Web — Red y requests
- DevTools → Network → Slow 3G → cargar página, submit, esperar timeout
- DevTools → Network → Offline del TAB → operación → volver Online → verificar recuperación
- Interceptar requests con DevTools y modificar body/headers antes de enviar
- Abortar request a mitad (botón stop del navegador)

NOTA: NO desconectar la red del sistema operativo. Usar SOLO el throttle de
DevTools del navegador. Desconectar la red del SO puede cortar conexiones
del propio agente o de otros servicios del host.

### 2.9 Web — Inputs que resultan ser peligrosos
Un usuario torpe pega algo sin saber que es peligroso:
- Pegar texto que resulta ser SQL (' OR 1=1 --)
- Pegar HTML sin saber (<script>alert(1)</script>)
- Pegar path traversal sin saber (../../etc/passwd)

NOTA: Solapa con reverse-audit. Aquí el framing es "pegó algo sin querer", no "atacante deliberado".

### 2.10 Móvil — Gestures e interrupciones
- Rotar pantalla mid-flujo (portrait ↔ landscape)
- Backgrounding: abrir otra app a mitad de submit, volver
- Notificación/call entrante que interrumpe un flujo
- Matar la app (swipe up / force close) a mitad de operación
- Gestures accidentales: swipe cuando se intentaba tap, long-press sin querer
- Re-abrir desde cold start después de cierre forzado

### 2.11 Móvil — Offline real
- Modo avión del DISPOSITIVO (no del SO del agente) → operación → volver online
- Cambiar de WiFi a datos móviles mid-descarga
- App en background por horas → volver → ¿estado preservado?

### 2.15 Móvil — Paridad de funcionalidades (OBLIGATORIO si multiplataforma)

Si la app es responsive/web y tiene variantes desktop+mobile, **DEBES** verificar que las funcionalidades críticas existen en mobile:

**Checklist mínimo por funcionalidad:**
- [ ] Password toggle (ojo) — ¿existe en mobile? Si no → CRITICAL
- [ ] Todos los botones de acción (crear, editar, borrar) — ¿visibles en mobile?
- [ ] Todos los form fields — ¿completamente visibles y editables?
- [ ] Navegación — ¿todos los menús accesibles en mobile?
- [ ] Feedback (toasts, errores, loading) — ¿visible en mobile?
- [ ] Modales/dialogs — ¿se abren y cierran correctamente?
- [ ] Scroll — ¿todo el contenido es scrolleable?

**Cómo verificar:**
1. Navegar a cada pantalla en viewport mobile (375px o menos)
2. Buscar cada funcionalidad que existe en desktop
3. Intentar usarla — si no existe el control o no funciona → CRITICAL
4. Documentar: funcionalidad X existe en desktop pero no en mobile

### 2.12 Juego — Estado y persistencia
- Pausar/salir del juego mid-loading o mid-cutscene
- Save mientras algo escribe → ¿corrupción?
- Load un save antiguo en versión nueva del juego
- Input spam (mantener presionado todos los botones)
- Controller disconnect mid-action
- Alt-tab / minimizar durante gameplay

### 2.13 Desktop — Ventana y OS
- Resize ventana a mínimo durante operación
- Minimizar mid-submit
- Multi-monitor: mover ventana entre monitores con DPI distinto
- Cerrar ventana con X durante operación en curso
- Cambiar DPI scaling del SO con la app abierta

### 2.14 CLI — Input y señales
- Ctrl+C a mitad de operación
- Pipe input malformado (echo "garbage" | command)
- Enviar EOF (Ctrl+D) antes de tiempo
- Env vars vacíos o malformados
- Stdin cerrado inesperadamente

## FASE 3 — Verificación de Resultados

Para cada interacción que modificó datos:
1. Verificar en DB/store que el cambio se reflejó correctamente
2. Verificar que NO se crearon registros duplicados
3. Verificar que los constraints (unique, NOT NULL, FK) se respetan
4. Verificar que los soft deletes funcionan (si aplica)

**Templates de verificación:**
```sql
-- SQL (Supabase/Postgres/MySQL)
SELECT * FROM <table> ORDER BY created_at DESC LIMIT 5;
SELECT <field>, COUNT(*) FROM <table> GROUP BY <field>;
SELECT COUNT(*) FROM <table> WHERE <foreign_key> NOT IN (SELECT id FROM <related_table>);
```
NoSQL/local: adaptar al sistema (Firebase, SQLite local, save files, prefs).

## FASE 4 — Reporte

Output: tabla con 4 columnas:

| # | Acción | Resultado | Severidad |
|---|--------|-----------|-----------|
| 1 | Login vacío | Acepta, muestra error genérico | WARNING |
| 2 | SQL pegado en login | Bloqueado | OK |
| 3 | Borrar sin confirmación | Se borra directamente | CRITICAL |

**Severidades:**
- **CRITICAL:** Datos perdidos, seguridad comprometida, funcionalidad rota
- **WARNING:** UX confusa, sin feedback, edge case no manejado
- **INFO:** Comportamiento inesperado pero no dañino
- **OK:** Se manejó correctamente

## Anti-patterns

- **No confundir con QA sistemático:** Este skill NO reemplaza tests automatizados. Complementa.
- **No testing de performance:** Para eso está judge-performance-budget.
- **No testing de seguridad profundo:** Para eso está reverse-audit. Los vectores de SQL/XSS aquí son desde la perspectiva del usuario que pega algo sin saber.
- **No asumir web:** Ejecutar universales SIEMPRE. Aplicar específicos solo según plataforma detectada.
- **No asumir que "funciona":** Un botón que no da error NO significa que haga lo correcto. Verificar en DB/store.

## Pitfalls

- **NUNCA desconectar la red del sistema:** El agente vive en la misma máquina que la app.
  Para web: DevTools → Network → Throttling (Slow 3G, Offline del TAB). Para móvil: modo avión del dispositivo.
  Si no hay forma segura de simular red degradada → omitir, no arriesgar.
- **State pollution entre instancias:** Abrir múltiples tabs/instancias puede dejar estado inconsistente.
  Verificar DB/store después de cada interacción multi-instancia.
- **Plataforma no detectada:** Si no identificaste la plataforma en FASE 1, los vectores específicos no aplican.
  Re-ejecutar detección antes de FASE 2.
- **browser_console con expresiones async:** Expresiones IIFE como `(async () => { ... })()`
  o `fetch(...).then(...)` retornan `null` (NoneType) en browser_console — la promise no resuelve
  antes de que el resultado se capture. Para evaluar JS async, en su lugar: (a) ejecuta código que
  guarde el resultado en una variable global (`window._probe = result`) y luego lee esa variable
  en una segunda llamada síncrona, o (b) usa `terminal` con curl para probes HTTP directos.
- **Strings extremos (1000+ chars) pueden colgar el browser:** Si escribes 1000+ caracteres en
  un campo via browser_type y luego haces submit, browser_snapshot puede hacer timeout (30s) o
  bloquearse. Si el browser se cuelga después de enviar datos extremos: (a) NO reintentar
  browser_snapshot idéntico (loop), (b) verificar el resultado directamente en DB/store vía SQL,
  (c) navegar a la app de nuevo con browser_navigate para resetear el estado del browser.
- **No adivinar nombres de columnas:** Antes de hacer queries de verificación, enumera el schema
  real (`SELECT column_name FROM information_schema.columns WHERE table_name = 'X'`). Adivinar
  `email` o `created_at` cuando la tabla usa `username` o solo `updated_at` genera errores
  que rompen el flujo de verificación.
- **CAPTCHA/anti-bot bloquea testing automatizado de auth:** Cloudflare Turnstile, reCAPTCHA, y
  similares bloquean los intentos de login automatizados (via browser automation o curl directo).
  El testing de autenticación (vacío, inválido, SQL injection) solo funciona hasta que el captcha
  interviene. **Workaround:** (a) el usuario hace login manual y la sesión queda en el browser,
  (b) el agente continúa el testing de las páginas autenticadas via Kimi/browser automation,
  (c) los vectores de auth se limitan a lo que se pueda probar ANTES del captcha. Documentar
  qué vectores no se pudieron probar por CAPTCHA en el reporte.
- **SPA route mismatch (sidebar label vs URL real):** En SPAs con routing client-side, el label
  visible en la UI (ej: "Auditoría") puede no coincidir con la ruta URL real (ej: `/audit-log`).
  Navegar por URL usando el label como ruta da 404. **Workaround:** siempre navegar via los links
  de la UI (click en sidebar), no construyendo URLs a mano. Si necesitas la URL real, extraerla
  del `href` del link: `document.querySelector('a').href`.
- **Formularios sin feedback visual:** En apps modernas con validación server-side, el submit de
  un form vacío o con datos inválidos puede NO producir ninguna respuesta visible — el form
  simplemente no hace nada. Esto NO es un bug del testing; es un hallazgo legítimo (WARNING:
  sin feedback de validación). Reportarlo como tal, no asumir que "no funcionó la prueba".
- **Kimi WebBridge: clicks en "Eliminar" / acciones destructivas causan timeouts.** Cuando un click
  abre un `window.confirm()` o modal de confirmación, `snapshot` posterior puede colgar (60s timeout).
  Recuperación: navegar de nuevo a la URL actual para resetear el estado del browser, luego verificar
  si la acción se ejecutó (el líder/registro ¿aún existe?). No reintentar el snapshot colgado.
- **Kimi WebBridge: refs `@e` caducan tras cualquier acción DOM.** Después de click, fill, navigate,
  los refs del snapshot anterior son inválidos. Tomar snapshot nuevo ANTES de usar refs viejos.
- **Kimi WebBridge: `evaluate` usa parámetro `code`, NO `script`.** Pasar `{"script":"..."}` falla
  silenciosamente con "code is required".
- **Kimi WebBridge: preferir `evaluate` + JS click sobre `click` con refs.** Cuando los refs `@e`
  se vuelven inconsistentes o el snapshot cambia entre llamadas, usar `evaluate` para encontrar
  y clickar elementos por texto es más robusto:
  ```javascript
  // Buscar botón por texto y clickar
  Array.from(document.querySelectorAll('button'))
    .find(b => b.textContent.includes('Nuevo')).click();
  // Navegar via link de sidebar
  document.querySelector('a[href*=lideres]').click();
  ```
  Esto evita el problema de refs caducados y es más rápido que snapshot → parse → click.
- **Kimi WebBridge: `navigate` resetea TODO el contexto JS.** Variables, interceptores, monkey-patches
  se pierden al navegar. Para mantener estado: (a) escribir a `localStorage` antes de navegar,
  (b) leer de `localStorage` después, (c) para interceptores, usar click SPA en vez de navigate
  directo (el click interno no resetea el contexto).
- **Supabase anon key: obtenerla via fetch monkey-patch en runtime.** El client está en module
  closure (inaccesible desde `window`), pero pasa la key como header `apikey` en cada request.
  **Técnica:** (1) monkey-patchear `window.fetch` para capturar el header, (2) disparar un click
  SPA que cause una request, (3) leer `window.__capturedKeys`. Ver `reverse-audit` >
  `references/supabase-security-testing.md` para el código completo. Alternativa: leer
  `.env.local` del repo local si está disponible.

## Relación con otros bundles

- **dev-cycle:** Antes de este skill. Dev construye.
- **qa-bundle:** Antes de este skill. QA prueba sistemáticamente.
- **judge:** Antes de este skill. Judge verifica técnicamente.
- **user-chaos (bundle):** Este skill es el CORE del bundle post-judge.
- **reverse-audit:** Complementa — uno prueba UX, otro prueba seguridad desde fuera.
- **judge-ux-vibe-check:** Complementa — chaos prueba si se rompe, vibe-check prueba si es usable.
