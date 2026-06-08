# Anti-Patterns de Prompt Engineering

10 anti-patterns de producción que degradan calidad silenciosamente. Basado en auditorías reales de producción (Digital Applied, 2026).

## Regla Universal

> "Cada táctica se convierte en anti-pattern cuando se aplica sin medir."

Si no tienes eval suite, no puedes saber si tu prompt es bueno o si se degradó.

---

## AP-01: Few-Shot Pollution

**Severidad**: MÁXIMA — causa #1 de regression silenciosa.

**Problema**: Ejemplos se añaden al inicio. Instrucciones se editan después. Ejemplos nunca se actualizan. Tres ejemplos contradictorios superan un párrafo de instrucciones en modelos frontier.

**Diagnóstico**:
1. Lista cada requirement de la instrucción
2. Verifica cada ejemplo contra cada requirement
3. 3+ contradicciones = regression casi segura

**Caso real**: Prompt de clasificación editado 12 veces. Ejemplos aún devolvían texto plano cuando la instrucción pedía JSON con campo de razón. Accuracy bajó ~15 puntos sin que nadie lo notara.

**Fix**:
- Versionar ejemplos e instrucciones juntos
- PR review debe verificar ejemplos explícitamente
- Eval case que aserte el output shape declarado en instrucciones

---

## AP-02: Instruction Stacking

**Severidad**: Alta — compuesta con cada nueva regla.

**Problema**: Cada bug report añade una regla. 15-20 bullet points saturan la atención del modelo. Pasados 8-10, el modelo hace triage de cuáles seguir.

**Síntoma**: Prompt maneja edge cases raros perfectamente pero falla en la tarea principal.

**Fix**: Compresión, no eliminación.
1. Escribir cada regla en un post-it
2. Agrupar por intención
3. Grupos típicamente < mitad de las reglas originales
4. Reescribir: una oración principista por grupo + bloque de ejemplos para edge cases

**Ejemplo de compresión**:
```
# ANTES (12 reglas):
- No uses jerga técnica
- Evita oraciones pasivas
- No repitas ideas
- Mantén párrafos cortos
- Usa vocabulario simple
- ... (7 más)

# DESPUÉS (3 principios + ejemplos):
Escribe en lenguaje directo y simple. Cada párrafo debe avanzar una idea.
Prioriza claridad sobre elegancia.

<examples>
  <good>Usa la opción "Exportar" del menú principal</good>
  <bad>La funcionalidad de exportación puede ser accedida a través del menú</bad>
</examples>
```

---

## AP-03: Format Via Example

**Severidad**: Media-Alta — invisible hasta que parsing rompe.

**Problema**: 1-2 ejemplos demuestran formato. Funciona en 80% del tráfico (inputs similares a ejemplos). Falla en 20% (inputs diferentes): YAML en vez de JSON, campos faltantes, comentarios extra.

**Fix**: Defense in depth.
1. **Schema explícito en instrucciones**: "returna JSON con campos X (string), Y (number), Z (array de strings)"
2. **Ejemplos para contenido, no estructura**: Schema es source of truth
3. **Provider-level enforcement**: `response_format` (OpenAI), tool-call schemas (Anthropic), response schema (Gemini)
4. **Eval adversarial**: Input intencionalmente diferente a los ejemplos, verificar schema intacto

---

## AP-04: Persona Stuffing

**Severidad**: Media — de inútil a activamente perjudicial.

**Problema**: "Eres un experto mundial en X" consume un slot de atención de alto peso sin aportar precisión. En modelos frontier actuales, es ruido.

**Cuándo funciona**:
- Tareas creativas donde el tono ES el deliverable
- Imitación de estilo, role-play, diálogo

**Cuándo daña**:
- Tasks técnicas: clasificación, extracción, código, razonamiento
- Añade ruido estilístico sin mejorar precisión factual
- Puede sesgar el modelo hacia respuestas más "elaboradas" cuando se necesita precisión

**Fix**: Strip persona. Ejecutar eval con y sin. Si empata o mejora sin persona → ship sin persona.

---

## AP-05: Negation Overload (Pink Elephant Problem)

**Severidad**: Media — efecto sutil pero medible.

**Problema**: "No uses mock data", "No inventes URLs", "Nunca repitas" → el modelo procesa el concepto prohibido como signal. "No pienses en un elefante rosa".

**Fix**: Siempre framing positivo.
```
# MAL:
No uses datos ficticios. No inventes URLs. No repitas información.

# BIEN:
Usa exclusivamente datos verificados. Incluye solo URLs que existan en los datos proporcionados. Cada punto debe aportar información nueva.
```

---

## AP-06: Reference-Free Constraints

**Severidad**: Media.

**Problema**: "Sé conciso", "Sé preciso", "Sé creativo" — sin referencia concreta, cada modelo interpreta diferente. "Conciso" para GPT puede ser 200 palabras; para Claude, 50.

**Fix**: Especificar concretamente.
```
# MAL:
Sé conciso pero completo.

# BIEN:
Responde en máximo 3 párrafos. Cada párrafo: 2-3 oraciones.
Si la respuesta requiere más detalle, resume primero y luego profundiza por secciones.
```

---

## AP-07: Lost in the Middle

**Severidad**: Alta para prompts largos.

**Problema**: Información en el medio del contexto se ignora. Performance curve es U-shaped: primero y último se procesan bien, el medio pierde ~30% de accuracy (Liu et al., 2024, 2500+ citas).

**Fix**:
- Instrucciones críticas: PRIMERO o ÚLTIMO
- Datos de referencia: al principio
- La pregunta/task: al final
- Contexto largo: usar RAG para filtrar solo lo relevante antes de inyectar

---

## AP-08: Prompt Drift

**Severidad**: Alta en producción.

**Problema**: Prompts se editan incrementalmente sin eval. Resultado: prompt original limpio se convierte en overlapped contradictory directives.

**Fix**:
- Git track de prompts (no hardcode en código)
- Eval suite que corre contra el prompt en CI/CD
- `git log -p` para revisar historia de cambios
- Cada cambio de prompt pasa por review con eval comparison

---

## AP-09: Over-Specification

**Severidad**: Baja-Media.

**Problema**: Especificar cada edge case imaginable. El prompt crece hasta que el modelo pierde la tarea principal entre las excepciones.

**Fix**: Especificar el happy path claramente. Cubrir los 2-3 edge cases más frecuentes con ejemplos. Dejar que el modelo generalice para el resto.

---

## AP-10: Eval Blindness

**Severidad**: Fundamental — sin esto, todo lo anterior es invisible.

**Problema**: No tener eval suite significa no poder medir mejoras ni detectar regresiones. "Funciona" se demuestra con 2-3 ejemplos manuales, no con cobertura real.

**Fix mínimo viable**:
1. 10-20 ejemplos input/output que representen el espacio de uso
2. Script que corre el prompt contra cada ejemplo
3. Check automático de formato + spot-check manual de calidad
4. Correr en CI/CD o antes de cada cambio de prompt

---

## Checklist de Auditoría de Prompts

Para cada prompt en producción:

```
[ ] Ejemplos sincronizados con instrucciones actuales
[ ] < 10 instrucciones distinctas
[ ] Schema explícito (no solo ejemplos) para formato output
[ ] Sin persona innecesaria (test: funciona igual sin ella?)
[ ] Framing positivo (reemplazar negaciones)
[ ] Instrucciones críticas al inicio o final
[ ] Word count en sweet spot (150-300 palabras)
[ ] Eval suite existe y pasa
[ ] Git trackeado con historial visible
[ ] No hay info stale (versiones, URLs que cambian)
```
