---
name: reverse-audit
description: "Análisis ofensivo desde fuera del sistema en cualquier plataforma (web, juegos, móvil, CLI, desktop). Intenta romper TODO lo explotable: OWASP Top 10 (2025), economy exploits, save manipulation, packet injection, enumeración de entidades. Use when: 'auditoría externa', 'reverse audit', 'attack surface', 'intenta romperlo', 'hack it', 'qué ve un atacante', o post-judge para una capa ofensiva adicional."
tags: [security, audit, owasp, attack-surface, exploit, post-judge]
---

# Reverse Audit

Análisis **ofensivo** desde fuera del sistema. No es solo seguridad web — es intentar romper TODO lo que se pueda explotar, en cualquier plataforma. Si es un juego, intentas duping y save editing. Si es una API, intentas IDOR y injection. Si es móvil, intentas APK decompilation y intent injection.

Mentalidad: eres un atacante determinado. Empiezas con probes fáciles y escalas hasta explotación agresiva. No te detienes en "parece seguro" — pruebas.

## Cuándo usar

- **Post-judge:** Capa ofensiva después del pipeline dev-qa-judge
- **Pre-launch:** Antes de exponer la app al mundo
- **Post-cambio:** Después de agregar features nuevas
- **Ad-hoc:** "Intenta romper esto" — en cualquier plataforma

## PRINCIPIO FUNDAMENTAL: Enumeración de Entidades

Antes de atacar, enumerar TODAS las entidades testables del sistema:

| Tipo de sistema | Entidades a enumerar |
|-----------------|---------------------|
| Web/API | Usuarios, roles, endpoints, recursos, tenants |
| Juego | Razas/clases, items, niveles/zonas, NPCs, personajes |
| Móvil | Cuentas, actividades, intents, permisos |
| CLI | Comandos, flags, inputs, env vars |
| Cualquiera | Cualquier categoría con múltiples instancias |

**REGLA:** NO probar una sola entidad y asumir que el resto funciona igual.

1. Listar todas las entidades de cada tipo (query DB, leer configs, explorar UI)
2. Probar al menos 3-5 representativas + edge cases:
   - La primera creada
   - La última creada
   - Una recién creada (puede tener datos incompletos)
   - Una con datos extremos (nombre de 1000 chars, valores negativos)
   - Una inactiva/archivada/soft-deleted
3. Probar combinaciones cross-entity (FASE 3)

**El usuario puede acotar:** "solo prueba usuarios admin" o "solo la raza elf".
Sin especificación → enumerar y probar todo lo accesible.

## FASE 0 — Reconocimiento (5 min)

### 0.1 Detectar plataforma
Identificar antes de atacar — determina qué vectores aplicar:
- **Web:** URLs, browser, DevTools, API endpoints
- **Juego:** game client, save files, network protocol, game state
- **Móvil:** APK/IPA, device/emulator, intents, storage
- **CLI:** stdin/stdout, flags, env vars, signals
- **Desktop:** binaries, files, IPC, registry

### 0.2 Recopilar info (según plataforma)
- **Web:** URL, headers HTTP (curl -I), X-Powered-By, robots.txt, sitemap.xml, .env, .git/config
- **Juego:** formato de saves (JSON/binary/SQLite), protocolo de red (si online), archivos de config, console commands
- **Móvil:** APK (jadx --decompile), AndroidManifest.xml, Info.plist, cert pinning
- **CLI:** help/--help output, man pages, config files
- **Desktop:** binarios, archivos de config, logs, IPC channels

**Técnica de recon para APIs REST (Supabase/PostgREST y similares):**
Los error messages de la API filtran nombres de tablas/recursos reales. Enviar un
GET con un nombre de tabla incorrecto al endpoint REST devuelve sugerencias:
`GET /rest/v1/profiles` → `{"hint":"Perhaps you meant the table 'public.geo_departments'"}`
Esto enumera el schema completo sin auth. Usar nombres en plural (Supabase usa
snake_case plural por convención: `profiles`, `contacts`, `audit_logs`).

### 0.3 Enumerar entidades
Aplicar el PRINCIPIO de enumeración. Listar concretamente:
- ¿Cuántos usuarios/roles existen? ¿Cuáles?
- ¿Cuántos items/razas/niveles? ¿Cuáles?
- ¿Cuántos endpoints/recursos? ¿Cuáles?
- Query DB si hay acceso, sino explorar via UI/API

