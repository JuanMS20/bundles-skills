---
name: legacy-to-modern-migration
description: "Migrate a legacy application (Google Apps Script, vanilla JS, spreadsheets-as-DB, localStorage) to a modern stack (React/Vite, Supabase, proper DB). Covers: legacy repo exploration, architectural grilling, CONTEXT.md + PRD creation, data model design, migration planning. Use when user says 'migrar', 'pasar a profesional', 'esto es un demo, quiero algo real', 'usar framework', 'base de datos real', or when you detect a legacy stack (GAS, localStorage, vanilla JS + Sheets) that needs modernization."
---

# Legacy to Modern Migration

Workflow completo para migrar aplicaciones legacy a stacks modernos. Basado en migraciones reales exitosas.

## Cuándo usar

- App tiene backend precario (Google Apps Script, localStorage, Google Sheets como DB)
- Frontend es vanilla JS/HTML sin framework
- Credenciales hardcodeadas o en texto plano
- Usuario dice "esto es un demo", "quiero algo profesional", "migrar a algo serio"

## FASE 0: Explorar el repo legacy ANTES de preguntar

**Obligatorio antes de hacer preguntas.** El grill se basa en realidad, no en suposiciones.

### Pasos

1. `web_extract` del repo GitHub → estructura de carpetas, README, PRD existente
2. Leer archivos clave: `package.json`, entry points, config files, `PRD.md`
3. Identificar: stack actual, DB, auth, tests, datos hardcodeados
4. Buscar seguridad: credenciales expuestas, passwords en plaintext, URLs de API visibles
5. Buscar datos de ejemplo/producción: CSVs, Excel, datos en código

### Output

Tabla resumen con: Stack | DB | Auth | Tests | Problemas de seguridad | Estado

## FASE 1: Grill arquitectónico

Cargar `grill-with-docs` y hacer preguntas EN ORDEN (una a la vez, esperar respuesta):

### Orden de decisiones (dependencias)

```
1. Framework frontend → (React/Vue/Next.js/Astro)
2. Backend → ¿API propia o BaaS directo? (Supabase/Firebase/Custom)
3. Auth → Email-based o custom (username/password)?
4. Roles → Qué roles, qué permisos
5. Modelo de datos → Entidades, relaciones, unique constraints
6. Geodata/referencias → ¿Catálogo en DB o hardcodeado?
7. Storage → ¿Dónde van archivos (certificados, PDFs, imágenes)?
8. Hosting → Cloudflare/Vercel/Netlify
9. Repo → ¿Mismo repo o nuevo?
```

### Reglas del grill

- Una pregunta a la vez
- Proveer MI recomendación con cada pregunta (no solo opciones)
- Si la pregunta se responde explorando el código → explorar en vez de preguntar
- Si el usuario da respuestas cortas ("lo que sea", "tú decides") → parar y construir
- Si el usuario dice "¿ya preguntaste todo?" → preguntar MÁS (timeline, equipo, rollback)

## FASE 2: Documentación inline

A medida que el usuario responde, crear:

### CONTEXT.md

```markdown
# [Proyecto] — Contexto de Dominio

## Glosario
| Término | Definición |

## Reglas de Negocio
1. [Regla con consecuencia clara]

## Decisiones Técnicas
| Decisión | Valor | Fecha |

## Stack
[Tabla con capas y tecnologías]
```

### PRD.md

```markdown
# PRD — [Proyecto] v[N]

## 1. Problema
## 2. Objetivo
## 3. Stack
## 4. Roles y Permisos (por rol)
## 5. Entidades (SQL schema con constraints)
## 6. Features (por feature: descripción + criterios)
## 7. RLS / Seguridad
## 8. Migración de Datos (fases)
## 9. Out of Scope
## 10. Criterios de Aceptación (checklist)
```

**Regla**: Cada decisión del grill se documenta INMEDIATAMENTE en el archivo correspondiente. No acumular para después.

## FASE 3: Esquema SQL

Diseñar el esquema basado en:
1. Datos existentes en el repo legacy (Excel, localStorage, Sheets)
2. Decisiones del grill (unique constraints, FK, enums)
3. Reglas de negocio

**Patrón estándar para apps con auth:**
```sql
profiles        → datos de usuario + rol (FK → auth.users)
[entidad_main]  → tabla principal de negocio (FK → profiles)
[entidades_rel] → tablas de relación (FK compuestas)
geo_*           → catálogos de referencia (si aplica)
```

## FASE 4: Plan de migración

Siempre en 3 fases:
1. **Estructura**: Crear tablas, RLS, catálogos
2. **Datos**: Migrar datos existentes, resolver duplicados
3. **Archivos**: Migrar storage (certificados, PDFs)

## FASE 5: Scaffolding del proyecto moderno

Después de planificar (FASE 0-4), el siguiente paso es crear el esqueleto del proyecto.

### Secuencia

1. `npm create vite@latest <temp-dir> -- --template react-ts`
2. Copiar configs al repo real; escribir package.json con deps propias
3. Configurar Tailwind v4 (plugin Vite + @import, SIN config files)
4. Configurar path alias `@/` (tsconfig.app.json paths + vite resolve.alias)
5. Escribir archivos base: main.tsx, App.tsx (con Router), lib/supabase.ts, routes/placeholder
6. `.env.example` + `.gitignore` antes de cualquier commit
7. `npm install`
8. Verificar: `npx tsc -b` + `npm run build` + dev server

**Verificado con**: Vite 8, React 19, TS 6, Tailwind v4, React Router v7 (jun 2026).

### Pitfalls de scaffolding

- **TS 6 deprecó `baseUrl`** — NO usar. `paths` funciona sin él. Error TS5101 si lo incluyes.
- **Tailwind v4 NO usa `tailwind.config.js` ni `postcss.config.js`** — Plugin `@tailwindcss/vite` + `@import "tailwindcss"` en CSS. Setup completo en 2 líneas.
- **Crear branches `feature/NNN` antes de tener código = ruido** — Ver `github-cli-batch-ops` P7. Un branch sin commits propios es ficción, no progreso.

### Referencia

- [React+Vite Scaffolding 2026](references/react-vite-scaffolding-2026.md) — Versiones actuales, Tailwind v4, TS 6 baseUrl, path alias, secuencia paso a paso

## Pitfalls

- **No explorar antes de preguntar** → Grill basado en suposiciones, no en realidad
- **Preguntar todo en una sola pregunta** → Usuario se abruma, responde mal
- **No documentar inline** → Se pierden decisiones, hay que re-preguntar
- **Copiar datos legacy sin limpiar** → Datos sucios (typos, duplicados) van a producción
- **Ignorar los tests existentes** → El repo viejo puede tener tests válidos que migrar
- **Elegir stack sin preguntar** → "React es lo mejor" no aplica a todos los casos
- **Olvidar RLS/seguridad hasta el final** → Debe ir desde el FASE 3, no como afterthought

## Referencias

- [Supabase Patterns](references/supabase-patterns.md) — Auth custom, RLS multi-rol, Storage, React integration
- [UI/UX Migration](references/ui-ux-migration.md) — Migrar LOOK AND FEEL de vanilla CSS a React+Tailwind (design system extraction, component patterns, Tailwind v4 config)
