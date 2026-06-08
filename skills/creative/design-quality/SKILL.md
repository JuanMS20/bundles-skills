---
name: design-quality
description: "Anti-generic design skill. Avoids AI slop (blue-purple gradients, Inter font, 3-box hero layouts). Produces professional UI with real color theory, distinctive typography, and intentional spacing. Use when building any visual frontend, UI, landing page, or when user mentions design, UI/UX, styling, themes, or 'make it look good'. Triggers: frontend UI, landing page, dark theme, light theme, responsive layout, CSS, Tailwind, Roblox UI, any visual output."
---

# Design Quality

Evitar el look AI generico. Producir diseno que parece hecho por humanos profesionales.

## El Problema: AI Slop

Los LLMs generan el "median" de su training data. En diseno, eso produce:

**Marcas del look AI:**
- Degradados blue-purple / indigo (origen: Tailwind `bg-indigo-500` default — Adam Wathan pidio perdon publicamente)
- Inter, Roboto, Arial como unica opcion tipografica
- Hero centrado → CTA → 3 boxes con iconos (layout cliché)
- border-radius: 8px en todo
- Sombras sutiles a exactamente 0.1 opacity
- Sin jerarquia visual real (solo "texto grande = titulo")
- Sin estados de error, validacion, ni accesibilidad

**Fuente:** prg.sh/ramblings/Why-Your-AI-Keeps-Building-the-Same-Purple-Gradient-Website

## Regla 1: Paleta con Intencion

### NUNCA usar defaults AI
```
PROHIBIDO por defecto:
- Indigo/purple como color primario
- Blue (#3B82F6) como acento
- Blancos puros (#FFFFFF) sin textura
- Grises planos sin calidez
```

### Usar paletas con personalidad
Elejir UNA de estas estrategias antes de empezar:

**A) Monocromo + 1 acento (Stripe/Linear/Vercel)**
- Base: negro, blanco, grises
- UN color que hace todo el trabajo: terracotta, emerald, coral, amber
- El acento se usa con moderacion — como el naranja Hermes

**B) Warm earth tones (tendencia 2026)**
- Neutrales calidos: #F5F0EB (cream), #2C2825 (warm black)
- Verdes suavizados: #7C9A82 (sage), #4A6741 (forest)
- Marrones: #8B7355, #A68B6B
- Sin azules ni purples

**C) Cultural/theme-based**
- "Paleta de lodge de ski de los 70s": burnt orange, avocado green, warm browns
- "Art deco": high contrast, geometric, gold + black
- "Japanese print": asymmetric, negative space, indigo + cream natural
- Desert: terracotta, sand, sage, warm stone

**D) Extraida de referencias reales**
- Pedir al usuario una marca, foto, o mood
- Extraer colores de esa referencia, no inventar

### Color con teoria real
- Complementary: colores opuestos en la rueda (alto contraste)
- Analogous: colores vecinos (armonia suave)
- Triadic: 3 colores equidistantes (vibrante pero balanceado)
- Aplicar 60-30-10: 60% dominante, 30% secundario, 10% acento

### Implementacion
Siempre usar CSS variables o design tokens:
```css
:root {
  --bg-primary: #FAFAF8;
  --bg-surface: #F0EDE8;
  --text-primary: #1A1A1A;
  --text-secondary: #6B6560;
  --accent: #C85A3A;
  --accent-hover: #B04E30;
  --border: #E0DCD5;
  --success: #5B8A5E;
  --error: #C44D3F;
}
```

Fuente: Pixeldarts — "Four Design Principles Behind Stripe, Linear, and Vercel" (Mayo 2026)

## Regla 2: Tipografia con Personalidad

### NUNCA defaults
```
PROHIBIDO sin justificacion:
- Inter (el default de AI)
- Roboto
- Arial / system-ui como unica opcion
- Cualquier fuente que el LLM sugiera "porque es legible"
```

### Estrategia de seleccion
1. **Display/Headings**: fuente con caracter (serif, geometric, condensed)
2. **Body**: fuente legible pero no aburrida
3. **Mono**: para codigo y datos tecnicos

**Combinaciones que funcionan:**
| Vibe | Heading | Body | Ejemplo real |
|------|---------|------|-------------|
| Tech sharp | Geist | Geist Sans | Vercel |
| Editorial | Playfair Display | Source Sans 3 | Notion-style |
| Engineer | IBM Plex Mono | IBM Plex Sans | Sanity |
| Warm craft | DM Serif Display | DM Sans | Cal.com-style |
| Minimal luxe | Sora | Inter (unico caso permitido) | Linear |
| Terminal | JetBrains Mono | Lexend | Warp-style |

**Regla**: maximo 2 familias tipograficas. 3 si una es mono.

