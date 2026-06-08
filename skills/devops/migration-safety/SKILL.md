---
name: migration-safety
description: "Patrones para migraciones DB que no rompen producción. Expand/contract, lista negra de operaciones peligrosas, rollback strategy, feature flags. Use when: migración de base de datos, cambio de schema, ALTER TABLE, rollback de deploy, 'no quiero romper producción', deploy con DB."
---

# MIGRATION SAFETY — Migraciones que no rompen producción

## Principio: Una migración mala = datos perdidos = app muerta.

La IA genera migraciones como si fuera código normal.
Pero las migraciones son irreversibles por naturaleza: DROP COLUMN
borra datos que no se pueden recuperar. Tu trabajo es asegurar
que cada migración sea segura, reversible y sin downtime.

## Cuándo aplicar esta skill

- Cualquier cambio al schema de DB (tablas, columnas, tipos, constraints)
- Deploy que incluye cambios de DB
- Feature nueva que requiere nueva tabla/columna
- Refactor que cambia estructura de datos existente

## FASE 0 — Detectar sistema de migraciones

| Herramienta | Cómo detectar | Comando de migración |
|-------------|---------------|---------------------|
| Supabase | `supabase/migrations/` dir | `supabase db push` / `supabase migration up` |
| Prisma | `prisma/schema.prisma` | `npx prisma migrate deploy` |
| Django | `migrations/` en cada app | `python manage.py migrate` |
| Rails | `db/migrate/` | `rails db:migrate` |
| Alembic | `alembic/` dir | `alembic upgrade head` |
| Knex | `knexfile.js` | `npx knex migrate:latest` |
| Raw SQL | scripts sueltos | Ejecución manual |

Si NO hay sistema de migraciones: ESTO ES UN PROBLEMA.
Declarar "Proyecto sin migraciones versionadas. Schema changes son no trackeados."

## FASE 1 — Clasificar el cambio

Antes de escribir la migración, clasificar el riesgo:

### Verdes (seguras, no bloquean)
- ADD COLUMN con DEFAULT o NULLABLE
- CREATE TABLE nueva
- CREATE INDEX (con CONCURRENTLY si hay datos)
- ADD CONSTRAINT CHECK con NOT VALID + VALIDATE separado

### Amarillas (precaución, requieren plan)
- ALTER COLUMN TYPE (puede reescribir toda la tabla)
- ADD COLUMN NOT NULL (sin default, bloquea en tablas grandes)
- CREATE INDEX sin CONCURRENTLY (bloquea escrituras)

### ROJAS (PELIGRO — requieren expand/contract o rechazar)
- DROP COLUMN
- DROP TABLE
- RENAME COLUMN/TABLE
- ALTER TYPE que cambia semántica (int -> string)
- NOT NULL constraint en columna con datos existentes

## FASE 2 — Patrón Expand/Contract (zero-downtime)

Para cambios ROJOS o AMARILLOS. Se ejecuta en 2+ deploys:

### Ejemplo: renombrar columna `usr_name` a `username`

**DEPLOY 1 (Expand):**
```sql
-- Añadir nueva columna
ALTER TABLE users ADD COLUMN username TEXT;
-- Copiar datos
UPDATE users SET username = usr_name;
-- App escribe en AMBAS columnas (legacy + nueva)
```

**DEPLOY 2 (Migración de código):**
```sql
-- App ahora solo lee/escribe 'username'
-- Backfill completado en deploy 1
```

**DEPLOY 3 (Contract):**
```sql
-- Solo cuando estés 100% seguro que nada usa usr_name
ALTER TABLE users DROP COLUMN usr_name;
```

### Ejemplo: cambiar tipo de columna (int a text)

**Expand:** añadir columna nueva de tipo text
**Backfill:** copiar datos casteando
**Migrate code:** app usa columna nueva
**Contract:** drop columna vieja

## FASE 3 — Rollback Strategy

Cada migración debe tener un plan de rollback. Preguntar:

### ¿Se puede revertir automáticamente?