**Output:** lista de entidades por tipo. Esta lista alimenta TODAS las fases siguientes.

## FASE 1 — OWASP Top 10 (2025) — SOLO WEB

> Si la plataforma NO es web → saltar a FASE 2.

Verificar CADA categoría contra la app, usando las entidades de FASE 0.3:

### A01: Broken Access Control
- Acceder a rutas protegidas sin auth (curl sin token)
- IDOR: cambiar ID en URLs para acceder a datos de otros usuarios
- Bypass de role checks (user → admin)
- Forced browsing a /admin, /debug

### A02: Security Misconfiguration
- Headers de seguridad faltantes (CSP, HSTS, X-Frame-Options)
- CORS con `*`
- Debug mode activo en producción
- Stack traces visibles al usuario
- Default credentials sin cambiar

### A03: Software Supply Chain Failures
- Dependencias con CVEs (npm audit, pip-audit)
- Componentes EOL o sin patch
- Dependencias sin lockfile
- CI/CD sin protección
- Typosquatting

### A04: Cryptographic Failures
- Contraseñas en texto plano o hash débil (MD5, SHA1)
- Tokens sin expiración
- HTTP accesible (sin HTTPS redirect)
- Secrets en client-side code
- Algoritmos deprecados

### A05: Injection
- SQL injection en search/filtros
- XSS reflected y stored
- Command injection (exec/eval con input del usuario)
- Template injection

### A06: Insecure Design
- ¿Falta rate limiting?
- ¿Client-side validation sin server-side?
- ¿Acciones sensibles sin step-up auth?
- ¿Flows que asumen usuario "bien comportado"? (precio en client-side)

### A07: Authentication Failures
- Brute force posible (sin rate limiting en login)
- Sesiones que no expiran
- Password reset con tokens predecibles
- MFA no implementado o bypassable
- Weak password policy

### A08: Software or Data Integrity Failures
- CDN sin SRI
- CI/CD sin firma de artifacts
- Auto-update sin verificación
- Deserialización insegura

### A09: Security Logging and Alerting Failures
- ¿Login fallidos se loggean?
- ¿Alertas por actividad sospechosa?
- ¿Logs revelan info sensible?
- ¿Eventos críticos se auditan?

### A10: Mishandling of Exceptional Conditions
- ¿Qué pasa cuando un servicio externo cae?
- ¿Out-of-memory o disk full?
- ¿Excepciones revelan stack traces?
- ¿Errores de DB dejan transacciones inconsistentes?
- ¿Timeouts colgados indefinidamente?

NOTA: SSRF ya no es categoría propia en 2025. Si la app hace server-side requests
con input del usuario, verificar bajo A01.

## FASE 2 — Vectores de Ataque por Plataforma

Aplicar los vectores de la plataforma detectada en FASE 0.1.
Para CADA vector, probar con múltiples entidades de FASE 0.3.

### 2.1 Web — Attack Surface
**Client-side:**
- Variables globales expuestas (window.__CONFIG, process.env)
- Source maps accesibles en producción
- Comentarios en HTML/JS con info interna
- API keys en JS bundle

**Server-side:**
- Endpoints que no deberían ser públicos
- Rate limiting ausente
- Timeouts ausentes (requests que cuelgan)

**Requests:**
- Modificar body/headers de requests con DevTools/Postman
- Replay de requests (enviar el mismo request 100 veces)
- Race condition: enviar 2 requests de transferencia simultáneos
- GraphQL: introspection habilitada, query depth attacks

### 2.2 Juego — Explotación de mecánicas
**Economía:**
- Comprar cantidad negativa (-1 items) → ¿dinero aumenta?
- Integer overflow: comprar MAX items → ¿precio wrappea a negativo?
- Duping: trade item a otro jugador y cancelar trade simultáneamente
- Vender item que no tienes (send crafted request)
- Price manipulation: cambiar precio en client-side antes de comprar

**Save files:**
- Editar save file (JSON/binary): items, stats, dinero, nivel
- Cargar save corrupto (truncado, campos faltantes, tipos wrong)
- Cargar save de otra cuenta/versión

