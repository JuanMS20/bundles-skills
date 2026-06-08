# React + Vite Scaffolding (2026 — Vite 8, React 19, TS 6, Tailwind v4)

Notas concretas de tooling actual. Verificado con `npm create vite@latest -- --template react-ts` en junio 2026.

## Versiones que trae el template (jun 2026)

| Paquete | Versión |
|---------|---------|
| vite | ^8.0.x |
| react / react-dom | ^19.2.x |
| typescript | ~6.0.x |
| @vitejs/plugin-react | ^6.0.x |
| eslint | ^10.x |

## Tailwind CSS v4 — setup radicalmente distinto a v3

**v3** necesitaba: `tailwind.config.js` + `postcss.config.js` + directivas `@tailwind` en CSS.

**v4** elimina ambos archivos. Setup completo:

1. Instalar plugin: `npm install tailwindcss @tailwindcss/vite`
2. En `vite.config.ts`:
   ```ts
   import tailwindcss from '@tailwindcss/vite'
   export default defineConfig({ plugins: [react(), tailwindcss()] })
   ```
3. En `src/index.css` (única línea):
   ```css
   @import "tailwindcss";
   ```

No hay `content` config, no hay `theme.extend`. Tailwind escanea automáticamente.

## TypeScript 6 — `baseUrl` deprecado

TS 6 emite error TS5101 si usas `baseUrl`:

```
Option 'baseUrl' is deprecated and will stop functioning in TypeScript 7.0.
Specify compilerOption '"ignoreDeprecations": "6.0"' to silence this error.
```

**Fix correcto**: eliminar `baseUrl`. `paths` funciona sin él:
```json
{
  "compilerOptions": {
    "paths": { "@/*": ["./src/*"] }
  }
}
```

NO agregar `ignoreDeprecations` — es silenciar el problema, no fixearlo.

## Path alias `@/` en Vite + TS

Requiere configuración en dos lugares:

1. `tsconfig.app.json` — `paths` (sin `baseUrl`)
2. `vite.config.ts` — `resolve.alias`:
   ```ts
   import path from 'path'
   export default defineConfig({
     resolve: { alias: { '@': path.resolve(__dirname, './src') } }
   })
   ```

## Template trae `tsconfig.json` sin `include`

El template divide en `tsconfig.app.json` (src) + `tsconfig.node.json` (vite.config.ts). El `tsconfig.json` raíz solo tiene `references`. Esto es intencional — no agregar `include` al raíz.

## Secuencia de scaffolding verificada

Sobre un repo existente con PRD.md, CONTEXT.md, supabase/ ya presentes:

1. `npm create vite@latest <temp-dir> -- --template react-ts` (directorio temporal)
2. Copiar configs: `tsconfig.json`, `tsconfig.node.json`, `eslint.config.js`
3. Escribir `package.json` propio (renombrar, añadir deps: supabase, react-router)
4. Escribir `vite.config.ts` con tailwindcss + alias
5. Escribir `tsconfig.app.json` con paths (sin baseUrl)
6. Escribir `src/` (main.tsx, App.tsx con router, index.css con @import tailwind, lib/supabase.ts, routes/placeholder)
7. Escribir `.env.example` + `.env` (placeholders)
8. Escribir `.gitignore` (node_modules, dist, .env)
9. `npm install`
10. Limpiar directorio temporal

## Verificación — 3 pasos obligatorios

```bash
npx tsc -b          # sin errores = TS compila
npm run build       # sin errores = Vite + Tailwind procesan OK
curl http://localhost:5173/   # devuelve HTML = dev server arranca
```

Si los 3 pasan, el scaffolding es real. Si cualquiera falla, NO commitear.

## Supabase client mínimo

```ts
// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

Variables en `.env`:
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

## React Router v7 setup

```tsx
// src/main.tsx
import { BrowserRouter } from 'react-router-dom'
// envolver App en <BrowserRouter>

// src/App.tsx
import { Routes, Route } from 'react-router-dom'
<Routes>
  <Route path="/login" element={<Login />} />
  <Route path="/" element={<Dashboard />} />
</Routes>
```
