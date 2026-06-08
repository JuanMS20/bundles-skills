---
name: code-review
description: "Revisión estática de código antes de merge — detecta code smells, problemas de seguridad, complejidad, error handling y cobertura de tests. Use when user says 'revisa el código', 'code review', 'revísalo antes de push', 'chequea que esté bien', 'review', o antes de abrir un PR."
tags: [code-review, quality, security, static-analysis, pre-merge]
---

# Code Review

Revisión estática del código antes de merge. No ejecuta — LEE y ANALIZA.

## Quick Start

1. Determinar modo de entrada y alcance (FASE 0)
2. Revisar por 7 dimensiones (FASE 1)
3. Clasificar → Reporte omitiendo secciones vacías (FASE 2-3)
4. Esperar decisión del usuario (FASE 4)

## Workflow

### FASE 0: Contexto y Alcance

Antes de revisar, determinar el MODO de entrada y el ALCANCE:

**Modo de entrada (detectar cuál aplica):**

| Modo | Señal | Acción |
|------|-------|--------|
| git diff | Hay repo con historial | `git diff` para ver qué cambió. Enfocar revisión en esos archivos |
| Archivos sueltos | Usuario pega código o indica paths | Revisar solo los archivos/fragmentos indicados |
| Codebase completo | "Revisa todo el proyecto" | Primero: ¿cuántos archivos? Si >50, pedir al usuario que delimite módulo o área |

**Alcance (crítico para codebases grandes):**
- >500 líneas sin git diff → pedir al usuario que delimite módulo/área
- Fragmento pegado → revisar solo eso, no asumas contexto externo
- git diff disponible → revisar SOLO lo que cambió

**Contexto adicional:**
1. **¿Por qué?** — requerimiento original, issue asociada
2. **¿Stack?** — detectar config files (anti-hallucination aplica)
3. **¿Hay ADRs o CONTEXT.md?** — Decisiones previas

Presentar: "Revisando N archivos/líneas, modo: [diff|fragmento|codebase], stack: [X]".

### FASE 1: Revisión por Dimensiones

Revisar CADA dimensión en orden. No saltes ninguna — aunque parezca "todo bien".

#### 1.1 Correctness
- ¿El código hace lo que el issue/PR dice?
- ¿Edge cases manejados? (empty input, null, boundaries, concurrent)
- ¿Lógica correcta en condicionales, loops, recursión?
- ¿Data flow correcto? ¿Dead code o branches inalcanzables?

#### 1.2 Security

**Heurísticas de detección visual** — busca estos patrones literalmente en el código:

| Patrón | Riesgo | Donde buscar |
|--------|--------|--------------|
| `eval(`, `exec(`, `Function(` | Code injection | JS, Python, Ruby |
| Concatenación en queries SQL | SQL injection | Cualquier lenguaje |
| `${...}` en HTML/JSX, `innerHTML`, `dangerouslySetInnerHTML` | XSS | JS/TS, Vue |
| Secrets hardcoded (API keys, passwords, tokens) | Credential leak | Cualquier lenguaje |
| Queries sin parametrización, `req.body` sin validación | Injection | Cualquier lenguaje |
| `os.system(`, `subprocess(shell=True)` | Command injection | Python |
| `DELETE FROM` / `DROP TABLE` sin WHERE | Data destruction | SQL |
| Archivos abiertos sin cleanup (with/defer/try-with) | Resource leak | Cualquier lenguaje |
| Import de script/widget de terceros (Turnstile, Stripe.js, GA, hCaptcha) sin actualizar CSP en `_headers` | Silent CSP block — widget no renderiza en producción | JS/TS con `_headers` o CSP meta tag |

**Checklist general:** inputs validados? Auth presente? Datos sensibles en logs? Dependencias con CVEs?

#### 1.3 Code Quality
- Naming claro y consistente?
- Functions: una cosa, <50 líneas, params razonables?
- DRY: duplicado >3 líneas que debería extraerse?
- Complexity alta? (nesting múltiple, booleanos encadenados)
- Coupling entre módulos que no deberían conocerse?
- Type safety? (any types, casts forzados)
- **Code judo:** ¿Existe una restructuración que ELIMINE ramas, condicionales o capas enteras —no solo las limpie? Si el diff añade complejidad que un refactor del modelo de datos o de la abstracción haría desaparecer, escalar a MAJOR con la restructura propuesta. Buscar:
  - Condicionales ad-hoc en flujos ajenos (feature logic leaking en shared paths)
  - One-off booleans, flags o nullable modes que ensucian control flow existente
  - Archivos cruzando 1k líneas → extract module antes de seguir
  - Wrappers/passthroughs que añaden indirección sin claridad
  - Orquestación secuencial donde work independiente podría ir en paralelo

#### 1.4 Error Handling
- Errores manejados o silenciados? (empty catch, bare except)
- Mensajes accionables? Cleanup en paths de error?
- Reintentos con backoff? Fallos de terceros degradando graceful?

#### 1.5 Testing
- ¿Tests existen para el cambio?
- ¿Cubren happy path Y edge cases?
- ¿Behavior-focused (no implementation-coupled)?
- ¿Mocks mínimos y justificados?
- ¿Algún test roto o omitido intencionalmente?

#### 1.6 Documentation
- Funciones públicas documentadas? Cambios de interfaz en docs?
- READMEs actualizados? CHANGELOG si es breaking change?

