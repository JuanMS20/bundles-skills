# Supabase auth.admin Pitfall — Frontend vs Server

## El problema

Descubierto en sesión de code review de NOVVA VALLE (2026-06-06). Tres llamadas a `supabase.auth.admin.*` desde el frontend:

- `Lideres.tsx`: `supabase.auth.admin.createUser({ email, password })`
- `Staff.tsx`: `supabase.auth.admin.createUser({ email, password })`
- `Credenciales.tsx`: `supabase.auth.admin.updateUserById(authId, { password })`

Estos métodos requieren la **service_role key**. El cliente frontend usa la **anon key**. Resultado: las llamadas fallan silenciosamente o con error de permisos en runtime.

## Por qué ocurre

Supabase JS client tiene dos modos:
1. **anon key** (frontend): respeta RLS, no puede gestionar usuarios admin-level
2. **service_role key** (server): bypass RLS, acceso total incluyendo `auth.admin.*`

La doc de `@supabase/supabase-js` lista `auth.admin` como disponible, pero no aclara que requiere service_role. Es fácil escribir el código correcto sintácticamente pero fundamentalmente roto.

## Señales de detección

- Código que crea usuarios desde React/Vue/etc. con `auth.admin.createUser`
- Reset de password desde frontend con `auth.admin.updateUserById`
- Cualquier `auth.admin.*` en archivos bajo `src/` o `client/`

## Solución 1: Edge Function user-admin (recomendado)

Template completo y verificado en `templates/edge-function-user-admin.ts`. Desplegar via:
```
mcp_supabase_deploy_edge_function(name='user-admin', verify_jwt=true)
```

Puntos criticos del template verificado:

1. **Verificacion de caller**: El Edge Function recibe el JWT del caller, crea un cliente user-side, y verifica que su `profile.role === 'admin'`. Sin esto, cualquiera puede crear usuarios.

2. **Rollback en fallo**: Si el INSERT en `profiles` falla tras crear el auth user, se elimina el auth user para evitar huerfanos:
```typescript
if (profileError) {
  await adminClient.auth.admin.deleteUser(authData.user.id);
  throw new Error(profileError.message);
}
```

3. **Multi-action**: Un solo Edge Function maneja create-user y reset-password via `body.action`. Mas limpio que deployar funciones separadas.

4. **GoTrue NULL fix (best-effort)**: Si se creo via `auth.admin.createUser`, GoTrue setea defaults razonables. Pero si el usuario fue creado via SQL directo, las columnas string quedan NULL. Llamar `fix_user_null_columns` RPC como best-effort.

5. **RPC helper en DB**: Crear antes de deployar:
```sql
CREATE OR REPLACE FUNCTION public.fix_user_null_columns(user_email text)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
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
  WHERE email = user_email;
END;
$$;
```

Desde el frontend:
```typescript
// Crear lider/staff
const { error } = await supabase.functions.invoke('user-admin', {
  body: { action: 'create-user', username, password, role: 'lider', profile: { nombre, ... } }
})

// Reset password
const { error } = await supabase.functions.invoke('user-admin', {
  body: { action: 'reset-password', authId, newPassword }
})
```

### Pitfall: Deno .catch() en RPC no funciona

En el runtime de Deno (Edge Functions), `adminClient.rpc(...).catch()` falla con `"rpc(...).catch is not a function"`. SIEMPRE usar try/catch para llamadas RPC best-effort:
```typescript
// MAL
await adminClient.rpc("fix_user_null_columns", { user_email }).catch(() => {})

// BIEN
try {
  await adminClient.rpc("fix_user_null_columns", { user_email });
} catch {
  // Non-critical
}
```

## Solución 2: Dashboard (temporal)

Para proyectos sin Edge Functions configuradas:
1. Crear usuarios desde Supabase Dashboard → Authentication → Users → Add user
2. Insertar profile manualmente en Table Editor o SQL Editor
3. Funcional pero no escalable — solo para setup inicial o apps pequeñas

## Solución 3: signUp desde el cliente (limitado)

```typescript
const { data, error } = await supabase.auth.signUp({
  email,
  password,
})
```

Limitaciones:
- El usuario se crea con sesión activa (no queremos eso para creación admin)
- No permite asignar metadatos arbitrarios que persistan en profiles sin trigger adicional
- El usuario debe confirmar email (a menos que se desactive en Dashboard)

## Trigger de Profile Creation

Independientemente de la solución elegida, se necesita un trigger para crear el profile automáticamente cuando se crea un usuario auth:

```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (auth_id, username, nombre, role)
  VALUES (
    NEW.id,
    split_part(NEW.email, '@', 1),  -- username del email sintético
    split_part(NEW.email, '@', 1),
    'lider'  -- role por defecto
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

## Lección

Cuando uses Supabase, antes de escribir cualquier operación de gestión de usuarios, pregúntate:
1. ¿Esta operación usa `auth.admin.*`?
2. ¿Está este código en el frontend?
3. Si ambas son sí → mover a Edge Function

Code review siempre debe grep por `auth.admin` en archivos frontend.
