# Bundle YAML Templates

## Estructura base

```yaml
name: nombre-del-bundle
description: Una línea describiendo qué hace
skills:
  - skill-1
  - skill-2
instruction: |
  El prompt que se ejecuta.
  Usa FASES SECUENCIALES.
  Referencia skills por nombre en cada fase.
```

## Templates por bundle

### plan-sprint (YA EXISTE en ~/.hermes/skill-bundles/)
```yaml
name: plan-sprint
description: Pipeline completo de planeación — contexto, PRD e issues.
skills:
  - grill-with-docs
  - to-prd
  - to-issues
instruction: |
  FASES SECUENCIALES — no avances hasta que el usuario lo autorice.
  FASE 1 (grill-with-docs): Protocolo completo. Una pregunta a la vez.
  FASE 2 (to-prd): Generar PRD con info de FASE 1.
  FASE 3 (to-issues): Desglosar PRD en issues.
```

### dev-cycle
```yaml
name: dev-cycle
description: Ciclo de desarrollo TDD — zoom-out, implementación, code review.
skills:
  - zoom-out
  - tdd
  - code-review
instruction: |
  FASE 0 (zoom-out): Análisis completo. DETENTE y espera confirmación.
  FASE 1 (tdd): Por cada issue: RED → GREEN → REFACTOR → Commit.
  FASE 2 (code-review): Checklist completo. BLOCKERs = fix inmediato.
```

### smoke-test
```yaml
name: smoke-test
description: Verificación rápida de startup — pass/fail binario.
skills: []
instruction: |
  Detecta tipo de app. Ejecuta comando de startup.
  PASS → capturar URL/port. FAIL → capturar error.
  Solo verificas arranque. No funcionalidad.
```

### qa-functional
```yaml
name: qa-functional
description: Testing funcional — test cases, error handling, aceptación.
skills:
  - judge-functional-test
  - judge-error-handling
instruction: |
  FASE 1 (judge-functional-test): Happy paths + edge cases + DB verification.
  FASE 2 (judge-error-handling): Try/catch, red, auth, DB.
  NO seguridad, performance, ni UX.
```

### security-audit
```yaml
name: security-audit
description: Auditoría OWASP — multi-vector + ofensivo externo.
skills:
  - judge-security-gates
  - reverse-audit
instruction: |
  FASE 1 (judge-security-gates): Multi-vector interno.
  FASE 2 (reverse-audit): Perspectiva de atacante externo.
  Mínimo 3 vectores por plataforma.
```

### performance-check
```yaml
name: performance-check
description: Métricas REALES — no estimaciones.
skills:
  - judge-performance-budget
instruction: |
  Web: Lighthouse, bundle, TTI. Móvil: cold start, memory.
  Juegos: FPS, frame time. CLI: startup, binary size.
  Cada métrica con valor REAL + threshold.
```

### ux-evaluation
```yaml
name: ux-evaluation
description: Usabilidad + AI slop detection.
skills:
  - judge-ux-vibe-check
  - design-quality
instruction: |
  FASE 1 (judge-ux-vibe-check): 5 second test, navegación, formularios.
  FASE 2 (design-quality): Detección de AI slop.
  Score UX < 50 = FAIL. AI slop > 50 = FAIL.
```

### chaos-test
```yaml
name: chaos-test
description: Testing desde FUERA — usuario torpe, edge cases.
skills:
  - user-chaos-tester
instruction: |
  Vectores: autenticación, entrada, confusión, timing, concurrencia.
  Verificar en DB después de cada interacción.
  Recovery testing. Mínimo 5 vectores.
```

### launch-readiness
```yaml
name: launch-readiness
description: Checklist producción — GO / NO-GO.
skills:
  - judge-launch-readiness
instruction: |
  Config, seguridad, observabilidad, resiliencia, distribución, docs.
  0 bloqueantes = GO. 1-2 = CONDICIONAL. 3+ = NO-GO.
```

### close-out
```yaml
name: close-out
description: Cierre — arquitectura, sostenibilidad, handoff.
skills:
  - improve-codebase-architecture
  - diagnose
  - handoff
instruction: |
  FASE 1 (improve-codebase-architecture): Arquitectura.
  FASE 2: Sostenibilidad (CI/CD, migraciones).
  FASE 3 (diagnose): Bugs conocidos.
  FASE 4 (handoff): Documento autocontenido.
```

### doc-forge
```yaml
name: doc-forge
description: Documentación profesional — manual + PDF.
skills:
  - project-mapper
  - manual-writer
  - pdf-export
instruction: |
  FASE 0: Clasificar tipo de doc.
  FASE 1 (project-mapper): Blueprint YAML.
  FASE 2 (manual-writer): Capítulos con muestra.
  FASE 3 (pdf-export): Generar PDF.
```