**Estado del juego:**
- Teleport a coordenadas inválidas (NaN, Infinity, negativos, fuera del mapa)
- Speed hack: modificar velocity/animation timers via memory o packet
- Equipar items de otra clase/raza (send crafted request)
- Usar item en objetivo inválido (item de curación en enemigo, etc.)

**Red (si es online):**
- Packet replay: capturar y reenviar packets de "ganar batalla"
- Packet injection: enviar packets con datos imposibles
- Rate exploit: enviar 1000 packets de "claim reward"

**Lógica:**
- Sequence breaking: trigger evento B antes del prerequisito A
- Skip de validación: saltar un step del tutorial/gacha directamente al reward
- Race condition en sistemas concurrentes (marketplace, trading)

### 2.3 Móvil — Explotación de plataforma
**APK/IPA analysis:**
- Decompilar (jadx) → buscar hardcoded secrets, API keys, endpoints
- Inspeccionar AndroidManifest.xml → actividades exportadas, permisos peligrosos
- Revisar network_security_config.xml → ¿permite HTTP plano?

**Intents (Android):**
- Enviar intents a actividades internas no exportadas (adb shell am)
- Intent injection: extras maliciosos en intents esperados
- Deep links con payloads maliciosos

**Storage:**
- Inspeccionar SharedPreferences/Keychain/Keystore → datos sensibles en texto plano
- SQLite local sin encryption
- Backup analysis (adb backup) → ¿datos accesibles?

**Runtime (si dispositivo rooteado):**
- Frida hooks → bypass de root detection, cert pinning
- Runtime method swizzling

### 2.4 CLI — Explotación de input
- TOCTOU: race condition entre check y use (symlink swap)
- Path traversal en argumentos (../../etc/passwd)
- Env var injection (LD_PRELOAD, PATH manipulation)
- Signal handling: SIGPIPE/SIGINT durante operación atómica
- Pipe input malformado (binary data a parser de texto)
- Argument injection (--flag peligroso via input del usuario)

