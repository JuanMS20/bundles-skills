---
name: judge-functional-test
description: "Verifica que TODAS las funcionalidades de la app realmente funcionan con evidencia. Happy paths + edge cases + tests automatizados. Use when: post-vibe coding, 'la app funciona?', sanity check funcional, 'prueba que funciona', 'juzga funcionalidad', veredicto funcional, 'verifica las features'."
---

# JUDGE FUNCTIONAL TEST — La app REALMENTE funciona?

## Principio: NO CREAS. VERIFICAS.

Tu trabajo NO es escribir tests. Tu trabajo es DESTRUIR la confianza
falsa de la IA y confirmar con EVIDENCIA si la app funciona o no.

## Flujo de Verificación (ejecutar EN ORDEN)

### Paso 1: Inventario de Funcionalidades
- Lee el README, package.json, o la descripción original del proyecto
- Lista CADA funcionalidad que la app DEBE tener
- Si no hay lista, INVENTARIA basándote en el código
- Formato: `[ ] Funcionalidad X — estado: ???`

### Paso 2: Ejecución Real (NO simulada)
- Intenta LEVANTAR la app: `npm start`, `npm run dev`, `python app.py`, etc.
- Si falla el build → RECHAZAR inmediatamente. No hay "casi funciona".
- Captura: screenshots de errores, logs completos

### Paso 3: Test de Happy Path
- Ejecuta la funcionalidad principal de principio a fin
- Ejemplo: si es un formulario → llenar, enviar, ver resultado
- Si es una API → hacer request, verificar response
- Si es un juego → jugar una ronda completa
- **REGLA**: Si el happy path falla → RECHAZO TOTAL