#### 1.7 Performance
- Complejidad algorítmica correcta? (O(n²) innecesario)
- N+1 queries o llamadas repetitivas?
- Memory leaks? (listeners sin remove, caches sin TTL, closures pesadas)
- Data structures apropiadas? (array→set/map para búsqueda)
- Lazy loading / pagination donde aplica?
- Operaciones bloqueantes en paths críticos?

### FASE 2: Clasificación de Hallazgos

Cada hallazgo se clasifica en:

| Severidad | Significado | Acción |
|-----------|-------------|--------|
| BLOCKER | Bug, security vulnerability, data loss risk | DEBE resolverse antes de merge |
| MAJOR | Code smell significativo, error handling faltante | DEBERÍA resolverse antes de merge |
| MINOR | Naming, estilo, oportunidad de mejora | Puede resolverse después |
| NIT | Preferencia personal, convenio de estilo | Info only, no bloquea |

### FASE 3: Reporte

Elegir formato según el contexto:

**Formato completo** — usado por defecto, para revisiones serias o cuando hay BLOCKERs:
```
## Code Review — [módulo/archivo]

**Archivos revisados:** N
**Dimensiones chequeadas:** 7/7

[solo incluir secciones con N>0]

### BLOCKER (N)
- [archivo:línea] Descripción → Sugerencia

### MAJOR (N)
- [archivo:línea] Descripción → Sugerencia

### MINOR (N)
- ...

### NIT (N)
- ...

### Resumen
- N blockers, N majors, N minors, N nits
- Veredicto: APPROVE / REQUEST_CHANGES / COMMENT
```

**Formato compacto** — usado para revisiones rápidas, fragmentos pequeños, o cuando solo hay MINORs/NITs:
```
Review: [archivo] — [N] hallazgos
[lista solo categorías con hallazgos]
→ Veredicto: APPROVE/REQUEST_CHANGES
```

**Reglas de formato:**
- Si N=0 en alguna categoría → OMITIR la sección completa (no mostrar "### BLOCKER (0)")
- Completo: >3 hallazgos, cualquier BLOCKER, revisiones de PR completas
- Compacto: ≤3 hallazgos, solo MINORs/NITs, fragmentos de código pegados

### FASE 4: Decisión
- BLOCKERs → REQUEST_CHANGES (obligatorio)
- Solo MAJORs → REQUEST_CHANGES (recomendado)
- Solo MINORs/NITs → APPROVE con notas
- Esperar decisión del usuario sobre qué corregir

## Anti-Patterns

- **Review a ciegas** → Sin contexto, pregunta ANTES de revisar.
- **Nitpicking masivo** → 40 MINORs/0 BLOCKERs = "APPROVE con notas", no pidas corregir todo.
- **Dilución estructural** → Si hay hallazgos code judo (MAJOR estructurales), NO los separes entre 15 NITs cosméticos. Prioriza pocos comentarios de alta convicción sobre listas largas de detalles superficiales. El reviewer pierde foco en el issue real entre ruido.
- **Sin suggested fix** → Cada BLOCKER/MAJOR incluye SUGERENCIA concreta.
- **Mezclar con QA** → Code review es ESTÁTICO. QA es runtime. No ejecutes código.
- **Cherry-picking dimensions** → Siempre chequea las 7 dimensiones.
- **Sin delimitar scope** → 2000 líneas sin contexto = preguntar qué enfocar.

## Relationship to Other Skills

- **anti-hallucination**: Verifica APIs dudosas durante la revisión.
- **qa-testing**: Complementario — code review = estático, QA = runtime.
- **improve-codebase-architecture**: Code review detecta symptoms, esta skill analiza root causes.
- **tdd**: Fix de bugs encontrados se hace con red-green-refactor.
- **pr-description**: Después de code review aprobado.

## Pitfalls

- **Revisar todo el repo cuando solo cambió 1 archivo** → Usa git diff, enfócate en lo que cambió.
- **Falta de contexto del issue** → Sin saber QUÉ se intentaba hacer, no puedes evaluar si el código lo logra.
- **Confundir estilo con correctness** → Prioriza correctness sobre convenciones de formato.
- **Backward compatibility** → Si la API pública cambió sin migration path → BLOCKER.
- **Transversal concerns** → Logging, monitoring, metrics — pregunta si aplica.
- **Reportar findings sin verificar estado actual** → Antes de listar un bug, verifica si ya fue corregido en el código actual. Los audits anteriores pueden estar desactualizados. SELECT del schema/estado actual > asumir que el finding persiste.

## Stack-Specific Pitfalls

### React Native / Expo
- **`gap` con valores negativos** → No soportado en React Native. Usa `marginRight: -N` o ajusta el layout.
- **`View` en lugar de `Text` para contenido textual** → Texto dentro de `<View>` no renderiza en RN. Siempre usar `<Text>`.
- **`opacity` property vs `${color}80`** → Para transparencias, usar hex con alpha (`#00308780`), no la propiedad `opacity` (afecta hijos).
- **expo-camera API changes** → `CameraView` varía entre versiones. Verificar `takePictureAsync` vs `takePicture` con defensive checks.
- **`@/` imports** → Requieren `babel-plugin-module-resolver` en `babel.config.js` y `paths` en `tsconfig.json`. Sin esto, los imports fallan silenciosamente.
- **TypeScript union types** → Syntax error común: `'a' 'b'` en lugar de `'a' | 'b'`. El linter no siempre lo detecta si no hay `strict: true`.
