# Crear usuarios via SQL directo (MCP execute_sql)

Cuando necesitas crear usuarios iniciales (admin, staff) y no tienes Edge Functions ni UI de signup. Usa `mcp_supabase_execute_sql` o el SQL Editor del Dashboard.

**ACTUALIZADO 2026-06-06:** Cost factor bcrypt corregido a 10, todas las columnas string NULL → '', insert en `auth.identities` agregado. Verificado end-to-end con login exitoso.

## SQL template verificado

```sql
-- Paso 1: Crear el usuario en auth.users
-- CRÍTICO: gen_salt('bf', 10) — GoTrue espera bcrypt cost 10, NO el default 6
-- CRÍTICO: Todas las columnas string DEBEN ser '' (empty string), NO NULL
-- CRÍTICO: confirmed_at es GENERATED COLUMN — NO incluir en el INSERT
INSERT INTO auth.users (
  instance_id,
  id,
  aud,
  role,
  email,
  encrypted_password,
  email_confirmed_at,
  raw_app_meta_data,
  raw_user_meta_data,
  is_sso_user,
  is_anonymous,
  created_at,
  updated_at,
  last_sign_in_at,
  confirmation_token,
  recovery_token,
  email_change_token_new,
  email_change,
  email_change_token_current,
  reauthentication_token,
  phone,
  phone_change,
  phone_change_token
) VALUES (
  '00000000-0000-0000-0000-000000000000',
  gen_random_uuid(),
  'authenticated',
  'authenticated',
  'admin@tudominio.local',
  crypt('password123', gen_salt('bf', 10)),   -- cost 10, NO 6
  now(),
  '{"provider":"email","providers":["email"]}',
  '{}',
  false,
  false,
  now(),
  now(),
  now(),
  '', '', '', '', '', '', '', '', ''           -- TODAS las strings a ''
)
RETURNING id, email;
```

```sql
-- Paso 2: Crear el identity record (SIN ESTO GoTrue NO encuentra el usuario)
INSERT INTO auth.identities (
  provider_id, user_id, identity_data, provider,
  last_sign_in_at, created_at, updated_at
) VALUES (
  'admin@tudominio.local',
  (SELECT id FROM auth.users WHERE email = 'admin@tudominio.local'),
  jsonb_build_object(
    'sub', (SELECT id FROM auth.users WHERE email = 'admin@tudominio.local'),
    'email', 'admin@tudominio.local'
  ),
  'email',
  now(), now(), now()
);
```

```sql
-- Paso 3: Crear el profile vinculado
-- Verificar los campos NOT NULL reales del schema antes de insertar
INSERT INTO profiles (auth_id, username, nombre, role)
VALUES (
  (SELECT id FROM auth.users WHERE email = 'admin@tudominio.local'),
  'admin',
  'Administrador',
  'admin'
);
```

## Pitfalls criticos (aprendidos en produccion)

### 1. GoTrue NULL string scan error (HTTP 500)

**Síntoma:** Login devuelve HTTP 500 `"Database error querying schema"`. Sin errores en consola del navegador.

**Causa raíz:** GoTrue está escrito en Go. Los structs que mapean `auth.users` usan tipo `string` (no `*string`) para columnas como `confirmation_token`, `recovery_token`, etc. Un SQL INSERT directo deja estas columnas en NULL. El scanner de Go no puede convertir NULL a `string` → panic → HTTP 500.

**Log real del error (visible via `mcp_supabase_get_logs(service='auth')`):**
```
error finding user: sql: Scan error on column index 3,
name "confirmation_token": converting NULL to string is unsupported
```

**Fix:** `COALESCE(column, '')` en todas las columnas string, o setearlas a `''` en el INSERT.

### 2. bcrypt cost factor

`gen_salt('bf')` sin segundo argumento usa cost factor **6**. GoTrue espera cost factor **10** (`$2a$10$`).

**Fix:** `gen_salt('bf', 10)`. Si usas cost 6, el hash se genera como `$2a$06$` y GoTrue puede rechazarlo.

### 3. auth.identities table

GoTrue requiere un registro en `auth.identities` para cada usuario. El endpoint de signup oficial lo crea automáticamente, pero un INSERT SQL directo NO. Sin este registro, el login falla.

### 4. confirmed_at es GENERATED COLUMN

`confirmed_at` es una columna generada a partir de `email_confirmed_at`. NO se puede INSERTAR directamente — Postgres lanza: `cannot insert a non-DEFAULT value into column "confirmed_at"`.

### 5. Columnas string completas que necesitan ''

