# Cascade Dependent Dropdowns (React + Supabase)

Patrón para N dropdowns dependientes donde cada nivel carga sus opciones
basado en la selección del padre. Verificado en NOVVA VALLE con 4 niveles
jerárquicos (departamento → municipio → puesto + barrio).

## Estructura de datos típica

Cada tabla hija tiene un FK al padre:

```
geo_departments (code, name)
  └─ geo_municipalities (code, name, dept_code FK→departments)
       ├─ geo_voting_stations (id, name, mun_code FK→municipalities)
       └─ geo_barrios       (id, name, mun_code FK→municipalities)
```

**Insight clave:** cuando dos hijos comparten el mismo FK padre (como
puestos y barrios que ambos dependen de mun_code), cargan en el mismo
`useEffect` — no hace falta un effect separado por hijo.

## Componente: cascada controlada

El componente emite un objeto con TODOS los valores (codes + names
resueltos). El padre no necesita saber nada de queries Supabase.

```typescript
export interface CascadaValue {
  dept_code: string;  mun_code: string
  station_id: string; barrio_id: string
  // Names resueltos — la DB suele guardar texto, no codes
  dept_name: string;  mun_name: string
  station_name: string; barrio_name: string
}

export const EMPTY_CASCADA: CascadaValue = { /* todos '' */ }
```

### Hooks: cargar opciones por nivel

```typescript
// Nivel raíz: carga una sola vez
useEffect(() => {
  supabase.from('geo_departments').select('code, name').order('name')
    .then(({ data }) => data && setDepartments(data))
}, [])

// Niveles hijos: useCallback + useEffect reacciona al cambio del padre
const loadMunicipalities = useCallback((deptCode: string) => {
  if (!deptCode) return setMunicipalities([])
  supabase.from('geo_municipalities').select('code, name')
    .eq('dept_code', deptCode).order('name')
    .then(({ data }) => data && setMunicipalities(data))
}, [])

// Cuando cambia el departamento, recargar municipios + limpiar hijos
useEffect(() => {
  if (value.dept_code) loadMunicipalities(value.dept_code)
  else setMunicipalities([])
}, [value.dept_code, loadMunicipalities])
```

### Cascada de 2 hijos con mismo padre

Puestos y barrios ambos dependen de `mun_code`. Un solo effect carga ambos:

```typescript
useEffect(() => {
  if (value.mun_code) {
    loadStations(value.mun_code)
    loadBarrios(value.mun_code)
  } else {
    setStations([]); setBarrios([])
  }
}, [value.mun_code, loadStations, loadBarrios])
```

### Reset en cascada al cambiar un padre

Al cambiar departamento → limpiar municipio, puesto, barrio.
Al cambiar municipio → limpiar puesto y barrio.

```typescript
onChange={{
  ...EMPTY_CASCADA,           // limpia TODO
  dept_code,                  // setea solo el nuevo
  dept_name: dept?.name ?? '',
}}
```

```typescript
onChange={{
  ...value,                   // conserva dept
  mun_code, mun_name: mun?.name ?? '',
  station_id: '', station_name: '',  // limpia hijos
  barrio_id: '', barrio_name: '',
}}
```

### Disabled hasta que el padre tenga valor

```tsx
<select disabled={!value.dept_code} className="... disabled:bg-gray-100">
```

## Integración con form del padre

La DB frecuentemente guarda texto (nombres), no codes. El componente
resuelve code→name y el padre lo mapea a campos de texto del form:

```typescript
function handleGeoChange(val: CascadaValue) {
  setGeoValue(val)
  setForm(prev => ({
    ...prev,
    municipio: val.mun_name,
    barrio: val.barrio_name,
    puesto_votacion: val.station_name,
  }))
}
```

**Limitación conocida:** al editar un registro existente, la cascada no
se pre-puebla automáticamente (no hay reverse-lookup name→code). Para
pre-poblar se necesita un query que busque el code por nombre, que es un
enhancement separado.

## Pitfall: React synthetic events en headless browser

Manipular `<select>.value` via DevTools/browser_console y disparar
`new Event('change')` NO activa el onChange de React. React usa
synthetic events internos que bypass eventos nativos.

Para testing E2E en headless: usar clicks reales (abrir dropdown →
click en opción) o frameworks como Playwright/Cypress que simulan
eventos a nivel de browser, no de DOM.
