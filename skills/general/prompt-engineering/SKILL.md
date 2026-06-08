---
name: prompt-engineering
description: "Framework para diseñar, optimizar y auditar prompts LLM. Cubre técnicas (CoT, few-shot, meta-prompting, ToT, ReAct), estructura (XML tags, delimiters, schema), anti-patterns de producción, y tácticas específicas por provider (Claude/GPT/Gemini). Use when user wants to write, improve, debug, or optimize a prompt, or asks about prompt engineering techniques."
---

# Prompt Engineering

Framework completo para diseñar prompts de alta calidad. No es "tips y tricks" — es ingeniería de contexto.

## Quick Start: Checklist de un Buen Prompt

Antes de escribir, verifica que tienes:
1. **Tarea clara** — una oración dice qué hacer, no cómo ser
2. **Contexto** — datos relevantes, no todo lo que tengas
3. **Restricciones** — formato, longitud, qué excluir
4. **Ejemplos** — 2-3 representativos del espacio de entrada
5. **Criterio de éxito** — cómo saber si el output es correcto

Después de escribir:
6. **Posición** — instrucciones clave al PRINCIPIO o FINAL, nunca en el medio
7. **Longitud** — 150-300 palabras es el sweet spot. >3000 tokens = degradación
8. **Reglas** — máximo 8-10 instrucciones. Más = triage del modelo
9. **Framing positivo** — "usa X" > "no uses Y"

## Estructura: XML Tags (Universal)

Todos los providers modernos reconocen XML tags. Son superiores a Markdown y JSON para prompts:

```xml
<context>
  [Datos, documentos, background]
</context>

<instructions>
  [Qué hacer, paso a paso]
</instructions>

<examples>
  <example>
    input: [caso representativo]
    output: [respuesta esperada]
  </example>
</examples>

<constraints>
  [Formato, longitud, exclusiones]
</constraints>

<output_format>
  [Schema explícito: campos, tipos, estructura]
</output_format>
```

**Regla de oro**: El schema va en `<output_format>` como texto explícito. Los ejemplos demuestran contenido, NO estructura.

## Técnicas por Problema

| Problema | Técnica | Cuándo usar |
|---|---|---|
| Razonamiento multi-paso | Chain-of-Thought | Skip en modelos reasoning (o-series, extended thinking) |
| Tarea ambigua | Step-back prompting | Context amplio primero, pregunta específica después |
| Múltiples caminos | Tree-of-Thoughts | Planning, diseño, puzzles |
| Output inconsistente | Few-shot (3-5 ejemplos) | Siempre en Gemini. Diversidad > perfección |
| Query compleja | Self-ask decomposition | Sub-preguntas → sub-respuestas → síntesis |
| Necesita herramientas | ReAct (Reason+Act) | Agentes con tools |
| Alta confianza requerida | Self-consistency | Múltiples respuestas, majority vote |
| Prompt mal definido | Meta-prompting | El modelo genera/refina su propio prompt |

Ver detalles y ejemplos en [references/techniques.md](references/techniques.md).

## Anti-Patterns Top 5

1. **Few-Shot Pollution** — Ejemplos contradicen instrucciones. El modelo sigue ejemplos sobre texto. Diagnostic: verificar cada ejemplo contra cada requirement.
2. **Instruction Stacking** — >10 reglas = triage del modelo. Comprimir en principios + ejemplos.
3. **Format Via Example** — Nunca asumir que 1-2 ejemplos generalizan formato. Schema explícito SIEMPRE.
4. **Persona Stuffing** — "Eres un experto mundial" es inútil en tareas técnicas. Solo ayuda en creatividad.
5. **Negation Overload** — "No hagas X, no hagas Y, nunca Z" → Pink Elephant Problem. Framing positivo siempre.

Ver detalles completos en [references/anti-patterns.md](references/anti-patterns.md).

## Model-Specific (Lo que cambia por provider)

**Claude (Anthropic):**
- XML tags obligatorios. Instrucciones literales — no generaliza lo que no dices.
- Lenguaje agresivo ("CRITICAL!", "NEVER EVER") empeora resultados.
- Effort parameter: `xhigh` para coding/agentic, `high` mínimo para tasks complejos.
- No pasar thinking blocks como input en siguientes turnos.

**GPT (OpenAI):**
- Prompts conversacionales. "Think step by step" HACE DAÑO en reasoning models.
- Zero-shot primero — GPT infiere bien. Few-shot solo si zero-shot falla.
- Pinar a snapshots específicos (router cambia comportamiento entre versiones).
- Delimiters: `"""`, `###`, ```` ``` ```` funcionan bien.

**Gemini (Google):**
- Pocas palabras, directo. Few-shot SIEMPRE (zero-shot no preferido).
- Preguntas específicas al FINAL del prompt, después del contexto.
- 2M tokens de contexto → posición es aún más crítica.

Ver detalles en [references/model-specific.md](references/model-specific.md).

## Iteración: Cómo Mejorar un Prompt Existente

1. **Medir primero** — sin eval, no sabes si mejoras o empeoras
2. **Cambiar una cosa** — nunca reescribir todo de golpe
3. **Añadir, no reemplazar** — si algo funciona, mantenerlo
4. **Compresión** — cada iteración debería reducir word count o mantenerlo
5. **Regression test** — verificar que lo que funcionaba sigue funcionando

## Fuentes

- Anthropic: docs.anthropic.com/en/docs/build-with-claude/prompt-engineering
- Google: kaggle.com/whitepaper-prompt-engineering (Lee Boonstra)
- OpenAI: platform.openai.com/docs/guides/text
- DAIR.AI: promptingguide.ai / github.com/dair-ai/Prompt-Engineering-Guide
- Digital Applied: "10 Anti-Patterns" (2026)
- Thomas Wiegold: "Prompt Engineering Best Practices 2026"
- Karpathy (Jun 2025): "LLM is a CPU, context window is RAM"
