---
name: sprint-setup
description: "Setup completo de sprint: CONTEXT.md, PRD, issues con dependencias, branch, .gitignore. Usar con /plan-sprint o 'prepara el proyecto'."
tags: [planning, sprint, project-setup, prd, issues]
related_skills: [to-prd, to-issues, tdd]
---

# Sprint Setup — Flujo completo de preparación de proyecto

Orquesta la creación de todo lo necesario para arrancar un sprint: contexto, PRD, issues, rama de trabajo, y .gitignore.

## Cuando usar

- Usuario dice "/plan-sprint", "setup sprint", "crea el plan", "prepara el proyecto"
- Proyecto nuevo o existente que necesita organización antes de codificar
- El usuario describe un equipo, un deadline, y funcionalidades a construir

## Flujo (6 pasos, en orden)

### 1. Recolectar contexto existente
- Leer todos los archivos de documentación del proyecto (README, docs, notas, propuestas)
- Verificar si el repo está clonado localmente (`find . -name ".git" -maxdepth 3`)
- Verificar branches existentes (`git branch -a`)
- Cargar skills `to-prd` y `to-issues` para sus templates

### 2. Crear CONTEXT.md
Archivo en la carpeta de trabajo del usuario (NO en el repo) con:
- Qué es el proyecto (1-2 oraciones)
- Stack tecnológico
- Arquitectura (estructura de directorios)
- Equipo y responsabilidades
- Scope (qué sí y qué no)
- Glosario de términos del dominio
- Repo URL y branches

### 3. Crear PRD
Seguir el template de `to-prd`: Problem Statement, Solution, User Stories (lista extensa), Implementation Decisions, Testing Decisions, Out of Scope, Further Notes (deadline, equipo, restricciones).

Punto de decisión: si hay issue tracker → publicar con label `needs-triage`. Si no hay → guardar como `PRD.md` local.

### 4. Crear issues (vertical slices)
Seguir el proceso de `to-issues`: un archivo individual por issue en `issues/` directory. Formato: `issues/NNN-kebab-title.md`. Incluir Type (HITL/AFK), What to build, Acceptance criteria, Blocked by.

**CRÍTICO:** Mapear dependencias entre issues y presentarlas al usuario ANTES de crear los archivos.

Clasificación:
- HITL: requiere aprobación humana (diseño, merge, validación)
- AFK: se implementa sin interacción humana

### 5. Crear branch de integración
```bash
git checkout main && git checkout -b integration
```

### 6. Crear .gitignore
Reglas estándar del stack + excluir documentación de producción (*.md excepto README, *.docx, *.pdf) + excluir directorio de docs.

## Pitfalls

1. **NO crear un solo archivo issues.md** — siempre archivos individuales por issue.
2. **NO asumir issue tracker** — verificar primero. Si no hay, modo local.
3. **NO crear issues sin mapear dependencias** — presentar el grafo al usuario primero.
4. **El .gitignore debe ser específico al stack** — un genérico no cubre `.expo/`, `dist/`, etc.
5. **CONTEXT.md va en carpeta del usuario, NO en el repo** — es documentación de trabajo.
6. **Issues HITL siempre al final** — integración y testing son HITL.
7. **En proyectos con equipo, paleta/diseño es HITL** — requiere aprobación antes de merge.

## References

- `references/context-template.md` — plantilla CONTEXT.md
- `references/gitignore-templates.md` — .gitignore para React Native/Expo
- `references/pitfalls.md` — pitfalls detallados: branch ownership, .gitignore, PRD desde docs, regla de diseño
