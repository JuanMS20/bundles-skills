# N+1 Query Elimination (React + Supabase)

Patrón para eliminar N+1 queries en dashboards y listas donde cada item
necesita contadores agregados de una tabla hija. Verificado en NOVVA VALLE
(Dashboard admin + MisLideres staff).

## El problema

Patrón típico que genera N+1 queries sin que el desarrollador lo note:

```typescript
// MAL: 1 + 2N queries
const { data: leaders } = await supabase.from('profiles')
  .select('id, nombre, username').eq('role', 'lider')

const rows = await Promise.all(
  leaders.map(async (lp) => {
    const { count: total } = await supabase.from('contacts')
      .select('*', { count: 'exact', head: true }).eq('lider_id', lp.id)
    const { count: votados } = await supabase.from('contacts')
      .select('*', { count: 'exact', head: true })
      .eq('lider_id', lp.id).eq('estado', 'voted')
    return { ...lp, total, votados }
  })
)
```

**Por qué `Promise.all` NO arregla nada:** paraleliza los N queries
(concurrentes en red) pero sigue siendo N round-trips al servidor. El
overhead de red y el consumo de conexiones del pool escala con N.

## La solución: single fetch + Map aggregation

Un solo query trae los campos mínimos de todos los registros relevantes.
La agregación (count, group-by) se hace en JS con un `Map` — O(n) en
memoria, O(1) en queries.

```typescript
// BIEN: 2 queries total (paralelas), sin importar N líderes
const [leaderResult, contactsResult] = await Promise.all([
  supabase.from('profiles').select('id, nombre, username')
    .eq('role', 'lider').order('nombre'),
  supabase.from('contacts').select('lider_id, estado'),  // ← campos mínimos
])

const leaderProfiles = leaderResult.data ?? []
const allContacts = contactsResult.data ?? []

// Agregar en O(n) con Map
const contactMap = new Map<string, { total: number; votados: number }>()
for (const c of allContacts) {
  const entry = contactMap.get(c.lider_id) ?? { total: 0, votados: 0 }
  entry.total++
  if (c.estado === 'voted') entry.votados++
  contactMap.set(c.lider_id, entry)
}

// Joinear con leaders para el resultado final
setLeaders(leaderProfiles.map((lp) => ({
  nombre: lp.nombre,
  username: lp.username,
  total: contactMap.get(lp.id)?.total ?? 0,
  votados: contactMap.get(lp.id)?.votados ?? 0,
})))
```

## Variante: contar registros por parent (sin sub-condiciones)

Cuando solo necesitas un count por parent (sin agrupar por estado):

```typescript
// BIEN: 1 query bulk
const { data: allContacts } = await supabase
  .from('contacts').select('lider_id').in('lider_id', leaderIds)

const counts: Record<string, number> = {}
for (const c of allContacts ?? []) {
  counts[c.lider_id] = (counts[c.lider_id] ?? 0) + 1
}
setLeaderContacts(counts)
```

## Cuándo usar este patrón vs alternativas

| Escenario | Solución |
|-----------|----------|
| < 10K registros hijos, pocos campos | **Este patrón** (bulk fetch + Map) |
| > 10K registros, o campos pesados | RPC con `GROUP BY` en Postgres |
| Necesitas paginación server-side | RPC con `LIMIT/OFFSET` + aggregate |

**Umbral práctico:** para sistemas electorales municipales (miles de
contactos, no millones), el bulk fetch + Map es la solución correcta.
Trae solo los campos necesarios (`lider_id, estado`), no `*`.

## Reglas

1. **Fetch campos mínimos:** `select('lider_id, estado')`, no `select('*')`.
   Menos datos por la red = más rápido incluso con muchos registros.
2. **`Map` > objeto plano para lookups:** O(1) sin colisiones de keys.
3. **`Promise.all` solo para queries independientes** (leaders + contacts
   no dependen entre sí para el fetch inicial), no para N queries dependientes.
4. **`head: true` con `count: 'exact'`** es bueno para un solo contador,
   pero no escalable cuando necesitas N contadores — ahí usar bulk fetch.
