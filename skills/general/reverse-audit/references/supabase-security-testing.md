# Supabase Security Testing Patterns

Patrones verificados para auditar apps con stack Supabase (PostgREST + Auth + Edge Functions + RLS).

## Recon: Enumeración de schema via API errors

PostgREST filtra nombres de tabla reales en sus error responses. Sin auth, enviar
requests con nombres incorrectos enumera el schema:

```python
# Probar nombres de tabla → los errores revelan nombres reales
for name in ['users', 'profiles', 'user_profiles', 'contacts']:
    r = requests.get(f"{URL}/rest/v1/{name}", headers={"apikey": ANON_KEY})
    if 'Perhaps you meant' in r.text:
        # Extraer nombre real del hint
        print(r.json()['hint'])
```

Convención Supabase: snake_case plural (`profiles`, `contacts`, `audit_logs`).

## RLS Testing Matrix

Verificar que RLS bloquea correctamente para cada combinación rol × acción × tabla:

```python
# Por cada rol, testear: SELECT, INSERT, UPDATE, DELETE en cada tabla
roles = {'anon': None, 'lider': lider_token, 'admin': admin_token}
actions = ['GET', 'POST', 'PATCH', 'DELETE']
tables = ['profiles', 'contacts', 'audit_logs', 'staff_leaders']

for role, token in roles.items():
    for action in actions:
        for table in tables:
            headers = {"apikey": ANON_KEY}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            r = requests.request(action, f"{URL}/rest/v1/{table}", headers=headers, json={})
            # 401/403 = bloqueado (esperado para roles no autorizados)
            # 200 = accesible (verificar si debería serlo)
```

**Patrón clave:** PostgREST devuelve 200 con array vacío `[]` cuando RLS filtra
todas las filas (no error). Esto NO es un bypass — RLS funciona, solo que no hay
filas que el rol pueda ver.

**CRÍTICO:** PostgREST devuelve 204 en DELETE/UPDATE incluso con 0 filas afectadas
(RLS bloqueó). Verificar SIEMPRE en la DB que el dato sigue presente.

## Role Escalation Vectors (verificado en campo)

**Hallazgo CRITICAL (Nova Valle, jun 2026):** Sin RLS que proteja el campo `role`,
un admin puede escalar privilegios de cualquier usuario via PATCH directo:

```javascript
// Escalar test.staff de staff → admin
fetch('https://PROJECT.supabase.co/rest/v1/profiles?username=eq.test.staff', {
  method: 'PATCH',
  headers: {
    'apikey': ANON_KEY,
    'Authorization': 'Bearer ' + ADMIN_TOKEN,
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
  },
  body: JSON.stringify({role: 'admin'})
}).then(function(r) { return r.text(); });
// → 200 con el profile actualizado, role: "admin"
```

**Verificación:** Siempre leer el profile después del PATCH para confirmar que el role cambió:
```javascript
fetch('https://PROJECT.supabase.co/rest/v1/profiles?select=username,role&username=eq.test.staff', {
  headers: {'apikey': ANON_KEY, 'Authorization': 'Bearer ' + ADMIN_TOKEN}
}).then(function(r) { return r.text(); });
// → [{"username":"test.staff","role":"admin"}]
```

**Otro vector confirmado — Crear admin sin auth_id:**
```javascript
// POST directo crea profile admin sin usuario auth asociado
fetch('https://PROJECT.supabase.co/rest/v1/profiles', {
  method: 'POST',
  headers: {
    'apikey': ANON_KEY,
    'Authorization': 'Bearer ' + ADMIN_TOKEN,
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
  },
  body: JSON.stringify({username: 'hacker.test', nombre: 'Hacker', role: 'admin'})
});
// → 201 Created con auth_id: null (sin usuario auth, pero existe en tabla con role admin)
```

**Fix requerido:** RLS policy en tabla `profiles` que:
1. Bloquee UPDATE del campo `role` para todos excepto via RPC con verificación
2. Bloquee INSERT con `role = 'admin'` sin auth_id válido
3. Registre cambios de role en audit_logs con before/after

### Otros vectores a probar

