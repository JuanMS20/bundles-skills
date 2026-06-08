# Nova Valle Security Fixes — Case Study

**Date:** 2026-06-08
**Project:** Nova Valle (React 19 + Supabase + Vite)

## Issues Found and Resolved

### SEC1 — Role Escalation (CRITICAL) ✅
**Finding:** PATCH profiles with `{role:'admin'}` could escalate any user to admin.
**Root Cause:** RLS policies existed but service_role key bypasses them.
**Fix:** Added `prevent_role_escalation` trigger on profiles table.

### SEC2 — Orphan Admin Profiles (CRITICAL) ✅
**Finding:** POST could create admin profiles without auth_id.
**Root Cause:** No validation on insert for admin role requirement.
**Fix:** Added `prevent_orphan_admin_profiles` trigger on profiles table.

### SEC3 — Incomplete Audit Logs (HIGH) ✅ (Already Fixed)
**Finding:** Audit logs supposedly missing old_data, new_data, changed_by.
**Reality:** Schema already had these columns. Audit finding was from older version.
**Verification:** Checked `information_schema.columns` and recent log entries.

### SEC4 — Table Enumeration via Hints (MEDIUM) 📋
**Finding:** PostgREST error hints expose real table names.
**Status:** Requires PostgREST config (not available in free tier UI).
**Mitigation:** RLS + triggers already prevent unauthorized access.

### SEC5 — Schema Fully Exposed (MEDIUM) 📋
**Finding:** `select=*` returns 19+ columns with personal data.
**Status:** Requires creating API views + revoking direct table access.
**Recommendation:** Create `api_profiles` and `api_contacts` views with safe columns.

## Patterns for Future Sessions

1. **Always verify current schema before assuming a finding persists** — SEC3 was already fixed
2. **Triggers are defense-in-depth** — RLS + triggers > RLS alone
3. **PostgREST config needs dashboard access** — Can't be done via SQL migrations
4. **Free tier has limitations** — Some security settings not available

## Migration Pattern

```sql
-- Apply both triggers in single migration
CREATE OR REPLACE FUNCTION prevent_role_escalation() ...
CREATE TRIGGER trg_prevent_role_escalation ...

CREATE OR REPLACE FUNCTION prevent_orphan_admin_profiles() ...
CREATE TRIGGER trg_prevent_orphan_admin ...
```

## Verification Commands

```sql
-- Verify triggers exist
SELECT trigger_name, event_manipulation 
FROM information_schema.triggers 
WHERE event_object_table = 'profiles' 
AND trigger_name LIKE 'trg_prevent%';

-- Verify audit logs complete
SELECT has_old_data, has_new_data, has_changed_by, COUNT(*)
FROM (
  SELECT 
    CASE WHEN old_data IS NOT NULL THEN 'YES' ELSE 'NO' END as has_old_data,
    CASE WHEN new_data IS NOT NULL THEN 'YES' ELSE 'NO' END as has_new_data,
    CASE WHEN changed_by IS NOT NULL THEN 'YES' ELSE 'NO' END as has_changed_by
  FROM audit_logs
) t
GROUP BY has_old_data, has_new_data, has_changed_by;
```
