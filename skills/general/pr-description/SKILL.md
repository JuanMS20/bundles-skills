---
name: pr-description
description: "Genera descripciones de PR con 7 elementos obligatorios. Gate final antes de push — requiere aprobación explícita del usuario. Use when opening a PR, before pushing any code for review, or when the user asks for a PR description."
---

# PR Description — 7 Elementos Obligatorios

Gate final antes de push. El usuario ve diff completo + estos 7 elementos y aprueba explícitamente.

## Quick Start

Los 7 elementos obligatorios en toda PR description:

1. **Referencia del ticket** — link/key del issue, o descripción del problema original
2. **Root Cause / Motivación** — cause confirmado (1-2 oraciones) o por qué se necesita (features)
3. **Breaking Commit** — SHA + subject del commit que introdujo el bug, o "always-existed", u omitir para features
4. **Qué Cambió** — resumen factual file-by-file
5. **Por Qué Cada Cambio** — razonamiento que conecta root cause con cada modificación
6. **Evidencia** — output fresco de tests + compilación de esta sesión
7. **Riesgos** — side effects, consideraciones para el reviewer

## Template

```markdown
## [Título del PR]

### Ticket
[Link o descripción]

### Root Cause / Motivación
[Cause confirmado o por qué]

### Breaking Commit
[SHA + subject / "always-existed" / omitir para features]

### Changes
- `path/file.ext` — [qué cambió]

### Why
- [Razonamiento para cada cambio]

### Evidence
[Output fresco de tests + build]

### Risks
[Side effects, monitoreo sugerido]
```

Ejemplo completo: [references/example.md](references/example.md)

## Pipeline Integration

Parte del pipeline `fix-issue` (Fase 7, gate final). También funciona standalone para cualquier PR.

## Reglas

- Gate siempre — push solo después de aprobación explícita del usuario.
- Si el usuario pide cambios: ajustar y re-presentar los 7 elementos.
- PRs triviales (typo, config) pueden ser breves pero los 7 elementos van.
- La evidencia (elemento 6) debe ser de esta sesión. Stale no cuenta.
