---
name: competitive-intelligence
description: "Investigador 'topo' universal. Teardown sistematico de cualquier producto (games, apps, SaaS, servicios). 8 dimensiones, 4 capas de profundidad, OSINT toolkit. Use when: analizando un competidor, deconstruyendo un producto exitoso, preparando battlecard, buscando gaps de mercado, o antes de lanzar un producto nuevo."
---

# Competitive Intelligence — Investigador Topo

Deconstruccion sistematica de cualquier producto. No opinar, extraer principios.

Filosofia: El marketing te dice lo que quieren que creas. El producto te dice lo que realmente priorizan.

## Cuando usar

- Antes de lanzar un producto → deconstruir 3-5 competidores
- Producto existente estancado → buscar que hacen los lideres
- Sales pierde deals contra un competidor especifico → teardown enfocado
- Buscando gaps de mercado → analizar lo que NADIE hace bien
- Inspiracion cross-industry → deconstruir un producto de otro sector y extraer patrones transferibles

**No usar si**: solo necesitas una feature checklist. Esto es para entender EL POR QUE detras de las decisiones.

## FASE 1: Preparacion (15 min)

### 1.1 Definir la persona de analisis

NO analizar como "analista". analizar como usuario target:

```
PRODUCTO: [nombre]
PERSONA: [rol/tipo de usuario]
CASO DE USO: [que intenta resolver]
NIVEL TECNICO: [basico/intermedio/avanzado]
CONTEXTO: [equipo de 1? enterprise? mobile? desktop?]
```

Esto cambia TODO. Un CRM deconstruido como startup de 5 personas vs enterprise de 500 da insights totalmente distintos.

### 1.2 Configurar captura

- Screen recording completo (OBS, Loom, browser built-in)
- Timestamped notes
- Screenshots clave: signup, primer pantalla, dashboard principal, pricing, settings

### 1.3 Acceso autentico

Registrarse con datos reales. Productos customizan la experiencia segun signup. Datos fake = experiencia fake.

Si requiere demo call, la experiencia sales-led ES parte del analisis.

## FASE 2: Las 8 Dimensiones (15 min cada una = 2h total)

Time-box estricto. 15 minutos por dimension, no mas. Si necesitas profundizar, segunda pasada.

### D1: Onboarding

**Pregunta clave:** Cuanto tarda el usuario en ver valor real?

- Pasos desde signup hasta primer "aha moment"
- Datos que piden upfront vs despues
- Guias, tooltips, empty states, videos
- Friction intencional vs accidental
- Tiempo hasta primera accion significativa

**Escorar por:** Time-to-value y reduccion de friction.

**Red flags:** Mas de 5 pasos antes de valor. Pedir payment antes de demostrar valor. Tutorial obligatorio de >2 min.

### D2: Core Workflow

**Pregunta clave:** Cuantos clicks/decisions para completar la tarea principal?

Completar el use case principal end-to-end como la persona definida:

- Analytics tool → crear reporte
- CRM → agregar contacto + avanzar deal
- Game → completar primera mision
- E-commerce → encontrar + comprar producto

Anotar CADA paso, click y decision. El workflow ES la estrategia revelada.

**Escorar por:** Eficiencia y claridad del flujo.

### D3: Feature Depth

**Pregunta clave:** Que tan profundo llega en los features que importan?

Seleccionar 3 features relevantes a la persona. Para cada uno:

- Opciones de configuracion
- Manejo de edge cases
- Escalado con volumen
- Automatizacion vs manual
- Limites ocultos (rate limits, caps, etc.)

**No escanear todo.** Profundizar en lo que importa al usuario.

**Escorar por:** Profundidad, no amplitud.

### D4: UX Quality

**Pregunta clave:** Se siente profesional o prototipo?

- Velocidad de carga (percepcion subjetiva)
- Consistencia de navegacion
- Feedback de interacciones (loading states, confirmaciones, errores)
- Diseno: moderno o datado
- Adaptacion mobile/desktop
- Accesibilidad basica (contraste, tamano fuente, navegacion keyboard)

**Escorar por:** Polish, velocidad y consistencia.

### D5: Integrations / Ecosystem

**Pregunta clave:** Esta aislado o conectado al ecosistema del usuario?

