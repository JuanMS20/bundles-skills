---
name: judge-ux-vibe-check
description: "Detecta 'AI slop' y valida UX real — multi-plataforma. Web: responsive, WCAG, focus. Móvil: thumb zones, gestures, offline. Juegos: tutorial, difficulty curve, HUD. CLI: help text, error formatting. Use when: 'se ve bien?', UX check, 'es usable?', juzgar UX/UI."
---

# JUDGE UX VIBE CHECK — Es usable o es "AI slop"?

## Principio: Funcionar ≠ Ser usable.

La IA genera UIs que "se ven bien en screenshot" pero son un desastre
al usarlas. Botones sin feedback, formularios sin validación visual,
colores que no contrastan, y flujos que confunden al usuario.
Tu trabajo es usar la app como usuario real y encontrar los problemas.

## FASE 0 — Detectar plataforma

- **Web**: HTML/JS frontend accesible via browser
- **Móvil**: app nativa o híbrida, touch interface
- **Juego**: Canvas/WebGL/engine, game loop, interacción en tiempo real
- **CLI**: entrada por terminal, args/stdin, output de texto
- **Desktop**: windowed app con elementos nativos o framework UI

---

## Checklist Universal (TODAS las plataformas)

### 1. Primera Impresión (5 segundos)
- [ ] El propósito de la app es obvio en 5 segundos?
- [ ] La acción principal es visible y clara?
- [ ] No hay clutter visual innecesario?
- [ ] Los colores tienen contraste suficiente?
- [ ] La tipografía es legible?

### 2. Flujo y Navegación
- [ ] El usuario sabe dónde está en todo momento?
- [ ] Puede volver/deshacer fácilmente?
- [ ] Los elementos interactivos son obvios? (no hay que adivinar)
- [ ] Hay loading states entre operaciones?
- [ ] Hay empty states cuando no hay datos?

### 3. Feedback y Estados
- [ ] Las acciones tienen respuesta visual inmediata?
- [ ] Hay confirmación de acciones destructivas?
- [ ] Hay notificación de éxito (toast/snackbar/etc)?
- [ ] Los errores tienen mensajes específicos y accionables?
- [ ] Hay estados de error que no sean genéricos?

### 4. Consistencia Visual
- [ ] Hay un sistema de diseño coherente? (colores, espaciado, tipografía)
- [ ] Los componentes similares se ven iguales en toda la app?
- [ ] No hay mezcla de estilos visuales inconsistentes?
- [ ] El espaciado es consistente?

## Checklist Web

- [ ] Funciona en 320px (iPhone SE) sin scroll horizontal?
- [ ] Funciona en 768px (tablet) sin elementos rotos?
- [ ] Funciona en 1920px (desktop) sin elementos estirados?
- [ ] Los botones son táctiles? (mínimo 44x44px)
- [ ] Hay alt text en imágenes?
- [ ] El focus indicator es visible?
- [ ] Se puede navegar con teclado? (Tab, Enter, Escape)
- [ ] Contraste pasa WCAG AA?
- [ ] Los labels están asociados a los inputs?

## Checklist Móvil

- [ ] Los controles están en zonas alcanzables por el pulgar? (thumb zones)
- [ ] No hay gesture conflicts? (swipe vs scroll vs drag)
- [ ] Hay feedback de offline / sin conexión?
- [ ] La app restaura estado al reabrir? (no pierde datos del form)
- [ ] Las transiciones son fluidas (no janky)?
- [ ] El teclado no tapa el campo activo?
- [ ] Pull-to-refresh funciona donde se espera?

## Checklist Juegos

- [ ] Hay tutorial o onboarding para mecánicas básicas?
- [ ] La dificultad escala de forma justa? (no spikes abruptos)
- [ ] El HUD muestra info crítica sin obstruir la acción?
- [ ] Los controles son responsivos y consistentes?
- [ ] Hay feedback claro de acciones del jugador? (visual + audio)
- [ ] Se puede pausar y el estado se preserva?
- [ ] Los game over / errores son informativos, no frustrantes?
- [ ] El menu principal es claro y navegable?

## Checklist CLI

- [ ] `--help` existe, es claro y tiene ejemplos?
- [ ] Los mensajes de error son accionables? (no stack traces crudos)
- [ ] El exit code es correcto? (0 éxito, !=0 error)
- [ ] El output funciona con pipes? (`miapp | grep`, `miapp > file.txt`)
- [ ] Las operaciones largas muestran progress? (barra, spinner, %)
- [ ] Los subcomandos siguen convención? (`git add`, no `git --add`)
- [ ] Color output se desactiva con `--no-color` o cuando no es TTY?

## Checklist Desktop

- [ ] Los atajos de teclado son intuitivos? (Ctrl+S, Ctrl+Z, etc)
- [ ] La ventana es redimensionable sin romper layout?
- [ ] Hay menús contextuales (right-click) donde se esperan?
- [ ] Drag & drop funciona donde debería?
- [ ] System tray / notifications nativas funcionan?
- [ ] Multi-ventana: ventanas hijas no se pierden detrás de la principal?

---

## AI Slop Detection (TODAS las plataformas)

### Señales de ALERTA:
- [ ] Gradients genéricos de azul a morado (web)
- [ ] Copy vacío tipo "Welcome to our platform"
- [ ] Features listadas sin contexto de por qué importan
- [ ] "Revolutionary" / "Cutting-edge" sin sustancia
- [ ] Acciones que dicen "Get Started" sin decir qué empiezas
- [ ] Formularios con 10 campos cuando necesitan 3
- [ ] Defaults genéricos sin pensar en el usuario real
- [ ] Mensajes de error tipo "Something went wrong" sin detalle
- [ ] En CLI: help text que no explica qué hace cada flag
- [ ] En juegos: tutorial que no enseña las mecánicas clave

### Señales de CALIDAD:
- [ ] Copy específico y orientado a acción
- [ ] CTAs que dicen exactamente qué pasa al interactuar
- [ ] Micro-interacciones que dan feedback
- [ ] Espacio usado estratégicamente (no relleno)
- [ ] Jerarquía visual clara (qué es importante primero)

---

## Formato de Veredicto

```
## VEREDICTO JUDGE UX VIBE CHECK

### Plataforma: [Web / Móvil / Juego / CLI / Desktop]

### Estado: [EXCELENTE / USABLE / NECESITA TRABAJO / AI SLOP]

### Puntuación por Categoría (0-100):
| Categoría | Score | Notas |
|-----------|-------|-------|
| Primera Impresión | X/100 | |
| Flujo/Navegación | X/100 | |
| Feedback/Estados | X/100 | |
| Consistencia | X/100 | |
| [Específico de plataforma] | X/100 | |

### Hallazgos Críticos (bloquean usabilidad):
1. [desc] — [problema] — [impacto]

### Señales de AI Slop: [lista o "ninguna"]

### Score General UX: [0-100]/100
### Es AI Slop: [SÍ / NO / PARCIALMENTE]
```

## Reglas de Oro
- **NUNCA** apruebes si no hay feedback visual para acciones del usuario
- **NUNCA** apruebes si hay errores genéricos sin información accionable
- **NUNCA** apruebes si la navegación confunde al usuario (web: scroll horizontal en móvil)
- **NUNCA** apruebes un CLI sin `--help` util o sin exit codes correctos
- **NUNCA** apruebes un juego sin tutorial o con controles no responsivos
- Si el score general < 50 -> AI SLOP. Rediseñar.
