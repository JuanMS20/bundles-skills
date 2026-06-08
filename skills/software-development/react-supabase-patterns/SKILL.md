---
name: react-supabase-patterns
description: "React + Supabase fullstack patterns: project structure, auth context, RLS, client setup, Tailwind v4, security hardening (triggers, API views), and critical pitfalls (auth.admin from frontend). Use when building or reviewing React web apps with Supabase backend, setting up Supabase client, or debugging Supabase-specific issues."
tags: [react, supabase, fullstack, postgresql, rls, tailwind, typescript]
---

# React + Supabase Patterns

Estructura, auth, RLS, cliente y pitfalls críticos para apps web con React + Supabase (PostgreSQL). Cubre Vite + React 19 + TS 6 + Tailwind v4.

## Project Structure

```
src/
├── types/
│   └── database.ts          # Interfaces que reflejan el schema SQL
├── lib/
│   └── supabase.ts          # Cliente createClient (singleton)
├── context/
│   └── AuthContext.tsx      # Session + profile + role
├── components/
│   ├── ProtectedRoute.tsx   # Gate por sesión y rol
│   ├── Layout.tsx           # Shell con nav filtrada por rol
│   └── CascadaGeo.tsx       # Widgets reutilizables
├── routes/                   # Una página por feature
│   ├── Login.tsx
│   ├── Dashboard.tsx
│   ├── Lideres.tsx
│   └── ...
├── App.tsx                   # Router + Providers
└── main.tsx                  # Entry: BrowserRouter + StrictMode
```

## Cliente Supabase

```ts
// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    'Missing Supabase env vars. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in .env.local'
  )
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

**Regla de oro:** El cliente frontend SIEMPRE usa la `anon_key`, NUNCA la `service_role_key`. La service_role key es server-only (Edge Functions, scripts backend).

## Auth Context Pattern

```tsx
// src/context/AuthContext.tsx
const [session, setSession] = useState<Session | null>(null)
const [profile, setProfile] = useState<Profile | null>(null)

useEffect(() => {
  supabase.auth.getSession().then(({ data: { session } }) => {
    setSession(session)
    if (session) loadProfile(session.user.id)
    else setLoading(false)
  })

  const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
    setSession(session)
    if (session) loadProfile(session.user.id)
    else { setProfile(null); setLoading(false) }
  })

  return () => subscription.unsubscribe()
}, [])
```

**Login con username:** Supabase Auth usa `email`. Para login por username, construir email sintético: `user@tudominio.local`. Mapear en tabla `profiles` con trigger que crea el profile al registrarse.

**Pitfall critico — @ prefix en username:** La UI muestra usernames con `@` prefix (ej: `@test.lider`, estilo redes sociales). Los usuarios copian el username CON el `@` del input. Si `signIn()` no lo strippea, construye `@test.lider@tudominio.local` — email inválido, auth falla sin error comprensible.

```tsx
async function signIn(username: string, password: string) {
  // Strip @ prefix + trim + lowercase. La UI muestra @username pero el
  // email interno debe ser username@dominio.local (sin doble @)
  const cleanUsername = username.replace(/^@+/, '').trim().toLowerCase()
  const email = `${cleanUsername}@${AUTH_DOMAIN}`
  const { error } = await supabase.auth.signInWithPassword({ email, password })
  if (error) return { error: error.message }
  return { error: null }
}
```

## Brute Force Protection (CAPTCHA + Rate Limiting)

Supabase Auth ya incluye rate limiting nativo por IP en `/auth/v1/token` (token bucket: burst 30, luego 1800 req/hora). **No necesitas una Edge Function custom para brute force básico.** Lo que falta en el Free tier:

1. **CAPTCHA** (Cloudflare Turnstile recomendado — invisible, gratis) — bloquea bots automatizados
2. **Leaked Password Protection** — verifica contra HaveIBeenPwned (requiere Pro Plan $25/mes)

**Ambos se activan desde el Dashboard de Supabase** (Authentication → Bot & Abuse Protection), no via SQL/MCP. Ver `references/cloudflare-turnstile-captcha.md` para implementación completa verificada (frontend widget + auth context + dashboard steps + backward-compatible pattern).

**Patrón clave — backward compatibility:** El widget Turnstile solo renderiza si `VITE_TURNSTILE_SITEKEY` está configurado. Sin sitekey, la app funciona normal sin CAPTCHA. Esto permite deployar el código antes de configurar el sitekey en Cloudflare/Supabase.

```tsx
// Login.tsx
import { Turnstile } from '@marsidev/react-turnstile'
const TURNSTILE_SITEKEY = import.meta.env.VITE_TURNSTILE_SITEKEY
const [captchaToken, setCaptchaToken] = useState<string | null>(null)

// En el form, antes del botón submit:
{TURNSTILE_SITEKEY && (
  <Turnstile
    siteKey={TURNSTILE_SITEKEY}
    onSuccess={(token) => setCaptchaToken(token)}
    onExpire={() => setCaptchaToken(null)}
    options={{ theme: 'light', size: 'flexible' }}
  />
)}

