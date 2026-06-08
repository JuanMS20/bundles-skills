# RLS Infinite Recursion — El Pitfall Más Insidioso de Supabase

## Síntoma

Login exitoso pero la app muestra "Error cargando perfil de usuario" o se queda en loading perpetuo. El fetch del profile retorna vacío o error. No hay error visible en consola del browser.

Error real en backend (solo visible via `execute_sql` simulando el rol authenticated):
```
ERROR: 42P17: infinite recursion detected in policy for relation "profiles"
```

## Root Cause

Las policies de RLS en una tabla llaman a funciones que consultan ESA MISMA tabla. Postgres detecta el ciclo y bloquea toda la consulta.

### Patrón que causa recursión

```sql
-- Tabla: profiles (RLS activado)
-- Policy que llama a get_user_role():
CREATE POLICY profiles_admin_all ON profiles
  FOR ALL USING (get_user_role() = 'admin');

-- Función que consulta profiles:
CREATE FUNCTION get_user_role() RETURNS user_role
SECURITY DEFINER AS $$
  SELECT role FROM profiles WHERE auth_id = auth.uid();
$$;
```

Ciclo: `profiles` RLS → `get_user_role()` → `profiles` → RLS → `get_user_role()` → ...

**SECURITY DEFINER NO rompe el ciclo.** Aunque la función se ejecuta como `postgres` (bypassing RLS), Postgres aún detecta la referencia circular a nivel de policy parsing.

### Recursión cross-tabla (MÁS insidiosa)

El ciclo puede ser indirecto — multiple tablas referenciándose mutuamente:

```sql
-- contacts policy referencia profiles:
CREATE POLICY contacts_lider_all ON contacts
  USING (lider_id = (SELECT profiles.id FROM profiles WHERE profiles.auth_id = auth.uid()));

-- profiles policy referencia staff_leaders que JOIN profiles:
CREATE POLICY profiles_staff_read ON profiles
  USING (id IN (
    SELECT sl.lider_id FROM staff_leaders sl
    JOIN profiles p ON p.id = sl.staff_id  -- <-- profiles dentro de policy de profiles = recursión
    WHERE p.auth_id = auth.uid()
  ));
```

Aquí el ciclo es: `profiles` → `staff_leaders` → `profiles`.

## Fix Pattern Verificado

### Estrategia: Cache de identidad en `auth.users.raw_app_meta_data`

`auth.users` NO tiene RLS. Las funciones helper pueden leer de ahí sin crear ciclos.

```sql
-- Step 1: Funciones helper que leen de auth.users (NO profiles)
CREATE OR REPLACE FUNCTION public.get_user_role()
RETURNS user_role
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT (raw_app_meta_data->>'role')::user_role
  FROM auth.users
  WHERE id = auth.uid();
$$;

CREATE OR REPLACE FUNCTION public.get_user_profile_id()
RETURNS uuid
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT (raw_app_meta_data->>'profile_id')::uuid
  FROM auth.users
  WHERE id = auth.uid();
$$;

-- Step 2: Trigger que sincroniza role + profile_id cuando profiles cambia
CREATE OR REPLACE FUNCTION sync_role_to_auth_meta()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  UPDATE auth.users
  SET raw_app_meta_data = jsonb_build_object(
    'provider', COALESCE(raw_app_meta_data->>'provider', 'email'),
    'providers', COALESCE(raw_app_meta_data->'providers', '["email"]'::jsonb),
    'role', to_jsonb(NEW.role::text),
    'profile_id', to_jsonb(NEW.id::text)
  )
  WHERE id = NEW.auth_id;
  RETURN NEW;
END;
$$;

CREATE TRIGGER profiles_role_sync
  AFTER INSERT OR UPDATE OF role ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION sync_role_to_auth_meta();

-- Step 3: Backfill existente
UPDATE auth.users u
SET raw_app_meta_data = jsonb_build_object(
  'provider', COALESCE(u.raw_app_meta_data->>'provider', 'email'),
  'providers', COALESCE(u.raw_app_meta_data->'providers', '["email"]'::jsonb),
  'role', to_jsonb(p.role::text),
  'profile_id', to_jsonb(p.id::text)
)
FROM profiles p
WHERE p.auth_id = u.id;

-- Step 4: Reescribir TODAS las policies que referencian profiles directa o indirectamente
-- Admin: sin subquery a profiles
CREATE POLICY profiles_admin_all ON profiles
  FOR ALL
  USING (get_user_role() = 'admin'::user_role)
  WITH CHECK (get_user_role() = 'admin'::user_role);

-- Lider: usa auth.uid() directo
CREATE POLICY profiles_lider_self ON profiles
  FOR ALL
  USING (get_user_role() = 'lider'::user_role AND auth_id = auth.uid())
  WITH CHECK (get_user_role() = 'lider'::user_role AND auth_id = auth.uid());

-- Staff: usa get_user_profile_id() en vez de JOIN profiles
CREATE POLICY profiles_staff_read ON profiles
  FOR SELECT
  USING (
    get_user_role() = 'staff'::user_role
    AND (
      auth_id = auth.uid()
      OR id IN (
        SELECT sl.lider_id FROM staff_leaders sl
        WHERE sl.staff_id = get_user_profile_id()
      )
    )
  );

-- contacts: usa get_user_profile_id() en vez de subquery a profiles
CREATE POLICY contacts_lider_all ON contacts
  FOR ALL
  USING (
    get_user_role() = 'lider'::user_role
    AND lider_id = get_user_profile_id()
  );

-- staff_leaders: usa get_user_profile_id()
CREATE POLICY staff_leaders_staff_read ON staff_leaders
  FOR SELECT
  USING (
    get_user_role() = 'staff'::user_role
    AND staff_id = get_user_profile_id()
  );
```

