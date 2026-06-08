# Cross-Service Rename / Rebrand Audit

Cuando el usuario pide renombrar un proyecto (rebrand, rename de dominio, cambio de nombre), hay 3 capas con riesgos distintos. Este patrón sistematiza el inventario ANTES de tocar nada.

## Capa 1 — Código (bajo riesgo)

Find-replace directo. Inventario por archivo:

```
search_files(pattern="NOMBRE_VIEJO")  →  todos los archivos
```

Archivos típicos a revisar:
- `package.json` — name del proyecto
- `index.html` — title
- `src/**/*.ts` / `src/**/*.tsx` — constantes de dominio, imports, strings
- `supabase/functions/**/*` — CORS origins, dominios internos
- `*.md` — README, PRD, CONTEXT, docs
- `.env.local` / `.env.example` — URLs de servicios
- `wrangler.toml` / `wrangler.json` — Cloudflare config
- `dist/**` — build artifacts (ignorar, se regenera)

## Capa 2 — Servicios Externos (requiere intervención manual)

| Servicio | Qué buscar | Dónde cambiar |
|----------|-----------|---------------|
| GitHub | Repo name, topics, description | Settings → General → Rename (auto-redirect old URL) |
| Cloudflare Pages | Project name, custom domains | Dashboard → Settings → Change project name |
| Supabase | Project name, Edge Function CORS | Dashboard → Settings; Edge Function source |
| Vercel | Project name | Dashboard → Settings |
| Netlify | Site name | Dashboard → Site settings |

**Pitfall:** Cloudflare Pages renombre el dominio automáticamente (`old.pages.dev` → `new.pages.dev`). Pero los preview deployments viejos (`.hash.old.pages.dev`) quedan muertos. Si hay links compartidos, notificar al usuario.

## Capa 3 — Base de Datos (alto riesgo)

El más peligroso. Si hay emails, URLs, o datos con el nombre viejo:

1. **Contar registros afectados:**
   ```sql
   SELECT COUNT(*) FROM auth.users WHERE email LIKE '%@OLD_DOMAIN';
   ```

2. **Migrar datos:**
   ```sql
   -- BACKUP primero
   CREATE TABLE auth_users_backup AS SELECT * FROM auth.users;
   
   -- UPDATE emails
   UPDATE auth.users SET email = REPLACE(email, '@old.local', '@new.local');
   
   -- Verificar
   SELECT email FROM auth.users WHERE email LIKE '%@new.local';
   ```

3. **Edge Functions / RLS:** Si CORS o policies referencian el dominio viejo, actualizar antes del deploy.

**Pitfall crítico:** Si cambias AUTH_DOMAIN en código SIN migrar la DB, los usuarios existentes NO pueden loguearse. La app rompe silenciosamente — no da error claro.

## Checklist de Renombro

```markdown
## RENAME AUDIT: [viejo] → [nuevo]

### Capa 1 — Código
- [ ] package.json name
- [ ] index.html title
- [ ] src/ constants (AUTH_DOMAIN, etc.)
- [ ] supabase/functions/ CORS origins
- [ ] *.md documentation
- [ ] .env URLs

### Capa 2 — Servicios
- [ ] GitHub repo renamed
- [ ] Cloudflare Pages project renamed
- [ ] Supabase project renamed
- [ ] Dominio DNS apuntando a nuevo nombre

### Capa 3 — Datos
- [ ] auth.users emails migrados
- [ ] Profiles/otros registros actualizados
- [ ] Edge Function CORS actualizado
- [ ] Tests corriendo con nuevo dominio
- [ ] Deploy exitoso + verificación
```

## Orden de ejecución

1. Auditar (inventario completo)
2. Code changes (Capa 1)
3. DB migration (Capa 3) — ANTES del deploy
4. Deploy código
5. Servicios externos (Capa 2) — puede ser después del deploy
6. Verificación: login, CORS, URLs
