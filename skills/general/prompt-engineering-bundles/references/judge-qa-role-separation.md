# Judge / QA / User-Chaos — Separación de Roles y Responsabilidades

> Documento de referencia para evitar mezcla entre bundles de verificación.
> Última corrección: v4 (Junio 2026) — corrigió error v3 donde judge y user-chaos duplicaban scopes.

## El Problema v3

En v3, los bundles de verificación se mezclaban en tres niveles:

1. **Rol duplicado:** Tanto `judge` como `qa-bundle` usaban `<role>Eres un QA Engineer...`
2. **Scope duplicado:** `user-chaos` FASE 2 "UX Real" era idéntico a `judge` FASE 5 `judge-ux-vibe-check`
3. **Scope duplicado:** `user-chaos` FASE 3 "Análisis Ofensivo" solapaba `judge` FASE 3 `judge-security-gates` + `reverse-audit`
4. **qa-bundle no existía:** El testing sistemático + fixes estaba implícito en judge FASE 1

Resultado: El agente no sabía si debía *ejecutar* tests o *evaluar* evidencia.

## La Corrección v4

### Separación por Rol (quién ejecuta)

| Bundle | Rol | Modo de operación | Analogía humana |
|--------|-----|-------------------|-----------------|
| **qa-bundle** | QA Engineer | Ejecuta, encuentra, fixea | Tester que corre pruebas y reporta bugs |
| **judge** | Technical Auditor | Evalúa evidencia ajena, emite veredicto | Auditor que revisa documentación y firma |
| **user-chaos** | Tester de Caos | Explora sin plan, rompe cosas | Usuario torpe que clica todo |

**Regla de oro:** Si dos bundles comparten el mismo `<role>`, uno está mal definido.

### Separación por Scope (qué verifica)

| Bundle | Verifica | No verifica |
|--------|----------|-------------|
| **qa-bundle** | Bugs funcionales, runtime, build pass | Seguridad profunda, UX scoring |
| **judge** | Cumplimiento del PRD, métricas formales, veredicto | Ejecución de tests (usa evidencia de qa-bundle) |
| **user-chaos** | Flujos rotos por uso real, dead ends, race conditions | Pentest OWASP (eso es judge FASE 3 + security-audit) |

### Fases corregidas de user-chaos (v4)

| Fase v3 | Problema | Fase v4 | Rationale |
|---------|----------|---------|-----------|
| FASE 1: Contexto | OK | FASE 1: Contexto | Sin cambios |
| FASE 2: UX Real (judge-ux-vibe-check) | Duplicado de judge FASE 5 | FASE 2: Navegación Confusa | Hallazgos de flujo, NO scoring numérico |
| FASE 3: Análisis Ofensivo (reverse-audit) | Duplicado de judge FASE 3 | FASE 3: Validación Cruzada | Verificar post-caos que judge sigue aprobado |
| FASE 4: Veredicto Combinado | OK | FASE 4: Veredicto Combinado | Sin cambios |

**Nota clave:** El scoring numérico de UX (0-100) es job de `judge-ux-vibe-check` (judge FASE 5). `user-chaos` FASE 2 busca anomalías de flujo, no genera scores.

## Anti-Pattern: "Soy un QA Engineer" en Judge

**Síntoma:** El prompt de judge empieza con `<role>Eres un QA Engineer...</role>`

**Por qué falla:**
- El agente ejecuta tests en lugar de evaluar evidencia
- El agente busca bugs en lugar de verificar que qa-bundle ya los encontró
- El agente no emite veredicto formal porque está ocupado testeando

**Fix:**
```xml
<!-- MAL (v3) -->
<role>
Eres un Senior QA Engineer ejecutando verificación post-QA.
Tu objetivo es validar que TODAS las fases pasan.
</role>

<!-- BIEN (v4) -->
<role>
Eres un Technical Auditor ejecutando un pipeline de juicio post-QA.
Tu objetivo es evaluar objetivamente si el sistema cumple con el PRD
emitiendo un veredicto formal con evidencia verificable.

NO ejecutas tests — eso es trabajo de qa-bundle.
NO haces fixes — eso es trabajo de dev-cycle.
Tú VERIFICAS que las pruebas presentadas por qa-bundle
sean válidas, completas, y cumplan con los criterios del PRD.
</role>
```

## Research que respalda la separación

Según research de 15+ fuentes (Monte Carlo, Openlayer, Tricentis, MindStudio, EvidentlyAI):

- **"Don't confuse your judges"** (Monte Carlo 2026): Cada judge evalúa UN solo criterio. Un bundle monolítico con 6 fases es aceptable si cada fase es secuencial y verificable.
- **"Un concern por prompt"** (DEV Community 2026): Mezclar testing + evaluación + seguridad en un solo prompt es el failure mode #1.
- **"Output vs Outcome separation"** (Tricentis): El veredicto (output) ≠ el funcionamiento real (outcome). Judge verifica output; qa-bundle verifica outcome.
- **"Cross-validate with secondary model"** (Openlayer): Judge debe ser modelo distinto al generador. En pipeline de bundles: judge es un "modelo conceptual" distinto (auditor vs engineer).

## Checklist para futuras revisiones

- [ ] `qa-bundle` dice "QA Engineer" o similar ejecutor
- [ ] `judge` dice "Auditor", "Judge", "Evaluator" — NUNCA "QA" ni "Engineer"
- [ ] `user-chaos` dice "Tester de Caos", "Usuario torpe" — NUNCA "Auditor" ni "QA"
- [ ] Ninguna skill se repite entre `judge` y `user-chaos` sin razón explícita
- [ ] El veredicto de judge tiene formato formal: ESTADO + evidencia por fase