1. **PATCH self-role:** Intentar cambiar propio role a admin
   `PATCH /rest/v1/profiles?id=eq.{own_id}` con `{"role": "admin"}`
   RLS debe bloquear (esperado: 200 con `[]` = 0 filas modificadas)

2. **UPSERT injection:** POST con mismo ID pero role diferente
   `POST /rest/v1/profiles` con `{"id": "{own_id}", "role": "admin"}`
   RLS debe bloquear

3. **DELETE cross-user:** DELETE intentando borrar a otro usuario
   RLS debe bloquear (devuelve 204 pero 0 filas afectadas)

## Edge Function Auth Bypass

```python
# 1. Sin auth header → debe dar 401
r = requests.post(f"{URL}/functions/v1/user-admin",
    headers={"apikey": ANON_KEY}, json={"action": "create-user", ...})
assert r.status_code == 401

# 2. Con token de rol inferior → debe dar 403
r = requests.post(f"{URL}/functions/v1/user-admin",
    headers={"apikey": ANON_KEY, "Authorization": f"Bearer {lider_token}"},
    json={"action": "create-user", "role": "admin", ...})
assert r.status_code == 403
```

## JS Bundle Secret Analysis

### Regex extraction (para bundles no-minificados)

```python
import re, base64

r = requests.get("https://app.pages.dev/assets/index-*.js")
js = r.text

# Buscar JWTs embebidos
jwts = re.findall(r'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}', js)
for jwt in jwts:
    payload = base64.b64decode(jwt.split('.')[1] + '==').decode()
    role = json.loads(payload).get('role')
    if role == 'service_role':
        print("CRITICAL: service_role key in JS bundle!")
    elif role == 'anon':
        print("OK: anon key (expected, public)")
```

### Vite minification: anon key truncada con "..."

**Patrón observado en apps Vite (verificado Nova Valle, jun 2026):** La `VITE_SUPABASE_ANON_KEY`
se embebe en el bundle como una concatenación de strings que Vite minifica con "..." en el medio:

```
stvdqrfpzmzhkyfxgmgh.supabase.co`,`eyJhbG...0X78
```

El regex anterior NO encuentra el JWT completo porque Vite lo rompe. El resultado es
un string truncado de ~127 chars (vs los ~200+ esperados para un JWT completo).

**Implicaciones para el audit:**
- La anon key NO se puede extraer del bundle estático con regex
- La key se construye en runtime (Vite concatena los fragmentos via module scope)
- `createClient(url, key)` se llama con la key completa en un closure ES module
- Desde el global scope (`window`), la key es inaccesible (closure del módulo)
- Monkey-patch de `fetch`/`XMLHttpRequest` NO funciona después de `navigate()` (el contexto JS se resetea)

**Estrategias alternativas para obtener la anon key:**
1. **Leer del repo local** si está clonado (`.env.local`, `.env.production`) — ojo: puede estar truncada también
2. **Interceptar en runtime** via Kimi `evaluate` ANTES de navigate — monkey-patch `fetch` y capturar el header `apikey` de requests salientes. Requiere que un navigate SPA (no reload) dispare el fetch ANTES de que el contexto se resetee
3. **Leer de Cloudflare Pages env vars** si tienes acceso al dashboard o via `wrangler`
4. **Usar `performance.getEntriesByType('resource')`** para ver URLs de requests pero NO los headers
5. **Probar la API sin key** — Supabase responde `{"message":"No API key found in request"}` confirmando que se necesita

**NOTA:** La anon key es pública por diseño (va en el cliente). Su ausencia en el bundle
no es una vulnerability — solo complica el testing automatizado. No reportar como hallazgo.

### Runtime key extraction via fetch monkey-patch (Kimi WebBridge)

**Técnica verificada (Nova Valle, jun 2026):** La forma más confiable de obtener la anon key
en apps Vite es interceptar el `apikey` header que el Supabase client envía en cada request.

