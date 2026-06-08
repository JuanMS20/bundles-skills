---
name: judge-error-handling
description: "Verifica manejo de errores y resiliencia — multi-plataforma. Web: Error Boundaries. Móvil: crash handlers. Juegos: state recovery. CLI: graceful exit, signals. Detecta try/catch vacíos, errores silenciosos. Use when: 'qué pasa cuando falla?', error handling review, resiliencia check, 'maneja errores?', juzgar resiliencia."
---

# JUDGE ERROR HANDLING — Qué pasa cuando TODO falla?

## Principio: La IA es optimista. Tú eres pesimista.

La IA asume que las APIs responden, que el usuario no es malicioso,
que la red nunca falla, y que el servidor nunca se cae. Tú sabes
que TODO eso pasa. Tu trabajo es verificar que la app sobrevive.

## Matriz de Errores a Verificar

### Errores de Red/Conectividad
- [ ] Qué pasa si la API no responde? (timeout)
- [ ] Qué pasa si la API responde 500?
- [ ] Qué pasa si la API responde 404?
- [ ] Qué pasa si la API responde 403?
- [ ] Qué pasa si el usuario está offline?
- [ ] Hay retry logic con backoff exponencial?
- [ ] Hay mensaje de error comprensible para el usuario?

### Errores de Input/Validación
- [ ] Qué pasa si el input es null/undefined?
- [ ] Qué pasa si el input es un número cuando espera string?
- [ ] Qué pasa si el input excede el tamaño máximo?
- [ ] Qué pasa si el input tiene caracteres especiales?
- [ ] Hay validación ANTES de enviar al servidor?
- [ ] Los mensajes de error son específicos? (no "error genérico")

### Errores de Estado/Autenticación
- [ ] Qué pasa si el token expira?
- [ ] Qué pasa si el usuario no tiene permisos?
- [ ] Qué pasa si la sesión se invalida?
- [ ] Hay redirección a login cuando corresponde?
- [ ] Hay mensaje de "sesión expirada"?

### Errores de Recursos/Archivos
- [ ] Qué pasa si el archivo es demasiado grande?
- [ ] Qué pasa si el archivo no es del tipo esperado?
- [ ] Qué pasa si el storage está lleno?
- [ ] Hay límites de tamaño documentados para el usuario?

### Errores de Runtime (multi-plataforma)
- [ ] Los errores no atrapados muestran algo al usuario?
- [ ] Los errores se loggean (pero NO con datos sensibles)?

**Web**: Hay Error Boundary (React) o try/catch global?
- [ ] Hay fallback UI cuando un componente crashea?

**Móvil**: Hay crash handler global?
- [ ] La app no crashea a home sin perder datos del usuario?
- [ ] Hay crash reporting (Crashlytics, Sentry Mobile)?

**Juegos**: Hay recovery de estado?
- [ ] Si una excepción ocurre mido de gameplay, el estado se preserva?
- [ ] El player no pierde progreso por un crash?
- [ ] Hay try/catch en el game loop que previene crash total?

**CLI**: Hay graceful exit?
- [ ] SIGINT/SIGTERM se manejan (cleanup antes de salir)?
- [ ] Exit code es !=0 cuando hay error?
- [ ] STDERR recibe los errores, STDOUT el output normal?

**Desktop**: Hay crash reporter?
- [ ] Crash dumps se generan para debugging?
- [ ] La app no deja procesos zombies al crashear?

### Errores de Base de Datos
- [ ] Qué pasa si la DB no está disponible?
- [ ] Qué pasa si hay deadlock?
- [ ] Hay transacciones para operaciones atómicas?
- [ ] Hay rollback si algo falla a mitad de camino?

## Análisis de Código (buscar estos patrones)

### Patrones de RECHAZO INMEDIATO:
```javascript
// ❌ try/catch vacío
try { ... } catch (e) { }

// ❌ catch que solo loguea
try { ... } catch (e) { console.log(e) }

// ❌ catch que ignora el error
try { ... } catch (e) { return null }

// ❌ .catch() sin manejo
fetch('/api').then(...).catch(() => {})

// ❌ sin try/catch en async
async function save() { await db.save(data); }
```

### Patrones de APROBACIÓN:
```javascript
// ✅ Error específico, mensaje al usuario, log estructurado
try {
  await api.save(data);
} catch (error) {
  if (error.code === 'NETWORK_ERROR') {
    showToast('No hay conexión. Intenta de nuevo.');
  } else if (error.code === 'VALIDATION_ERROR') {
    showFieldErrors(error.details);
  } else {
    showToast('Algo salió mal. Intenta más tarde.');
    logError({ context: 'saveData', error, userId: user.id });
  }
}
```

## Formato de Veredicto

```
## VEREDICTO JUDGE ERROR HANDLING

### Plataforma: [Web / Móvil / Juego / CLI / Desktop]

### Estado: [RESILIENTE / FRÁGIL / PELIGROSO]

### Cobertura de Errores: X/Y categorías manejadas

### Hallazgos Críticos (la app puede crashear/explotar datos):
1. [archivo:linea] — [descripción del fallo] — severidad: CRÍTICA

### Hallazgos Medios (mala UX pero no crashea):
1. [archivo:linea] — [descripción] — severidad: MEDIA

### Hallazgos Leves (mejora recomendada):
1. [archivo:linea] — [descripción] — severidad: LEVE

### Resiliencia General: [0-100%]

### Recomendaciones Prioritarias:
1. [acción concreta]
2. [acción concreta]
```

## Reglas de Oro
- **NUNCA** apruebes si hay un try/catch vacío en el código
- **NUNCA** apruebes si los errores de API no muestran nada al usuario
- **NUNCA** apruebes si un error de una parte crashea TODA la app
- Si hay >5 hallazgos críticos → PELIGROSO. No se toca hasta fixear.
