---
name: cloudflare-pages-deploy
description: "Deploy de apps frontend (React, Vue, Svelte, etc.) a Cloudflare Pages con wrangler CLI. Incluye setup, secrets, SPA routing, security headers (_headers file), y verificación. Use when: 'deploy a Cloudflare', 'deploy a Pages', 'cloudflare deploy', production deploy de SPA."
tags: [deploy, cloudflare, pages, production, hosting]
---

# Deploy a Cloudflare Pages

## Prerrequisitos

- Node.js instalado
- Cuenta de Cloudflare (https://dash.cloudflare.com/sign-up)

## Workflow Completo

### 1. Instalar wrangler (si no está)

```bash
npm install -g wrangler
```

### 2. Autenticar

```bash
wrangler login
# Abre browser para OAuth — acepta los permisos
wrangler whoami  # Verificar autenticación
```

### 3. Crear proyecto

```bash
wrangler pages project create <nombre-proyecto> --production-branch main
```

El URL será: `https://<nombre-proyecto>.pages.dev`

### 4. Configurar env vars del build

Hay DOS tipos de env vars en Cloudflare Pages — son mutuamente exclusivas:

| Tipo | Comando | Cuándo se inyecta | Visible en bundle |
|------|---------|-------------------|-------------------|
| **Build-time** (Dashboard) | Cloudflare Dashboard → Settings → Environment variables | Durante `npm run build` | Sí, embebida en JS |
| **Runtime secret** (CLI) | `wrangler pages secret put KEY` | En el worker, post-build | No, solo server-side |

**Para `VITE_*` vars → SIEMPRE Build-time (Dashboard).** Vite reemplaza `import.meta.env.VITE_*` en compile time. Si no están disponibles durante el build, quedan como `undefined` y la app crasha.

```bash
# Runtime secret (NO sirve para VITE_* en builds automáticos)
wrangler pages secret put VITE_SUPABASE_URL --project-name <nombre>
# Esto pone el valor en el worker, pero NO se inyecta durante el build de Cloudflare Pages CI
```

**El anon key de Supabase queda visible en el JS bundle** — esto es correcto y esperado para SPAs (el anon key está diseñado para ser público, RLS protege los datos).

### 5. Build + Deploy

```bash
npm run build
wrangler pages deploy dist --project-name <nombre-proyecto> --commit-dirty=true
```

### 6. Verificar

**Verificación mínima (HTTP + contenido del bundle):**

```bash
# 6a. HTTP status
curl -s -o /dev/null -w "%{http_code}" https://<nombre-proyecto>.pages.dev
# Debe retornar 200

# 6b. ¿Las env vars se embebieron en el bundle? (CRÍTICO)
# Reemplazar <project-ref> con el ref real (ej: stvdqrfpzmzhkyfxgmgh)
BUNDLE=$(curl -s https://<nombre-proyecto>.pages.dev/ | grep -oP 'assets/index-[A-Za-z0-9_-]+\.js' | head -1)
curl -s "https://<nombre-proyecto>.pages.dev/$BUNDLE" | grep -c '<project-ref>'
# Debe retornar >=1. Si retorna 0 → las env vars NO se embebieron → blank page.
```

**Verificación real (abrir en browser):**
Si tenés acceso a browser tools, navegar a la URL y confirmar que React monta. HTTP 200 NO es suficiente — una blank page también retorna 200. Para diagnóstico completo ver [references/diagnostic-blank-page.md](references/diagnostic-blank-page.md).

## SPA Routing (CRÍTICO)

Apps SPA con React Router necesitan configuración especial. Sin esto, rutas como `/lideres` retornan 404 en Cloudflare Pages.

**Opción A**: Crear `dist/_redirects` (en el build output):
```
/*  /index.html  200
```

**Opción B**: Crear `_redirects` en `public/` (se copia a dist en build):
```
/*  /index.html  200
```

**Opción C**: Usar `_headers` + `_redirects` juntos:
```
# public/_redirects
/*  /index.html  200

# public/_headers
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
```

## Security Headers (Recomendado)

Crear `public/_headers` (Vite lo copia a `dist/` automáticamente en el build). Cloudflare Pages lo lee en deploy y sirve los headers en cada response.

**Mínimo recomendado (4 headers básicos):**
```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
```

**Con Content-Security-Policy (recomendado para producción):**

CSP es el header de seguridad más importante — bloquea XSS, data exfiltration, y mixed content por defecto. Para apps React+Supabase, el CSP debe permitir explícitamente el dominio de Supabase en `connect-src`, fuentes externas en `font-src`, y estilos inline en `style-src` (Vite/Tailwind inyecta styles inline).

Ver template completo en [templates/\_headers-supabase](./templates/_headers-supabase) — listo para copiar y modificar.

**Pitfalls CSP comunes:**
- `connect-src` sin el URL de Supabase → todas las llamadas API bloqueadas (app no carga datos). Siempre incluir `https://<project-ref>.supabase.co`
- `style-src` sin `'unsafe-inline'` → Tailwind/Vite injected styles bloqueados, app se renderiza sin estilos
- `font-src` sin Google Fonts → iconos/texto se rompen si usas Google Fonts
- CSP demasiado restrictiva en desarrollo (localhost) — para dev, añadir `http://localhost:*` en `connect-src`
- **Integrar widgets de terceros sin actualizar CSP** → el script se bloquea silenciosamente, el widget no renderiza. Cada servicio requiere dominios en directivas específicas: `script-src` (carga del JS), `frame-src` (si embebe un iframe), `connect-src` (si hace XHR/fetch). Ej: Turnstile necesita `challenges.cloudflare.com` en las tres. Ver [references/csp-third-party-domains.md](references/csp-third-party-domains.md) para el mapeo completo de servicios comunes. **Siempre verificar con `curl -sI` post-deploy que los nuevos dominios aparecen en la CSP live.**

**Verificar headers en producción después del deploy:**
```python
import requests
r = requests.get("https://<proyecto>.pages.dev/")
for h in ['content-security-policy', 'x-frame-options', 'x-content-type-options', 'referrer-policy', 'permissions-policy']:
    print(f"{h}: {'OK' if r.headers.get(h) else 'MISSING'}")
```
Si algún header sale MISSING, verificar que `dist/_headers` existe tras el build (`cat dist/_headers`) y que el deploy subió ese archivo.

## Deploy Automático con GitHub

### Antes de automatizar: ¿realmente necesitas CI/CD?

**Para proyectos pre-lanzamiento o con pocos usuarios, el deploy manual de un comando es la opción correcta — no es un workaround.**

```bash
npm run build && npx wrangler pages deploy dist --project-name <nombre>
```

No configures GitHub Actions, no crees API tokens, no agregues complejidad. Un comando y listo. Automatizar deploy cuando hay 2 usuarios de prueba es sobreingeniería.

**Cuándo SÍ automatizar (indicadores reales):**
- Múltiples desarrolladores haciendo push a main
- Deploy frequency > 1-2 por semana
- Necesitas preview deployments por branch
- El proyecto está en producción con usuarios reales

Si ninguno de estos aplica, el comando manual es suficiente. El usuario te lo dirá (o lo pedirá) cuando necesite auto-deploy.

### ⚠️ Limitación crítica: direct-upload ≠ Git-connected

Cloudflare Pages tiene dos tipos de proyecto MUTUAMENTE EXCLUSIVOS:
- **Git-connected**: creado desde el dashboard conectando un repo. Auto-deploy en cada push.
- **Direct-upload**: creado con `wrangler pages project create`. Deploy manual con wrangler.

**NO se pueden convertir entre sí.** Un proyecto direct-upload NO puede conectarse a Git después. Un proyecto Git-connected no acepta deploys de wrangler. Si creaste el proyecto con wrangler y quieres auto-deploy, tienes dos opciones:

### Opción A: GitHub Actions + wrangler (sin borrar nada)

Crear `.github/workflows/deploy.yml` en el repo. Usa `cloudflare/wrangler-action@v3` para deployar en cada push a main. Requiere un Cloudflare API Token (no OAuth):

```yaml
name: Deploy to Cloudflare Pages
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      deployments: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
        env:
          VITE_SUPABASE_URL: ${{ secrets.VITE_SUPABASE_URL }}
          VITE_SUPABASE_ANON_KEY: ${{ secrets.VITE_SUPABASE_ANON_KEY }}
      - uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: pages deploy dist --project-name=<nombre-proyecto>
```

GitHub Secrets necesarios (repo → Settings → Secrets and variables → Actions):
- `CLOUDFLARE_API_TOKEN`: crear en https://dash.cloudflare.com/profile/api-tokens → "Edit Cloudflare Workers" template, o custom con `Cloudflare Pages:Edit` permission
- `CLOUDFLARE_ACCOUNT_ID`: visible en el dashboard de Cloudflare (cualquier página del proyecto)
- Todas las `VITE_*` vars que el build necesite

Ver template completo en [templates/github-actions-deploy.yml](./templates/github-actions-deploy.yml).

### Opción B: Borrar y recrear conectado a Git

Si prefieres la integración nativa de Cloudflare:
1. Borrar proyecto actual: `wrangler pages project delete <nombre-proyecto>`
2. Ir a Cloudflare Dashboard → Workers & Pages → Create application → Pages → Connect to Git
3. Seleccionar repo y branch
4. Build command: `npm run build`, output: `dist`
5. Configurar env vars en Settings → Environment variables
6. Deploy

**Consecuencia**: si hay custom domain conectado, desvincularlo primero del proyecto viejo y revincularlo al nuevo.

## Pitfalls

### Proyectos Pages NO se pueden renombrar
Cloudflare Pages no permite cambiar el nombre de un proyecto existente. Para renombrar (ej: rebrand de la app):
1. Crear proyecto nuevo: `wrangler pages project create <nuevo-nombre> --production-branch main`
2. Deploy al nuevo proyecto: `wrangler pages deploy dist --project-name <nuevo-nombre>`
3. Verificar: `curl -s -o /dev/null -w "%{http_code}" https://<nuevo-nombre>.pages.dev` → 200
4. Eliminar proyecto viejo: `wrangler pages project delete <viejo-nombre>`
5. Actualizar CORS allowlist en Edge Functions/backend para apuntar solo a la URL nueva

### Metadata de GitHub repo (separada del contenido)
Al renombrar/rebrandear un proyecto, `gh repo edit` actualiza metadata que NO vive en los archivos del repo:
```bash
gh repo edit <owner>/<repo> --description "Nueva descripción"
gh repo edit <owner>/<repo> --homepage "https://nuevo-nombre.pages.dev"
```
El find/replace del código NO toca esta metadata — es un paso aparte que se escapa fácil. Verificar con `gh repo view --json description,homepageUrl`.

**Estrategia de transición CORS (2 fases):** Si hay Edge Functions con CORS allowlist, NO eliminar el proyecto viejo inmediatamente. Primero deployar la función con AMBAS URLs (vieja+nueva) en el allowlist. Luego eliminar el proyecto viejo. Luego deployar de nuevo con solo la URL nueva. Esto evita downtime donde la app no puede llamar al backend.

**wrangler Pages NO se conecta a Git automáticamente.** Un proyecto creado con `wrangler pages project create` usa direct upload, NO auto-deploy en cada push. Para auto-deploy: conectar el repo desde Cloudflare Dashboard → Pages → Settings → Connect to Git. Si no se conecta, futuros deploys requieren `wrangler pages deploy dist --project-name <nombre>` manual.

### SPA 404 en rutas directas
Sin `_redirects`, navegar a `https://app.pages.dev/lideres` directamente da 404. Cloudflare Pages no sabe que React Router maneja las rutas. FIX: siempre crear `public/_redirects` con `/* /index.html 200`.

### Secrets no disponibles en build (distinción crítica)

`wrangler pages secret put` crea **runtime secrets** (disponibles en el worker, NO durante el build). Para `VITE_*` vars que Vite embebe en compile time, hay que usar **Build-time env vars** en el Dashboard de Cloudflare Pages (Settings → Environment variables).

La confusión es común: el nombre "secret" sugiere que es la forma segura de manejar credenciales, pero para Vite SPAs las credenciales necesitan estar en el build step. La excepción: GitHub Actions inyecta `${{ secrets.VITE_* }}` directamente en el paso de build — eso sí funciona porque el secret se pasa como env var del proceso de build.

### 🔴 Página en blanco tras deploy — env vars ausentes (2 variantes)

**Variante 1 — App lanza error explícito**: El repo tiene Git-connected auto-deploy. Hacés push → Cloudflare Pages builda automáticamente → el bundle se genera SIN las env vars → la app lanza `Error('Missing Supabase env vars...')` en runtime → React nunca monta → `#root` vacío → página en blanco.

**Variante 2 — App crasha silenciosamente (SIN error message)**: El build se hizo sin env vars pero la librería (ej: Supabase JS client) NO lanza error en initialization — solo falla al primer uso. `createClient(undefined, undefined)` no throw, el objeto se crea, pero cualquier query posterior falla. React monta el provider, el provider crashea al fetch profile, el ErrorBoundary (si existe) captura o no, el resultado es `#root` vacío. La consola del browser muestra un JS error con message VACÍO (`""`, source: `"exception"`). **Este patrón es más difícil de diagnosticar porque no hay error visible.**

**Verificar** (diagnóstico rápido para ambas variantes, ver [references/diagnostic-blank-page.md](references/diagnostic-blank-page.md)):
```bash
# ¿La URL de Supabase está embebida en el bundle?
BUNDLE=$(curl -s https://<proyecto>.pages.dev/ | grep -oP 'assets/index-[A-Za-z0-9_-]+\.js' | head -1)
curl -s "https://<proyecto>.pages.dev/$BUNDLE" | grep -oP '<project-ref>\.supabase\.co'
# Vacío → las env vars no se inyectaron en el build
```

**FIX** (3 opciones, según el tipo de proyecto):

**Opción A — Convertir secrets a plain_text vía Cloudflare API (fix permanente para direct-upload):**
Si el proyecto fue creado con `wrangler` (direct-upload) y las env vars se setearon con `wrangler pages secret put`, son tipo `secret_text` (encrypted, runtime-only, NO disponibles en build time). Convertirlas a `plain_text` vía API:

```bash
# 1. Obtener account_id y OAuth token
wrangler whoami  # muestra account_id
# En Windows, el OAuth token está en: %APPDATA%/xdg.config/.wrangler/config/default.toml
# (busca oauth_token = "..." en la primera línea)

# 2. PATCH a la API de Cloudflare (reemplazar valores)
TOKEN="cfoat_..."  # del wrangler config
ACCOUNT="2273..."
curl -s -X PATCH "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT/pages/projects/<nombre>" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"deployment_configs":{"production":{"env_vars":{
    "VITE_SUPABASE_URL":{"type":"plain_text","value":"https://<ref>.supabase.co"},
    "VITE_SUPABASE_ANON_KEY":{"type":"plain_text","value":"eyJ..."}
  }}}}'

# 3. Verificar que success: true y type cambió a plain_text
```

**Opción B — Configurar env vars en Dashboard (fix permanente para Git-connected):**
Cloudflare Dashboard → Pages → tu proyecto → Settings → Environment variables → agregar `VITE_SUPABASE_URL` y `VITE_SUPABASE_ANON_KEY` (Production + Preview) → redeployar.

**Opción C — Build local + deploy directo (fix inmediato):**
```bash
# 1. Crear .env con las credenciales
echo 'VITE_SUPABASE_URL=https://<project-ref>.supabase.co' > .env
echo 'VITE_SUPABASE_ANON_KEY=<anon-key>' >> .env

# 2. Build local (las vars se embeben en el bundle)
npm run build

# 3. Verificar que la URL está embebida
grep -oP '<project-ref>\.supabase\.co' dist/assets/index-*.js

# 4. Deploy directo
wrangler pages deploy dist --project-name <nombre> --commit-dirty=true
```

Opción C es el fix rápido cuando necesitás que funcione AHORA. Opción A o B es el fix permanente para que futuros deploys funcionen. **Hacé ambas** — C para arreglar hoy, A o B para que no vuelva a romper.

**Pitfall**: Cloudflare Pages NO hereda env vars de `.env` ni de `.env.local` ni de GitHub Secrets por defecto. Hay que configurarlas EXPLÍCITAMENTE. Las vars seteadas con `wrangler pages secret put` son `secret_text` (encrypted, runtime-only) — útiles para server-side secrets pero **NO para `VITE_*` build-time vars**.

### Wrangler config y OAuth token
En Windows, el OAuth token de wrangler está en `%APPDATA%/xdg.config/.wrangler/config/default.toml` (path MSYS: `/c/Users/<user>/AppData/Roaming/xdg.config/.wrangler/config/default.toml`). La primera línea contiene `oauth_token = "..."`. Este token se puede usar para llamadas a la Cloudflare API (`Authorization: Bearer <token>`) cuando wrangler CLI no cubre la operación — ej: convertir env vars de `secret_text` a `plain_text`. Preferir wrangler CLI cuando cubre la operación; usar el token directamente solo para lo que wrangler no expone.

**Nota**: El token expira. Si una llamada API retorna 401, el token caducó — re-autenticar con `wrangler login`.

### Escalar en vez de loopear
Si después de 2-3 intentos no encontrás el path del config, el token, o la API correcta → **preguntá al usuario**. Ir en loops con `find`, `grep`, `ls` en paths inventados pierde tiempo y contexto. El usuario tiene acceso directo al dashboard y puede darte lo que necesitás en segundos.

### SSL propagation delay
Después del primer deploy, SSL puede tardar 10-30 segundos en propagar. Si `curl` falla con SSL error, espera y reintenta.

### --commit-dirty=true
Si el repo tiene cambios sin commitear, wrangler rechaza el deploy. Usa `--commit-dirty=true` para forzar, o haz commit primero.

### Tráfico inesperado en Analytics (US, Ucrania, etc.)
Después del primer deploy, Cloudflare Analytics muestra requests de países donde NO estás (EE.UU., Ucrania, etc.). Esto es normal:
- **EE.UU.**: Bots de indexación, health checks de Cloudflare, herramientas de CI/CD que verifican el deploy
- **Países aleatorios**: Bots escaneando URLs públicas (cualquier URL pública recibe esto en los primeros minutos)
- **Tu país**: Tu tráfico real

No es un ataque. Para bloquear bots conocidos: Cloudflare Dashboard → Security → Bots → Bot Fight Mode.

## Costo

Cloudflare Pages free tier:
- 500 builds/mes
- 1 sitio custom domain
- Ancho de banda ilimitado
- Sin límite de requests

Para una app electoral como NOVA VALLE, el free tier es más que suficiente.
