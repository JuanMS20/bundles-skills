# Skill Quality Research — 50 Búsquedas (2026-06-08)

## El Estándar Abierto (agentskills.io)

Un skill es un **directorio**, no un archivo:
```
skill-name/
  SKILL.md          # Requerido: YAML frontmatter + instrucciones
  scripts/          # Opcional: código ejecutable
  references/       # Opcional: docs suplementarios (carga bajo demanda)
  assets/           # Opcional: templates, schemas
```

YAML Frontmatter mínimo:
```yaml
name: skill-name          # Max 64 chars
description: Cuando usar   # Max 1024 chars, ROUTING TRIGGER
```

## Tres Capas de Progressive Disclosure

| Capa | Contenido | Cuándo | Budget |
|------|-----------|--------|--------|
| Index | name + description | Cada sesión | ~100 tokens |
| Load | Full SKILL.md | Cuando activa | <5,000 tokens (<500 líneas) |
| Runtime | scripts/, references/ | Bajo demanda | Sin límite |

## La "Tax Test" (Perplexity)

Aplicar a cada oración: **"¿El agente haría esto mal sin esta instrucción?"**
Si NO → ELIMINAR. Cada skill es un impuesto sobre el contexto.

## Descripción = Routing Trigger

NO es documentación — es el gatillo de activación:
- Empezar con "Use when..." o "Load when..."
- Max 50 palabras
- Incluir trigger phrases reales del usuario
- Probar con prompts positivos y negativos

## Anti-Hallucination en Skills

| Patrón | Cómo | Por qué |
|--------|------|---------|
| Gotchas | Hechos específicos del entorno | Mayor valor — previene asunciones |
| Ejemplos negativos | "NO hagas X" | Más poderoso que "haz Y" |
| Defaults concretos | Un approach que funciona | Reduce decisiones del modelo |
| Scripts deterministas | Parsers en scripts/ | Elimina ambigüedad |
| Output templates | Formato exacto | Contrato consistente |

## Verificación de Skills

Tres capas:
1. Trigger → ¿Se activa en prompts correctos?
2. Execution → ¿El agente siguió pasos?
3. Output → ¿Cumple el contrato?

Métodos: checks deterministas, LLM-as-Judge, 10-20 prompts, 3-5 trials.

## 6 Modos de Fallo de Agentes

| Modo | Prevención |
|------|------------|
| Context degradation | Progressive disclosure, checkpoints |
| Specification drift | Output templates, verification steps |
| Sycophantic confirmation | Gotchas, negative examples |
| Tool call failures | Retry with backoff, timeout |
| Cascading failure | Checkpointing, graceful degradation |
| Silent failure | Verification steps, LLM-as-Judge |

## SkillsBench Evidence

- Skills curadas: +16.2pp pass rate
- Skills enfocadas (2-3 módulos) > docs comprehensivas
- Models pequeños CON Skills = models grandes SIN Skills
- Self-generated Skills: CERO beneficio

## Seguridad

- 26.1% skills community tienen vulnerabilidades
- Scripts ejecutables: 2.12x más propensos a vulnerabilidades
- Siempre escanear antes de instalación