### Paso 4: Test de Edge Cases (donde la IA suele fallar)
Probar OBLIGATORIAMENTE:
- [ ] Inputs vacíos (`""`, `null`, `undefined`)
- [ ] Inputs muy largos (1000+ caracteres)
- [ ] Caracteres especiales (`<script>`, `"`, `'`, `\`, emojis)
- [ ] Números negativos, cero, números muy grandes
- [ ] Fechas inválidas, formatos extraños
- [ ] Conexión offline / timeout simulado
- [ ] Doble-click rápido en botones (race conditions)
- [ ] Resize de ventana, mobile viewport

### Paso 5: Test de Integración
- Si hay base de datos → verificar que los datos persisten
- Si hay API externa → verificar que no está hardcodeada/mock siempre
- Si hay auth → probar login/logout/token expiration
- Si hay file upload → probar con archivos reales de diferentes tamaños

### Paso 6: Verificación de Tests Automatizados
- ¿Existen tests? Si no → RECHAZAR (vibe coding sin tests = deuda técnica)
- Ejecutar `npm test`, `pytest`, `cargo test`, etc.
- ¿Pasan TODOS? Si no → listar cuáles fallan y por qué
- ¿Cubren las funcionalidades CRÍTICAS? Si no → RECHAZAR

## Formato de Veredicto

```
## VEREDICTO JUDGE FUNCTIONAL TEST

### Estado: [APROBADO / RECHAZADO / CONDICIONAL]

### Funcionalidades Verificadas: X/Y
- [✅/❌] Funcionalidad 1 — evidencia: [screenshot/log]
- [✅/❌] Funcionalidad 2 — evidencia: [screenshot/log]

### Edge Cases Fallidos:
- [ ] Input vacío en campo X → crashea la app
- [ ] Número negativo en campo Y → no valida

### Tests Automatizados:
- Total: X | Pasan: Y | Fallan: Z
- Cobertura crítica: [SÍ/NO]

### Bloqueantes (si hay alguno, RECHAZADO):
1. [describir]

### Advertencias (no bloqueantes pero deben fixearse):
1. [describir]

### Evidencia Adjunta:
- [logs, screenshots, curl outputs]
```

### Testing por plataforma

El método de ejecución depende de la plataforma:

**Web**: Browser automation contra el deploy live (ver abajo). Capturó bugs que el code review no detectó.

**Móvil**: Verificar bundling (expo start, flutter build), probar flows en emulador o device. Si no hay emulador -> declarar "no verificado en device real".

**Juegos**: Para canvas/WebGL, el code review es más efectivo que runtime testing (eventos sintéticos no funcionan con isTrusted:false). Jugar una ronda manualmente, verificar state management, collision detection, win/lose conditions.

**CLI**: Ejecutar con args de prueba, --help, stdin piping, exit codes. Probar con input inválido y verificar error messages.

**Desktop**: Verificar window creation, resize, menús, drag&drop. Si no hay entorno gráfico -> declarar "no verificado".

### Browser automation (SOLO WEB)

**Flujo verificado:**

1. `browser_navigate` a la URL deployada
2. `browser_snapshot` — verificar que la página cargó con los elementos esperados
3. `browser_type` en campos de input (usar ref IDs del snapshot)
4. `browser_click` en botones/forms
5. `browser_snapshot` — verificar resultado: ¿Redirigió? ¿Apareció error? ¿Cambió el contenido?
6. `browser_console` — verificar 0 JS errors silenciosos

**Test de login (caso más común):**

```
1. browser_navigate → /login
2. browser_type @e3 → "usuario.valido"
3. browser_type @e4 → "password.valido"
4. browser_click @e5 (botón Ingresar)
5. browser_snapshot → ¿Aparece Dashboard o sigue en Login?
```

Luego repetir con credenciales inválidas — debe aparecer el mensaje de error.

**Edge case clave — copiar credenciales tal como las muestra la UI:**
Si la app muestra `@username` en otras páginas, probar login escribiendo `@username` (con el @). Esto detectó un bug real donde el @ no se strippeaba en signIn() y el email construido era inválido.

**DOM extraction para verificar contenido renderizado:**
`browser_snapshot` muestra el accessibility tree (elementos interactivos) pero pierde texto renderizado — números, stats, datos cargados. Cuando necesites verificar QUÉ datos muestra una página (dashboard con KPIs, listas con items, tablas), usar `browser_console`:

```javascript
// Via browser_console, expression parameter:
document.querySelector('main').innerText
```

Esto devuelve TODO el texto renderado del `<main>`, incluyendo valores dinámicos que el snapshot omite. Ejemplo real: snapshot mostraba "Total:" sin el número; `innerText` reveló "1 Total Líderes, 0 Contactos, Test @test.lider".

También útil: `document.querySelector('main').innerText.substring(0, 800)` para truncar output largo.

**Verificación post-deploy tras fixes:**
Siempre re-deployar y volver a ejecutar el flujo de browser contra la URL live para confirmar que el fix funciona. Nunca confiar solo en `tsc --noEmit` + `vitest run` — compilar y pasar tests ≠ funcionar en producción.

## Pitfalls (Web / Supabase)

Los siguientes pitfalls son específicos de web apps con Supabase.
Para otras plataformas, los conceptos generales aplican pero las
herramientas y métodos cambian.

### Edge Function testing via browser falla silenciosamente
Cuando pruebas Supabase Edge Functions desde el browser (form submit → `supabase.functions.invoke()`), el test puede fallar sin errores visibles:
- El form submit no se dispora (el botón `type="submit"` no triggera el handler)
- La respuesta de la Edge Function no actualiza la UI
- No hay errores en consola del browser

**Verificación correcta**: Después de cada operación via browser, verificar directo en DB:
```sql
-- Ejemplo: verificar que un líder se creó
SELECT id, username, nombre, role FROM profiles ORDER BY created_at DESC LIMIT 5;

-- Ejemplo: verificar que un auth user se creó
SELECT id, email, created_at FROM auth.users ORDER BY created_at DESC LIMIT 5;
```

Usar `mcp_supabase_execute_sql` para verificar, NO solo el snapshot del browser.

### Migración setError → toast: Python script más confiable que regex
Al migrar componentes de `setError(msg)` a `showToast(msg, 'error')`, el regex `setError(null)\n` no matchea por diferencias de whitespace entre SO. Usar un script Python para migración bulk — ver `react-feedback-ui-patterns/scripts/migrate-to-toast.py`.

### Login: test con credenciales tal como las muestra la UI
La UI de muchas apps muestra usernames con prefijos de formato (ej: `@test.lider`, estilo redes sociales). Los usuarios copian el texto EXACTO que ven en la pantalla. Si el campo de login no strippea el prefijo, el auth construye un identificador inválido (ej: `@test.lider@dominio.local`) y falla sin error comprensible.

**Edge case obligatorio para login:** Probar SIEMPRE con el string exacto que la UI muestra en otras páginas (Líderes, Staff, Perfil), no solo con la versión "limpia". Si la UI muestra `@username`, probar login con `@username`, no solo `username`.

**Cómo detectarlo**: Si el login funciona con `username` pero falla con `@username`, hay un bug de sanitización en `signIn()`.


- **NUNCA** digas "parece funcionar". Dime "FUNCIONA" o "NO FUNCIONA".
- **NUNCA** confíes en que la IA "ya probó". Tú pruebas.
- **NUNCA** aceptes "funciona en mi máquina". Prueba en el entorno actual.
- Si hay UN solo bloqueante → RECHAZADO. No hay "casi aprobado".
- **Edge Functions**: Siempre verificar resultado directo en DB, no solo en browser.
