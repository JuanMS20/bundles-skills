# Test Plan Template

## Metadatos

```
Proyecto: [nombre]
Versión: [X.Y.Z]
Fecha: [YYYY-MM-DD]
Autor: [nombre]
Herramientas disponibles: [Playwright | Cypress | Selenium | Kimi WebBridge | Ninguna]
```

## Alcance

### In-Scope
- Flujos críticos de usuario (P0, P1)
- Validación cross-browser básica
- Responsive smoke test

### Out-of-Scope
- Performance load testing (requiere JMeter/k6)
- Visual regression (requiere Percy/Chromatic)
- Seguridad profunda (requiere Burp Suite/OWASP ZAP)

## Flujos a validar

| ID | Flujo | Prioridad | Rol necesario | Método |
|---|---|---|---|---|
| E2E-01 | Registro de usuario | P0 | Guest | [Auto | Manual | Plan] |
| E2E-02 | Login / Logout | P0 | User | [Auto | Manual | Plan] |
| E2E-03 | Core loop principal | P0 | User | [Auto | Manual | Plan] |
| E2E-04 | Checkout / Pago | P0 | User | [Auto | Manual | Plan] |
| E2E-05 | Onboarding wizard | P1 | New User | [Auto | Manual | Plan] |
| E2E-06 | Admin: CRUD usuarios | P1 | Admin | [Auto | Manual | Plan] |

## Casos de prueba por flujo

### E2E-01: Registro de usuario

```
Precondición: Usuario no autenticado, email no registrado

Happy Path:
  1. Navegar a /register
  2. Completar formulario con datos válidos
  3. Submit → redirige a /onboarding
  4. Verificar usuario creado en DB / auth

Edge Cases:
  □ Email duplicado → error claro, no crea usuario
  □ Password débil → indica requisitos
  □ Campos vacíos → validación en submit
  □ Email inválido → validación en tiempo real
  □ Resubmit del form → no crea duplicado

Validación:
  □ Responsive en 375px
  □ Accessible: labels, focus management, error announcements
```

## Checklist pre-deploy (smoke)

```
□ [ ] Homepage carga en < 3 segundos
□ [ ] Login funciona con credenciales válidas
□ [ ] Core loop principal completo sin errores
□ [ ] No hay errores 500/403 visibles al usuario
□ [ ] Logout limpia sesión y redirige
□ [ ] Mobile: no scroll horizontal forzado
□ [ ] Desktop: navegación principal accesible
□ [ ] Forms: validación visible en errores
```

## Ejecución

| Fecha | Ejecutor | Herramienta | Resultado | Bugs |
|---|---|---|---|---|
| | | | | |

## Próximos pasos

- [ ] Automatizar flujos P0 con [framework propuesto]
- [ ] Integrar en CI/CD
- [ ] Programar ejecución periódica (semanal)
