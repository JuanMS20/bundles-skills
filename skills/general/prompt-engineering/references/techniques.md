# Técnicas de Prompt Engineering

Catálogo de técnicas con ejemplos concretos y cuándo usar/cada una.

## 1. Zero-Shot Prompting

Instrucción directa sin ejemplos. Baseline para cualquier tarea.

```
Clasifica el siguiente texto como POSITIVO, NEGATIVO o NEUTRO:
Texto: "El servicio fue aceptable pero la comida demoró demasiado"
Clasificación:
```

**Cuándo**: Tareas simples, modelos grandes (GPT-5+, Claude Opus), primer intento.
**Cuándo NO**: Formato output crítico, tarea ambigua, modelo pequeño.

---

## 2. Few-Shot Prompting

2-5 ejemplos input/output antes de la tarea real.

**Regla clave (Min et al., 2022)**: La distribución del espacio de input importa más que la corrección de labels individuales. Incluso ejemplos con labels random superan zero-shot.

```
Clasifica las reseñas:

Reseña: "Increíble experiencia, volvería sin dudar"
Sentimiento: POSITIVO

Reseña: "Peor servicio que he recibido en mi vida"
Sentimiento: NEGATIVO

Reseña: "Estaba bien, nada especial"
Sentimiento: NEUTRO

Reseña: "El ambiente era agradable pero los precios excesivos"
Sentimiento:
```

**Mejores prácticas**:
- 3-5 ejemplos con diversidad de inputs (no solo casos fáciles)
- Para Claude: envolver en `<example>` tags
- Para Gemini: SIEMPRE incluir few-shot (zero-shot no preferido por Google)
- Para GPT: probar zero-shot primero, añadir few-shot solo si falla

---

## 3. Chain-of-Thought (CoT)

El modelo razona paso a paso antes de dar la respuesta final.

```
Un tren viaja 30 millas en 50 minutos. ¿Cuánto viajará en 1.5 horas a la misma velocidad?
Piensa paso a paso antes de dar la respuesta final.
```

**Cuándo**: Razonamiento multi-paso, matemáticas, deducción lógica, debugging.
**Cuándo NO**: Modelos reasoning (o-series, Claude Extended Thinking, Gemini Thinking Mode) — ya lo hacen internamente. Añadir "think step by step" es redundante o perjudicial.

**Few-Shot CoT**: Ejemplos que muestran el razonamiento:
```
P: ¿Es impar la suma de los dígitos de 342?
R: Los dígitos de 342 son 3, 4 y 2. Suma = 3+4+2 = 9.
   9 es impar. Respuesta: Sí.

P: ¿Es impar la suma de los dígitos de 578?
R:
```

---

## 4. Tree-of-Thoughts (ToT)

Generalización de CoT: explorar múltiples ramas de solución.

```
Diseña un sistema de autenticación para una app móvil bancaria.

Primero, propone 3 enfoques diferentes (Thought 1, 2, 3).
Para cada uno, evalúa pros y contras brevemente.
Decide cuál es mejor y explica por qué.
Luego detalla los pasos de implementación del enfoque elegido.
```

**Cuándo**: Planning, arquitectura, diseño, puzzles, problemas con múltiples caminos válidos.
**Cuándo NO**: Tareas con respuesta única correcta, consultas directas.

---

## 5. Self-Ask Decomposition

El modelo descompone una pregunta compleja en sub-preguntas, responde cada una, y sintetiza.

```
Descompone la pregunta del usuario en las sub-preguntas necesarias para responderla.
Responde cada sub-pregunta.
Luego proporciona la respuesta final sintetizada.

Pregunta: "¿Cuál es la mejor opción para una startup de 5 personas que necesita 
colaboración en documentos en tiempo real con presupuesto limitado?"
```

**Cuándo**: Queries multi-faceta, comparaciones, recomendaciones complejas.
**Patrón**: Aparece naturalmente en modelos reasoning, pero explicitarlo mejora estructura.

---

## 6. Step-Back Prompting

Dos etapas: análisis amplio primero, pregunta específica después.

**Etapa 1** (broad):
```
Lista los factores principales que afectan la retención de usuarios en una app móvil.
```

**Etapa 2** (targeted):
```
Dados esos factores, ¿qué pasos recomendarías para reducir churn en nuestra app de fitness?
```

**Cuándo**: Contexto amplio necesario antes de responder. Tareas donde el modelo necesita "preparar el terreno".
**Ventaja**: Output más estructurado y comprehensivo que pregunta directa.

---

## 7. Meta-Prompting

El modelo genera o refina su propio prompt antes de responder.

```
Reescribe la pregunta del usuario para hacerla más precisa y detallada para un 
asistente de planificación de viajes, luego responde la pregunta refinada.

Pregunta del usuario: "Quiero ir a Europa barato"
```

**Variante — Prompt como output**:
```
Genera el mejor prompt posible para la siguiente tarea:
"Tengo 1000 emails de clientes y necesito clasificarlos por urgencia"
```

**Cuándo**: Queries vagas, under-specified tasks, cuando necesitas estructurar un problema antes de resolverlo.

---

## 8. ReAct (Reason + Act)

Alternar entre razonamiento y acciones (tool calls). El agente piensa, actúa, observa, repite.

```
Eres un asistente de investigación. Para cada pregunta:
1. Thought: Razona qué necesitas saber
2. Action: Usa la herramienta adecuada (search, calculator, etc.)
3. Observation: Analiza el resultado
4. Repite hasta tener suficiente información
5. Answer: Proporciona la respuesta final

Pregunta: "¿Cuál es la población combinada de las 3 ciudades más grandes de Brasil?"
```

**Cuándo**: Agentes con herramientas, tareas que requieren lookup/verificación externa.
**Base de**: La mayoría de frameworks de agentes (LangChain, AutoGPT, etc.).

---

## 9. Self-Consistency

Generar múltiples respuestas independientes y seleccionar la más consistente (majority vote).

```
Responde esta pregunta 5 veces de forma independiente:
[pregunta]

Luego compara las respuestas y proporciona la respuesta final 
basada en la respuesta más frecuente/coherente.
```

**Cuándo**: Alta confianza requerida, tasks con alta varianza, evaluaciones críticas.
**Trade-off**: 5x el costo para aproximarse a majority vote.

---

## 10. Contextual Priming (RAG Pattern)

Prepend contexto relevante antes de la pregunta.

```xml
<context>
AcmeTech se especializa en energías renovables. Ofrece paneles solares, 
turbinas eólicas y sistemas de almacenamiento. Clientes objetivo: PYMEs.
</context>

<question>
Genera una estrategia de marketing Q4 para lanzar una nueva línea de 
baterías domésticas de almacenamiento solar.
</question>
```

**Regla**: Contexto debe caber en la ventana. Mantenerlo conciso y relevante.
**Placement**: Para Gemini, la pregunta va DESPUÉS del contexto (siempre al final).
**Cuándo**: Información específica del dominio, datos actualizados, knowledge que el modelo no tiene.

---

## Combinaciones Recomendadas

| Escenario | Combinación |
|---|---|
| Clasificación con formato fijo | Few-shot + Schema explícito |
| Análisis complejo | Step-back + CoT |
| Agente con tools | ReAct + Self-ask |
| Output creativo controlado | Few-shot (estilo) + Constraints |
| Query vaga del usuario | Meta-prompting + Step-back |
| Alta confiabilidad | Self-consistency + CoT |
