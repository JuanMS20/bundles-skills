# SECURITY DEFINER Function Security in Supabase

## Problem

When you create a `SECURITY DEFINER` function in Supabase, it's callable by `anon` role by default via `/rest/v1/rpc/<function>`. This is a security risk.

## Example

```sql
-- This function is callable by anyone (anon role) by default!
CREATE OR REPLACE FUNCTION public.get_user_role()
RETURNS text
LANGUAGE sql
SECURITY DEFINER
AS $$
  SELECT role FROM profiles WHERE auth_id = auth.uid();
$$;
```

## Solution

```sql
-- Revoke from PUBLIC (includes anon)
REVOKE EXECUTE ON FUNCTION public.get_user_role() FROM PUBLIC;

-- Grant only to authenticated users
GRANT EXECUTE ON FUNCTION public.get_user_role() TO authenticated;

-- If only Edge Functions need it (service_role):
-- Don't grant to authenticated, only service_role gets it automatically
```

## Verification

Check actual grants (not advisor cache):

```sql
SELECT routine_name, grantee, privilege_type
FROM information_schema.routine_privileges
WHERE routine_schema = 'public'
  AND routine_name IN ('get_user_role', 'fix_user_null_columns');
```

## Supabase Advisor Limitations

The advisor (`get_advisors(type='security')`) caches results. After REVOKE, it may still show warnings. Verify via `information_schema.routine_privileges` instead.

## search_path

Always set `search_path` on SECURITY DEFINER functions to prevent search path injection:

```sql
ALTER FUNCTION public.get_user_role() SET search_path = 'public';
```

## Recursion Pitfall (CRÍTICO)

SECURITY DEFINER funciones que consultan la MISMA tabla cuyas RLS policies las llaman causan **infinite recursion** (`ERROR 42P17`). El ciclo es: policy de `profiles` → `get_user_role()` → `profiles` → policy → `get_user_role()` → ...

SECURITY DEFINER **no resuelve esto** — aunque la función bypassa RLS, Postgres detecta la referencia circular a nivel de policy parsing.

Fix: la función debe leer de una tabla SIN RLS (ej: `auth.users.raw_app_meta_data`). Ver `references/rls-infinite-recursion.md` para el debugging path y fix pattern completo.

## Permisos para RLS Policies

Si una SECURITY DEFINER función es usada por RLS policies, el rol `authenticated` NECESITA `GRANT EXECUTE`. Si haces `REVOKE FROM authenticated`, las policies fallan con `permission denied for function`.

```sql
-- CORRECTO: anon no puede llamar, authenticated sí (para RLS)
REVOKE EXECUTE ON FUNCTION public.get_user_role() FROM anon;
GRANT EXECUTE ON FUNCTION public.get_user_role() TO authenticated;
```

## Common Patterns

1. **get_user_role()** - Used in RLS policies. Should be callable by `authenticated` only.
2. **fix_user_null_columns()** - GoTrue NULL fix. Should be callable by `service_role` only (Edge Functions).
3. **Custom RPC functions** - Audit each one individually.
