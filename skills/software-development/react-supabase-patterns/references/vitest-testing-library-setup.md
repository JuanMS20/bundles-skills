# Vitest + Testing Library Setup (Vite + React + TS)

Receta verificada para agregar testing a un proyecto Vite + React 19 + TypeScript.

## 1. Instalar dependencias

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

## 2. Configurar vite.config.ts

```ts
/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  test: {
    globals: true,           // describe/it/expect sin import
    environment: 'jsdom',    // DOM simulado para componentes
    setupFiles: ['./src/test/setup.ts'],
    css: true,               // procesa CSS (necesario para Tailwind)
  },
})
```

**Pitfall:** El triple-slash reference `/// <reference types="vitest/config" />` es NECESARIO para que TS reconozca la propiedad `test` en `defineConfig`. Sin esto, TS da error de tipo.

## 3. Setup file

```ts
// src/test/setup.ts
import '@testing-library/jest-dom/vitest'
```

Esto agrega matchers como `toBeInTheDocument()`, `toBeDisabled()`, etc. al entorno de vitest.

## 4. Scripts en package.json

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest"
  }
}
```

## 5. Mock de Supabase para componentes

Los componentes que usan `supabase.from()` necesitan un mock del modulo. Patron verificado:

```ts
// En el test file, ANTES de los imports del componente:
vi.mock('@/lib/supabase', () => ({
  supabase: (() => {
    function createBuilder(data: unknown[]) {
      return {
        select: vi.fn().mockReturnThis(),
        eq: vi.fn().mockReturnThis(),
        order: vi.fn().mockReturnThis(),
        in: vi.fn().mockReturnThis(),
        then: (resolve: (val: { data: unknown }) => void) =>
          resolve({ data }),
      }
    }
    return {
      from: vi.fn().mockImplementation((table: string) => {
        const data: Record<string, unknown[]> = {
          geo_departments: [{ code: '76', name: 'Valle del Cauca' }],
          // ... mas datos de prueba
        }
        return createBuilder(data[table] ?? [])
      }),
    }
  })(),
}))
```

**Pitfall:** El mock debe retornar un objeto con `.then()` (thenable) para que `await supabase.from(...).select(...)` funcione. Supabase JS usa thenables internamente.

## 6. Patron de test para componente con Supabase

```tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

describe('MiComponente', () => {
  it('renderiza datos cargados de Supabase', async () => {
    render(<MiComponente />)

    // waitFor para datos async (Supabase mock resuelve en microtask)
    await waitFor(() => {
      expect(screen.getByText('Dato esperado')).toBeInTheDocument()
    })
  })

  it('interaccion dispara onChange con datos correctos', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(<MiComponente onChange={onChange} />)

    await waitFor(() => { /* datos cargados */ })

    const select = document.querySelectorAll('select')[0]
    await user.selectOptions(select, 'valor')

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ campo: 'valor' })
    )
  })
})
```

## 7. Extraccion de funciones puras para testabilidad

Cuando la logica esta inline en el componente, extraerla a un modulo separado:

```ts
// src/lib/utils.ts — funciones puras exportadas
export function aggregateContactsByLeader<T extends { lider_id: string }>(
  contacts: T[]
): Map<string, { total: number; votados: number }> {
  // ... logica pura
}
```

```ts
// src/routes/Dashboard.tsx — importa y usa
import { aggregateContactsByLeader } from '@/lib/utils'
// ...
const contactMap = aggregateContactsByLeader(allContacts)
```

```ts
// src/lib/utils.test.ts — test directo, sin mocks
describe('aggregateContactsByLeader', () => {
  it('cuenta total y votados por lider', () => {
    const result = aggregateContactsByLeader([
      { lider_id: 'A', estado: 'voted' },
      { lider_id: 'A', estado: 'pending' },
    ])
    expect(result.get('A')).toEqual({ total: 2, votados: 1 })
  })
})
```

## Pitfalls

| Pitfall | Causa | Fix |
|---------|-------|-----|
| `toBeInTheDocument is not a function` | Falta `import '@testing-library/jest-dom/vitest'` en setup.ts | Agregar import |
| Tests pasan local pero fallan en CI | `css: true` no seteado, Tailwind rompe render | Agregar `css: true` al config de vitest |
| `selectOptions` no dispara onChange | React 19 synthetic events no capturan native DOM manipulation en jsdom | Usar `userEvent.setup()` + `user.selectOptions()` en vez de `dispatchEvent` |
| Mock de Supabase retorna `undefined` | Builder no tiene `.then()`, `await` no resuelve | Agregar `.then: (resolve) => resolve({ data })` al builder |
| `describe`/`it` no reconocidos | Falta `globals: true` en config de vitest | Agregar al config |
| TSC error: `Type 'Mock<Procedure>' is not assignable` en `onChange` prop | `vi.fn()` retorna tipo genérico incompatible con firma tipada. Ej: `let onChange: ReturnType<typeof vi.fn>` no asigna a `(val: CascadaValue) => void` | Usar tipo explícito: `let onChange: (val: CascadaValue) => void`. El `vi.fn()` asignado cumple la interfaz por structural typing. |