### Jerarquia tipografica
Definir escala ANTES de escribir CSS:
```
display: 48-72px / 700 weight / tight letter-spacing (-0.02em)
h1: 36-48px / 600-700
h2: 28-36px / 600
h3: 22-28px / 600
body: 16-18px / 400 / 1.5-1.7 line-height
caption: 13-14px / 500 / wide letter-spacing (0.04em)
mono: 14px / monospace
```

Fuente: awesome-design-md (VoltAgent, 83k stars) — formato DESIGN.md de Google Stitch

## Regla 3: Espaciado Intencional

### El doble-truco de Stripe/Linear/Vercel
> "Toma el espaciado que sientes que es suficiente, y duplicalo"

- Whitespace no es vacio — es aire
- Layouts densos hacen trabajar los ojos, layouts abiertos dejan que el contenido trabaje
- Los 3 usan significativamente mas espacio del que "parece necesario" — y eso es lo que los hace sentir premium

### Escala de espaciado consistente
Usar escala de 4px:
```
4px - micro (inline gaps)
8px - small (icon-text)
12px - medium (input padding)
16px - standard (card padding)
24px - large (section gaps)
32px - xl (component spacing)
48px - 2xl (section separator)
64px - 3xl (page sections)
```

### Padding en componentes
- Botones: 12px vertical, 24px horizontal (minimo)
- Cards: 24px padding interno
- Inputs: 12px vertical, 16px horizontal
- Sections: 64-96px entre secciones

Fuente: Pixeldarts — principio de whitespace generoso

## Regla 4: Layout No Generico

### NUNCA el cliché AI
```
PROHIBIDO como layout default:
[        HERO CENTRADO         ]
[      CTA button purple       ]
[  box1  ] [  box2  ] [  box3  ]  ← 3 feature boxes
[  icon  ] [  icon  ] [  icon  ]
[     testimonial carousel     ]
[         footer links         ]
```

### Layouts que si funcionan
- **Asimetrico**: contenido desplazado, no centrado
- **Editorial**: columnas de texto con jerarquia tipo revista
- **Dashboard-dense**: grids de datos con informacion densa
- **Split-screen**: imagen izq / contenido der (o viceversa)
- **Bento grid**: cards de diferentes tamanos organizadas como grid japones

### Grid system
- 12 columnas con gutters de 24-32px
- Max-width: 1200px para contenido, full-bleed para backgrounds
- Sidebar: 240-280px fijo

## Regla 5: Motion Explicativo, No Decorativo

> "Over-animated interfaces feel oddly aggressive, like someone is gesturing over-the-top when trying to explain a point." — Envato, 2026

**Motion que funciona:**
- Indica QUE paso, QUE esta pasando, QUE va a pasar
- Progress indicators claros (no spiners genericos)
- Transiciones entre estados (0.2-0.3s ease)
- Stagger en grupos (animation-delay escalonado)

**Motion que NO funciona:**
- Particulas flotantes de fondo
- Hover effects excesivos en todo
- Animaciones de entrada en cada elemento
- Bounce en cosas que no deberian rebotar

Fuente: Envato "UX/UI Design Trends 2026" (Marzo 2026)

## Regla 6: Accesibilidad No Negociable

No es feature, es infraestructura:
- Contraste minimo 4.5:1 (WCAG AA) para texto normal
- Contraste minimo 3:1 para texto grande
- Touch targets de minimo 44px
- Estados de focus visibles (no outline:none sin reemplazo)
- No depender solo de color para convey informacion
- Labels en inputs, no solo placeholders
- Estados de error, loading, empty y success en todo componente interactivo

## Regla 7: Antes de Disenar, Preguntar

Si el usuario no da direccion de diseno, preguntar:
1. **Vibe**: Profesional/tech? Calido/amigable? Premium/luxe? Oscuro/claro?
2. **Referencia**: Hay alguna marca, web, o imagen que le guste?
3. **Publico**: Developers? Consumidores? Enterprise? Ninos?
4. **Plataforma**: Web? Mobile? Roblox? Desktop app?

Si el usuario da respuestas cortas ("lo que sea mejor"), usar defaults segun contexto:
- SaaS tech → estilo Linear (dark, monocromo, sharp)
- Consumidor → estilo Notion (warm, serif headings, soft surfaces)
- Juego → segun el tema del juego

## DESIGN.md Template

Cuando se arranca un proyecto nuevo, crear un `DESIGN.md` en la raiz:

