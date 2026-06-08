# UI/UX Migration: Vanilla CSS → React+Tailwind

Migrar el LOOK AND FEEL de una app legacy a un stack moderno.

## Cuándo usar

- Usuario dice "quiero el diseño del proyecto viejo"
- "Hacer un mix de diseños"
- "Que se vea como el demo/anterior"
- Redesign from reference project

## Principio

El usuario tiene un diseño que LE GUSTA. NO lo "mejores". REPLICLA la esencia.

## Paso 1: Extraer Design System del CSS Legacy

Leer TODOS los CSS del proyecto fuente. Extraer valores exactos:

```
PALETA:       --color-primary: #1a9696; --color-secondary: #2d3748;
TIPOGRAFÍA:   font-family: 'Sora', sans-serif; weights: 300-700
BORDER RADIUS --r: 12px; modals: 24px; pills: 99px
SHADOWS:      --shadow: 0 4px 24px rgba(26,122,122,.12)
COMPONENTES:  .card, .avatar, .badge, .modal, .toast, .stat-card
PATRONES:     avatar circles, filter pills, search with icon, empty states
ANIMACIONES:  slide-up, spin, fade-in
RESPONSIVE:   breakpoints, mobile adjustments
```

## Paso 2: Tailwind v4 Configuration

**Tailwind v4 NO usa tailwind.config.js.** Configuración via CSS:

```css
@import "tailwindcss";

@theme {
  --color-teal-500: #1a9696;
  --font-sans: 'Sora', system-ui, sans-serif;
  --radius-md: 12px;
  --shadow-md: 0 4px 24px rgba(26, 122, 122, 0.12);
}
```

**Pitfall:** Buscar `tailwind.config.js` que no existe en v4.

## Paso 3: Componentes Base en CSS Global

Crear clases reutilizables en `src/index.css`:

| Clase | Uso |
|-------|-----|
| `.card` | Tarjeta con shadow + hover |
| `.avatar` | Círculo con gradiente + iniciales |
| `.badge-*` | Pills de estado (success/warning/error/info) |
| `.search-input` | Input con icono lupa |
| `.filter-pill` | Pills de filtro (active = teal bg) |
| `.form-input`, `.form-label` | Inputs de formulario |
| `.stat-card` | Card con borde superior de color |
| `.modal-overlay`, `.modal` | Modal con slide-up |
| `.btn-gradient` | Botón con gradiente |
| `.empty-state` | Estado vacío con icono |
| `.loading-spinner` | Spinner animado |

## Paso 4: Layout Migration

**Sidebar → Topbar + Nav Tabs:**
- `sticky top-0 z-50` para topbar
- Nav tabs debajo con `border-b-2` para active
- User avatar con iniciales
- Responsive: misma topbar, tabs scroll horizontal

## Paso 5: Component Patterns

**Tablas → Cards:**
```jsx
<div className="card flex items-center gap-4 p-4">
  <div className="avatar h-11 w-11 text-sm">{initials}</div>
  <div className="flex-1 min-w-0">
    <p className="font-semibold">{name}</p>
    <p className="text-xs text-navy-400">{meta}</p>
  </div>
</div>
```

**Inputs con labels:**
```jsx
<div>
  <label className="form-label">Campo *</label>
  <input className="form-input" />
</div>
```

## Pitfalls

- **No copiar CSS literal** → Selectores legacy no aplican a React/Tailwind
- **No olvidar Google Fonts** → `<link>` en index.html
- **Bundle size** → Fonts + CSS custom suben bundle. Verificar < 500KB gzip
- **No romper funcionalidad** → Solo cambiar UI, no lógica
- **SVG logos** → Extraer del HTML viejo como JSX inline
- **getInitials helper** → Crear función para avatares con iniciales