// Botón bloqueado hasta que el CAPTCHA verifique:
<button disabled={loading || (!!TURNSTILE_SITEKEY && !captchaToken)}>
```

```tsx
// AuthContext.tsx — signIn acepta captchaToken opcional
async function signIn(username: string, password: string, captchaToken?: string) {
  const { error } = await supabase.auth.signInWithPassword({
    email, password,
    options: captchaToken ? { captchaToken } : undefined,
  })
}
```

## AFK Auto-Logout (Idle Detection)

Para apps sensibles (electoral, financiero, admin), la sesión no debe persistir indefinidamente. Supabase Auth auto-refresca el JWT via `refresh_token`, por lo que la sesión persiste mientras el browser esté abierto — incluso horas. Hay que implementar idle detection en el cliente.

```tsx
// AuthContext.tsx — dentro de AuthProvider, después del effect de onAuthStateChange

const IDLE_TIMEOUT_MS = 20 * 60 * 1000 // 20 minutos
const IDLE_CHECK_INTERVAL_MS = 30_000   // poll cada 30s
const ACTIVITY_EVENTS = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart'] as const

const lastActivityRef = useRef<number>(Date.now())

useEffect(() => {
  if (!session) return

  lastActivityRef.current = Date.now()

  const resetActivity = () => { lastActivityRef.current = Date.now() }
  ACTIVITY_EVENTS.forEach(e => window.addEventListener(e, resetActivity, { passive: true }))

  const interval = setInterval(() => {
    if (Date.now() - lastActivityRef.current >= IDLE_TIMEOUT_MS) {
      sessionStorage.setItem('idle-logout', 'true')
      window.dispatchEvent(new CustomEvent('session-idle-expired'))
      supabase.auth.signOut()
    }
  }, IDLE_CHECK_INTERVAL_MS)

  return () => {
    ACTIVITY_EVENTS.forEach(e => window.removeEventListener(e, resetActivity))
    clearInterval(interval)
  }
}, [session])
```

**Notas de diseño:**
- `useRef` (no `useState`) para `lastActivity` — no queremos re-render en cada mousemove.
- `{ passive: true }` en listeners para no bloquear scroll/touch.
- Interval de 30s (no cada segundo) — suficientemente responsivo, bajo overhead.
- El effect depende de `[session]` — se reinicia al login, se limpia al logout.

**Feedback al usuario (implementado + verificado):** El signOut solo es silencioso si no se implementa feedback. El patrón verificado usa sessionStorage + CustomEvent para que el Login page muestre el motivo del logout:

```tsx
// AuthContext.tsx — antes de signOut (ver código arriba):
//   sessionStorage.setItem('idle-logout', 'true')
//   window.dispatchEvent(new CustomEvent('session-idle-expired'))

// Login.tsx — listener que muestra el mensaje al volver
useEffect(() => {
  const showIdleMessage = () => {
    setError('Tu sesión expiró por inactividad. Vuelve a ingresar.')
    sessionStorage.removeItem('idle-logout')
  }
  // Caso 1: el usuario fue deslogueado en OTRA pestaña y abrió el login aquí
  if (sessionStorage.getItem('idle-logout') === 'true') {
    showIdleMessage()
  }
  // Caso 2: el idle timer disparó signOut y React Router redirigió al login
  // en la MISMA pestaña — el CustomEvent se recibe en el listener
  window.addEventListener('session-idle-expired', showIdleMessage)
  return () => window.removeEventListener('session-idle-expired', showIdleMessage)
}, [])
```

**Por qué sessionStorage y no solo CustomEvent:** Si el idle timer dispara en la pestaña A y el usuario tiene el login abierto en la pestaña B, sessionStorage persiste el flag para que la pestaña B lo muestre al enfocar. El CustomEvent cubre el caso same-tab (redirect inmediato). Entre ambos, todos los escenarios están cubiertos.

## ProtectedRoute por Rol

```tsx
function ProtectedRoute({ children, roles }: { children: ReactNode; roles: UserRole[] }) {
  const { session, profile, loading } = useAuth()
  if (loading) return <p>Cargando...</p>
  if (!session) return <Navigate to="/login" />
  // Guard: session exists but profile fetch failed (network error, RLS misconfigured, etc.)
  if (!profile) return <p>Error cargando perfil. <button onClick={() => window.location.reload()}>Reintentar</button></p>
  if (roles && !roles.includes(profile.role)) return <Navigate to="/" />
  return <>{children}</>
}
```

## Tailwind CSS v4 Setup (2026)

Sin `tailwind.config.js`. Sin `postcss.config.js`. Solo:

```bash
npm install @tailwindcss/vite
```

```ts
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'
export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

```css
/* src/index.css — única línea necesaria */
@import "tailwindcss";
```

## TypeScript 6 + Path Aliases

TS 6 **depreca `baseUrl`**. `paths` funciona standalone:

```json
// tsconfig.app.json
{
  "compilerOptions": {
    "paths": { "@/*": ["./src/*"] }
  }
}
```

```ts
// vite.config.ts — alias debe ir también aquí
resolve: {
  alias: { '@': path.resolve(__dirname, './src') }
}
```

## CRITICAL: auth.admin NO funciona desde el frontend

`supabase.auth.admin.createUser()` y `supabase.auth.admin.updateUserById()` requieren la **service_role key**. Con la `anon_key` del cliente frontend, estas llamadas fallan en runtime.