### 2.5 Desktop — Explotación de OS
- IPC injection (named pipes, shared memory, COM)
- DLL hijacking (plantar DLL malicioso en path de carga)
- Registry/config manipulation
- Protocol handlers (custom://) con payloads
- Auto-start persistence mechanisms

## FASE 3 — Ataque Cross-Entity (combinatorial)

Usar las entidades enumeradas en FASE 0.3. Probar interacciones ENTRE entidades.

### 3.1 Cross-entity access (todas las plataformas)
- ¿Entidad A puede acceder a datos de entidad B?
  - Web: user/1 → GET /api/users/2 (IDOR)
  - Juego: personaje A → inventario de personaje B
  - Multi-tenant: tenant A → datos de tenant B
- ¿Los permisos de un tipo se filtran a otro?
  - Usuario regular hereda permisos de admin via cache/token stale
  - Personaje de nivel 1 equipa item exclusivo de nivel 99

### 3.2 Múltiples entidades simultáneas
- Dos entidades operando sobre el mismo recurso (race condition)
  - user/1 y user/2 editan el mismo registro
  - Dos jugadores reclaman el mismo reward simultáneamente
- Cascada: borrar entidad A que tiene FK a entidad B → ¿orphan, restrict, cascade?

### 3.3 Entidades edge case
- Entidad recién creada (datos incompletos, sin inicializar)
- Entidad soft-deleted/archivada (¿aún accesible? ¿aún referenciada?)
- Entidad con datos extremos (nombre 10k chars, valor negativo, fecha futura)
- Entidad duplicada (mismo nombre/ID — ¿unique constraint?)

## FASE 4 — Verificación de Datos

Para cada explotación que modificó datos:
1. Verificar en DB/store que el cambio se reflejó (o NO se reflejó si debería)
2. **NUNCA confiar solo en el HTTP status code.** Un 200/204 puede ser un RLS silent
   block (ver Pitfall sobre PostgREST 204). Un 403 en INSERT puede parecer error de
   validación cuando en realidad es RLS protegiendo correctamente. Siempre cruzar el
   status code con el estado real de la DB.
3. Verificar que NO se crearon registros duplicados
4. Verificar que constraints (unique, NOT NULL, FK) se respetan
5. Verificar consistencia: si el exploit cambió X, ¿Y sigue siendo consistente?

```sql
-- SQL (Supabase/Postgres/MySQL)
SELECT * FROM <table> ORDER BY created_at DESC LIMIT 5;
SELECT <field>, COUNT(*) FROM <table> GROUP BY <field> HAVING COUNT(*) > 1;
```
NoSQL/local: adaptar al sistema (Firebase, SQLite local, save files, prefs).

## FASE 5 — Reporte

Output: tabla con severidad, plataforma y categoría:

| # | Hallazgo | Plataforma | Cat | Severidad | Evidencia |
|---|----------|-----------|-----|-----------|-----------|
| 1 | IDOR user/1→user/2 | Web | A01 | CRITICAL | curl GET /api/users/2 con token de user/1 |
| 2 | Buy -1 items → +gold | Juego | Econ | CRITICAL | POST /shop/buy {qty:-1} |
| 3 | APK tiene API key | Móvil | Secret | HIGH | jadx → string API_KEY en com.app.Config |

**Severidades:**
- **CRITICAL:** Explotable directamente, datos comprometidos, economy rota
- **HIGH:** Requiere poco esfuerzo, impacto serio
- **MEDIUM:** Requiere condiciones específicas
- **LOW:** Defence-in-depth, hardening

## Anti-patterns

- **No asumir web:** Si la plataforma no es web, OWASP no aplica. Usar vectores de la plataforma correcta.
- **No probar una sola entidad:** Si hay N usuarios/razas/items, probar múltiples. Una entidad no representa todas.
- **No confundir con pentest profesional:** No tienes Burp Suite, Wireshark, ni Cheat Engine. Haces lo posible con herramientas disponibles (curl, DevTools, jadx, sqlite3, file editing). Documenta lo que NO pudiste probar.
- **No asumir "no hay bugs":** Ausencia de evidencia ≠ evidencia de ausencia.

## Pitfalls

- **Versiones de OWASP:** El estándar vigente es OWASP Top 10 (2025). Verificar en
  https://owasp.org/Top10/ antes de tocar categorías. Los nombres y posiciones cambian
  entre versiones.
- **NO "corregir" versiones sin verificar:** Si encuentras una referencia a "2025" y tu
  instinto dice que está mal → TU INSTINTO PUEDE ESTAR STALE. Verificar antes de cambiar.
- **Herramientas no disponibles:** Algunos vectores requieren herramientas especializadas
  (Wireshark, Frida, Cheat Engine) que el agente no tiene. Si no se puede ejecutar un
  vector → documentarlo como "no probado, requiere [tool]" en lugar de omitirlo.
- **Frontmatter vs body:** Actualizar ambos si cambias algo (versión, scope, descripción).
- **PostgREST/Supabase 204 ≠ éxito:** PostgREST devuelve 204 (No Content) en
  DELETE/UPDATE incluso cuando RLS bloquea la operación (0 filas afectadas). Un 204
  parece "operación exitosa" pero puede ser un RLS silent block. **SIEMPRE verificar
  en la DB** que el dato fue realmente modificado/eliminado antes de reportar como
  vulnerabilidad. Falso positivo común: reportar CRITICAL "cualquier usuario puede
  borrar admin" cuando en realidad RLS bloqueó el delete silenciosamente.

## Relación con otros skills

- **judge-security-gates:** Complementa. Ese revisa código estático; este ataca desde fuera.
- **user-chaos-tester:** Complementa. Uno prueba UX como usuario torpe; otro explota como atacante.
- **post-mortem-forense:** Si se encuentra una vulnerabilidad ya explotada, forense investiga impacto.
- **anti-hallucination:** Verificar que las APIs, protocolos y herramientas existen antes de usarlas.

## Referencias

- [OWASP Top 10 2025](references/owasp-top-10-2025.md) — Categorías y cambios desde 2021
- [Supabase Security Testing](references/supabase-security-testing.md) — Patrones verificados para auditar apps Supabase (RLS, PostgREST quirks, Edge Functions, JS bundle analysis, rate limiting)
- [Supabase SPA Key Extraction](references/supabase-spa-key-extraction.md) — Técnicas y pitfalls para extraer la anon key de una app Supabase en producción