### Permisos de funciones helper

```sql
-- Helper functions: authenticated puede llamar (RLS policies lo necesitan), anon NO
GRANT EXECUTE ON FUNCTION public.get_user_role() TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_user_profile_id() TO authenticated;
REVOKE EXECUTE ON FUNCTION public.get_user_role() FROM anon;
REVOKE EXECUTE ON FUNCTION public.get_user_profile_id() FROM anon;

-- Trigger function: nadie la llama via API (solo el trigger)
REVOKE EXECUTE ON FUNCTION public.sync_role_to_auth_meta() FROM anon, authenticated;
```

**Pitfall:** Si haces `REVOKE ... FROM authenticated` en las funciones helper, las RLS policies fallan con `permission denied for function`. El rol `authenticated` NECESITA EXECUTE para que las policies puedan invocar las funciones internamente.

## Diagnóstico: Cómo Detectar Recursión

```sql
-- Simular query como usuario autenticado
SET LOCAL role authenticated;
SET LOCAL request.jwt.claims TO '{"sub":"<user-uuid>","role":"authenticated"}';
SELECT * FROM profiles WHERE auth_id = '<user-uuid>';
-- Si retorna "infinite recursion detected in policy" → tienes el bug

-- Buscar TODAS las policies que referencian profiles (directa o indirectamente)
SELECT tablename, policyname, cmd, qual
FROM pg_policies
WHERE schemaname = 'public'
  AND (qual ILIKE '%profiles%' OR with_check ILIKE '%profiles%')
ORDER BY tablename;

-- Buscar funciones que consultan profiles
SELECT proname, prosrc
FROM pg_proc
WHERE prosrc ILIKE '%profiles%' AND pronamespace = 'public'::regnamespace;
```

## Regla de Oro

**Ninguna policy de RLS en tabla X debe contener un subquery o JOIN a la tabla X.** Ni directa ni indirectamente (a través de otra tabla que también referencia X en sus policies).

Si una policy necesita datos de otra fila de la misma tabla (ej: "staff puede ver líderes asignados"), extraer esos datos a `auth.users.raw_app_meta_data` o a una tabla de mapeo separada sin RLS.

## Verificación Post-Fix

1. `SET LOCAL role authenticated` + query → debe retornar filas (no error de recursión)
2. Admin puede ver todos los profiles
3. Lider solo ve su propio profile
4. Staff ve su profile + los líderes asignados
5. `get_advisors(type='security')` → sin nuevos warnings de recursion
6. Login end-to-end desde el browser → profile carga correctamente