**Soluciones:**
1. **Edge Functions** (recomendado): crear endpoint server-side con service_role. Template verificado en `templates/edge-function-user-admin.ts`. Desde el frontend:
```typescript
// Crear usuario
const { error } = await supabase.functions.invoke('user-admin', {
  body: { action: 'create-user', username, password, role: 'lider', profile: { ... } }
})
// Reset password
const { error } = await supabase.functions.invoke('user-admin', {
  body: { action: 'reset-password', authId: user.auth_id, newPassword: '...' }
})
// Eliminar usuario (borra auth user, NO el profile — hacerlo aparte)
const { error } = await supabase.functions.invoke('user-admin', {
  body: { action: 'delete-user', authId: user.auth_id }
})
```
2. **Supabase Dashboard**: gestionar usuarios manualmente mientras no hay Edge Functions
3. **Custom signup flow**: usar `supabase.auth.signUp()` desde el cliente (limitado, no crea perfiles arbitrarios)
4. **SQL directo vía MCP** (`execute_sql`): insertar en `auth.users` + `auth.identities` + `profiles` directamente. Útil para seed de usuarios admin iniciales sin UI de signup. **CUIDADO:** GoTrue escanea columnas string como no-nullable — todas deben ser `''` no NULL, o login falla con HTTP 500. Ver `references/supabase-user-creation-via-sql.md` para el SQL exacto verificado (incluye password reset via SQL, reset masivo por rol, y verificacion post-reset).

Ver `references/supabase-auth-admin-pitfall.md` para detalles y soluciones.
Ver `templates/edge-function-user-admin.ts` para template completo y verificado del Edge Function que resuelve crear-usuarios, reset-password, y delete-user server-side (con verificacion de caller admin, rollback, fix de GoTrue NULLs, y CORS completo).
Ver `references/edge-function-cors.md` para diagnóstico completo de errores de Edge Functions: CORS preflight OPTIONS + headers obligatorios, pitfall `verify_jwt: true` vs auth interna (500), y extracción de mensajes de error reales del SDK (`FunctionsHttpError.context.json()`).
Ver `references/supabase-mcp-setup.md` para configurar el MCP server (gestión remota del proyecto, deploy de Edge Functions que resuelven este pitfall).
Ver `references/supabase-user-creation-via-sql.md` para crear usuarios admin iniciales vía SQL.
Ver `references/cascade-dependent-dropdowns.md` para patrón de dropdowns dependientes multi-nivel (dept→municipio→puesto+barrio) con hooks React y Supabase.
Ver `references/n1-query-elimination.md` para eliminar N+1 queries en dashboards y listas con contadores agregados (single bulk fetch + Map aggregation).
Ver `references/vitest-testing-library-setup.md` para setup completo de testing con vitest + @testing-library/react (instalacion, config, mocks de Supabase, patron de test de componentes).
Ver `references/responsive-sidebar-drawer.md` para patron de sidebar responsive con Tailwind (hamburger, drawer, overlay, breakpoints).
Ver `references/vitest-mock-typing-pitfall.md` para fix de errores de tipo con `vi.fn()` en tests (usar tipo de función real, no `ReturnType<typeof vi.fn>`).
Ver `references/supabase-auth-config-and-observability.md` para limitaciones de auth config via SQL/MCP (Leaked Password Protection, password policies requieren Dashboard — no accesibles via `execute_sql`), patrón de health-check Edge Function, y logging real en ErrorBoundary.
Ver `references/audit-db-verification.md` para verificación de estado actual de triggers y RLS policies antes de implementar fixes de auditoría (queries SQL para pg_trigger, pg_policies, geo tables).
Ver `references/cloudflare-turnstile-captcha.md` para implementación completa de Cloudflare Turnstile CAPTCHA en login de Supabase Auth (instalación, widget React, AuthContext integration, dashboard config steps, gotchas de Pro Plan).
Ver `references/rls-infinite-recursion.md` para el pitfall más insidioso de RLS: recursión infinita cuando policies referencian la misma tabla directa o indirectamente. Incluye debugging path (simular rol authenticated via SET LOCAL), fix pattern completo (cachear role/profile_id en auth.users.raw_app_meta_data), y regla de oro anti-recursión.

## Auth: errores de retorno vs excepción

**Pitfall critico:** `supabase.auth.signInWithPassword()` NO lanza excepción cuando las credenciales son inválidas. Retorna `{ data: { user: null, session: null }, error: AuthError }`. Si el AuthContext expone `signIn` que retorna `{ error }` y el componente de Login solo usa `try/catch`, los errores de credenciales incorrectas se ignoran — el usuario ve que no pasa nada.

**Patron correcto en el componente Login:**

```tsx
async function handleSubmit(e: React.FormEvent) {
  e.preventDefault()
  setError(null)
  setLoading(true)
  try {
    const result = await signIn(username, password)
    if (result.error) {
      // Traducir mensajes de Supabase Auth (vienen en inglés)
      const msg = result.error
      if (msg.includes('Invalid login credentials')) {
        setError('Usuario o contraseña incorrectos')
      } else {
        // NO mapear "Email not confirmed": con emails sintéticos (username@dominio.local)
        // la confirmación por email es imposible. Si aparece, es un problema de config
        // (email confirmation mal desactivado en Supabase), no un mensaje para el usuario.
        setError('No se pudo iniciar sesión. Verifica tus datos o contacta al administrador.')
      }
      return // NO navegar
    }
    navigate('/')
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Error al iniciar sesión')
  } finally {
    setLoading(false)
  }
}
```

**Mapeo de mensajes comunes de Supabase Auth:**