```javascript
// 1. Monkey-patch fetch ANTES de que la app haga su próxima request
window.__capturedKeys = [];
var _f = window.fetch;
window.fetch = function(u, o) {
  try {
    if (typeof u === 'string' && u.indexOf('supabase') > -1) {
      var h = (o && o.headers) || {};
      var ak = h.apikey || h['apikey'] ||
               (typeof h.get === 'function' ? h.get('apikey') : null);
      if (ak && window.__capturedKeys.indexOf(ak) < 0)
        window.__capturedKeys.push(ak);
    }
  } catch(e) {}
  return _f.apply(this, arguments);
};

// 2. Disparar un navigate via click (NO navigate directo — resetea el contexto JS)
document.querySelector('a[href*=lideres]').click();

// 3. Leer la key capturada (después de que la request se complete)
window.__capturedKeys[0]; // → JWT completo de ~208 chars
```

**Por qué funciona:** El Supabase client construye la key en module closure (inaccesible
desde `window`), pero la pasa como header en cada fetch call. El monkey-patch captura
ese header ANTES de que se envíe.

**Requisitos clave:**
- El monkey-patch DEBE hacerse ANTES de un click SPA (no `navigate` que resetea el JS context)
- Verificar que la key no contenga "..." (longitud ~200+ chars, sin truncamiento)
- Funciona en Kimi WebBridge y browser tools con capacidades de evaluate

### Enumeración paralela de tablas via browser evaluate

```javascript
// Probar múltiples nombres de tablas en paralelo desde el browser
window._tabs = [];
var names = ['profiles', 'contacts', 'audit_logs', 'geo_departments',
             'certificates', 'votes', 'sessions', 'tokens'];
Promise.all(names.map(function(n) {
  return fetch('https://PROJECT.supabase.co/rest/v1/' + n + '?limit=1', {
    headers: {'apikey': ANON_KEY, 'Authorization': 'Bearer ' + TOKEN}
  }).then(function(r) {
    return r.text().then(function(t) {
      window._tabs.push(n + ':' + r.status + ':' + t.substring(0, 60));
    });
  }).catch(function(e) { window._tabs.push(n + ':err'); });
})).then(function() {
  window._tabResult = window._tabs.join(' | ');
});
// Leer: window._tabResult → "profiles:200:[...] | contacts:200:[] | ..."
```

Las respuestas 200 = tabla existe y accesible. Las 404 con `PGRST205` contienen hints
con nombres reales. Las 404 sin hint = tabla no existe.

### Supabase REST API requiere `apikey` header

PostgREST **siempre** requiere el header `apikey` (la anon key), incluso con un Bearer token válido. Sin `apikey`, la respuesta es:

```json
{"message":"No API key found in request","hint":"No `apikey` request header or url param was found."}
```

Para probes via curl:
```bash
curl -s "https://PROJECT.supabase.co/rest/v1/profiles" \
  -H "apikey: ANON_KEY" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

Sin la anon key, no se puede testear RLS ni endpoints via curl, incluso con un access_token válido extraído de localStorage.

## Brute Force Rate Limiting

```python
# Supabase Free tier: sin rate limiting en Auth
# 30 intentos consecutivos, ninguno devuelve 429
for i in range(30):
    r = requests.post(f"{URL}/auth/v1/token?grant_type=password",
        headers={"apikey": ANON_KEY},
        json={"email": "admin@app.com", "password": f"wrong{i}"})
    if r.status_code == 429:
        print(f"Rate limited at attempt {i+1}")
        break
