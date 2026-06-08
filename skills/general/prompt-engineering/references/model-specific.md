# Tácticas Específicas por Provider

Los tres providers principales tienen diferencias significativas en cómo procesan prompts. No existe "un prompt para todos".

---

## Claude (Anthropic)

**Principio**: Literal. No generaliza lo que no le dices explícitamente.

### Estructura: XML Tags

XML es el formato nativo de Claude. Superior a Markdown y numbered lists.

```xml
<task>
Analiza el código y reporta bugs.
</task>

<code>
def process(data):
    result = data.filter(x => x.active)
    return sorted(result)
</code>

<rules>
- Reportar todo bug que encuentres, incluyendo incertidumbres
- No filtrar por severidad — un paso separado hará eso
- Tu objetivo es cobertura
</rules>

<output_format>
Para cada bug:
- Línea: [número]
- Tipo: [bug/tipo]
- Descripción: [qué está mal]
- Severidad: [alta/media/baja]
</output_format>
```

### Esfuerzo y Pensamiento (Effort Parameter)

| Nivel | Uso |
|---|---|
| `xhigh` | Coding, agentic — empezar aquí |
| `high` | Mínimo para tasks de alta inteligencia |
| `medium` | Balanceado |
| `low` | Latency-sensitive (riesgo de under-thinking) |

A `xhigh`/`max`: setear `max_tokens` a 64k+.

### Anti-Patterns Específicos de Claude

- **Lenguaje agresivo empeora**: "CRITICAL!", "YOU MUST", "NEVER EVER" → peor output. Usar instrucciones calmas y directas.
- **Thinking blocks no se reenvían**: No pasar thinking blocks como input en turnos siguientes.
- **Literal following**: Si necesitas scope amplio, decirlo explícito: "Aplica esto a TODAS las secciones, no solo la primera".

### Frontend/Design Defaults

Claude Opus 4.7 tiene un "house style" persistente:
- Backgrounds crema/off-white (~`#F4F1EA`)
- Tipografía serif (Georgia, Fraunces, Playfair)
- Acentos terracota/amber

Para override efectivo:
1. **Paleta concreta**: Dar hex codes exactos
2. **Proponer antes de construir**: Pedir 4 opciones de dirección visual, usuario elige una

**Anti-slop mínimo**:
```xml
<frontend_aesthetics>
No usar estética genérica: fonts overused (Inter, Roboto, Arial), 
color schemes cliché (gradientes purple), layouts predecibles.
Usar fonts únicos, colores cohesivos, animaciones con propósito.
</frontend_aesthetics>
```

### Subagentes

Claude 4.x spawnea menos subagentes por defecto. Es steerable:
```
No spawnees un subagente para trabajo que puedes completar en una sola respuesta.
Spawnea múltiples subagentes en el mismo turno cuando bifurques 
entre items o leas múltiples archivos.
```

---

## GPT (OpenAI)

**Principio**: Conversacional. Infers bien desde contexto mínimo.

### Estructura: Delimiters

GPT funciona bien con delimiters de texto:

```
Sumariza el texto como bullet points de los puntos más importantes.

###Texto###
{text aquí}###
```

Delimiters comunes: `"""`, `###`, ```` ``` ````, `---`.

### Reasoning Models (o-series, GPT-5)

- **"Think step by step" puede EMPEORAR** resultados en reasoning models — ya lo hacen internamente
- Zero-shot primero. GPT-5 infiere bien; añadir few-shot solo si zero-shot falla
- "Think hard about this" puede trigger el modelo reasoning literalmente
- **Pinar a snapshots**: `gpt-5-2025-08-07` en vez de solo `gpt-5`. El router cambia comportamiento.

### Prompts Conversacionales

GPT prefiere prompts que suenan naturales:
```
# BIEN para GPT:
Necesito que analices este código y me digas qué está mal. 
Aquí está:
[código]

# MENOS EFECTIVO (funciona pero no óptimo):
<task>Analyze the following code for defects</task>
<code>[código]</code>
```

### Structured Outputs

OpenAI tiene `response_format` con JSON schema enforcement:
```python
response = client.chat.completions.create(
    model="gpt-4o",
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "analysis",
            "schema": {
                "type": "object",
                "properties": {
                    "bugs": {"type": "array", "items": {"type": "string"}},
                    "severity": {"type": "string", "enum": ["low","medium","high"]}
                }
            }
        }
    }
)
```

---

## Gemini (Google)

**Principio**: Directo y few-shot obligatorio.

### Reglas de Google (Whitepaper Lee Boonstra)

1. **Few-shot siempre**: Zero-shot NO es preferido para Gemini. Incluir ejemplos siempre.
2. **Preguntas al final**: La pregunta/task va DESPUÉS del contexto/datos. Nunca antes.
3. **Directo**: Prefiere prompts más cortos y directos que Claude o GPT.

### Estructura Recomendada

```
[Contexto/Datos aquí]

[Ejemplos aquí]

[Pregunta específica aquí — siempre al final]
```

### Ventana de 2M Tokens

- Posición es CRÍTICA con ventana grande. Lost-in-the-middle se agrava.
- RAG + compresión es obligatorio para contexto largo.
- No llenar la ventana porque puedes — llenarla porque necesitas.

### Prompting Strategies

```
# Ejemplo Gemini-style:
Contexto: AcmeTech es una empresa de paneles solares fundada en 2020...

Ejemplos:
P: "¿Cuál es nuestro producto estrella?" → R: "Paneles solares ACME-400X"
P: "¿Mercado objetivo?" → R: "PYMEs con techo propio"

P: "¿Qué estrategia recomiendas para Q4 2026?"
```

---

## Comparación Rápida

| Aspecto | Claude | GPT | Gemini |
|---|---|---|---|
| Estructura | XML tags | Delimiters/conversacional | Directo + ejemplos |
| Ejemplos | 3-5 en `<example>` | Zero-shot primero | Siempre few-shot |
| CoT explícito | Útil en non-thinking models | Skip en reasoning | Generalmente útil |
| Persona | Solo creatividad | Innecesario | Innecesario |
| Posición pregunta | Flexible | Flexible | SIEMPRE al final |
| Lenguaje | Calmo, directo | Natural, conversacional | Conciso, directo |
| Schema output | En `<output_format>` | `response_format` API | En instrucciones |
| Agresividad | Empeora resultados | Neutral | Neutral |
| Snapshot | Estable | CAMBIA (router) | Estable |

---

## Optimización Automática

Para prompts que se usan en producción repetidamente, considerar optimización automática:

### DSPy
Framework declarativo que optimiza prompts automáticamente. Trata prompts como código compilable:
- Define signature (input → output)
- Proporciona ejemplos de training
- DSPy optimiza el prompt automáticamente
- Útil para pipelines con múltiples pasos LLM

### Meta-Prompting Auto-Refine
El modelo genera mejoras a su propio prompt:
```
Aquí está un prompt y 5 ejemplos de output incorrecto.
Analiza los patrones de error y sugiere 3 cambios específicos 
al prompt que los prevenirían.
```

### A/B Testing con Eval Suite
Siempre que sea posible:
1. Prompt A (actual) vs Prompt B (modificado)
2. Correr contra 50+ ejemplos representativos
3. Medir accuracy, formato, latencia
4. Ship B solo si mejora estadísticamente significativa