| Mensaje original (en) | Traducción (es) |
|---|---|
| `Invalid login credentials` | `Usuario o contraseña incorrectos` |
| `User already registered` | `Este usuario ya está registrado` |
| `Password should be at least 6 characters` | `La contraseña debe tener al menos 6 caracteres` |

**Nota sobre "Email not confirmed":** NO incluir en el mapeo. Con auth por username usando emails sintéticos (`user@dominio.local`), la confirmación por email es imposible — los emails son falsos. Si este error aparece, significa que "Confirm email" está activado en Supabase Dashboard → Authentication → Settings. Desactivarlo. Nunca mostrar este mensaje al usuario final.

## Patrón: credenciales visibles tras crear/resetear usuario

Supabase Auth usa bcrypt. Las contraseñas son **irrecuperables** después del hash. Cuando un admin crea usuarios o resetea contraseñas, debe ver las credenciales generadas antes de cerrar el modal — si no, se pierden.

**Implementación verificada (3 piezas):**

1. **Estado del modal de credenciales:**
```tsx
const [createdCreds, setCreatedCreds] = useState<{ username: string; password: string } | null>(null)
```

2. **Capturar credenciales tras crear** (NO llamar generatePassword() de nuevo — da resultado diferente):
```tsx
const username = form.username || generateUsername(form.primer_nombre, form.primer_apellido)
const password = form.password || generatePassword()
const { error: fnError } = await supabase.functions.invoke('user-admin', {
  body: { action: 'create-user', username, password, role: 'lider', profile: { ... } },
})
if (fnError) throw fnError
setCreatedCreds({ username, password }) // capturar las variables locales, no regenerar
```

3. **Modal de confirmación con credenciales visibles:**
```tsx
{createdCreds && (
  <div className="modal-overlay" onClick={() => setCreatedCreds(null)}>
    <div className="modal" onClick={(e) => e.stopPropagation()}>
      {/* Mostrar username y password en font-mono para legibilidad */}
      {/* Aviso: "La contraseña no se puede recuperar después" */}
    </div>
  </div>
)}
```

**Pitfall: regenerar credenciales al mostrar.** Si llamas `generatePassword()` otra vez en el modal, obtienes una contraseña diferente a la que se envió al Edge Function. Siempre capturar las variables locales inmediatamente después del invoke exitoso.

**Reset de contraseña:** mismo patrón. Tras reset exitoso, cambiar el modal a modo "credenciales mostradas" (botón "Cerrar" reemplaza a "Confirmar"/"Cancelar"). El campo de password debe ser `type="text"` (visible) con botón "Generar" para password aleatorio.

## Code-Splitting con React.lazy por Rol

En apps multi-rol (admin, líder, staff), cada rol ve rutas distintas. Sin code-splitting, TODOS descargan TODO el código (incluyendo páginas admin que nunca ven). Vite genera warning cuando el bundle supera 500KB raw.

**Patrón verificado:** Login eager (first paint), todo lo demás lazy:

```tsx
import { lazy, Suspense } from 'react'
import Login from '@/routes/Login' // eager — first paint

const Dashboard = lazy(() => import('@/routes/Dashboard'))
const Lideres = lazy(() => import('@/routes/Lideres'))
const Staff = lazy(() => import('@/routes/Staff'))
const Geodata = lazy(() => import('@/routes/Geodata'))
const AuditLog = lazy(() => import('@/routes/AuditLog'))
// ... resto de rutas lazy

const PageLoader = () => (
  <div className="flex min-h-screen items-center justify-center">
    <svg className="h-8 w-8 animate-spin text-teal-500" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  </div>
)

function App() {
  return (
    <AuthProvider>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<ProtectedRoute>...<Dashboard />...</ProtectedRoute>} />
          <Route path="/geodata" element={<ProtectedRoute roles={['admin']}>...<Geodata />...</ProtectedRoute>} />
          {/* ... */}
        </Routes>
      </Suspense>
    </AuthProvider>
  )
}
```

**Resultado medido (app real, 9 rutas):**
- Antes: 1 chunk 511 KB raw (warning Vite >500KB) → 136 KB gzip para todos
- Después: vendor 438 KB + 11 chunks bajo demanda → 126 KB gzip inicial
- Un líder/staff nunca descarga Geodata (8.5KB), AuditLog (7.2KB), Credenciales (5.7KB), Staff (7KB), Lideres (14.4KB)

**Suspense fallback:** Usar un spinner consistente con el design system (mismo color/estilo que los loading states internos). NO usar texto genérico "Loading...".

**Login se mantiene eager** porque es el first paint — un Suspense boundary ahí causaría flash blanco en la pantalla inicial.

## Security Triggers como Defense-in-Depth

RLS policies son la primera línea de defensa, pero tienen limitaciones:
- Si el service_role key se filtra al frontend, RLS se bypassa
- Si una policy tiene un bug (subquery incorrecta, recursive reference), el漏洞 queda abierto
- Edge Functions con service_role pueden hacer cualquier operación

**Triggers SECURITY DEFINER** actúan como segunda capa — se ejecutan en el servidor de PostgreSQL independientemente de cómo se hizo la operación (REST API, Edge Function, SQL directo).

### Patrón: prevenir role escalation

```sql
-- Evita que usuarios no-admin cambien el campo role
CREATE OR REPLACE FUNCTION prevent_role_escalation()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  -- Si el role está cambiando y el usuario actual NO es admin → bloquear
  IF old.role IS DISTINCT FROM new.role THEN
    IF get_user_role() != 'admin' THEN
      RAISE EXCEPTION 'No tienes permisos para cambiar roles de usuario';
    END IF;
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_role_escalation
  BEFORE UPDATE ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION prevent_role_escalation();
```