| Sistema | Rollback automático | Comando |
|---------|-------------------|---------|
| Prisma | NO (solo forward) | N/A |
| Django | SÍ si migration lo define | `manage.py migrate app 0004` |
| Rails | SÍ si `def down` existe | `rails db:rollback` |
| Alembic | SÍ si `downgrade()` existe | `alembic downgrade -1` |
| Supabase | NO nativo | Manual SQL revert |
| Raw SQL | NO | Manual |

### Si NO hay rollback automático:
Documentar SQL exacto para revertir, hacer backup antes de migrar, tener rollback SQL listo.

Template: guardar junto a cada migración `-- Rollback: ALTER TABLE users DROP COLUMN IF EXISTS username;`

## FASE 4 — Supabase específico

Comandos: `supabase migration list` (pendientes), `supabase db push` (aplicar), `supabase db push --dry-run` (simular).

Reglas críticas:
- auth.users: NUNCA modificar schema. Para datos extra: tabla `profiles` con FK a auth.users.id
- `supabase db reset`: ¡DESTRUCTIVO! Solo dev
- RLS policies: tener policy nueva lista ANTES de drop la vieja

## FASE 5 — Checklist pre-deploy

Antes de ejecutar cualquier migración en producción:

- [ ] ¿La migración usa expand/contract para operaciones ROJAS?
- [ ] ¿Hay backup de las tablas afectadas?
- [ ] ¿Hay rollback SQL documentado y listo?
- [ ] ¿Se probó la migración en un entorno staging/dev?
- [ ] ¿La app funciona con el schema viejo Y el nuevo (durante expand)?
- [ ] ¿No hay DROP/RENAME sin transición?
- [ ] ¿Los CREATE INDEX usan CONCURRENTLY en tablas con datos?
- [ ] ¿El dry-run pasa sin errores?

Si CUALQUIER item falla: NO DESPLEGAR.

## FASE 6 — Feature Flags

Para desactivar una feature en producción sin redeployar:

- **Nivel 1**: Variable de entorno (`FEATURE_NEW_LOGIN=false`). Requiere redeploy.
- **Nivel 2**: Tabla `feature_flags(key TEXT PK, enabled BOOLEAN)` en DB. Cambiable via SQL.
- **Nivel 3**: Por usuario (`key, user_id, enabled`). Rollout gradual.

Regla: feature nueva en producción -> DEBE tener feature flag.

## Formato de Veredicto

```
## VEREDICTO MIGRATION SAFETY

### Sistema: [Supabase / Prisma / Django / etc.]
### Riesgo: [VERDE / AMARILLO / ROJO]

### Cambios detectados:
1. [operación] — tabla/columna — riesgo: [VERDE/AMARILLO/ROJO]

### Expand/Contract:
- Requerido: [SÍ/NO]
- Deploys necesarios: [N]

### Rollback:
- Automático: [SÍ/NO]
- SQL documentado: [SÍ/NO]
- Backup: [SÍ/NO]

### Veredicto: [SEGURO PARA DESPLEGAR / REQUIERE PLAN / NO DESPLEGAR]
```

## Pitfalls

### Prisma migrate reset borra todo
`npx prisma migrate reset` en producción borra TODA la data. NUNCA ejecutar en prod.
Si se ejecuta por accidente: restaurar desde backup inmediatamente.

### ALTER COLUMN TYPE bloquea la tabla
En Postgres, `ALTER TABLE ... ALTER COLUMN ... TYPE` reescribe toda la tabla.
En producción con millones de filas, bloquea TODO por minutos u horas.
Usar expand/contract o crear columna nueva.

### CREATE INDEX bloquea escrituras
`CREATE INDEX` sin `CONCURRENTLY` bloquea INSERT/UPDATE/DELETE hasta terminar.
Usar `CREATE INDEX CONCURRENTLY` (toma más tiempo pero no bloquea).

### Migración pasa en dev, falla en prod
Dev DB tiene 10 filas. Prod tiene 10 millones. Lo que toma 0.1s en dev
puede tomar horas en prod. Siempre probar con datos grandes o declarar
el riesgo explícitamente.
