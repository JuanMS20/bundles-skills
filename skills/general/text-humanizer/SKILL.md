---
name: text-humanizer
description: "Reescribe texto eliminando patrones detectables de IA (perplejidad baja, baja burstiness, buzzwords, hedging) preservando registro y esencia. Use when user pide 'humanizar', 'pasar filtros de IA', 'reescribir sin que suene a IA', 'bypass AI detection', 'no suene a robot', o quiere texto que lea como escrito por humano. Adapta a registros académico, profesional y general."
---

# Text Humanizer

Reescribe texto eliminando patrones que los detectores de IA buscan, preservando esencia y rigor.

## Cómo detectan la IA (investigado mayo 2026)

Los detectores (GPTZero, Turnitin, Originality.ai, Copyleaks) usan 4 métricas principales:

1. **Perplejidad (Perplexity)**: Qué tan "predecible" es el texto. IA produce texto de baja perplejidad (siguiente palabra obvia). Humanos usan elecciones menos predecibles.
2. **Burstiness**: Variación en longitud/complejidad de oraciones. IA produce oraciones uniformes. Humanos mezclan oraciones de 3 y 35 palabras.
3. **Embeddings semánticos**: IA organiza conceptos de forma predecible en espacio vectorial.
4. **Fingerprinting estilístico**: Cada modelo tiene "tells" específicos (ChatGPT: "delve", "dive into"; Claude: estructuración enumerada sistemática).

## Patrones IA — Detección y Ruptura

### Léxicos (buzzwords y frases red flag)

Basado en Forbes (Feb 2026) y Olivia Cal Copywriting (2026):

**Eliminar o sustituir:**

| Categoría | Red Flags | Alternativa humana |
|-----------|-----------|-------------------|
| Aperturas | "In today's fast-paced world", "At its core", "Imagine a world" | Ir al grano directo |
| Verbos IA | "delve", "leverage", "foster", "empower", "ignite", "streamline", "navigate" (metafórico) | "analizar", "usar", "ayudar", "mejorar" |
| Adjetivos vacíos | "cutting-edge", "seamless", "robust", "scalable", "dynamic", "transformative" | Descripciones concretas con datos |
| Metáforas espaciales | "landscape", "realm", "tapestry", "ecosystem", "journey", "roadmap" | Lenguaje directo sin metáfora |
| Transiciones formulaicas | "Furthermore", "Moreover", "Additionally", "It is important to note" | "También", "Además", o transición implícita |
| Falsedades dramáticas | "Here's the kicker", "The best part?", "Honestly?" | Dejar que el contenido hable |
| Validación sin sentido | "You're not alone", "It's worth noting", "It's important to remember" | Eliminar. Si no aporta, no va |
| Cierre genérico | "In conclusion", "In summary", "Ultimately" | Cierre orgánico: implicación, pregunta, statement |
| "Quietly" como cojín | "Quietly growing", "Quiet confidence", "The quiet truth" | Eliminar la palabra "quiet/quietly" en la mayoría de casos |

### Estructurales

- **Sentences that march in formation** (Forbes #8): oraciones idénticas en longitud → variar entre 1 y 6+ oraciones por párrafo
- **Rectangle paragraphs**: 3 oraciones de 15-20 palabras c/u → romper con fragmentos, oraciones cortas
- **Hedging automático**: "It could be argued that", "aims to explore" → claims directos cuando hay evidencia
- **Faux balance**: "both sides" sin costo real → tomar posición cuando el contexto lo permite
- **Logic teleportation** (Forbes #10): conclusiones sin puente lógico → mostrar el razonamiento intermedio
- **Over-tidy self-references**: "As mentioned above" excesivo, loops al inicio → estructura natural sin reciclar

### Rítmicos (aumentar burstiness)

Introducir variación deliberada:

- Oraciones de 3 a 35+ palabras en el mismo párrafo
- Fragmentos: "No siempre. Pero a veces sí."
- Inicios con conjunción: "Y", "Pero", "Porque"
- Puntuación variada: dos puntos, guiones, paréntesis
- Técnica high-low: oración larga → punch corta

### Emocionales

- **Neutral temperature** (Forbes #11): IA mantiene tono neutro siempre → agregar postura genuina
- **Missing emotional spikes**: sin reacciones → agregar frustración, entusiasmo, posición
- **Correct words, wrong context**: sinónimos técnicamente correctos pero socialmente extraños → usar vocabulario natural del contexto

## Modos de Registro

### Académico (papers, tesis, informes de investigación)

Mantener: terminología técnica, precisión referencial, densidad conceptual, voz pasiva donde convención lo exija
Romper: paralelismo excesivo, conectores formulaicos, hedging automático, oraciones uniformes
Permitir: primera persona plural ("observamos"), voz activa en metodología
NO: coloquialismos, simplificación excesiva, relajar rigor

**Precaución**: escritores académicos son grupo de alto riesgo para falsos positivos (Turnitin 4-8% falso positivo en docs completos). La reescritura debe INCREMENTAR burstiness y perplejidad sin perder rigor.

### Profesional (reportes, propuestas, whitepapers)

Mantener: formalidad, claridad, datos concretos
Romper: mismos patrones que académico, más libertad para voz activa
Permitir: bullets con variación, tono directo, opiniones respaldadas con datos

### General (blogs, posts, artículos)

Mantener: coherencia, claridad, esencia del mensaje
Romper: todo patrón IA sin restricción
Permitir: coloquialismos moderados, primera persona, humor si aplica, "Pub Test" (¿dirías esto a un colega?)

## Workflow

1. **Analizar** texto → listar patrones IA detectados (perplejidad, burstiness, léxicos, estructurales, emocionales)
2. **Identificar** registro y requisitos del contexto
3. **Reescribir** aplicando ruptura según registro
4. **Verificar fidelidad**: ideas, datos, cifras, nombres, citas → exactos. Cero tolerancia.
5. **Entregar** texto reescrito (+ variante si se pide)

## Formato de Salida

**Texto reescrito directamente** si el usuario ya conoce la skill.

**Si pide análisis o es primera vez**:
```
### Patrones detectados
- [lista con ubicación]

### Texto reescrito
[texto]

### Variante [registro alternativo] (si se pide)
[versión alternativa]
```

## Pitfalls

- **Sobre-humanizar**: introducir errores o informalidad excesiva. Un académico humano escribe con rigor. No necesitas hacerlo casual.
- **Perder datos**: cifras, nombres, citas, datos fácticos → exactos siempre.
- **Over-correction** (Olivia Cal #7): usar humanizers genera "syntax salad" — gramaticalmente correcto pero antinatural. Si una oración suena rara, revertir.
- **Falsos positivos**: escritura técnica/académica ya tiene baja burstiness naturalmente. No castigar a quien escribe claro y estructurado — solo romper monotonía donde existe.
- **Homogeneizar estilos**: si el autor tiene voz propia, preservarla. Humanizar no es estandarizar.