### Patrón: prevenir profiles admin huérfanos

```sql
-- Evita crear profiles con role admin sin auth_id válido
CREATE OR REPLACE FUNCTION prevent_orphan_admin_profiles()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.role = 'admin' AND NEW.auth_id IS NULL THEN
    RAISE EXCEPTION 'No se puede crear perfil de administrador sin usuario de autenticación asociado';
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_orphan_admin
  BEFORE INSERT ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION prevent_orphan_admin_profiles();
```

### Cuándo usar triggers vs RLS

| Escenario | Solución |
|-----------|----------|
| Control de acceso por rol (quién lee/escribe qué) | RLS policies |
| Proteger columnas específicas (role, auth_id) | SECURITY DEFINER trigger |
| Validación de datos compleja (cédula única, cascade) | Trigger (ya cubierto en schema) |
| Auditar quién hizo un cambio | Trigger (ya cubierto en schema) |

**Regla de oro:** RLS controla FILAS. Triggers controlan COLUMNAS y OPERACIONES. Usar ambos en conjunto.

### Verificar triggers existentes

```sql
SELECT trigger_name, event_manipulation, action_statement
FROM information_schema.triggers
WHERE event_object_table = 'profiles'
AND trigger_name LIKE 'trg_prevent%'
ORDER BY trigger_name;
```

## RLS (Row Level Security)

El schema SQL debe definir policies para cada tabla. Patrón típico:

```sql
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Users can read their own profile
CREATE POLICY "profiles_select_own" ON profiles
  FOR SELECT USING (auth.uid() = auth_id);

-- Admins can do everything
-- ⚠️ NUNCA hacer subquery a profiles dentro de una policy de profiles → recursión infinita
-- Usar función helper que lee de auth.users (sin RLS)
CREATE POLICY "profiles_admin_all" ON profiles
  FOR ALL USING (get_user_role() = 'admin');
```

**Pitfall:** Si RLS está activada sin policies → la tabla es **inaccesible** desde el cliente (no open por defecto). Siempre definir al menos una policy de SELECT.

**Pitfall CRÍTICO — Recursión infinita:** Ninguna policy de RLS en tabla X debe contener un subquery o JOIN a la tabla X. Si una policy necesita el role del usuario, usar una función SECURITY DEFINER que lea de `auth.users.raw_app_meta_data` (tabla sin RLS). Ver `references/rls-infinite-recursion.md` para debugging y fix completo.

## Storage Pattern

```ts
// Upload
const { error } = await supabase.storage
  .from('bucket-name')
  .upload(`${userId}/${filename}`, file, { upsert: true })

// Get public URL
const { data: { publicUrl } } = supabase.storage
  .from('bucket-name')
  .getPublicUrl(`${userId}/${filename}`)
```

## Anti-Patterns

