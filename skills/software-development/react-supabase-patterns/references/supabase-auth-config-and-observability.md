# Supabase Auth Config Limitations + Observability

## Auth config NO es accesible via SQL ni MCP

La configuración de Supabase Auth (GoTrue) **vive fuera de Postgres**. No existe tabla queryable:

```sql
-- Esto retorna EMPTY — no hay tablas de config en schema auth
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'auth' AND table_name LIKE '%config%';
-- Resultado: []
```

### Settings que requieren Dashboard o Management API

| Setting | Dónde | Notas |
|---------|-------|-------|
| Leaked Password Protection | Dashboard → Auth → Providers → Email | **Requiere Pro Plan+**. No disponible en Free tier |
| Password minimum length | Dashboard → Auth → Providers → Email | |
| Password required characters | Dashboard → Auth → Providers → Email | |
| Email confirmation | Dashboard → Auth → Settings | |
| MFA | Dashboard → Auth → MFA | |
| OTP expiry | Dashboard → Auth → Settings | |

### Management API (no expuesto via MCP)

La Management API de Supabase (`api.supabase.com/v1/projects/{ref}/config/auth`) puede modificar estos settings vía PATCH, pero requiere `SUPABASE_ACCESS_TOKEN` (no el service_role key). El MCP server de Supabase NO expone este endpoint.

**Conclusión:** Si necesitas cambiar auth config, es acción manual en el Dashboard. No pierdas tiempo buscando la tabla SQL.

## Health Check Edge Function (observabilidad)

Patrón verificado para monitoreo de uptime/salud. Edge Function pública (`verify_jwt: false`) que retorna JSON sin datos sensibles.

```typescript
// supabase/functions/health-check/index.ts
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

Deno.serve(async () => {
  const timestamp = new Date().toISOString();

  return new Response(
    JSON.stringify({
      status: "healthy",
      service: "app-name",
      version: "0.1.0",
      timestamp,
    }),
    {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "no-store",
      },
    }
  );
});
```

**Deploy:**
```
mcp_supabase_deploy_edge_function(
  name="health-check",
  verify_jwt=false,  // público por diseño
  ...
)
```

**URL:** `https://{project_ref}.supabase.co/functions/v1/health-check`

**Por qué `verify_jwt: false`:** Es un endpoint de salud — no accede a datos, no requiere auth. Cualquier monitor (UptimeRobot, Cloudflare Workers, cron) puede hacer GET sin token.

**Por qué `Cache-Control: no-store`:** Evita que CDN/cachees sirvan un status stale cuando el servicio acaba de caer.

**Seguridad:** No incluye datos sensibles (sin user info, sin DB internals, sin secrets). Solo status + timestamp. Seguro de exponer públicamente.

## ErrorBoundary: logging real vs no-op

Un ErrorBoundary con `componentDidCatch` vacío es una falsa promesa de observabilidad. El comentario `// logged to error tracking service` sin código real significa que los errores crashean silenciosamente en producción.

**Patrón correcto (sin Sentry, mínimo viable):**

```tsx
componentDidCatch(error: Error, errorInfo: ErrorInfo) {
  console.error('[ErrorBoundary]', error.message, {
    stack: error.stack,
    componentStack: errorInfo.componentStack,
    timestamp: new Date().toISOString(),
  })
}
```

Cuando se integre Sentry/u otro error tracking, reemplazar el `console.error` con `Sentry.captureException(error, { extra: { componentStack: errorInfo.componentStack } })`.
