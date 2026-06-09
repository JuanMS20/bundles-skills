---
name: e2e-testing
description: |
  End-to-end testing: valida flujos críticos de usuario sin importar qué herramientas tengas.
  Genera planes de prueba, guía testing exploratorio con browser real (Kimi WebBridge), 
  o escribe tests automatizados si hay framework (Playwright, Cypress, Selenium).
  Use cuando el usuario pida "tests E2E", "end-to-end", "probar que funciona",
  "validar flujos", "smoke test", o cuando qa-bundle necesite verificar desde la perspectiva del usuario.
---

# E2E Testing

## Quick Start — Detección de herramientas disponibles

Antes de actuar, detectar qué se tiene:

| # | Check | Qué buscar | Si existe → modo |
|---|---|---|---|
| 1 | Framework E2E | `playwright.config.*`, `cypress/`, `*.spec.ts` en `tests/e2e/` | **Modo A**: escribir tests automatizados |
| 2 | Browser control | `kimi-webbridge` disponible, navegador abierto, URL accesible | **Modo B**: testing exploratorio guiado |
| 3 | Nada | No hay framework ni browser control | **Modo C**: generar plan de prueba + checklist |

**La skill aporta valor en los 3 modos.** No requiere Playwright.

## Core Principles (universales)

1. **Test user-visible behavior, not implementation.** Lo que el usuario ve y hace → no código interno.
2. **One flow = one objective.** Tests monolíticos de 100 pasos son imposibles de debuggear.
3. **Parallel-ready isolation.** Cada flujo debe poder validarse solo, sin dependencias.
4. **Evidencia > claims.** Screenshot, URL actual, estado DOM → no "debería estar ahí".

---

## Modo A — Tests Automatizados (con framework)

Aplica si hay Playwright, Cypress, Selenium o similar.

### FASE A.0 — Evaluar calidad actual

| Check | Rojo → Acción |
|---|---|
| ¿Selectores usan CSS/XPath crudo? | Refactorizar a role-based o testid |
| ¿Hay `waitForTimeout` o `cy.wait(ms)`? | Reemplazar por waits condicionales |
| ¿Tests comparten estado (login, data)? | Aislar con `cy.session()` o `storageState` |
| ¿Fallan 1 de 10 veces sin cambio de código? | Diagnosticar flakiness (ver referencias) |

### FASE A.1 — Estrategia de datos

**Jerarquía (más rápido → más lento):**

1. **API setup**: `POST /api/users` → guardar token/session
2. **DB seed / factory**: SQL insert o factory (Prisma, TypeORM)
3. **Fixtures JSON**: solo datos inmutables (catálogos)
4. **UI clicks**: último recurso

### FASE A.2 — Selectores (ranked)

| Prioridad | Selector | Ejemplo |
|---|---|---|
| 1 | Role + name | `getByRole('button', {name: 'Submit'})` |
| 2 | Label | `getByLabel('Email address')` |
| 3 | Test ID | `getByTestId('checkout-submit')` |
| 4 | Text | `getByText('Welcome back')` (fragile en i18n) |
| 5 | CSS/XPath | `.btn-primary > span` — ÙLTIMO RECURSO |

### FASE A.3 — Estructura

Organizar por **feature**, no por página:

```
tests/
├── auth/login.spec.ts
├── checkout/cart.spec.ts
└── fixtures/users.ts   # factories, no JSON estático
```

### FASE A.4 — Cobertura mínima E2E

Máximo 5-10 flujos críticos. Prioridad:

1. **Auth** — login, logout, password reset, session expiry
2. **Onboarding** — primer uso, wizard, empty states
3. **Core loop** — acción que hace 80% de usuarios
4. **Pagos** — checkout, errores de pago, refund
5. **Admin** — CRUD críticos, bulk actions

**NO escribir E2E para:** validación de campo (unit test), cálculos (unit), estilos visuales (visual regression), permisos granulares (integration).

### FASE A.5 — Output

```
Framework: [Playwright | Cypress | Selenium | Appium]
Tests escritos: [N]
Flujos cubiertos: [lista]
Selectores: [role-based | testid | CSS — justificado]
Setup de datos: [API | DB seed | Fixtures | UI clicks]
Anti-flakiness: [lista]
CI checklist: [PASS/FAIL por item]
```

---

## Modo B — Testing Exploratorio Guiado (con browser real)

Aplica si tenés Kimi WebBridge, un navegador abierto, o podés navegar la app manualmente.
**No necesitás un framework de testing.**

### FASE B.0 — Preparación

1. Identificar la **URL base** de la app (local, staging, o producción)
2. Listar **usuarios de prueba** con roles distintos (admin, user, guest)
3. Limpiar estado: cookies, localStorage, sessionStorage (fresh start)

### FASE B.1 — Ejecutar flujo crítico (ejemplo: checkout)

Para cada flujo, seguir este script y **documentar evidencia**:

