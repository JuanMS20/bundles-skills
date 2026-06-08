---
title: PostgreSQL Audit Log con Triggers
impact: HIGH
impactDescription: Audit trail completo de INSERT/UPDATE/DELETE con diff de cambios, solo visible para admin.
tags: security, audit, triggers, rls, supabase, postgresql
---

# Audit Log con PostgreSQL Triggers

Patrón completo para registrar quién hizo qué, cuándo, y qué cambió — sin modificar la aplicación.

## Cuándo aplicar

- Cualquier sistema con datos sensibles (electoral, financiero, salud)
- Cuando se necesita trazabilidad de cambios para compliance
- Cuando el usuario pide "saber quién hizo qué"

## Implementación

### 1. Tabla audit_logs

```sql
CREATE TABLE audit_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  table_name text NOT NULL,
  record_id text NOT NULL,
  action text NOT NULL CHECK (action IN ('INSERT','UPDATE','DELETE')),
  old_data jsonb,
  new_data jsonb,
  changed_by uuid REFERENCES profiles(id),
  changed_at timestamptz NOT NULL DEFAULT now()
);

-- Índices para consultas frecuentes
CREATE INDEX idx_audit_logs_table_name ON audit_logs(table_name);
CREATE INDEX idx_audit_logs_changed_at ON audit_logs(changed_at DESC);
CREATE INDEX idx_audit_logs_changed_by ON audit_logs(changed_by);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
```

### 2. RLS: solo admin lee

```sql
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "audit_logs_admin_select" ON audit_logs
  FOR SELECT
  USING (get_user_role() = 'admin');
```

### 3. Trigger function (SECURITY DEFINER)

```sql
CREATE OR REPLACE FUNCTION log_audit_change()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_record_id text;
  v_changed_by uuid;
BEGIN
  IF TG_OP = 'DELETE' THEN
    v_record_id := OLD.id::text;
  ELSE
    v_record_id := NEW.id::text;
  END IF;

  -- Resolver quién hizo el cambio (auth.uid() → profiles.id)
  SELECT id INTO v_changed_by
  FROM profiles
  WHERE auth_id = auth.uid();

  IF TG_OP = 'INSERT' THEN
    INSERT INTO audit_logs (table_name, record_id, action, new_data, changed_by)
    VALUES (TG_TABLE_NAME, v_record_id, 'INSERT', to_jsonb(NEW), v_changed_by);
  ELSIF TG_OP = 'UPDATE' THEN
    INSERT INTO audit_logs (table_name, record_id, action, old_data, new_data, changed_by)
    VALUES (TG_TABLE_NAME, v_record_id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), v_changed_by);
  ELSIF TG_OP = 'DELETE' THEN
    INSERT INTO audit_logs (table_name, record_id, action, old_data, changed_by)
    VALUES (TG_TABLE_NAME, v_record_id, 'DELETE', to_jsonb(OLD), v_changed_by);
  END IF;

  RETURN COALESCE(NEW, OLD);
END;
$$;
```

### 4. Permisos (PITFALL: Supabase)

```sql
-- SIEMPRE revoke de PUBLIC + anon + authenticated (no solo PUBLIC)
REVOKE EXECUTE ON FUNCTION log_audit_change() FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION log_audit_change() TO service_role;
```

Ver pitfall en `references/security-definer-functions.md` sección "Pitfall: REVOKE FROM PUBLIC Does NOT Remove anon/authenticated".

### 5. Aplicar triggers

```sql
-- En cada tabla que quieras auditar
CREATE TRIGGER audit_profiles
  AFTER INSERT OR UPDATE OR DELETE ON profiles
  FOR EACH ROW EXECUTE FUNCTION log_audit_change();

CREATE TRIGGER audit_contacts
  AFTER INSERT OR UPDATE OR DELETE ON contacts
  FOR EACH ROW EXECUTE FUNCTION log_audit_change();

CREATE TRIGGER audit_staff_leaders
  AFTER INSERT OR UPDATE OR DELETE ON staff_leaders
  FOR EACH ROW EXECUTE FUNCTION log_audit_change();
```

## Frontend: mostrar audit log

### Datos a mostrar
- **Acción**: badge con color (INSERT=verde, UPDATE=ámbar, DELETE=rojo)
- **Tabla**: qué tabla se modificó
- **Quién**: join con profiles para mostrar nombre
- **Cuándo**: timestamp formateado
- **Diff**: para UPDATE, mostrar solo campos cambiados (comparar old_data vs new_data)

### Filtros recomendados
- Por tabla (dropdown)
- Por acción (dropdown)
- Por usuario (si hay muchos registros)
- Por rango de fechas

### Verificación de cambios (diff)

```typescript
function getChangedFields(oldData: Record<string, unknown> | null, newData: Record<string, unknown> | null): string[] {
  if (!oldData || !newData) return []
  const keys = new Set([...Object.keys(oldData), ...Object.keys(newData)])
  return [...keys].filter(key => JSON.stringify(oldData[key]) !== JSON.stringify(newData[key]))
}
```

## Consideraciones

- **Performance**: Los triggers son AFTER INSERT/UPDATE/DELETE, no bloquean la operación original. jsonb es eficiente para almacenar diffs.
- **Storage**: El campo `new_data` puede crecer mucho si la tabla tiene muchas columnas. Considerar LIMIT 200 en queries.
- **Cascada**: Si una UPDATE dispara un trigger que hace otra UPDATE, ambas se registran.
- **Operaciones directas SQL**: `changed_by` será NULL si se ejecuta SQL directo (sin auth.uid()). Esto es correcto — muestra "Sistema" en el frontend.
- **Tests**: Los triggers no se pueden testear desde el frontend directamente. Verificar con queries SQL directas después de operaciones CRUD.

## Referencias

- https://www.postgresql.org/docs/current/plpgsql-trigger.html
- https://supabase.com/docs/guides/auth/row-level-security
- https://supabase.com/docs/guides/database/database-linter
