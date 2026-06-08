# Supabase Security Pitfalls

## SECURITY DEFINER Function Grants

**Problem:** When you create a `SECURITY DEFINER` function in Supabase, it's callable by `anon` role by default via `/rest/v1/rpc/<function>`. This is a security risk.

**Solution:**
```sql
-- Revoke from PUBLIC (includes anon)
REVOKE EXECUTE ON FUNCTION public.your_function() FROM PUBLIC;

-- Grant only to specific roles
GRANT EXECUTE ON FUNCTION public.your_function() TO authenticated;
-- If only Edge Functions need it, don't grant to authenticated
```

**Verification:** Check actual grants (not advisor cache):
```sql
SELECT routine_name, grantee, privilege_type
FROM information_schema.routine_privileges
WHERE routine_schema = 'public'
  AND routine_name IN ('your_function');
```

## search_path on SECURITY DEFINER

**Problem:** Without explicit `search_path`, the function's search path is mutable and exploitable.

**Solution:**
```sql
ALTER FUNCTION public.your_function() SET search_path = 'public';
```

## Supabase Advisor Limitations

The advisor (`get_advisors(type='security')`) caches results. After REVOKE, it may still show warnings. Verify via `information_schema.routine_privileges` instead.

## Testing Edge Functions

**Problem:** Browser-based testing of Edge Functions is unreliable due to React form submission timing.

**Solution:** Verify success by:
1. Database query: `SELECT * FROM profiles ORDER BY created_at DESC`
2. Edge Function logs: `get_logs(service='edge-function')`
3. Direct curl with proper auth headers
