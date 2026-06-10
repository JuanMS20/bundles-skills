---
name: repo-onboarding
description: |
  Onboarding automático de repositorios desconocidos. 
  Carga cuando el agente detecta un directorio de proyecto sin contexto previo
  o cuando el usuario dice "ayuda con este proyecto/repo/código" sin especificar.
  
  Mapea la codebase, analiza arquitectura, stack, y estado del código en 3 pasos.
  Produce un resumen estructurado que el agente usa para decidir qué bundle ejecutar.
  
  No ejecuta código, no hace tests, no edita archivos. Solo entiende.
  
  Trigger automático: si el working directory es un git repo o tiene package.json/
  requirements.txt/pyproject.toml sin contexto previo, cargar esta skill primero.
---

# Repo Onboarding — Entender antes de actuar

## Quick Start

```
/graphify . --update
# Leer graphify-out/GRAPH_REPORT.md
# Leer 5 archivos clave
# Verificar conclusiones
# Emitir resumen
```

## Trigger automático

Cargar esta skill cuando:
- El usuario dice "ayuda con este proyecto/repo/código"
- El usuario dice "no sé qué hacer con esto"
- El working directory es un git repo sin contexto previo
- Hay package.json/requirements.txt pero no hay CONTEXT.md

No cargar cuando:
- El usuario especifica claramente qué hacer ("agrega login con OAuth")
- Ya hay un PRD o CONTEXT.md con arquitectura definida
- El agente ya trabajó en este repo en la sesión actual

---

## Paso 1 — Mapear (graphify)

```
/graphify . --update
```

Leer `graphify-out/GRAPH_REPORT.md` y extraer:

| Campo | Qué extraer |
|---|---|
| **Stack** | Lenguajes principales, frameworks, dependencias clave |
| **God nodes** | Archivos/funciones más importantes (más conectados) |
| **Communities** | Módulos separados (frontend, backend, tests, etc.) |
| **Surprises** | Dependencias circulares, código muerto, archivos huérfanos |
| **Health score** | Cobertura de tests, CI/CD, documentación |

---

## Paso 2 — Panorama (zoom-out)

Leer exactamente 5 archivos:

1. **README.md** — ¿Qué es? ¿Qué hace? ¿Cómo se ejecuta?
2. **Config de stack** — package.json / requirements.txt / pyproject.toml / Cargo.toml
3. **Entry point** — index.tsx / main.py / app.py / main.rs
4. **Un test** — Entender si hay tests y qué cubren
5. **Config de build** — vite.config.ts / next.config.js / Dockerfile / .github/workflows

Extraer:
- Arquitectura (MVC, layered, microservices, monolith)
- Estado (moderno, legacy, híbrido)
- Tests (hay / no hay / desactualizados)
- CI/CD (GitHub Actions, Jenkins, nada)
- Documentación (README completo / vacío / inexistente)

---

## Paso 3 — Verificar (anti-hallucination)

Verificar cada conclusión contra evidencia real:

| Conclusión | Verificación |
|---|---|
| "Es un proyecto React" | ¿package.json tiene react? ¿Hay .tsx? |
| "Usa Express" | ¿Hay routes/ o app.js con require('express')? |
| "Tiene tests" | ¿Hay __tests__/ o *.test.*? ¿Qué framework? |
| "Arquitectura limpia" | ¿Hay separation of concerns? ¿O todo en un archivo? |
| "Es legacy" | ¿Dependencias viejas? ¿Sin tests? ¿Código sin tipos? |

Si hay duda, re-leer. Mejor lento que equivocado.

---

## Output

Emitir resumen estructurado:

```
## Repo: [nombre]

### Stack
- Lenguaje: [ej: TypeScript]
- Framework: [ej: React + Vite]
- Runtime: [ej: Node.js 20]
- DB: [ej: PostgreSQL + Prisma]
- Tests: [ej: Vitest, cobertura ~30%]
- CI/CD: [ej: GitHub Actions, deploy a Vercel]

### Arquitectura
- [Ej: Cliente-servidor, frontend React, backend Express + Prisma]
- [Ej: Monorepo, apps/ y packages/ separados]

### Estado
- [Ej: Código moderno, bien estructurado, falta tests en backend]
- [Ej: Legacy PHP con capa de React moderno encima, deuda técnica alta]

### God nodes (archivos críticos)
- [Ej: src/auth/AuthProvider.tsx — todo el flujo de auth]
- [Ej: api/routes/users.ts — 40 endpoints en un archivo]

### Red flags
- [Ej: Dependencia circular entre auth y users]
- [Ej: Sin tests de integración]
- [Ej: package.json con 200 dependencias, 50 sin usar]

### Recomendación de bundle
[Ej: "Este es un proyecto React moderno con backend Express. Para agregar una feature nueva, usa dev-cycle. Para un bug, usa qa-bundle."]
```

---

## Pitfalls

### Asumir sin leer
Nunca decir "Es un proyecto React" sin haber visto package.json. Si hay ambigüedad (ej: package.json con react y vue), reportar la ambigüedad.

### Leer demasiado
5 archivos es suficiente. Si leés 20, estás haciendo un code review, no un onboarding.

### Ignorar red flags
Si `graphify` detecta dependencias circulares o god nodes monolíticos, esto debe ser el primer dato del resumen, no un footnote.

### Reportar sin verificar
El output se usa para decidir qué bundle ejecutar. Si el stack está mal identificado, se cargará el bundle equivocado.

---

## Referencias

- `graphify-out/GRAPH_REPORT.md` — Análisis de graphify
- `graphify-out/graph.json` — Knowledge graph queryable