- Integraciones nativas (cuantas? que categorias?)
- API publica? Documentacion?
- Webhooks para data flow en tiempo real?
- Marketplace de third-party?
- Import/export de datos?

**Escorar por:** Amplitud del ecosistema + profundidad de integracion.

### D6: Pricing / Business Model

**Pregunta clave:** Como capturan valor y donde esta el gate?

- Tiers, precios, que esta gated en cada nivel
- Modelo: per-seat / usage / flat / freemium / ads / IAP / subscription
- Limite del free tier (es funcional o demo?)
- Descuentos enterprise (inferir)
- Patron de monetizacion: que venden vs que dan gratis y POR QUE

**El pricing ES la estrategia.** Lo que dan gratis = acquisition. Lo que cobran = donde esta el valor real.

### D7: Support / Documentation

**Pregunta clave:** Puedo resolver un problema sin hablar con un humano?

Buscar 3 preguntas comunes en el knowledge base. Evaluar:

- Profundidad de docs para features complejos
- Comunidad activa (forum, Discord, Reddit)
- Tiempo/respuesta de soporte (testear si es posible)
- Video tutorials, in-app help
- Calidad de API docs (si aplica)

**Escorar por:** Resolucion self-serve.

### D8: Unique Capabilities / Moat

**Pregunta clave:** Que tienen que yo no puedo copiar facilmente?

- Propiedad intelectual / patents
- Network effects
- Data advantages (datos propietarios, ML models entrenados)
- Switching costs (vendor lock-in)
- Exclusivas / partnerships
- Brand / comunidad

**Esto define si es un competidor real o un feature.**

## FASE 3: 4 Capas de Profundidad

Cada dimension se analiza en 4 capas, de superficie a fondo:

```
CAPA 1 - FUNCIONALIDAD: Que hace? (features, capacidades)
CAPA 2 - USABILIDAD: Que tan facil es? (friction, workflow, errores)
CAPA 3 - TECNICO: Como esta construido? (stack inferido, arquitectura, limites)
CAPA 4 - BUSINESS: Por que estas decisiones? (modelo, estrategia, target, positioning)
```

Ejemplo aplicado:

| Capa | Pregunta | Insight tipo |
|------|----------|-------------|
| 1 | Tienen dark mode? | Si, toggle en settings |
| 2 | Es facil de encontrar? | 3 clicks, solo en desktop |
| 3 | Como lo implementan? | CSS variables, no theme switch |
| 4 | Por que ahi? | Low priority, no es core para su target (enterprise) |

**La capa 4 es la que vale.** Las otras 3 son datos; la 4 es inteligencia.

## FASE 4: OSINT Toolkit

Herramientas y tecnicas para investigar sin acceso directo al producto:

### Herramientas por tipo

| Tipo | Herramientas | Que encontrar |
|------|-------------|---------------|
| **Web/SEO** | SimilarWeb, Ahrefs, SEMrush | Trafico estimado, keywords, growth trends |
| **Tech Stack** | BuiltWith, Wappalyzer, StackShare | Frameworks, hosting, APIs, CDN |
| **Social/Community** | Reddit, Discord, Twitter/X, LinkedIn | Sentimiento, quejas, feature requests |
| **Reviews** | G2, Capterra, ProductHunt, App Store | Fortalezas/debilidades percibidas |
| **Jobs/Career** | LinkedIn Jobs, Greenhouse, Lever | Que estan construyendo (roles que contratan) |
| **Financials** | Crunchbase, PitchBook, SEC filings | Funding, revenue estimado, growth |
| **Code** | GitHub, GitLab, npm stats | Librerias publicas, contribuidores |
| **Mobile** | Sensor Tower, App Annie | Downloads, revenue, ratings por pais |
| **Games** | SteamDB, Roblox stats, Sensor Tower | CCU, retention, monetizacion |

### Signals de inteligencia

**Contrataciones revelan estrategia:**
- Contratan ML engineers → van hacia AI features
- Contratan mobile devs → expansion mobile
- Contratan compliance/legal → targeting enterprise/regulacion

**Changelog revela prioridades:**
- Frecuencia de updates → ritmo de desarrollo
- Que fixean vs que agregan → donde estan los users
- Breaking changes → refactoring grande en camino