| Patrón | Problema | Solución |
|--------|----------|----------|
| `auth.admin.*` en frontend | Requiere service_role, falla con anon_key | Edge Function o Dashboard |
| RLS sin policies | Tabla inaccesible | Definir al menos SELECT policy |
| `useEffect([], [])` con función que usa `profile` | Componente carga antes que el auth profile → datos vacíos o crash | `useEffect(() => { if (profile) loadData() }, [profile])` — depende de profile, no de `[]` |
| N+1 queries en dashboard | Loop de queries por item (`Promise.all` paraleliza pero NO reduce query count) | Single bulk fetch + Map aggregation client-side. Ver `references/n1-query-elimination.md` |
| `baseUrl` en TS 6 | Deprecated warning | Solo `paths` sin `baseUrl` |
| Email real para cada user | Supabase requiere email | Email sintético `user@dominio.local` |
| Profile no se crea tras signUp | Falta trigger | Trigger `on_auth_user_created` que inserta en profiles |
| Login silencioso (no redirige, sin error visible) | Múltiples causas, error tragado | Ver debugging checklist abajo |
| Edge Function sin CORS | Navegador bloquea OPTIONS preflight → "Failed to send a request to the Edge Function" | Handler OPTIONS + CORS headers en todas las respuestas. Ver `references/edge-function-cors.md` |
| Edge Function CORS con `Access-Control-Allow-Origin: *` | Cualquier origen puede llamar al endpoint — riesgo si se añaden endpoints públicos | Allowlist dinámica: leer `Origin` header, permitir solo dominios conocidos + wildcard para previews. Ver `references/edge-function-cors.md` sección "Allowlist dinámica" |
| `verify_jwt: true` + auth interna en Edge Function | POST → 500 Internal Server Error (gateway choca con auth propia de la función) | `verify_jwt: false` al deployar. La función verifica auth internamente con getUser() + role check |
| `err.message` en catch de `functions.invoke` | Usuario ve "Edge Function returned a non-2xx status code" en vez del error real | Helper `extractFnError()` que lee `.context.json()`. Ver `references/edge-function-cors.md` sección "non-2xx status code" |
| `signIn()` retorna `{ error }` y caller solo usa `try/catch` | Login falla silenciosamente: credenciales inválidas NO lanzan excepción, retornan `{ error: "Invalid login credentials" }`. Si el caller solo hace `await signIn()` y confía en `catch`, el error se ignora | Leer el return value: `const { error } = await signIn(...)`. Si `error`, mostrarlo al usuario. Ver sección "Auth: errores de retorno vs excepción" abajo |
| Contraseñas generadas no mostradas al admin | Al crear usuarios (vía Edge Function o signUp), username/password se generan pero el admin nunca los ve. bcrypt las hace irrecuperables después | Tras crear, mostrar modal con credenciales antes de cerrar. En reset, mostrar nueva contraseña antes de cerrar. Ver sección "Patrón: credenciales visibles" abajo |
| `error.message` en inglés sin traducir | Supabase Auth retorna mensajes en inglés ("Invalid login credentials") | Mapear strings conocidos a español antes de mostrar al usuario. NO mapear "Email not confirmed" (ver nota en tabla de mapeo) |
| UI muestra `@username` y `signIn()` no strippea el `@` | Usuario copia `@test.lider` de la UI, se construye `@test.lider@dominio.local` (email inválido), auth falla sin error claro | Stripper en `signIn()`: `username.replace(/^@+/, '').trim().toLowerCase()` antes de construir el email |
| Intentar configurar auth settings (Leaked Password Protection, password policies) via `execute_sql` o MCP | Auth config vive en GoTrue service, NO en Postgres. `information_schema.tables WHERE table_schema='auth'` retorna vacío. Tiempo perdido buscando tablas inexistentes | Dashboard → Authentication → Providers/Settings. Algunos features requieren Pro Plan+. Ver `references/supabase-auth-config-and-observability.md` |
| `componentDidCatch` vacío con comentario "// logged to error tracking service" | Falsa observabilidad: errores de runtime se tragan silenciosamente, el comment es una mentira | Log real con `console.error('[ErrorBoundary]', error.message, { stack, componentStack, timestamp })`. Ver `references/supabase-auth-config-and-observability.md` |
| `error.message.includes('cedula')` para matchear error de trigger DB | Frágil: depende de que el texto del `RAISE EXCEPTION` en PostgreSQL contenga exactamente esa palabra. Si el trigger dice `'Ya existe un contacto'` (sin "cédula"), el check falla y el usuario ve error genérico | Verificar el texto real del trigger con `SELECT prosrc FROM pg_proc p JOIN pg_trigger t ON t.tgfoid=p.oid WHERE tgname='trg_check_cedula'`. Usar un substring que SÍ aparezca en el mensaje del trigger. Considerar códigos de error estructurados (SQLSTATE custom) en vez de string matching. Ver `references/audit-db-verification.md` |
| Sesión persiste indefinidamente en browser abierto | Supabase Auth auto-refresca el JWT via `refresh_token`. Sin idle detection, un usuario puede volver horas después con sesión activa | AFK auto-logout con idle detection en AuthContext. Ver sección "AFK Auto-Logout" arriba |
| RLS policy en tabla X con subquery/JOIN a tabla X | Recursión infinita: `ERROR 42P17: infinite recursion detected in policy for relation "profiles"`. Login exitoso pero profile fetch falla → "Error cargando perfil de usuario". El ciclo puede ser indirecto (profiles → staff_leaders → profiles). SECURITY DEFINER NO lo resuelve | Cachear role + profile_id en `auth.users.raw_app_meta_data` (sin RLS). Funciones helper leen de ahí. Reescribir TODAS las policies que referencian la misma tabla. Ver `references/rls-infinite-recursion.md` para debugging path completo y fix pattern verificado |
| Geo tables con RLS policy `qual = true` | Cualquiera (sin auth) puede leer datos potencialmente sensibles | Policy `USING (auth.uid() IS NOT NULL)` — requiere autenticación. Datos departamentales son públicos pero barrios/puestos pueden ser sensibles en contexto electoral |
| Sin CAPTCHA en login — bots pueden brute forcear | Supabase Auth rate limiting nativo (30 burst / 1800/hr por IP) es permisivo para brute force dirigido | Cloudflare Turnstile (invisible, gratis) via `@marsidev/react-turnstile`. Pasar `captchaToken` en `options` de `signInWithPassword`. Ver sección "Brute Force Protection" arriba |
| Construir Edge Function custom para rate limiting de login | Over-engineering — Supabase Auth ya tiene token bucket rate limiting nativo por IP en `/auth/v1/token` | Usar CAPTCHA (Turnstile) + Leaked Password Protection (Pro Plan) desde Dashboard. No necesita código server-side |

## Debugging: Login Silencioso

Cuando el form de login no redirige y no hay errores en consola:

