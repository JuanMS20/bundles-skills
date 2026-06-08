# Supabase Patterns — Auth, RLS, Storage, React

Patrones verificados en migración real (NOVVA VALLE, jun 2026). Supabase Free tier.

## 1. Auth con username/password (no email)

Cuando los usuarios no tienen email real (líderes de campo, staff operativo):

### Estrategia: email ficticio

```typescript
// Registro
const { data, error } = await supabase.auth.signUp({
  email: `${username}@app.local`,  // email ficticio
  password: password,
  options: {
    data: {
      username: username,
      display_name: nombre,
      role: 'lider'  // o 'staff', 'admin'
    }
  }
})

// Login
const { data, error } = await supabase.auth.signInWithPassword({
  email: `${username}@app.local`,
  password: password
})
```

### Notas

- Supabase requiere email para auth interna, pero nunca se envía al usuario
- El dominio `app.local` no existe → no hay riesgo de colisión
- `user_metadata` almacena username y role para acceso rápido
- Para buscar usuarios por username: usar tabla `profiles` con UNIQUE en `username`

### Crear admin inicial

```sql
-- Via SQL directo en Supabase Dashboard > SQL Editor
INSERT INTO auth.users (id, email, encrypted_password, email_confirmed_at)
VALUES (
  gen_random_uuid(),
  'admin@app.local',
  crypt('password_seguro', gen_salt('bf')),
  now()
);
```

**Pitfall**: No intentar crear auth users desde el frontend para el seed inicial. Usar SQL Editor del dashboard.

## 2. RLS Multi-Rol

### Patrón: role en tabla profiles

```sql
CREATE TABLE profiles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_id uuid UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
  username text UNIQUE NOT NULL,
  nombre text NOT NULL,
  role text NOT NULL CHECK (role IN ('admin', 'staff', 'lider')),
  created_at timestamptz DEFAULT now()
);

-- Función helper para obtener role actual
CREATE OR REPLACE FUNCTION get_user_role()
RETURNS text AS $$
  SELECT role FROM profiles WHERE auth_id = auth.uid()
$$ LANGUAGE sql SECURITY DEFINER STABLE;

CREATE OR REPLACE FUNCTION get_profile_id()
RETURNS uuid AS $$
  SELECT id FROM profiles WHERE auth_id = auth.uid()
$$ LANGUAGE sql SECURITY DEFINER STABLE;
```

### Políticas RLS por tabla

```sql
-- PROFILES
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "admin_full_access" ON profiles
  FOR ALL USING (get_user_role() = 'admin');

CREATE POLICY "staff_read_profiles" ON profiles
  FOR SELECT USING (get_user_role() IN ('staff', 'admin'));

CREATE POLICY "lider_own_profile" ON profiles
  FOR ALL USING (auth_id = auth.uid());

-- CONTACTS
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "admin_contacts" ON contacts
  FOR ALL USING (get_user_role() = 'admin');

CREATE POLICY "staff_contacts" ON contacts
  FOR SELECT USING (
    get_user_role() = 'staff' AND
    lider_id IN (
      SELECT lider_id FROM staff_leaders WHERE staff_id = get_profile_id()
    )
  );

CREATE POLICY "lider_contacts" ON contacts
  FOR ALL USING (lider_id = get_profile_id());
```

### Validación de cédula única

```sql
CREATE OR REPLACE FUNCTION check_cedula_unique()
RETURNS TRIGGER AS $$
BEGIN
  IF EXISTS (SELECT 1 FROM contacts WHERE cedula = NEW.cedula) THEN
    RAISE EXCEPTION 'Esta cédula ya está registrada. Contacte un administrador.'
      USING ERRCODE = 'unique_violation';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cedula_unique
  BEFORE INSERT ON contacts
  FOR EACH ROW EXECUTE FUNCTION check_cedula_unique();
```

**Pitfall**: UNIQUE constraint en `cedula` da error genérico. El trigger da mensaje amigable. Usar AMBOS.

## 3. Supabase Storage

### Bucket setup

```sql
INSERT INTO storage.buckets (id, name, public)
VALUES ('certificados', 'certificados', true);
```

### Upload desde React

```typescript
async function uploadCertificado(contactId: string, file: File) {
  const profileId = getProfileId()
  const filePath = `${profileId}/${contactId}-${file.name}`

  const { error } = await supabase.storage
    .from('certificados')
    .upload(filePath, file, { upsert: true })

  if (error) throw error

  const { data: urlData } = supabase.storage
    .from('certificados')
    .getPublicUrl(filePath)

  await supabase.from('contacts')
    .update({ certificado_url: urlData.publicUrl })
    .eq('id', contactId)
}
```

### Visor inline

```tsx
function CertificadoViewer({ url }: { url: string }) {
  if (!url) return <span>Sin certificado</span>
  if (/\.(jpg|jpeg|png|gif|webp)$/i.test(url))
    return <img src={url} alt="Certificado" style={{ maxWidth: '100%' }} />
  if (/\.pdf$/i.test(url))
    return <iframe src={url} style={{ width: '100%', height: '70vh', border: 'none' }} />
  return <a href={url} target="_blank">Ver certificado</a>
}
```

## 4. React + Vite + Supabase

### Setup

```bash
npm create vite@latest . -- --template react-ts
npm install @supabase/supabase-js
```

### Cliente singleton

```typescript
// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'
export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)
```

**Pitfall**: `VITE_` prefix es obligatorio. Sin él, la variable no existe en `import.meta.env`.

## 5. Migración desde Excel/Sheets

1. Exportar a CSV
2. Script Node.js con `@supabase/supabase-js` (service_role key, bypass RLS)
3. Leer CSV → transformar → insertar en batch
4. Log de errores (duplicados, FK inválidas)

**Pitfall**: `service_role` key bypass RLS. Solo en scripts de migración, NUNCA en frontend.

## 6. Geodata cascade hook

```typescript
function useGeoCascade() {
  const [dept, setDept] = useState<string | null>(null)
  const [mun, setMun] = useState<string | null>(null)

  const depts = useQuery(['departments'], () =>
    supabase.from('geo_departments').select('*').order('name'))

  const muns = useQuery(['municipalities', dept], () =>
    supabase.from('geo_municipalities').select('*').eq('dept_code', dept).order('name'),
    { enabled: !!dept })

  const stations = useQuery(['stations', mun], () =>
    supabase.from('geo_voting_stations').select('*').eq('mun_code', mun).order('name'),
    { enabled: !!mun })

  return {
    departments: depts?.data ?? [],
    municipalities: muns?.data ?? [],
    stations: stations?.data ?? [],
    dept, setDept: (v) => { setDept(v); setMun(null) },
    mun, setMun
  }
}
```
