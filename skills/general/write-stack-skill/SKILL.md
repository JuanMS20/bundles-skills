---
name: write-stack-skill
description: "Create verified stack-specific skills (API reference, patterns, anti-patterns) with research against official docs. Use when user says 'create skill for [stack]', 'add skill for React/Flutter/Roblox/etc', or when dev-cycle detects a stack without a corresponding skill."
---

# Write Stack Skill

Procedimiento para crear skills de stack verificadas contra documentacion oficial. No improvisar APIs.

## Cuando crear una skill de stack

- Dev-cycle detecta un stack sin skill correspondiente
- Usuario trabaja repetidamente con un framework/libreria
- El anti-hallucination protocol falla repetidamente en el mismo stack (senal: necesitas conocimiento cacheado)

**No crear si**: el proyecto es one-off o el stack tiene <3 scripts que lo usen.

## FASE 1: Research

### 1.1 Identificar el stack

Leer config del proyecto:
- `package.json` -> Node/React/React Native/Next.js/Vue/Svelte
- `pubspec.yaml` -> Flutter/Dart
- `requirements.txt` / `pyproject.toml` -> Python (FastAPI/Flask/Django)
- `go.mod` -> Go
- `Cargo.toml` -> Rust
- `.csproj` -> C#/.NET
- `build.gradle` / `pom.xml` -> Java/Kotlin
- `Gemfile` -> Ruby (Rails/Sinatra)
- `*.sql` / schema files -> SQL (PostgreSQL, MySQL, SQLite)
- Sin config + Roblox Studio detectado -> Luau/Roblox Engine

### 1.2 Pipeline de busqueda (ejecutar EN ORDEN)

```
Paso 1: web_search x3
  - "[Stack] official documentation [current year]"
  - "[Stack] API reference [current year]"
  - "[Stack] new features deprecated [current year]"

Paso 2: Filtrar fuentes
  - Priorizar URLs de dominios oficiales del stack (docs.*, developer.*, *.dev)
  - Si todas las URLs son blogs de terceros, marcar datos como [SIN VERIFICAR] desde aqui
  - Extraer las 3-5 URLs mas relevantes del paso 1

Paso 3: web_extract
  - Extraer contenido de las URLs filtradas

Paso 4: Si el sitio bloquea o requiere JS:
  -> invisible-browser stealth_extract / stealth_screenshot

Paso 5: Context7 (si existe):
  mcp_context7_resolve_library_id -> obtener ID
  mcp_context7_query_docs -> consultar APIs especificas

Paso 6: web_search x2
  - "[Stack] best practices [current year]"
  - "[Stack] common mistakes anti-patterns [current year]"
```

### 1.3 Regla de citado

TODO dato de API que entre en la skill DEBE tener fuente:
- URL de docs oficiales
- Nombre del post DevForum / blog oficial
- Version del engine/libreria

Si no encuentras fuente, marca como `[SIN VERIFICAR - valor inferido]`.

## FASE 2: Estructura

Toda skill de stack sigue esta estructura. Las secciones marcadas [OBLIGATORIA] siempre van. Las demas van si aplican.

### Secciones obligatorias

1. **Core APIs** — Servicios/clases principales con firma de metodos reales. Ejemplos reales (no pseudocodigo). Parametros y tipos correctos. Limitaciones conocidas.

2. **Common Patterns** — Patrones de uso correcto con snippets verificables. Cada patron resuelve un problema concreto.

3. **Anti-Patterns / Gotchas** — Lo que NO hacer y por que. Incluir deprecated APIs con reemplazo.

4. **Verification Checklist** — Checklist para verificar que el codigo usa APIs correctas.

### Secciones opcionales (agregar si aplica)

5. **Platform Differences** — Si el stack corre en multiples plataformas (desktop/mobile/console/web). Diferencias de performance, limites, APIs no disponibles.

6. **Security / Anti-Exploit** — Solo si aplica. Modelo de amenaza, validacion server-side, datos NUNCA confiables del cliente.

7. **Performance** — Solo si el stack tiene pitfalls de performance no obvios. Limites del engine/runtime, budgets, optimizaciones.

8. **Current Year Updates** — Features nuevas, APIs deprecadas, breaking changes del ano actual. Fecha de release (mes + ano). Status (Beta / Release / Deprecated).

### Reglas de estructura

- SKILL.md: < 200 lineas. Si necesitas mas, split en `references/`.
- Cada seccion: ejemplos concretos, no prosa abstracta.
- Codigos en bloques de codigo con lenguaje especificado.
- Terminologia consistente dentro de la skill.

