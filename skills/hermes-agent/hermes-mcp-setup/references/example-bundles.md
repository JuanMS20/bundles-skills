# Example Skill Bundles

Dos bundles funcionales creados para un workflow Matt Pocock.

## plan-sprint

Pipeline completo de planeación. Un solo comando para grill → PRD → issues.

**Bundle:** `~/.hermes/skill-bundles/plan-sprint.yaml`
**Slash:** `/plan-sprint`

```yaml
name: plan-sprint
description: Pipeline completo de planeación — contexto, PRD e issues.
skills:
  - grill-with-docs
  - to-prd
  - to-issues
instruction: |
  FASES SECUENCIALES — no avances hasta que el usuario lo autorice.

  FASE 1 (grill-with-docs): Ejecuta el protocolo completo de grill-with-docs.
  Haz todas las preguntas relevantes, una por una. Espera la respuesta del
  usuario después de cada pregunta o ronda de preguntas relacionadas.
  NO pases a la FASE 2 hasta que el usuario diga explícitamente
  "continuemos", "siguiente fase", "pasa al PRD" o similar.

  FASE 2 (to-prd): Con toda la información recolectada en FASE 1,
  ejecuta el protocolo de to-prd para generar el documento de requerimientos.
  Espera aprobación o correcciones del usuario antes de continuar.

  FASE 3 (to-issues): Una vez el PRD esté aprobado, desglosa en issues
  usando el protocolo de to-issues. Confirma con el usuario antes de
  publicar si es necesario.
```

## close-out

Cierre de feature. improve-codebase-architecture → diagnose → handoff.

**Bundle:** `~/.hermes/skill-bundles/close-out.yaml`
**Slash:** `/close-out`

```yaml
name: close-out
description: Cierre de feature — mejora arquitectura, diagnóstico y handoff.
skills:
  - improve-codebase-architecture
  - diagnose
  - handoff
instruction: |
  FASES SECUENCIALES — no avances hasta que el usuario lo autorice.

  FASE 1 (improve-codebase-architecture): Ejecuta el protocolo completo de
  improve-codebase-architecture. Inspecciona la arquitectura actual, identifica
  deuda técnica y oportunidades de mejora. Puedes hacer preguntas al usuario
  si necesitas claridad. NO pases a FASE 2 sin autorización explícita del
  usuario ("continuemos", "siguiente", "pasa a diagnose").

  FASE 2 (diagnose): Si el usuario reportó bugs o hay issues conocidos,
  ejecuta el protocolo de diagnose. Reproduce, minimiza, hipotetiza,
  instrumenta, repara. Espera confirmación del usuario antes de continuar.

  FASE 3 (handoff): Una vez resueltos arquitectura y bugs, genera el
  handoff document completo para que la próxima sesión retome sin
  pérdida de contexto.
```

## Bundle Anatomy

| Field | Propósito |
|---|---|
| `name` | Slug usado para `/name` |
| `description` | Texto que aparece en `hermes bundles list` |
| `skills` | Lista de skills a cargar (deben existir individualmente) |
| `instruction` | **Se pierde si usas `hermes bundles create`** — añádelo manualmente. Sobrescribe el user query con estas instrucciones. |