1. **AUTH_DOMAIN mismatch**: El código construye el email como `username@AUTH_DOMAIN`. Si AUTH_DOMAIN no coincide con el dominio del email en `auth.users`, Supabase Auth rechaza sin error visible en la UI. Leer el valor real de `AUTH_DOMAIN` en el código (suele estar como constante en AuthContext.tsx).
2. **Network tab**: Abrir DevTools → Network → filtrar por `auth/v1/token`. Si la respuesta es 400/401, el problema es credenciales o email incorrecto. Si es 200 pero la app no navega, el problema es el redirect/profile fetch.
3. **`email_confirmed_at` NULL**: Si el usuario fue creado via SQL y `email_confirmed_at` no se seteó, Supabase puede rechazar el login (dependiendo de config del proyecto).
4. **RLS bloquea profile SELECT**: Tras auth exitosa, `loadProfile()` hace SELECT a `profiles`. Si RLS no tiene una policy que permita al usuario leer su propio profile, el fetch devuelve vacío/error y la app puede quedarse en estado de loading o volver al login.
5. **Error tragado / return value ignorado**: `signInWithPassword` NO lanza excepción en credenciales inválidas — retorna `{ error }`. Si el caller solo usa `try/catch` sin leer el return value, el error se ignora silenciosamente. Ver sección "Auth: errores de retorno vs excepción" arriba. Agregar `console.error` temporal para ver el objeto error real de `signInWithPassword`.
6. **GoTrue NULL string scan (HTTP 500)**: Si el usuario fue creado via SQL directo y GoTrue devuelve `"Database error querying schema"` (500), la causa raíz es que columnas string como `confirmation_token` quedaron NULL. GoTrue las escanea como `string` no-nullable y crashea. Fix: `UPDATE auth.users SET confirmation_token = COALESCE(confirmation_token, ''), ...` para todas las columnas string. Ver `references/supabase-user-creation-via-sql.md` sección "Pitfalls criticos". **Para ver el error real**: `mcp_supabase_get_logs(service='auth')` y buscar el campo `error`.
7. **bcrypt cost factor incorrecto**: `gen_salt('bf')` sin argumento usa cost 6. GoTrue espera cost 10 (`$2a$10$`). Si el hash prefix es `$2a$06$`, regenerar con `gen_salt('bf', 10)`.
8. **auth.identities vacío**: GoTrue requiere un registro en `auth.identities` por usuario. El signup oficial lo crea automáticamente; un INSERT SQL directo NO. Sin este registro el login falla.
9. **@ prefix en username**: La UI muestra usernames como `@test.lider`. Si el usuario escribe o copia el username con `@`, `signIn()` construye `@test.lider@dominio.local` — email inválido, auth falla con "Invalid login credentials" (que parece indicar credenciales equivocadas, no un problema de formato). Fix: strippear `@` prefix en `signIn()` con `username.replace(/^@+/, '').trim().toLowerCase()`.
10. **RLS infinite recursion**: Login exitoso pero profile fetch falla → "Error cargando perfil de usuario" o loading perpetuo. La causa: policies de `profiles` llaman a `get_user_role()` que consulta `profiles` (o indirectamente via `contacts`/`staff_leaders`). Postgres detecta el ciclo y bloquea. Diagnosticar con `SET LOCAL role authenticated` + query a profiles → error `42P17`. Ver `references/rls-infinite-recursion.md`.

## Migrar emails de auth.users (ej: rename de dominio)

Cuando se cambia el dominio de auth (ej: rebrand de `@viejo.local` a `@nuevo.local`), hay que actualizar DOS tablas. Si solo se actualiza `auth.users`, GoTrue puede no encontrar el usuario al hacer login porque usa `auth.identities.identity_data` para lookup:

```sql
-- 1. auth.users: campo email directo
UPDATE auth.users 
SET email = REPLACE(email, '@viejo.local', '@nuevo.local')
WHERE email LIKE '%@viejo.local';

-- 2. auth.identities: email embebido en JSONB identity_data
UPDATE auth.identities 
SET identity_data = jsonb_set(
  identity_data, '{email}', 
  to_jsonb(REPLACE(identity_data->>'email', '@viejo.local', '@nuevo.local'))
)
WHERE identity_data->>'email' LIKE '%@viejo.local';
```

**Verificar post-migración:** contar registros antes/después, y hacer un login real con el email nuevo para confirmar que GoTrue resuelve correctamente.

## Security Hardening de Forms

**Input validation en el cliente (defense-in-depth):** RLS y Edge Functions protegen el backend, pero los inputs del frontend deben tener `maxLength` en TODOS los campos de texto. Sin esto, un usuario puede pegar 1000+ caracteres que el backend puede aceptar (Supabase TEXT no tiene límite por defecto), causando UI rota o abusos.

**Valores recomendados por tipo de campo:**

| Campo | maxLength |
|-------|-----------|
| Nombre completo / Nombres / Apellidos | 200 |
| Primer/Segundo nombre o apellido individual | 100 |
| Documento de identidad | 20 |
| Teléfono / Celular | 20 |
| Código geográfico (DANE) | 10 |
| Nombre geográfico (depto/municipio/puesto) | 100 |
| Dirección | 200 |
| Contraseña | 128 |

**Verificar que todos los inputs tienen maxLength (via browser console):**
```js
JSON.stringify(Array.from(document.querySelectorAll('input')).map(i => i.placeholder + ' [maxLength=' + i.maxLength + ']'))
```
maxLength=-1 significa SIN límite (default HTML). Revisar todos los inputs con -1 que acepten texto libre del usuario.

**CSP + headers de seguridad:** Ver `cloudflare-pages-deploy` skill → sección "Security Headers" + `templates/_headers-supabase`. El CSP necesita `connect-src 'self' https://<project-ref>.supabase.co` o las llamadas API quedan bloqueadas.

## Verification Checklist

