# Migrar UI/UX de App de Referencia a App Existente

## Contexto

Cuando el usuario tiene una app vieja/demo con un diseño que le gusta y quiere aplicarlo a una app nueva con funcionalidad diferente. Ejemplo: demo en vanilla HTML/JS → app en React + Tailwind.

## Workflow

### FASE 1: Análisis del Diseño de Referencia

1. **Leer CSS files** del demo — extraer:
   - Paleta de colores (CSS variables, hex values)
   - Tipografía (font families, weights)
   - Border radius, shadows
   - Espaciado (padding, margins, gaps)
   
2. **Leer HTML** del demo — extraer:
   - Estructura de layout (topbar, sidebar, nav)
   - Componentes UI (cards, modals, badges, avatars)
   - Iconos y emojis usados
   - Animaciones y transiciones

3. **Crear inventario** de componentes UI:
   ```
   | Componente | Demo viejo | App nueva | Acción |
   |------------|-----------|-----------|--------|
   | Topbar     | SVG + nav | Sidebar   | Reemplazar |
   | Cards      | avatar+badge | tabla | Reemplazar |
   ```

### FASE 2: Configurar Design System

1. **Tailwind v4**: Configurar en `src/index.css` con `@theme` block:
   ```css
   @theme {
     --color-teal-500: #1a9696;
     --font-sans: 'Sora', system-ui, sans-serif;
     --radius-md: 12px;
     --shadow-md: 0 4px 24px rgba(26,122,122,0.12);
   }
   ```

2. **Google Fonts**: Agregar en `index.html`:
   ```html
   <link rel="preconnect" href="https://fonts.googleapis.com" />
   <link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
   ```

3. **Utility classes**: Definir en CSS para patrones reusables:
   - `.card`, `.avatar`, `.badge`, `.btn-gradient`
   - `.search-input`, `.filter-pill`, `.form-input`
   - `.modal-overlay`, `.modal`, `.stat-card`
   - `.empty-state`, `.loading-spinner`

### FASE 3: Migrar Componentes (orden importa)

1. **Layout** primero (topbar/sidebar/nav) — todos lo usan
2. **Login** — es la primera impresión
3. **Dashboard** — muestra el nuevo look
4. **CRUD pages** (Lideres, Staff, etc.) — cards en vez de tablas
5. **Modales** — slide-up animation, form sections
6. **Empty states** — iconos grandes + mensajes

### FASE 4: Patrones de Migración

#### Tabla → Cards
```tsx
// ANTES: tabla HTML
<table><tr><td>{name}</td></tr></table>

// DESPUÉS: card con avatar
<div className="card flex items-center gap-4 p-4">
  <div className="avatar h-11 w-11 text-sm">{initials}</div>
  <div className="flex-1">
    <p className="font-semibold">{name}</p>
    <span className="badge badge-info">Role</span>
  </div>
</div>
```

#### setError → showToast
```tsx
// ANTES
const [error, setError] = useState(null)
setError(err.message)
{error && <div className="error">{error}</div>}

// DESPUÉS
const { showToast } = useToast()
showToast(err.message, 'error')
// No error display needed — toast handles it
```

#### Sidebar → Topbar + Nav Tabs
```tsx
// ANTES: sidebar fijo
<aside className="fixed inset-y-0 left-0 w-64">

// DESPUÉS: topbar sticky + nav tabs
<header className="sticky top-0 z-50">
  <div className="flex h-14 items-center">...</div>
  <nav className="flex gap-1 bg-teal-600">
    {items.map(item => <Link className="nav-tab">{item.icon} {item.label}</Link>)}
  </nav>
</header>
```

## Pitfalls

### getInitials helper duplicado
Cada componente necesita `getInitials(name)`. Extraer a `utils.ts` y importar.

### Tailwind v4 vs v3 syntax
Tailwind v4 usa `@theme` block en CSS, no `tailwind.config.js`. Los custom colors se definen como `--color-*` theme variables.

### Error state no eliminado
Al migrar a showToast, asegurarse de eliminar TODOS los `setError(null)` calls y el display `{error && ...}`. Quedan referencias sueltas que causan errores de TypeScript.

### Subagentes modifican archivos en paralelo
Cuando se delegan tareas a subagentes, pueden modificar archivos que el padre también va a tocar. SIEMPRE re-leer archivos después de delegar antes de hacer cambios adicionales.
