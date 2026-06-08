# Edge Function CORS — Diagnóstico y Fix

## Problema

Supabase Edge Functions NO incluyen headers CORS por defecto. Cuando una app
deployada en un dominio distinto (ej. Cloudflare Pages) llama al Edge Function,
el navegador envía una petición OPTIONS preflight antes del POST real.

Sin handler de OPTIONS, el Edge Function responde 405 (Method not allowed),
el navegador bloquea el POST, y el SDK reporta:

```
Failed to send a request to the Edge Function
```

## Síntomas en logs

```
OPTIONS | 405 | user-admin    ← CORS preflight RECHAZADO
```

El POST nunca llega a ejecutarse. No hay error 500 ni 401 — el navegador
bloquea la petición a nivel de preflight.

## Fix

### 1. Allowlist dinámica de orígenes (recomendado sobre `*`)

`Access-Control-Allow-Origin: *` permite cualquier origen. Aunque la función
requiera auth, endurecer el CORS con allowlist es defensa en profundencia:
si se añade un endpoint público, no queda expuesto a cualquier dominio.

```typescript
const ALLOWED_ORIGINS = [
  "https://<app-domain>.pages.dev",
  "http://localhost:5173",
];

function getAllowedOrigin(req: Request): string | null {
  const origin = req.headers.get("Origin");
  if (!origin) return null;
  if (ALLOWED_ORIGINS.includes(origin)) return origin;
  // Cloudflare Pages preview deployments: <hash>.<app-domain>.pages.dev
  if (origin.endsWith(".<app-domain>.pages.dev")) return origin;
  return null;
}
```

Patrón wildcard `endsWith` para previews de Cloudflare Pages: los deploys
preview generan URLs como `https://a1b2c3d4.mi-app.pages.dev` que cambian
en cada deploy. Verificar el sufijo permite todos los previews sin hardcodear.

### 2. Handler de OPTIONS preflight + CORS en todas las respuestas

```typescript
Deno.serve(async (req: Request) => {
  const origin = getAllowedOrigin(req);
  const corsHeaders: Record<string, string> = origin
    ? {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
      }
    : {};

  function json(data: unknown, status = 200) {
    return new Response(JSON.stringify(data), {
      status,
      headers: {
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        ...corsHeaders,
      },
    });
  }

  // CORS preflight — reject unknown origins
  if (req.method === "OPTIONS") {
    if (!origin) return new Response(null, { status: 403 });
    return new Response(null, { status: 204, headers: corsHeaders });
  }
  // ... resto del código
});
```

**Nota:** `corsHeaders` y `json()` se definen DENTRO de `Deno.serve` para
acceder al `origin` calculado por request. Si se definen fuera, el origin
sería estático.

### 3. Verificación post-deploy — 4 escenarios

```bash
FN_URL="https://<project>.supabase.co/functions/v1/<name>"

# 1. Origin permitido → 204 + CORS headers
curl -s -o /dev/null -w "%{http_code}" -X OPTIONS "$FN_URL" \
  -H "Origin: https://<app-domain>.pages.dev" \
  -H "Access-Control-Request-Method: POST" -D -
# Esperado: 204 + access-control-allow-origin header

# 2. Origin NO permitido → 403
curl -s -o /dev/null -w "%{http_code}" -X OPTIONS "$FN_URL" \
  -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: POST"
# Esperado: 403

# 3. Sin Origin header → 403
curl -s -o /dev/null -w "%{http_code}" -X OPTIONS "$FN_URL" \
  -H "Access-Control-Request-Method: POST"
# Esperado: 403

# 4. Preview deployment wildcard → 204 + CORS headers
curl -s -o /dev/null -w "%{http_code}" -X OPTIONS "$FN_URL" \
  -H "Origin: https://<hash>.<app-domain>.pages.dev" \
  -H "Access-Control-Request-Method: POST" -D -
# Esperado: 204 + access-control-allow-origin header
```

Los 4 escenarios deben pasar. Si el origen no permitido devuelve 204 en vez
de 403, el allowlist no está funcionando.

## Orden de prioridad al diagnosticar

1. **OPTIONS → 405**: Falta handler de CORS preflight (este fix)
2. **OPTIONS → 204 pero POST → 401**: Sesión expirada o token inválido
3. **OPTIONS → 204 pero POST → 500**: Error interno — ver pitfall verify_jwt abajo, o agregar console.log en cada paso y revisar logs con `mcp_supabase_get_logs(service='edge-function')`

## Pitfall crítico: verify_jwt: true + auth interna = 500

Cuando un Edge Function hace su propia verificación de auth internamente
(`getUser()` + role check con service_role), `verify_jwt: true` en el
gateway causa **500 Internal Server Error** en el POST.

**Fix:** `verify_jwt: false`. La función ya verifica auth internamente.

```
verify_jwt: true  → POST 500 (gateway rechaza o interactúa mal)
verify_jwt: false → POST 200 (la función hace su propia auth check)
```

Al deployar vía MCP: `mcp_supabase_deploy_edge_function(verify_jwt=false)`.

`verify_jwt: true` NO afecta el preflight OPTIONS — Supabase deja pasar
OPTIONS sin validar JWT para que el CORS handshake funcione. El problema
es exclusivamente en el POST cuando hay auth duplicada (gateway + función).

## Pitfall: "Edge Function returned a non-2xx status code"

El SDK de Supabase JS envuelve errores non-2xx en `FunctionsHttpError`
con un mensaje genérico: `"Edge Function returned a non-2xx status code"`.

El mensaje real del error está en `.context` (el objeto Response original).
Sin extraerlo, el usuario ve un mensaje inútil.

**Fix:** helper `extractFnError()` que lee `.context.json()`:

```typescript
export async function extractFnError(error: unknown): Promise<string> {
  if (error && typeof error === 'object' && 'context' in error) {
    try {
      const body = await (error as { context: Response }).context.json()
      if (body?.error) return body.error
    } catch {
      // Body ya consumido o no es JSON
    }
  }
  if (error instanceof Error) return error.message
  return 'Error desconocido'
}
```

Uso en catch blocks:
```typescript
} catch (err) {
  showToast(await extractFnError(err), 'error')
}
```

**Regla:** TODOS los catch blocks que puedan recibir errores de Edge Functions
deben usar `extractFnError` en lugar de `err instanceof Error ? err.message : ...`.