Lista exhaustiva (verificada contra GoTrue v2.189.0):
- `confirmation_token`
- `recovery_token`
- `email_change_token_new`
- `email_change`
- `email_change_token_current`
- `reauthentication_token`
- `phone`
- `phone_change`
- `phone_change_token`

## Debugging: cuando el login SQL-created user falla

1. **Probar via curl primero** (más rápido que navegador):
```bash
curl -s -X POST "https://PROJECT_REF.supabase.co/auth/v1/token?grant_type=password" \
  -H "apikey: ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@tudominio.local","password":"password123"}'
```

2. **Si devuelve HTTP 500:** Leer auth logs:
```
mcp_supabase_get_logs(service='auth')
```
Buscar el campo `error` en los JSON de nivel `error`. El mensaje real revela la causa exacta.

3. **Si devuelve 400 `email_address_invalid`:** El dominio `.local` es rechazado por el endpoint público de signup. Pero funciona en login (`/token`) y en INSERT SQL directo. Solo el signup público valida el formato del email.

4. **Si devuelve 401 `invalid_credentials`:** Password hash incorrecto. Verificar que `crypt(password, encrypted_password)` devuelve true:
```sql
SELECT crypt('password123', encrypted_password) = encrypted_password as match
FROM auth.users WHERE email = 'admin@tudominio.local';
```

## Fix rapido para user ya creado con NULLs

Si ya insertaste el usuario y login falla con 500:

```sql
UPDATE auth.users SET
  confirmation_token = COALESCE(confirmation_token, ''),
  recovery_token = COALESCE(recovery_token, ''),
  email_change_token_new = COALESCE(email_change_token_new, ''),
  email_change = COALESCE(email_change, ''),
  email_change_token_current = COALESCE(email_change_token_current, ''),
  reauthentication_token = COALESCE(reauthentication_token, ''),
  phone = COALESCE(phone, ''),
  phone_change = COALESCE(phone_change, ''),
  phone_change_token = COALESCE(phone_change_token, '')
WHERE email = 'admin@tudominio.local';
```

## Password Reset via SQL

Cuando necesitas resetear la contraseña de un usuario existente (olvidada, seed de testing, acceso de emergencia). Mucho más simple que la creacion — solo se actualiza una columna.

```sql
UPDATE auth.users
SET encrypted_password = crypt('nuevaPassword123', gen_salt('bf', 10))
WHERE email = 'admin@tudominio.local';
```

**Cost factor:** Usar `gen_salt('bf', 10)` — cost 10, consistente con GoTrue. `gen_salt('bf')` sin argumento usa cost 6, que TECNICAMENTE FUNCIONA para login (bcrypt lee el cost del hash prefix al verificar, no requiere un cost fijo), pero es mas debil. Siempre usar 10.

### Reset masivo (todos los usuarios de un rol)

```sql
UPDATE auth.users
SET encrypted_password = crypt('pass123', gen_salt('bf', 10))
WHERE email IN (
  SELECT u.email FROM auth.users u
  JOIN profiles p ON p.auth_id = u.id
  WHERE p.role = 'lider'
);
```

### Verificacion post-reset

```sql
SELECT email,
       substring(encrypted_password, 1, 7) as hash_prefix,  -- debe ser '$2a$10$'
       crypt('nuevaPassword123', encrypted_password) = encrypted_password as match
FROM auth.users
WHERE email = 'admin@tudominio.local';
-- match = true: password correcta, lista para login
```

### No tocar auth.identities ni otras tablas

A diferencia de la creacion, el reset solo modifica `auth.users.encrypted_password`. No hay que tocar `auth.identities`, `profiles`, ni columnas string NULL. La sesion JWT existente NO se invalida automaticamente — el usuario con sesion activa no sera expulsado hasta que su JWT expire o haga signOut.

## Verificacion post-creacion

```sql
SELECT u.email,
       u.email_confirmed_at IS NOT NULL as confirmed,
       substring(u.encrypted_password, 1, 7) as hash_prefix,  -- debe ser '$2a$10$'
       p.username, p.role,
       EXISTS(SELECT 1 FROM auth.identities i WHERE i.user_id = u.id) as has_identity
FROM auth.users u
JOIN profiles p ON p.auth_id = u.id
WHERE u.email = 'admin@tudominio.local';
```

## Contexto

Alternativa a Dashboard manual y Edge Functions. Util para:
- Seed de usuarios iniciales en deploy
- Creacion masiva de usuarios staff/lideres
- Testing con roles especificos

Limitacion: no escala para produccion (sin rate limiting, sin email verification real, sin password policy). Para produccion, migrar a Edge Function con service_role.
