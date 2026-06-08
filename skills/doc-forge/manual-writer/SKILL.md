---
name: manual-writer
description: "Generate comprehensive user/programmer manuals from a project blueprint. Produces book-structured Markdown with chapters, TOC, glossary, and index. Use when user says 'manual', 'guía de usuario', 'documentar el sistema', 'crear libro', or needs structured documentation for end users or developers."
---

# Manual Writer

Transforms a project blueprint (from `project-mapper`) into a book-quality manual in structured Markdown. Supports multiple audience modes.

## When to Use

- User asks for a manual, user guide, or book about a project
- After `project-mapper` produces a blueprint
- When updating an existing manual after project changes
- User says "manual", "guía", "libro", "documentar para usuarios"

## Input

Requires a blueprint YAML from `project-mapper`. If none exists:
1. Check `<project>/docs/blueprint.yaml`
2. If missing, run `project-mapper` first
3. If user provides description verbally, create a minimal blueprint inline

## Audience Modes

| Mode | For | Focus | Language |
|------|-----|-------|----------|
| `usuario` | End users, non-technical | Features, workflows, UI navigation | Simple Spanish, no jargon |
| `programador` | Developers integrating/extending | APIs, architecture, data models, config | Technical Spanish, code examples |
| `admin` | System administrators | Deployment, config, monitoring, troubleshooting | Technical, CLI-focused |

Default: `usuario` unless user specifies otherwise.

## Book Structure

Every manual follows this structure:

```
cover.md          — Portada (nombre, versión, fecha, tipo de manual)
toc.md            — Índice general
00-intro.md       — Introducción: qué es, para quién, qué incluye
01-quickstart.md  — Inicio rápido (5 minutos)
02-N-[topic].md   — Capítulos temáticos (1 por feature/área)
...
99-reference.md   — Referencia rápida (tablas, configs, atajos)
glossary.md       — Glosario de términos
```

## Process

### FASE 1 — Plan

1. Read the blueprint YAML
2. Confirm audience mode with user (or infer from request)
3. Propose chapter outline:
   ```
   Capítulos propuestos:
   1. Introducción
   2. Inicio rápido
   3. [Feature principal 1]
   4. [Feature principal 2]
   ...
   N. Referencia rápida
   N+1. Glosario
   ```
4. Get user approval before writing

### FASE 2 — Write

For each chapter:

**Portada (`cover.md`)**:
```markdown
# [Nombre del Proyecto]

## [Tipo de Manual: Manual de Usuario / Guía del Programador / Manual de Administración]

**Versión:** [versión]
**Fecha:** [fecha]
**Autor:** [equipo/organización]
```

**Introducción (`00-intro.md`)**:
- Qué es el sistema (1 párrafo)
- Para quién es este manual
- Qué encontrarás en este manual
- Convenios tipográficos (negrita = UI, `código` = comandos, 📌 = nota importante)

**Inicio rápido (`01-quickstart.md`)**:
- Requisitos previos
- Pasos numerados para empezar a usar (máximo 10 pasos)
- "Tu primera [acción principal]" como walkthrough

**Capítulos temáticos (`02-N-*.md`)**:
Cada capítulo:
```markdown
# [Nombre del Capítulo]

## ¿Qué es [feature]?
[1-2 párrafos explicando qué hace y por qué importa]

## Cómo usar [feature]
[Pasos numerados con ejemplos]

## Ejemplo práctico
[Caso de uso real, paso a paso]

## Errores comunes
[Tabla: Error | Causa | Solución]

## Preguntas frecuentes
[Si aplica]
```

**Referencia rápida (`99-reference.md`)**:
- Tabla de todos los endpoints/comandos
- Variables de entorno
- Atajos de teclado (si aplica)
- Configuraciones por defecto

**Glosario (`glossary.md`)**:
- Términos del dominio definidos en 1 línea
- Organizados alfabéticamente
- Incluir solo términos que el lector podría no conocer

### FASE 3 — Review

Present to user:
1. Table of contents with page estimates
2. Sample chapter (pick the most complex one)
3. Ask: tone ok? depth ok? missing topics?

### FASE 4 — Save

Write all files to `<project>/docs/manual-[mode]/`:
```
docs/manual-usuario/
  cover.md
  toc.md
  00-intro.md
  01-quickstart.md
  02-*.md
  ...
  99-reference.md
  glossary.md
```

## Writing Rules

- **Short paragraphs**: max 4 sentences per paragraph
- **Active voice**: "El sistema guarda los datos" not "Los datos son guardados por el sistema"
- **Concrete over abstract**: "Haz clic en Guardar" not "Utilice la función de guardado"
- **Numbered steps**: any sequence of actions = numbered list
- **Screenshots as complement**: text first, screenshot to reinforce
- **One concept per heading**: if a section covers 2 things, split it
- **Cross-references**: "Ver Capítulo 3: [nombre]" instead of repeating content

## Mode-Specific Adaptations

| Section | usuario | programador | admin |
|---------|---------|-------------|-------|
| Quickstart | UI walkthrough | Setup + first API call | Deploy + verify |
| Features | What it does, how to use | How it works, API surface | How to configure, monitor |
| Errors | "Si ves X, haz Y" | Error codes + stack trace | Log analysis + rollback |
| Reference | Keyboard shortcuts | API tables | Config reference |

## Pitfalls

- **Writing for yourself, not the reader**: You know the system. The reader doesn't. Every implicit assumption must be explicit.
- **Feature-list manual**: A manual that lists features without showing how to USE them is useless. Every feature needs a workflow example.
- **Too technical in user mode**: "The JWT token is refreshed via the /auth/refresh endpoint" → "Cuando tu sesión expira, el sistema te reconecta automáticamente."
- **Too shallow in programmer mode**: Developers need actual API signatures, data types, and error codes. Don't hand-wave.
- **Stale manual**: Include a "Última actualización" date. Flag chapters that reference specific versions.

## Updating an Existing Manual

When the project changes:
1. Run `project-mapper` to get fresh blueprint
2. Diff old vs new blueprint
3. Update only affected chapters (patch, don't rewrite)
4. Update "Última actualización" date
5. Add changelog entry at the top of the manual
