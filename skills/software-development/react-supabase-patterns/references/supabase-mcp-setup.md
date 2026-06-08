# Supabase MCP Server Setup

El MCP server oficial de Supabase permite gestionar proyectos (SQL, migrations, Edge Functions, auth, advisor) desde el agente. Es HTTP remoto con OAuth 2.1 PKCE — no stdio.

## Configuración en Hermes

```yaml
# config.yaml → mcp_servers
supabase:
  url: https://mcp.supabase.com/mcp?project_ref=<PROJECT_REF>
  auth: oauth
  enabled: true
```

Habilitar/deshabilitar sin perder config:
```bash
hermes config set mcp_servers.supabase.enabled true
```

## Autenticación OAuth

```bash
hermes mcp test supabase
```

Abre browser automáticamente → login Supabase → Authorize. Tokens se guardan en `~/AppData/Local/hermes/mcp-tokens/supabase.client.json`.

**Timeout:** El test expira en 40s. Si el OAuth no se completa a tiempo, re-ejecutar. Para CI: usar PAT (Personal Access Token) vía header `Authorization: Bearer <token>`.

## Query Parameters

| Param | Efecto | Ejemplo |
|-------|--------|---------|
| `project_ref=<id>` | Scopaea a un proyecto, desactiva tools de account | `?project_ref=abc123` |
| `read_only=true` | Solo SELECT, desactiva mutations | `?read_only=true` |
| `features=<groups>` | Habilita solo grupos específicos | `?features=database,docs` |

## Tool Groups Disponibles

| Grupo | Tools clave | Default |
|-------|------------|---------|
| `database` | `list_tables`, `execute_sql`, `apply_migration`, `list_migrations` | ✅ |
| `development` | `get_project_url`, `get_publishable_keys`, `generate_typescript_types` | ✅ |
| `functions` | `list_edge_functions`, `deploy_edge_function` | ✅ |
| `debugging` | `get_logs`, `get_advisors` | ✅ |
| `docs` | `search_docs` | ✅ |
| `account` | `list_projects`, `create_project`, `pause/restore` | ✅ (si no hay project_ref) |
| `storage` | `list_storage_buckets`, `get/update_storage_config` | ❌ |

## Uso: Fix del pitfall auth.admin

El MCP server permite `deploy_edge_function` — la solución directa al problema `auth.admin` desde frontend:

1. Deployar Edge Function que reciba datos del líder/staff
2. La función usa `service_role_key` (server-side) para `auth.admin.createUser()`
3. El frontend llama la Edge Function vía `supabase.functions.invoke()`

También `apply_migration` para aplicar el schema SQL completo sin copiar/pegar en Dashboard.

## Agent Skills oficiales (instaladas)

Desde `github.com/supabase/agent-skills`:

- **`supabase`**: Skill comprehensiva — todos los productos Supabase, integraciones SSR, auth, changelog verification.
- **`supabase-postgres-best-practices`**: 8 categorías de optimización Postgres (query performance, connection management, indexes, locks, security, schema, monitoring, advanced).

Instalación: `git clone` + copiar a `~/AppData/Local/hermes/skills/`.

## Verificación

```bash
hermes mcp test supabase   # Debe mostrar ✓ tras OAuth completado
hermes mcp list            # Debe mostrar supabase como ✓ enabled
```
