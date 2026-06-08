# Supabase Security Hardening Patterns

## Role Escalation Prevention

**Problem:** Users can PATCH profiles via REST API to escalate their own role to admin.

**Solution:** Trigger that blocks role changes by non-admin users.

```sql
CREATE OR REPLACE FUNCTION prevent_role_escalation()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF old.role IS DISTINCT FROM new.role THEN
    IF get_user_role() != 'admin' THEN
      RAISE EXCEPTION 'No tienes permisos para cambiar roles de usuario';
    END IF;
  END IF;
  RETURN new;
END;
$$;

CREATE TRIGGER trg_prevent_role_escalation
  BEFORE UPDATE ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION prevent_role_escalation();
```

## Orphan Admin Prevention

**Problem:** POST to profiles can create admin users without auth_id (no linked auth user).

**Solution:** Trigger that blocks admin inserts without auth_id.

```sql
CREATE OR REPLACE FUNCTION prevent_orphan_admin_profiles()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF new.role = 'admin' AND new.auth_id IS NULL THEN
    RAISE EXCEPTION 'No se puede crear perfil de administrador sin usuario de autenticación asociado';
  END IF;
  RETURN new;
END;
$$;

CREATE TRIGGER trg_prevent_orphan_admin
  BEFORE INSERT ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION prevent_orphan_admin_profiles();
```

## API Views for Column Limiting

**Problem:** `select=*` returns sensitive columns (address, birth_date, profession, education).

**Solution:** Create views that expose only safe columns.

```sql
-- Safe profile view (removes: direccion, fecha_nacimiento, estado_laboral, 
-- profesion, nivel_educativo, titulo_nivel, titulo_pregrado)
CREATE OR REPLACE VIEW public.api_profiles AS
SELECT 
  id, auth_id, username, nombre, primer_nombre, segundo_nombre,
  primer_apellido, segundo_apellido, tipo_doc, doc, celular,
  ciudad, zona, role, staff_asignado, created_at, updated_at
FROM profiles;

-- Grant access to API roles
GRANT SELECT ON public.api_profiles TO anon, authenticated;
GRANT SELECT ON public.api_contacts TO anon, authenticated;
```

## Data API Configuration

**Dashboard path:** Project Settings → Integrations → Data API → Settings

1. **Disable auto-exposure:** Toggle OFF "Automatically expose new tables"
2. **Expose views instead of tables:** Add `api_profiles`, `api_contacts` to exposed tables
3. **Keep original tables for writes:** Don't revoke INSERT/UPDATE/DELETE on originals (RLS handles access control)

## Audit Logs (Already in Schema)

The Nova Valle schema already captures:
- `old_data` (jsonb) for UPDATE/DELETE
- `new_data` (jsonb) for INSERT/UPDATE
- `changed_by` (uuid) via profile lookup

Verify with:
```sql
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'audit_logs' 
AND column_name IN ('old_data', 'new_data', 'changed_by');
```

## Cloudflare Pages Security Headers

Instead of dashboard configuration, use `public/_headers` file:

```
/*
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; ...
  Permissions-Policy: camera=(), microphone=(), geolocation=()
```

This is version-controlled and deploys automatically with Cloudflare Pages.

## Migration Safety

When applying security migrations via MCP Supabase:
1. Use `mcp_supabase_apply_migration` with descriptive name
2. Verify triggers with: `SELECT trigger_name FROM information_schema.triggers WHERE event_object_table = 'profiles'`
3. Test RLS policies with actual user roles before production
