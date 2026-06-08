# CSP Third-Party Domain Mapping

Dominios requeridos en Content-Security-Policy para servicios comunes.
Usar como checklist al integrar un nuevo servicio — cada directiva debe listar el dominio explícitamente.

## Cloudflare Turnstile (CAPTCHA)

```
script-src:  https://challenges.cloudflare.com
frame-src:   https://challenges.cloudflare.com
connect-src: https://challenges.cloudflare.com
```

**Notas:**
- El widget renderiza un iframe invisible (managed mode) — `frame-src` es obligatorio.
- El script principal carga desde `challenges.cloudflare.com` — `script-src` es obligatorio.
- El widget hace llamadas de verificación — `connect-src` es obligatorio.
- **NO habilitar Pre-clearance** en la config del widget — solo aplica si el sitio está proxied por Cloudflare (orange cloud). En `*.pages.dev` no tiene efecto.

## Stripe.js (Payments)

```
script-src:  https://js.stripe.com
frame-src:   https://js.stripe.com https://hooks.stripe.com
connect-src: https://api.stripe.com
img-src:     https://*.stripe.com
```

## Google Analytics (GA4)

```
script-src:  https://www.googletagmanager.com https://www.google-analytics.com
connect-src: https://www.google-analytics.com https://region1.google-analytics.com
img-src:     https://www.google-analytics.com
```

## Google Fonts

```
style-src:   https://fonts.googleapis.com 'unsafe-inline'
font-src:    https://fonts.gstatic.com
```

**Nota:** `'unsafe-inline'` en `style-src` ya es necesario para Vite/Tailwind — Google Fonts CSS se carga vía `style-src`.

## hCaptcha (CAPTCHA alternativo)

```
script-src:  https://js.hcaptcha.com
frame-src:   https://hcaptcha.com
connect-src: https://api.hcaptcha.com
style-src:   https://hcaptcha.com
```

## Supabase (Auth + Data)

```
connect-src: https://<project-ref>.supabase.co
```

**Nota:** Supabase no requiere `script-src` ni `frame-src` — todo es vía SDK (fetch/WebSocket). Solo `connect-src`.

## Verificación post-deploy

```bash
# Verificar que los dominios nuevos están en la CSP live
curl -sI https://<proyecto>.pages.dev | grep -i content-security-policy
```

Si un dominio falta, el navegador bloquea el recurso silenciosamente (revisar Console tab → verás "Refused to load ... violates CSP directive").
