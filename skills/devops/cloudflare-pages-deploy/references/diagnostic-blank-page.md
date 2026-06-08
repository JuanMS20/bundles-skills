# Diagnóstico: Página en blanco en Cloudflare Pages

## Quick check (30 segundos)

```bash
# 1. Obtener el nombre del bundle actual
BUNDLE=$(curl -s https://<proyecto>.pages.dev/ | grep -oP 'assets/index-[A-Za-z0-9_-]+\.js' | head -1)

# 2. ¿La URL de Supabase (o tu backend) está embebida en el bundle?
curl -s "https://<proyecto>.pages.dev/$BUNDLE" | grep -c '<project-ref>'
# 0 → las env vars NO se inyectaron en el build → ROOT CAUSE confirmado
# >=1 → las env vars SÍ están, el problema es otro (revisar consola del browser)
```

## Dos variantes del mismo problema

### Variante 1 — Error explícito
La app tiene un guard `if (!import.meta.env.VITE_SUPABASE_URL) throw new Error(...)`. El bundle contiene el string del error. En consola del browser se ve el error con message completo.

### Variante 2 — Crash silencioso (MÁS DIFÍCIL DE DETECTAR)
La librería cliente (ej: `@supabase/supabase-js`) NO valida sus argumentos al inicializar. `createClient(undefined, undefined)` retorna un objeto válido sin lanzar error. React monta el AuthProvider, el provider llama `supabase.auth.getSession()`, esa llamada falla internamente, el error no se propaga correctamente, React no monta nada.

**Síntomas en consola del navegador**:
- Un solo JS error con message VACÍO (`""`, source: `"exception"`)
- `document.getElementById('root').innerHTML` retorna `""` (string vacío)
- Los scripts cargan con 200 OK
- El HTML tiene `<div id="root"></div>` vacío
- NO hay error visible de "Missing env vars" ni nada accionable

**Este patrón es engañoso porque**: HTTP 200, headers correctos, scripts cargando, CSP correcta — todo se ve bien. Solo abriendo en browser real se detecta.

## Causa raíz

Los env vars `VITE_*` se configuraron como `secret_text` (vía `wrangler pages secret put`) en lugar de `plain_text`. Los secrets son encrypted y runtime-only — NO están disponibles durante el build de Vite. Vite los reemplaza con `undefined`.

Esto afecta tanto a proyectos Git-connected (auto-deploy desde GitHub) como a direct-upload (deploy manual con wrangler).

## Fix

Ver SKILL.md → "Página en blanco tras deploy" para las 3 opciones de fix (API, Dashboard, build local).

**Regla**: siempre verificar con el bundle grep (paso 2 del quick check) después de cualquier deploy donde `VITE_*` vars estén involucradas.

## Wrangler config location (Windows)

El OAuth token de wrangler está en:
```
C:\Users\<user>\AppData\Roaming\xdg.config\.wrangler\config\default.toml
```
MSYS path: `/c/Users/<user>/AppData/Roaming/xdg.config/.wrangler/config/default.toml`

Primera línea: `oauth_token = "cfoat_..."` — usar como Bearer token para llamadas directas a la Cloudflare API cuando wrangler CLI no cubre la operación.