### Wording best practices (consenso Anthropic/OpenAI/Google)

- **Instrucciones primero, datos despues, tarea al final.** Orden: reglas → contexto → pregunta/accion.
- **Framing positivo por defecto.** "Usa X" > "No uses Y". Los 3 providers coinciden: instrucciones negativas generan worse adherence.
- **Especificidad sobre vaguedad.** "3-5 oraciones" > "breve". "Lista los 5 metodos principales" > "lista los metodos".
- **Scope explicito.** Si una regla aplica a multiples elementos, declaralo: "Aplica a TODAS las secciones, no solo la primera".
- **Separadores claros** entre secciones de distinto tipo (instrucciones vs datos vs ejemplos). XML tags, `###` o `"""` funcionan.

## FASE 3: Verificacion

Antes de declarar la skill lista, ejecutar:

```
[ ] Todo dato de API tiene fuente URL citada
[ ] Cero metodos inventados — cada .MethodName existe en docs oficiales
[ ] Anti-patterns basados en docs o incidentes reales, no opinion
[ ] Seccion "Current Year Updates" tiene al menos 1 busqueda web del ano actual
[ ] No hay info que sera stale en <30 dias (no incluir version exacta de paquete)
[ ] Description incluye triggers especificos ("Use when...")
[ ] Sin contenido copia-pega sin procesar de docs — todo reformulado con valor agregado
```

## FASE 4: Registro

Despues de crear la skill:

1. `skill_manage(action='create', category='[categoria]')` — crear la skill
2. `memory(action='add', target='memory')` — registrar que existe
3. Si hay bundles existentes del mismo stack, considerar actualizar el bundle

## Mantenimiento (Just-In-Time)

NO crear cron jobs de auto-actualizacion. Actualizar cuando:

1. **Usas la skill y encuentras un gap** -> parchear inmediatamente con `skill_manage(action='patch')`
2. **El stack tiene un release mayor** -> una pasada de web_search + patch
3. **Un test falla por API incorrecta** -> la skill tenia info mala -> parchear

Senal de que una skill necesita update: el agente busca web_search para algo que deberia estar en la skill. Eso significa que la skill esta incompleta.

## Pitfalls

- **Sobre-abstraccion**: No crear una skill "general de backend". Crear skills especificas: "express-routing", "prisma-orm", etc. Una skill = un dominio claro.
- **Copiar docs sin procesar**: La skill no es un espejo de la documentacion. Es conocimiento condensado con juicios de valor (que usar, que evitar, en que orden).
- **Incluir config temporal**: No poner numeros de version exactos, tokens, o URLs de endpoints que cambian. Usar patrones.
- **Skill demasiado larga**: Si pasa 200 lineas, el agente no la va a consumir bien. Split en references/.
- **No verificar contra el ano actual**: La info de 2024 no sirve en 2026. Siempre buscar updates del ano actual.
- **Stack detection incompleta**: Siempre verificar TODOS los config files posibles antes de decidir el stack. Un proyecto puede tener múltiples stacks (monorepo, frontend+backend).
- **General vs Stack**: Si la skill es para software general (code-review, testing, architecture), NO crear secciones por stack. Usar tablas de heurísticas genéricas. Las skills de stack van en write-stack-skill, no aquí.

## Pipeline Anti-Patterns

1. **Research sin sintesis** — web_extract devuelve 5 paginas de docs y el agente las parafrasea en orden. Resultado: skill que es un indice de documentacion, no conocimiento condensado. Señal: la skill tiene mas de 3 bloques de codigo consecutivos sin explicacion de cuando usar cada uno.

2. **Anti-patterns sin evidencia** — El agente inventa anti-patterns que "suenan bien" pero no estan en docs ni en issues reales. Señal: el anti-pattern no tiene URL de fuente ni referencia a un issue/commit especifico.

3. **Skill para stack que no necesita skill** — El pipeline se dispara porque detecto un `package.json` con una libreria menor. Se crea una skill de 200 lineas para un stack que se usa en 2 archivos. Señal: la skill se usa <2 veces en 30 dias.

## Relacion con otras skills

- **anti-hallucination**: Version proactiva — cachea conocimiento verificado para que anti-hallucination tenga donde buscar primero.
- **write-a-skill**: Skill general de creacion. Esta es la especializacion para stacks.
- **prompt-engineering**: Base de conocimiento sobre redaccion de prompts. Consultar cuando la skill creada necesita ejemplos de few-shot, estructura XML, o ajuste por provider.
- **dev-cycle bundle**: En PASO 0, si detecta un stack sin skill, sugerir crearla con este procedimiento.
