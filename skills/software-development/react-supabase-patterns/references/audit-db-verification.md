# Audit-Driven DB Verification

Cuando trabajas desde un reporte de auditoría (security, UX, chaos), NO asumas que todos los issues están abiertos. El código y el schema pueden haber cambiado desde que se ejecutó la auditoría. Verifica el estado actual de cada issue ANTES de implementar.

## Queries de verificación rápidas

### Triggers: verificar mensaje de RAISE EXCEPTION

```sql
SELECT tgname, prosrc
FROM pg_trigger t
JOIN pg_proc p ON t.tgfoid = p.oid
WHERE t.tgname LIKE '%check%' OR t.tgname LIKE '%validate%';
```

Lee el `prosrc` para ver el texto exacto del `RAISE EXCEPTION`. El cliente debe matchear este texto en `error.message.includes(...)`.

**Patrón correcto (alineado):**
```sql
-- Trigger
raise exception 'Ya existe un contacto con esta cédula';
```
```tsx
// Cliente
if (error.message.includes('Ya existe un contacto')) {
  throw new Error('Ya existe un contacto con esta cédula.')
}
```

**Patrón incorrecto (desalineado):**
```sql
-- Trigger dice "Contacte un administrador" (sin "cedula")
```
```tsx
// Cliente busca "cedula" → nunca matchea → error genérico
if (error.message.includes('cedula')) { ... }
```

### RLS: verificar policies actuales

```sql
SELECT tablename, policyname, cmd, qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

Lee el `qual` para verificar qué condiciones aplican. Common issues encontrados en auditorías:

| Issue detectado | `qual` problemático | Fix |
|---|---|---|
| Lectura sin auth | `true` | `auth.uid() IS NOT NULL` |
| Staff ve todos los registros | `get_user_role() = 'staff'` sin filtro | Subquery a tabla de asignaciones (`staff_leaders`) |
| RLS sin policies | (vacío) | Crear al menos SELECT policy |

### Geo tables: verificar acceso público

```sql
SELECT tablename, policyname, qual
FROM pg_policies
WHERE schemaname = 'public'
AND tablename LIKE 'geo_%'
AND policyname LIKE '%read%';
```

Si `qual = true`, cualquiera puede leer sin auth. Para datos potencialmente sensibles (barrios en contexto electoral), cambiar a `auth.uid() IS NOT NULL`.

## Migración para fix RLS de geo tables

```sql
DROP POLICY IF EXISTS geo_barrios_read ON public.geo_barrios;
CREATE POLICY geo_barrios_read ON public.geo_barrios
  FOR SELECT USING (auth.uid() IS NOT NULL);

-- Repetir para geo_departments, geo_municipalities, geo_voting_stations
```

Usar `mcp_supabase_apply_migration` para aplicar como migración versionada.

## Security Triggers: verificar existencia

```sql
-- Verificar triggers de seguridad en profiles
SELECT trigger_name, event_manipulation, action_statement
FROM information_schema.triggers
WHERE event_object_table = 'profiles'
AND trigger_name LIKE 'trg_prevent%'
ORDER BY trigger_name;
```

Resultado esperado si los triggers existen:
- `trg_prevent_role_escalation` (UPDATE) — previene role escalation
- `trg_prevent_orphan_admin` (INSERT) — previene profiles admin sin auth_id

Si no existen, crearlos con el patrón de la sección "Security Triggers como Defense-in-Depth" en el SKILL.md principal.

## Checklist: verificar antes de implementar fixes de auditoría

1. **Triggers:** `SELECT prosrc FROM pg_proc JOIN pg_trigger` — ¿el texto matchea el claim del auditor?
2. **RLS policies:** `SELECT qual FROM pg_policies` — ¿la policy sigue siendo vulnerable o ya se fixeó?
3. **Security triggers:** `SELECT trigger_name FROM information_schema.triggers WHERE trigger_name LIKE 'trg_prevent%'` — ¿existen los triggers de defensa?
4. **Código actual:** leer el archivo (no confiar en el line number del auditoría) — ¿ya tiene el fix?
5. **`maxLength` en inputs:** verificar en el JSX actual, no en la claim de auditoría
6. **Counts con `?? 0`:** verificar en el componente Dashboard/stats actual

**Tiempo ahorrado:** esta verificación tomó ~5 min y evitó reimplementar 3 issues que ya estaban resueltos (#5 apellidos maxLength, #6 dashboard stats, #7 profiles_staff_read RLS).