# Si no hay 429 → reportar como MEDIUM (A07: Authentication Failures)
```

## Headers de Seguridad (Cloudflare Pages)

Cloudflare Pages no añade CSP, X-Frame-Options ni X-Content-Type-Options por defecto.
Para auditar:

```python
# Desde el sandbox de execute_code puede fallar DNS temporalmente
# Alternativa: usar browser_console con fetch
```

```javascript
// Via browser_console
fetch('/').then(r => {
  const h = {}; r.headers.forEach((v,k) => h[k]=v);
  console.log(JSON.stringify(h));
})
```

Sin `_headers` file ni `wrangler.toml` en el repo → faltan headers de seguridad.
Fix: crear `_headers` en la raíz del proyecto con:

```
/*
  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
```

## Auditar RLS Policies via SQL (MCP)

En lugar de (o además de) probe-ar via API, cuando tienes acceso MCP a Supabase,
enumera TODAS las policies de una vez. Esto es mucho más eficiente y completo:

```sql
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

**Qué buscar en los resultados:**
1. **`qual = 'true'`** — la policy permite acceso a TODOS (incluido anon). Solo OK
   para datos públicos (ej: geografía). Peligroso en datos sensibles.
2. **Over-permissive staff/intermediate roles** — policy que filtra por role pero
   no por relación (ej: staff ve TODOS los perfiles en vez de solo los asignados).
3. **Falta de `with_check`** en policies INSERT/UPDATE — permite escribir filas que
   luego no se pueden leer (data smuggling).

**Verificar funciones helper usadas en policies:**

Las policies suelen llamar funciones como `get_user_role()`. Estas funciones
deben ser `SECURITY DEFINER` (corren con privilegios del owner, no del invocante).
Si son `SECURITY INVOKER`, un usuario con pocos privilegios podría bypassearlas.

```sql
SELECT proname, prosecdef, proconfig
FROM pg_proc
WHERE proname IN ('get_user_role', 'get_user_id', ...);
-- prosecdef = true → SECURITY DEFINER (correcto para helpers de RLS)
-- proconfig debe incluir search_path = 'public' (evita search_path injection)
```

Si la función NO tiene `search_path` hardcoded → reportar como MEDIUM (bypass
potencial via search_path hijack en schemas maliciosos).

## Audit Log Incompleteness (patrón de riesgo)

**Patrón detectado (Nova Valle, jun 2026):** Audit triggers que registran solo
`action` + `table_name` sin before/after values ni el usuario que ejecutó la acción.

```javascript
// Verificar qué registra el audit log
fetch('https://PROJECT.supabase.co/rest/v1/audit_logs?select=*&limit=3&order=changed_at.desc', {
  headers: {'apikey': ANON_KEY, 'Authorization': 'Bearer ' + TOKEN}
});
// Si devuelve solo: {id, action, table_name, changed_at}
// → Falta: old_values, new_values, performed_by, changed_fields
```

**Por qué es problema:** Una escalación de role (PATCH profiles con role:admin)
se registra como "UPDATE profiles" genérico. Imposible distinguir un cambio de
nombre legítimo de una escalación de privilegios.

**Severidad:** HIGH — no es explotable directamente, pero hace imposible detectar
abuso post-facto. Un atacante que escala roles no deja rastro auditable.

**Fix:** El trigger debe registrar:
1. `auth_uid()` como performed_by
2. `old.*` y `new.*` como JSONB (o al menos los campos sensibles: role, username)
3. Diferencia entre campos (changed_fields)

## Trigger-Message Mismatch (bug de UX común en Supabase)

**Patrón:** Un trigger DB lanza `RAISE EXCEPTION 'mensaje A'`. El cliente JS hace
`error.message.includes('palabra clave')` para mostrar un mensaje específico.
Si el mensaje del trigger NO contiene la palabra clave → el check falla → el
usuario ve un error genérico en lugar del específico.

**Cómo detectarlo:**
1. Leer el código del cliente: buscar `.includes(` o `.match(` en handlers de error
2. Leer el trigger DB: `SELECT pg_get_triggerdef(oid) FROM pg_trigger WHERE ...`
3. Leer la función del trigger: `SELECT pg_get_functiondef(oid) FROM pg_proc WHERE ...`
4. Comparar: ¿el string que busca el cliente aparece en el RAISE EXCEPTION del trigger?

**Ejemplo real (Nova Valle):**
- Trigger: `RAISE EXCEPTION 'Contacte un administrador'`
- Cliente: `if (error.message.includes('cedula')) { ... }`
- Resultado: el check NUNCA hace match → usuario ve "Error al guardar" genérico
- La protección SÍ funciona (no se crean duplicados), pero el UX es incorrecto

**Severidad:** WARNING (UX pobre, no es vulnerability de seguridad). Reportarlo
en la sección de UX o como hardening.

## Cleanup Post-Testing

Los tests crean usuarios/registros basura. Limpiar via SQL (MCP) o API:

```sql
-- Borrar profiles huerfanos (Edge Function delete solo borra auth.users)
DELETE FROM profiles WHERE username IN ('test.user', '.', 'test.emoji', ...);
```

Nota: el Edge Function `delete-user` borra de `auth.users` pero NO de `profiles`
(no hay CASCADE o trigger). Los profiles quedan huérfanos hasta limpieza manual.