**Reviews revelan la verdad:**
- Reviews 1-2 estrellas: quejas reales (ignorar trolls)
- Reviews 5 estrellas: frecuentemente paid o power users
- Reviews 3-4 estrellas: los mas honestos
- Buscar patrones: si 30% menciona "slow support", es real

**Pricing changes revelan estrategia:**
- Suben precios → confidentes en posicionamiento
- Bajan precios → perdiendo market share o cambiando modelo
- Nuevo tier → capturando segmento diferente

## FASE 5: Sintesis

### 5.1 One-Pager de salida

Despues de la investigacion, producir un documento con esta estructura:

```
## [PRODUCTO] — Teardown Summary

### Veredicto en una linea
[Ej: "CRM para SMBs que gana por simplicidad, pierde por depth en enterprise"]

### Los 3 principios detras de sus decisiones
1. [Principio inferido de capa 4]
2. ...
3. ...

### Fortalezas reales (no marketing)
- [Con evidencia]

### Debilidades explotables
- [Con evidencia]

### Que copiar (principio, no feature)
- [Ej: "Onboarding con valor en <60s" → no "copiar su wizard"]

### Que NO copiar
- [Con razon]

### Gaps identificados
- [Que no cubren que si cubre otro producto o ninguno]
```

### 5.2 Matriz comparativa (si hay multiples teardowns)

| Dimension | Producto A | Producto B | Producto C | Tu Producto |
|-----------|-----------|-----------|-----------|-------------|
| Onboarding | 9/10 | 6/10 | 7/10 | ?/10 |
| Core Flow | 8/10 | 9/10 | 5/10 | ?/10 |
| ... | ... | ... | ... | ... |

**Regla:** Nunca poner tu producto por encima sin evidencia. El sesgo de confirmacion es el enemigo.

## Anti-Patterns

1. **Feature checklist** — "Tienen X? Si/No" no es teardown. Es una tabla inutil siempre sesgada a favor de quien la hace.
2. **Copiar features sin entender el principio** — Slack tiene canales, no por que canales son magicos, sino porque resuelven ruido de email.
3. **Analizar como experto, no como usuario** — Tu usuario no va a leer la API docs. No juzgues por eso.
4. **Ignorar el modelo de negocio** — Un producto free con ads toma decisiones distintas a uno enterprise $500/mes. Contexto importa.
5. **Sesgo de confirmacion** — Si llegas buscando "son mejores", vas a encontrar "son mejores". Llegar con preguntas, no conclusiones.
6. **Solo analizar directos** — Los mejores insights vienen de productos de OTRO sector. Duolingo gamifica education; aplica a tu app de fitness.
7. **Teardown unico** — Productos cambian. Repetir cada 6 meses. Lo que era debilidad puede ser fortaleza ahora.

## Checklist rapido (10 min)

Cuando no hay tiempo para teardown completo:

```
[ ] Que resuelve en una frase?
[ ] Cuanto tarda el onboarding hasta primer valor?
[ ] Cuantos clicks para la accion principal?
[ ] Como monetiza? (modelo + que esta gated)
[ ] Cual es su moat? (por que no los copian facil)
[ ] Que 1 cosa haria diferente y por que?
```

6 preguntas, 10 minutos, 80% del valor.

## Adaptacion por tipo de producto

| Tipo | Dimensiones a priorizar | Senal clave |
|------|------------------------|-------------|
| **SaaS/B2B** | D5 Integrations, D6 Pricing, D7 Support | Integration depth = stickiness |
| **Mobile App** | D1 Onboarding, D4 UX, D6 Pricing | Time-to-value < 30s o churn |
| **Game** | D2 Core Loop, D4 UX, D6 Monetization | Retention dia 1 + dia 7 |
| **E-commerce** | D2 Checkout flow, D4 UX, D8 Moat | Conversion rate + repeat purchase |
| **Marketplace** | D5 Ecosystem, D8 Moat, D6 Pricing | Liquidez (supply vs demand balance) |
| **Dev Tool** | D3 Feature Depth, D5 Integrations, D7 Docs | Developer experience = todo |

## Fuentes

- oscom.ai 8-dimension teardown framework (2025)
- AriseGTM CI Automation 2026 Playbook — reactive vs proactive CI, 5-phase maturity model
- LogRocket product teardown guide (2025) — 4 analysis layers, tools by category
- Department of Play — game deconstruction methodology, Pareto 20/80 applied to teardowns