| Paso | Acción | Qué verificar | Evidencia |
|---|---|---|---|
| 1 | Navegar a `/products` | Página carga, productos visibles | Screenshot + URL |
| 2 | Click "Add to Cart" en producto | Cart counter aumenta a 1 | Screenshot del counter |
| 3 | Click cart icon → checkout | Redirige a `/checkout` | URL actual |
| 4 | Llenar shipping form | Campos aceptan input, validación en tiempo real | Screenshot del form |
| 5 | Submit order | Redirige a `/order-confirmation/{id}` | URL + número de orden |
| 6 | Verificar orden en `/orders` | Orden aparece con status "pending" | Screenshot de la lista |

**Regla:** Si un paso falla → STOP. Documentar: qué paso, qué esperabas, qué viste, URL actual.

### FASE B.2 — Variantes y edge cases

Después del happy path, probar:

- **Empty state**: carrito vacío → checkout → ¿qué pasa?
- **Error state**: network lento (throttle en DevTools) → ¿spinner? ¿retry?
- **Auth boundary**: intentar acceder a `/admin` como user normal → ¿403? ¿redirect?
- **Mobile viewport**: redimensionar a 375px → ¿responsive? ¿botones tapables?

### FASE B.3 — Reporte de sesión exploratoria

```
Flujo: [nombre]
Duración: [X min]
Herramienta: [Kimi WebBridge | Chrome manual | Firefox manual]

Happy Path:
  [X] Paso 1: [descripción] → [PASS/FAIL] → evidencia: [URL/screenshot]
  [X] Paso 2: ...

Edge Cases probados:
  [ ] Empty state → [resultado]
  [ ] Error state → [resultado]
  [ ] Auth boundary → [resultado]

Bugs encontrados:
  1. [Severidad] [Descripción] → repro steps → evidencia

Próximos pasos:
  - [ ] Automatizar flujo crítico con Playwright/Cypress
  - [ ] Fix bug #[N]
```

---

## Modo C — Plan de Prueba + Checklist (sin herramientas)

Aplica si no hay framework ni acceso a browser. Generar un documento ejecutable.

### FASE C.0 — Inventario de flujos

Identificar todos los flujos que un usuario real puede hacer:

```
Flujo: Registro de nuevo usuario
  Trigger: Usuario visita landing → click "Sign Up"
  Steps:
    1. Formulario muestra campos: name, email, password, confirmPassword
    2. Validación en tiempo real (email format, password strength)
    3. Submit → POST /api/auth/register
    4. Éxito: redirige a /onboarding
    5. Error: mensaje específico (email taken, weak password)
  
  Verificación:
    [ ] Happy path con datos válidos → usuario creado en DB, token válido
    [ ] Email duplicado → error 409, mensaje claro
    [ ] Password débil → error 400, indica requisitos
    [ ] Campos vacíos → error 400, no crea usuario parcial
    [ ] Responsive: form usable en 375px
```

### FASE C.1 — Priorización por riesgo

| Flujo | Frecuencia de uso | Impacto si falla | Prioridad |
|---|---|---|---|
| Login | 100% de usuarios | App inaccesible | P0 |
| Checkout | 30% de usuarios | Pérdida de ingresos | P0 |
| Onboarding | 10% de usuarios (solo nuevos) | Churn temprano | P1 |
| Settings | 5% de usuarios | Frustración menor | P2 |

**Regla:** Solo P0 y P1 requieren validación E2E. P2 puede ser manual ocasional.

### FASE C.2 — Checklist de smoke test (5 minutos)

Checklist que cualquier humano puede ejecutar antes de un deploy:

```
Pre-deploy Smoke Test
□ [ ] Homepage carga en < 3s
□ [ ] Login funciona con credenciales válidas
□ [ ] Core loop principal funciona (ej: crear post, añadir al carrito)
□ [ ] No hay errores 500 visibles al usuario
□ [ ] Logout limpia session y redirige a login
□ [ ] Mobile: no hay scroll horizontal forzado
□ [ ] Desktop: menú principal es navegable
```

---

## FASE Z — Anti-Flakiness (todos los modos)

| Síntoma | Causa | Fix |
|---|---|---|
| Elemento no aparece | Lazy loading / skeleton | Esperar a que el spinner desaparezca antes de interactuar |
| "Funcionaba ayer" | Deploy con cambio de DOM | Revisar selectores: ¿se movió el elemento? |
| Resultado diferente en staging vs prod | Datos de prueba distintos | Usar mismos fixtures/factories en ambos |
| Flaky en CI pero estable local | Network lento, race conditions | Añadir retry o esperar señal específica (no tiempo fijo) |

**Regla de oro:** Si un flujo falla 1 de 10 veces sin cambio de código, es un bug del test/plan, no de la app. Fix inmediato.

---

## References

- [references/locators.md](references/locators.md) — Selectores por framework (Modo A)
- [references/anti-flakiness.md](references/anti-flakiness.md) — Diagnóstico de tests flaky (Modo A)
- [references/ci-cd-patterns.md](references/ci-cd-patterns.md) — CI configs (Modo A)
- [references/test-data-strategies.md](references/test-data-strategies.md) — Setup de datos (Modo A)
- [references/exploratory-testing.md](references/exploratory-testing.md) — Técnicas de testing exploratorio (Modo B)
- [references/test-plan-template.md](references/test-plan-template.md) — Template de plan de prueba (Modo C)
