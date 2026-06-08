# PR Description — Ejemplo Completo

## Fix: Auth middleware no renueva refresh token expirado

### Ticket
AUTH-142 / https://github.com/org/repo/issues/142

### Root Cause
El middleware de auth verificaba que el access token fuera válido, pero al expirar intentaba usar un refresh token ya vencido sin renovarlo primero. Las requests subsecuentes fallaban con 401 silenciosamente.

### Breaking Commit
`a1b2c3d` "feat: add token refresh middleware" (2026-03-15)

### Changes
- `src/auth/middleware.ts` — Agregada renovación proactiva de refresh token antes del threshold de expiración
- `src/auth/__tests__/middleware.test.ts` — Tests del nuevo flujo de renovación (3 casos)
- `src/config/constants.ts` — Agregado `REFRESH_THRESHOLD_SECONDS` como config extraída

### Why
- `middleware.ts` — El root cause era token expirando sin renovación. La renovación proactiva antes del threshold evita la ventana de 401s.
- `middleware.test.ts` — Probar que la renovación ocurre exactamente cuando el token está por expirar, ni antes ni después.
- `constants.ts` — El threshold era un magic number (300). Moverlo a config permite ajustarlo sin tocar lógica y facilita testing con valores controlados.

### Evidence
```
$ npm test
  auth/middleware
    ✓ should refresh token before expiration (12ms)
    ✓ should not refresh token when valid (3ms)
    ✓ should handle refresh failure gracefully (5ms)
  3 passing (45ms)

$ npx tsc --noEmit
  (no errors)
```

### Risks
- El refresh es ahora proactivo — si el endpoint de refresh falla intermitentemente, los usuarios verán más errores. Mitigado con retry con backoff exponencial.
- No afecta el flujo de login, solo la renovación silenciosa.
- Sugerir monitorear `auth.refresh.failure` en producción las primeras 48h.
