# Cloudflare Turnstile CAPTCHA para Supabase Auth

Implementación verificada de CAPTCHA invisible en login de Supabase Auth usando Cloudflare Turnstile. Resuelve el issue de brute force protection sin Edge Functions custom.

## Por qué Turnstile y no hCaptcha

- **Turnstile** (Cloudflare): invisible, sin interacción del usuario, gratis. Recomendado para usuarios no técnicos (contexto electoral, apps de gobierno).
- **hCaptcha**: alternativa que Supabase también soporta, pero requiere interacción (seleccionar imágenes).

Supabase Auth soporta ambos nativamente via el parámetro `captchaToken` en las funciones de auth.

## Lo que Supabase Auth ya tiene (Free tier)

- **Rate limiting por IP**: token bucket en `/auth/v1/token` — burst de 30, luego 1800 req/hora. Retorna HTTP 429 al exceder.
- **CAPTCHA toggle**: Dashboard → Authentication → Bot & Abuse Protection → Enable CAPTCHA.

**Lo que NO tiene en Free:**
- **Leaked Password Protection** (verifica contra HaveIBeenPwned): requiere Pro Plan ($25/mes). Dashboard → Authentication → Providers → Email → activar. Si estás en Free, la opción no aparece.

## Implementación (3 piezas + 4 pasos dashboard)

### Pieza 1: Instalación

```bash
npm install @marsidev/react-turnstile
```

Librería React wrapper para Cloudflare Turnstile. 0 dependencias, ~15KB.

### Pieza 2: AuthContext — signIn acepta captchaToken opcional

```tsx
// src/context/AuthContext.tsx

interface SignInResult {
  error: string | null
}

const signIn = useCallback(
  async (username: string, password: string, captchaToken?: string): Promise<SignInResult> => {
    const cleanUsername = username.replace(/^@+/, '').trim().toLowerCase()
    const email = `${cleanUsername}@${AUTH_DOMAIN}`

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
      // Pasar captchaToken solo si existe. Supabase lo valida contra
      // el proveedor configurado en Bot & Abuse Protection.
      options: captchaToken ? { captchaToken } : undefined,
    })

    if (error) return { error: error.message }
    return { error: null }
  },
  []
)
```

**Clave:** `captchaToken` es opcional. Si no se pasa, Supabase Auth funciona sin CAPTCHA (backward compatible). Si CAPTCHA está activado en el Dashboard pero no se pasa token, Supabase rechaza el login con error.

### Pieza 3: Login.tsx — widget + token state + button gating

```tsx
// src/routes/Login.tsx
import { Turnstile } from '@marsidev/react-turnstile'
import type { FormEvent } from 'react'

// Si no hay sitekey, el widget no renderiza y la app funciona sin CAPTCHA
const TURNSTILE_SITEKEY = import.meta.env.VITE_TURNSTILE_SITEKEY

export default function Login() {
  const [captchaToken, setCaptchaToken] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const { signIn } = useAuth()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const result = await signIn(username, password, captchaToken ?? undefined)
      if (result.error) {
        // Supabase retorna errores específicos cuando CAPTCHA falla:
        // - "captcha failed" (token inválido o expirado)
        // - "Invalid login credentials" (credenciales)
        if (result.error.toLowerCase().includes('captcha')) {
          setError('Verificación de seguridad falló. Recarga la página e intenta de nuevo.')
        } else {
          setError('Usuario o contraseña incorrectos')
        }
        setCaptchaToken(null) // forzar re-verificación del widget
        return
      }
      navigate('/')
    } catch {
      setError('Error al iniciar sesión')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* ... campos de username/password ... */}

      {TURNSTILE_SITEKEY && (
        <Turnstile
          siteKey={TURNSTILE_SITEKEY}
          onSuccess={(token) => setCaptchaToken(token)}
          onExpire={() => setCaptchaToken(null)}
          onError={() => setCaptchaToken(null)}
          options={{ theme: 'light', size: 'flexible' }}
        />
      )}

      <button
        type="submit"
        disabled={loading || (!!TURNSTILE_SITEKEY && !captchaToken)}
      >
        {loading ? 'Ingresando...' : 'Ingresar'}
      </button>
    </form>
  )
}
```

**Notas de diseño:**
- `size: 'flexible'` adapta el widget al ancho del contenedor (responsive).
- `onExpire` resetea el token — el token de Turnstile expira (~5 min). El usuario debe re-verificar.
- Tras un error de login, resetear `captchaToken` a null fuerza al usuario a re-verificar el widget (seguridad: previene reintentar con un token expirado o ya usado).
- `!!TURNSTILE_SITEKEY && !captchaToken` — el botón solo se bloquea si CAPTCHA está configurado Y no hay token. Si no hay sitekey, el botón funciona normal.

### .env.example

```bash
# Cloudflare Turnstile — obtener en dash.cloudflare.com → Turnstile → Add widget
VITE_TURNSTILE_SITEKEY=
```

### Pasos del Dashboard (manuales — no accesibles via MCP/SQL)

1. **Crear widget Turnstile en Cloudflare** (gratis):
   - dash.cloudflare.com → Turnstile → Add widget
   - Mode: **Managed** (Cloudflare decide cuándo mostrar challenge)
   - Hostname: `tu-app.pages.dev` (o dominio custom)
   - Copiar **SITEKEY** (va en `.env.local` y Cloudflare Pages env vars)
   - Copiar **SECRET KEY** (va en Supabase)

2. **Activar CAPTCHA en Supabase**:
   - Dashboard → Authentication → Bot & Abuse Protection
   - Enable CAPTCHA → **ON**
   - Provider: **Cloudflare Turnstile**
   - Pegar SECRET KEY
   - Save

3. **Configurar env vars** (2 lugares):
   - Local: `.env.local` con `VITE_TURNSTILE_SITEKEY=tu-sitekey`
   - Cloudflare Pages → Settings → Environment Variables: misma key y valor
   - Re-deployar tras configurar (las env vars se leen en build time)

4. **Leaked Password Protection** (opcional, requiere Pro Plan):
   - Dashboard → Authentication → Providers → Email
   - Activar toggle
   - Si estás en Free Plan, la opción **no aparece** — no es un bug

## Verificación

Después de configurar todo:

1. **Sin CAPTCHA activo** (sitekey vacío): login funciona normal, widget no aparece.
2. **CAPTCHA activo** (sitekey configurado): widget aparece, botón disabled hasta verificar, login funciona.
3. **CAPTCHA activo pero Supabase Dashboard NO activado**: login falla con "captcha failed" (Supabase recibe token pero no está configurado para validarlo).
4. **Token expirado**: tras ~5 min sin interactuar, el login falla — el usuario debe recargar para re-verificar.

## Gotchas

- **Turnstile en localhost**: funciona con mode Managed (Cloudflare detecta localhost). Si hay issues, agregar `127.0.0.1` como hostname en el widget.
- **CSP**: Turnstile carga scripts de `challenges.cloudflare.com`. El CSP necesita `script-src 'self' https://challenges.cloudflare.com`. Si tienes CSP estricto y no agregas este dominio, el widget no renderiza (error silencioso).
- **No requiere Pro Plan**: Turnstile widget en Cloudflare es gratis. Leaked Password Protection en Supabase sí requiere Pro Plan.
- **Backup de sitekey/secret**: el secret key solo se muestra una vez en Cloudflare. Si se pierde, hay que crear un widget nuevo.
