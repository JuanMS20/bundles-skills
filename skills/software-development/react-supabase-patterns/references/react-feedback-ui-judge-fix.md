# Judge → Fix Workflow

## Patrón observado
Cuando el usuario ejecuta el judge bundle y hay advertencias, la expectativa es que se reparen TODAS, no solo se documenten.

## Flujo correcto
1. Ejecutar judge bundle completo (6 fases)
2. Presentar veredicto con advertencias
3. **Inmediatamente** preguntar si se procede a fixear — o mejor, fixear directamente si el usuario dice "continua"
4. Implementar fixes en orden de severidad
5. Verificar build + tests después de cada fix
6. Commit al final

## Orden de fixes típico
1. **Seguridad** (REVOKE, search_path, credenciales) — via MCP Supabase
2. **Error boundaries** — class component wrapper
3. **404 page** — ruta catch-all `*`
4. **Toast system** — ToastProvider + useToast
5. **Loading spinners** — SVG animate-spin en botones
6. **Confirmaciones** — confirm() nativo o ConfirmDialog

## Pitfall: migración bulk de setError → toast
Cuando hay 4+ archivos con el mismo patrón `setError`/`setMessage`, NO editar uno por uno.
Usar Python script batch (`scripts/migrate-to-toast.py`) para migrar todos de una vez.
Luego hacer `npm run build` para verificar que no quedaron referencias rotas.

## Pitfall: setError(null) residual
El regex de migración a veces no captura todos los `setError(null)` por diferencias de whitespace.
Después de la migración automática, hacer `grep -rn "setError\|setMessage" src/` para verificar.
