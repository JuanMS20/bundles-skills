---
title: SECURITY DEFINER Functions — Privilege Isolation
impact: HIGH
impactDescription: SECURITY DEFINER functions run as the function owner. Wrong grants let anon/authenticated users bypass RLS via RPC.
tags: security, privileges, security-definer, supabase, functions
---

## SECURITY DEFINER Functions — Privilege Isolation

SECURITY DEFINER functions execute with the privileges of the **function owner** (usually postgres), not the calling role. This is intentional for RLS helper functions (like `get_user_role()`), but Supabase exposes all `public` schema functions as REST RPC endpoints by default.

### The Problem

By default, Supabase grants EXECUTE on new functions to `PUBLIC` (which includes `anon` and `authenticated`). A SECURITY DEFINER function callable by `anon` lets unauthenticated users execute privileged operations.

**Supabase advisor lints that flag this:**
- `anon_security_definer_function_executable` — anon role can call SECURITY DEFINER function
- `authenticated_security_definer_function_executable` — authenticated users can call it (sometimes undesired)

### Pitfall: REVOKE FROM anon Does NOT Work

```sql
-- ❌ DOES NOT WORK if the grant is to PUBLIC
REVOKE EXECUTE ON FUNCTION public.get_user_role() FROM anon;
-- anon still has access because PUBLIC includes anon
```

**Why:** Postgres privilege inheritance — `PUBLIC` is a pseudo-role that includes all roles. `REVOKE FROM anon` removes a *specific* grant, but the `PUBLIC` grant still applies.

### Correct Pattern: REVOKE FROM PUBLIC + Explicit anon/authenticated

```sql
-- ✅ Step 1: Revoke from PUBLIC AND from specific Supabase roles
-- Pitfall: Supabase grants EXECUTE to anon/authenticated independently
-- of the PUBLIC grant. REVOKE FROM PUBLIC alone may NOT remove their access.
REVOKE EXECUTE ON FUNCTION public.fix_user_null_columns(text) FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION public.get_user_role() FROM PUBLIC;

-- ✅ Step 2: Explicitly revoke from Supabase API roles
-- NECESSARY even after REVOKE FROM PUBLIC in Supabase projects.
REVOKE EXECUTE ON FUNCTION public.fix_user_null_columns(text) FROM anon, authenticated;
REVOKE EXECUTE ON FUNCTION public.get_user_role() FROM anon, authenticated;

-- ✅ Step 3: Grant ONLY to the roles that need it
-- get_user_role: needed by authenticated users (used in RLS policies)
GRANT EXECUTE ON FUNCTION public.get_user_role() TO authenticated;

-- fix_user_null_columns: only needed by service_role (Edge Functions)
-- Do NOT grant to authenticated — only service_role and postgres retain access
GRANT EXECUTE ON FUNCTION public.fix_user_null_columns(text) TO service_role;
```

### Pitfall: REVOKE FROM PUBLIC Does NOT Remove anon/authenticated in Supabase

Supabase's PostgREST layer grants EXECUTE to `anon` and `authenticated` roles explicitly on functions in the `public` schema. `REVOKE ... FROM PUBLIC` removes the implicit grant, but the explicit Supabase grants survive.

**Symptom:** After `REVOKE FROM PUBLIC`, the Supabase linter still reports:
- `anon_security_definer_function_executable`
- `authenticated_security_definer_function_executable`

**Fix:** Always revoke from all three: `PUBLIC, anon, authenticated`:
```sql
REVOKE EXECUTE ON FUNCTION public.my_func() FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.my_func() TO service_role;
```

**Verify:**
```sql
SELECT grantee, privilege_type
FROM information_schema.routine_privileges
WHERE routine_schema = 'public'
  AND routine_name = 'my_func'
ORDER BY grantee;
-- Should show ONLY: postgres + service_role (+ authenticated if intentional)
```

### Verify Grants

```sql
SELECT 
  routine_name,
  grantee,
  privilege_type
FROM information_schema.routine_privileges
WHERE routine_schema = 'public'
  AND routine_name IN ('fix_user_null_columns', 'get_user_role')
ORDER BY routine_name, grantee;
```

Expected result after fixes:
| routine_name | grantee | privilege_type |
|---|---|---|
| fix_user_null_columns | postgres | EXECUTE |
| fix_user_null_columns | service_role | EXECUTE |
| get_user_role | authenticated | EXECUTE |
| get_user_role | postgres | EXECUTE |
| get_user_role | service_role | EXECUTE |

### Pitfall: search_path Mutable Functions

Supabase advisor lint `function_search_path_mutable` flags functions where `search_path` is not set. An attacker could manipulate the search path to call a malicious function instead of the intended one.

```sql
-- ❌ Vulnerable: search_path depends on caller's session setting
CREATE FUNCTION public.get_user_role() ...

-- ✅ Fixed: explicit search_path
ALTER FUNCTION public.get_user_role() SET search_path = 'public';
```

Apply to all SECURITY DEFINER functions:
```sql
ALTER FUNCTION public.update_updated_at() SET search_path = 'public';
ALTER FUNCTION public.get_user_role() SET search_path = 'public';
ALTER FUNCTION public.check_cedula_unique() SET search_path = 'public';
ALTER FUNCTION public.fix_user_null_columns(text) SET search_path = 'public';
```

### Supabase-Specific Notes

- `service_role` key always retains access (it's a superuser-like role)
- Edge Functions use `service_role` server-side — this is the intended pattern for admin operations
- The advisor warnings persist in the Supabase dashboard even after REVOKE — they check function definition metadata, not actual grants. Verify with `information_schema.routine_privileges` instead.
- `get_user_role()` being SECURITY DEFINER is **correct** — it needs to read `profiles` table regardless of the caller's RLS restrictions. The fix is restricting *who can call it*, not removing SECURITY DEFINER.

### Quick Checklist

- [ ] All SECURITY DEFINER functions have `SET search_path = 'public'`
- [ ] `fix_user_null_columns` only callable by `postgres` + `service_role`
- [ ] `get_user_role()` callable by `authenticated` + `postgres` + `service_role` (NOT `anon`)
- [ ] Verify with `information_schema.routine_privileges`, not just advisor lints
- [ ] REVOKE from `PUBLIC` first, then GRANT to specific roles

Reference: https://supabase.com/docs/guides/database/database-linter