- [ ] `npx tsc -b` sin errores
- [ ] `npm run build` pasa
- [ ] `.env` tiene placeholders (NO credenciales reales en repo)
- [ ] `.env.example` existe con keys correctas
- [ ] RLS activada en TODAS las tablas con datos sensibles
- [ ] Cero llamadas `auth.admin.*` desde código frontend
- [ ] Trigger de profile creation existe en schema
- [ ] Storage bucket creado con policies correctas
- [ ] Login end-to-end funcional (credenciales validas redirigen al dashboard)
- [ ] `AUTH_DOMAIN` en codigo coincide con dominio de emails en `auth.users`
- [ ] `npm test` pasa con al menos tests de logica critica (ver `references/vitest-testing-library-setup.md` para setup)
- [ ] Todos los inputs de texto tienen `maxLength` (verificar con browser console)
- [ ] `public/_headers` con CSP + security headers (ver `cloudflare-pages-deploy` skill)
- [ ] CAPTCHA activado en login si la app maneja datos sensibles (ver `references/cloudflare-turnstile-captcha.md`)

---

## React Feedback UI Patterns

Subsumed from `react-feedback-ui-patterns`. Covers toasts, error boundaries, loading states, and confirmations for React+Vite+Tailwind apps. Implements the patterns that `judge-ux-vibe-check` demands.

### When to apply
- Judge bundle reports "sin feedback visual", "sin error boundaries", "sin loading states"
- User requests toasts, notifications, or action feedback
- App crashes without showing anything to the user (missing error boundary)
- Buttons stuck without progress indication

### Architecture

```
App.tsx
├── ErrorBoundary          ← catches React crashes
│   └── ToastProvider      ← global notification context
│       ├── AuthProvider
│       │   └── Routes
│       └── ToastContainer ← renders toasts (fixed position)
```

### Required components

**1. Error Boundary (class component)**
- Wrap entire app in App.tsx as first child
- Show fallback UI with "Retry" + "Go to home"
- `componentDidCatch` logs to console.error (not Sentry in dev)

**2. Toast System (context + hook)**
- Three types: `success` (green), `error` (red), `info` (blue)
- Auto-dismiss configurable (default 4s)
- Hook `useToast()` → `{ showToast, toasts, removeToast }`

**3. Loading spinners on buttons**
```tsx
<button disabled={saving} className="inline-flex items-center gap-2 ...">
  {saving && (
    <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  )}
  {saving ? 'Guardando...' : 'Crear'}
</button>
```

**4. Delete confirmation pattern (deletingId state)**
```tsx
const [deletingId, setDeletingId] = useState<string | null>(null)

async function handleDelete(id: string) {
  if (!confirm('¿Eliminar?')) return
  setDeletingId(id)
  try {
    // ... delete logic
    showToast('Eliminado', 'success')
  } catch (err) {
    showToast(err.message, 'error')
  } finally {
    setDeletingId(null)
  }
}
```

### Migration: setError → Toast

1. Add `useToast` import
2. Replace `const [error, setError] = useState<string | null>(null)` with `const { showToast } = useToast()`
3. Replace `setError(msg)` with `showToast(msg, 'error')`
4. Remove `{error && (<div>...</div>})` block
5. For success: `showToast('Operación exitosa', 'success')`

**Script**: `scripts/migrate-to-toast.py` — bulk migration for regex patterns.

### Pitfalls

- **Toast z-index MUST be the highest in the entire app.** Typical: header `z-50` < modal `z-500` < loading `z-999` < **toast `z-[10000]`**. If toast has z-50, modals hide it.
- **ToastProvider must wrap AuthProvider**, not the reverse.
- **ErrorBoundary does NOT catch**: event handler errors, async/code errors, errors in the ErrorBoundary itself.
- **Don't use `position: fixed` on toast container if parent uses transform** — use portal or place outside Layout.
- **Auto-dismiss**: 4s default. For severe errors, consider 8s or no auto-dismiss.
- **Multiple toasts**: Array grows without limit. Consider max 5 visible with auto-dismiss of oldest.

### Reference
- `references/react-feedback-ui-judge-fix.md` — full judge fix workflow

---

## React UI Migration

Subsumed from `react-ui-migration`. Covers extracting design tokens from a reference project and applying them to a React+Tailwind app.

### Principle: Extract, don't copy
Don't copy CSS from the old project. Extract **design tokens** (colors, typography, spacing, components) and reimplement with the target framework.

### Workflow

**1. Analyze reference project** — Read CSS, HTML, identify tokens (palette, fonts, border-radius, shadows, components, animations, responsive breakpoints).

**2. Configure design system** — Tailwind v4 (NO v3):
```css
/* index.css */
@import "tailwindcss";

@theme {
  --color-primary-500: #1a9696;
  --color-primary-600: #0d6666;
  --font-sans: 'Sora', system-ui, sans-serif;
  --radius-md: 12px;
  --shadow-md: 0 4px 24px rgba(26, 122, 122, 0.12);
}
```

**PITFALL**: Tailwind v4 does NOT use `tailwind.config.js`. Everything goes in `@theme {}` inside CSS.

**3. Create CSS utility classes** — `.card`, `.avatar`, `.badge`, `.form-input`, `.modal-overlay`, `.empty-state`

**4. Migrate components** in order: Layout → Login → Dashboard → CRUD components → Auxiliaries (modals, forms)

**5. Bulk migration with Python** for repetitive changes (setError → showToast, gray-* → navy-*)

**6. Verification**: `npm run build` + `npm test -- --run` + browser check

### Migration order (dependency-driven)
1. Layout (topbar/sidebar)
2. Login (entry page)
3. Dashboard (shows design system)
4. CRUD components
5. Auxiliary components

### Reference
- `references/ui-migration-design-tokens.md` — extracted design tokens from Novva project
