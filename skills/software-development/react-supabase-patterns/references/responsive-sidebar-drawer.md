# Responsive Sidebar Drawer (Tailwind v4 + React)

Patron verificado para sidebar responsive en apps con Layout fijo.

## Patron

Desktop (md+): sidebar fijo w-64, main con ml-64.
Mobile (<md): sidebar oculto (-translate-x-full), hamburger button, overlay oscuro al abrir.

## Implementacion

```tsx
import { useState } from 'react'

export default function Layout({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-slate-800 text-white transition-transform duration-200 md:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Header con boton cerrar (solo mobile) */}
        <div className="flex h-16 items-center justify-between border-b border-slate-700 px-6">
          <span className="text-lg font-bold tracking-tight">LOGO</span>
          <button
            onClick={() => setSidebarOpen(false)}
            className="text-slate-400 hover:text-white md:hidden"
            aria-label="Cerrar menú"
          >
            ✕
          </button>
        </div>

        <nav className="mt-4 space-y-1 px-3">
          {items.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              onClick={() => setSidebarOpen(false)}  // cerrar al navegar
              className={/* ... activo vs inactivo */}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* User info + logout al fondo */}
        <div className="absolute bottom-0 w-full border-t border-slate-700 p-4">
          {/* ... */}
        </div>
      </aside>

      {/* Main content */}
      <main className="min-h-screen p-4 md:ml-64 md:p-8">
        {/* Hamburger (solo mobile) */}
        <div className="mb-4 flex items-center md:hidden">
          <button
            onClick={() => setSidebarOpen(true)}
            className="rounded-md p-2 text-gray-600 hover:bg-gray-200"
            aria-label="Abrir menú"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <span className="ml-3 text-lg font-bold text-slate-800">LOGO</span>
        </div>
        {children}
      </main>
    </div>
  )
}
```

## Clases clave de Tailwind

| Elemento | Mobile | Desktop (md+) |
|----------|--------|---------------|
| Sidebar | `-translate-x-full` (oculto) | `md:translate-x-0` (visible) |
| Sidebar abierto | `translate-x-0` | (override por md:translate-x-0) |
| Overlay | `fixed inset-0 z-30 bg-black/50 md:hidden` | No se renderiza |
| Hamburger | Visible (`md:hidden` en el boton de cerrar) | Oculto (`md:hidden`) |
| Main | `p-4` | `md:ml-64 md:p-8` |

## Pitfalls

- **z-index**: overlay debe ser z-30, sidebar z-40 (sidebar sobre overlay)
- **Cierre al navegar**: siempre agregar `onClick={() => setSidebarOpen(false)}` en los Links
- **Boton cerrar vs hamburger**: el boton cerrar esta DENTRO del sidebar (solo md:hidden), el hamburger esta DENTRO del main (solo md:hidden). No confundir.
- **transition-transform**: necesario para animacion suave al abrir/cerrar