```markdown
# [Project] Design System

## Visual Theme
[Vibe en 1-2 oraciones]

## Color Palette
| Token | Hex | Role |
|-------|-----|------|
| bg-primary | #... | Fondo principal |
| bg-surface | #... | Cards, modals |
| text-primary | #... | Titulos |
| text-secondary | #... | Body text |
| accent | #... | CTAs, links, highlights |
| border | #... | Bordes, separadores |

## Typography
| Element | Font | Size | Weight | Spacing |
|---------|------|------|--------|---------|
| display | ... | 56px | 700 | -0.02em |
| h1 | ... | 36px | 600 | -0.01em |
| body | ... | 16px | 400 | normal |

## Spacing Scale
[4, 8, 12, 16, 24, 32, 48, 64]px

## Components
### Buttons
[primary, secondary, ghost — estilos con estados]

### Cards
[padding, border, shadow, border-radius]

### Inputs
[padding, border, focus state, error state]

## Anti-Patterns
- [3-5 cosas especificas a evitar en ESTE proyecto]
```

Fuente: formato Google Stitch / awesome-design-md

## Brand-Aligned Landing Pages

Cuando el usuario pide una landing page para un negocio existente con marca definida:

### Flujo de extracción de marca
1. **Instagram/social**: Analizar la imagen con vision_AI para extraer paleta, tipografía, motifs decorativos, tono visual
2. **PDF/documentos del negocio**: Extraer con pymupdf (web_extract no funciona con archivos locales). Obtener: nombre, servicios, target, propuesta de valor, equipo
3. **Logo**: Pedir ruta del archivo. Si el usuario comparte un screenshot del nombre de archivo (no la imagen), buscar el archivo real con `find`/`ls`
4. **Redes sociales**: Pedir URLs reales. No inventar handles. Verificar que existen antes de enlazar

### Patrón de landing page de un solo archivo
- HTML + CSS + JS inline en un solo `index.html`
- Google Fonts via CDN (no local)
- CSS variables para tokens de marca
- Scroll animations con IntersectionObserver (fade-in, no bounce)
- Nav sticky con efecto glass al scroll
- WhatsApp floating button (SVG icon, wa.me link con mensaje pre-cargado)
- Responsive: mobile-first, sin overflow horizontal

### Decisiones de diseño que el usuario corrige
- **Sin contenido falso**: No inventar testimonios, reviews, ni datos de clientes. El usuario prefiere secciones vacías o "próximamente" sobre contenido fabricado.
- **Sin precios si la marca no los publica**: En vez de inventar precios, "para más info visita nuestras redes" o "escríbenos por WhatsApp"
- **Contacto = links directos, no formularios**: Tarjetas clickeables con iconos de redes sociales que abren la app/link real. Formularios generan fricción innecesaria para negocios pequeños que ya tienen WhatsApp/IG activo.
- **WhatsApp float es obligatorio** para negocios LATAM: botón verde fijo, esquina inferior, SVG del logo WA, tooltip al hover

### Pitfalls
- **No inventar redes sociales**: Si el usuario no da handles, pedirlos. `@chicadiez` no es lo mismo que `@diezbeautystudio` — verificar.
- **Pymupdf para PDFs locales**: `web_extract` bloquea URLs `file://`. Usar `uv pip install pymupdf` + extracción directa en Python.
- **Screenshots como logos**: Cuando el usuario dice "el logo está en esta ruta" y comparte un screenshot, el screenshot es el NOMBRE del archivo, no el logo. Buscar el archivo real en el sistema.
- **Logo real > tipografía decorativa**: Si el usuario tiene logo digital, usarlo. Si no, recrear con tipografía cursive (Dancing Script, Great Vibes) + elementos decorativos (corona, destellos).

## Verification Checklist

```
[ ] No hay indigo/purple como color primario sin justificacion
[ ] Tipografia NO es Inter/Roboto/Arial sin justificacion
[ ] Layout NO es el cliché hero+CTA+3boxes
[ ] Paleta tiene teoria de color detras (complementary, analogous, etc.)
[ ] Espaciado sigue escala consistente (4px base)
[ ] CSS variables o tokens definidos
[ ] Estados de error/loading/empty existen en componentes interactivos
[ ] Motion es funcional, no decorativo
[ ] Accesibilidad basica cubierta (contraste, touch targets, focus)
[ ] No parece "AI generated" a primera vista
```

## Fuentes

- Envato "UX/UI Design Trends 2026" (Marzo 2026) — calm interfaces, cognitive clarity
- prg.sh "Why Your AI Keeps Building the Same Purple Gradient Website" — AI slop analysis + system prompt
- Medium/Kai Ni "Design Observation: Why AI Favors Blue-Purple Gradients" — Tailwind indigo bias
- Pixeldarts "Four Design Principles Behind Stripe, Linear, Vercel" (Mayo 2026) — high contrast, whitespace, monocromo+accent, sharp type
- awesome-design-md (VoltAgent, 83k GitHub stars) — 73 DESIGN.md format reference
- UX Design Institute "7 Fundamental UX Design Principles 2026" — accessibility as infrastructure

## Referencias Adicionales

- **Migración UI/UX** → [references/ui-ux-migration-pattern.md](references/ui-ux-migration-pattern.md) — Patrón para migrar diseño de app de referencia a app existente (demo HTML → React)
