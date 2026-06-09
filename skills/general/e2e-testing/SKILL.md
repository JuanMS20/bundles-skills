---
name: e2e-testing
description: |
  End-to-end testing para aplicaciones web, mobile y desktop.
  Escribe, revisa y debuggea tests E2E siguiendo el Testing Trophy (static → unit → integration → e2e).
  Use cuando el usuario pida "tests E2E", "end-to-end", "automatizar flujos de usuario",
  detecte un framework de testing (Playwright, Cypress, Selenium, etc.),
  o cuando qa-bundle necesite validar flujos críticos desde la perspectiva del usuario.
---

# E2E Testing

## Quick Start

1. Detectar framework existente (`playwright.config.*`, `cypress/`, `*.spec.js`)
2. Si no existe → proponer setup según stack (web → Playwright, mobile → Appium, desktop → Playwright/Selenium)
3. Si existe → evaluar calidad actual (selectores, isolation, flakiness, cobertura)
4. Escribir o refactorizar tests siguiendo este skill

## Core Principles

1. **Test user-visible behavior, not implementation.** `getByRole('button', {name: 'Submit'})` > `.btn-primary.submit`
2. **API shortcuts for state setup.** `cy.request()` / `request.post()` > clicks de UI para login/data seed.
3. **One assertion per test objective.** Tests monolíticos de 100 pasos son imposibles de debuggear.
4. **No arbitrary waits.** `waitForTimeout(5000)` es fuente garantizada de flakiness. Usa auto-waits o `waitForResponse`.
5. **Parallel-ready isolation.** Cada test debe poder ejecutarse en cualquier orden, en paralelo, sin estado compartido.

## FASE 0 — Detección

Evalúa el proyecto antes de escribir una línea:

| # | Check | Qué buscar |
|---|---|---|
| 1 | Framework existente | `playwright.config.*`, `cypress.config.*`, `wdio.conf.*`, `nightwatch.conf.*` |
| 2 | Stack | `package.json` → web (React, Vue, Angular), mobile (RN, Flutter), desktop (Electron, Tauri) |
| 3 | Infra de tests | Carpetas `tests/`, `e2e/`, `cypress/`, `.github/workflows/*.yml` |
| 4 | Cobertura actual | ¿Hay tests E2E? ¿Pasan? ¿Cuántos son flaky? |
| 5 | Auth strategy | ¿Login por UI, API, o `cy.session()` / `storageState`? |

**Decisión de framework según plataforma:**

| Plataforma | Recomendado 2026 | Cuándo NO usarlo |
|---|---|---|
| Web moderno (SPA/MPA) | Playwright | Proyecto legacy con Selenium Grid ya establecido |
| Web Chromium-only | Cypress | Necesitás cross-browser real (Firefox, Safari) |
| Mobile nativo | Appium / Maestro | No reemplaza testing de unidades en mobile |
| Desktop (Electron) | Playwright | — |
| Enterprise polyglot | Selenium 4 + BiDi | Equipo pequeño con preferencia TS/JS |

## FASE 1 — Estrategia de Datos

**Jerarquía de setup (más rápido → más lento):**

1. **API setup** (rápido, confiable): `POST /api/users` → `storageState` / `localStorage`
2. **Database seed** (directo): SQL insert o factory (Prisma, TypeORM, Sequelize)
3. **Fixtures estáticas** (JSON): únicamente para datos inmutables (catálogos, config)
4. **UI clicks** (lento, frágil): último recurso. Solo cuando no hay API expuesta.

**Auth: nunca loguees por UI en cada test.**

```typescript
// Playwright — globalSetup + storageState
// cypress.config.ts — cy.session()
// Cypress — cy.session([email, password], () => { ... }, { validate() { ... } })
```

## FASE 2 — Selectores (Ranked por Resiliencia)

| Prioridad | Selector | Ejemplo | Por qué |
|---|---|---|---|
| 1 | Role + name | `getByRole('button', {name: 'Add to Cart'})` | A11y-first, sobrevive refactor CSS |
| 2 | Label | `getByLabel('Email address')` | Vinculado al `<label for="">` |
| 3 | Test ID | `getByTestId('checkout-submit')` | Explícito, estable si el equipo lo respeta |
| 4 | Text | `getByText('Welcome back')` | Frágil en i18n, usar con cautela |
| 5 | CSS/XPath | `.btn-primary > span` | ÙLTIMO RECURSO. Documentar por qué. |

**Regla:** Si usás prioridad 4-5, justificá por qué no hay alternativa semántica.

## FASE 3 — Estructura de Tests

**Organizar por feature, no por página.** Playwright sharddea por archivo; feature grouping mantiene tests relacionados en el mismo worker.

```
tests/
├── auth/
│   ├── login.spec.ts
│   └── register.spec.ts
├── checkout/
│   ├── cart.spec.ts
│   └── payment.spec.ts
└── fixtures/
    └── users.ts          # Factories, no JSON estático
```

**Patrón: Page Object Model (POM) vs App Actions.**

| Patrón | Cuándo | Ejemplo |
|---|---|---|
| **POM** | Apps grandes, equipos múltiples, páginas reutilizables | `checkoutPage.fillShipping(data)` |
| **App Actions** | Apps pequeñas-medianas, testing-library style | `addToCart({productId: '123'})` — helper que encapsula UI + API |
| **Mixto** | Por feature: POM para páginas estables, App Actions para flujos dinámicos | — |

## FASE 4 — Anti-Flakiness

| Síntoma | Causa probable | Fix |
|---|---|---|
| `Timeout waiting for element` | Render condicional / lazy loading | Usá `getByRole` + auto-wait, o `waitForResponse` antes de interactuar |
| `Element detached from DOM` | Re-render tras fetch | Usá `locator` (re-query) en vez de `ElementHandle` (stale) |
| `State leaked between tests` | Auth/data compartido | `storageState` por worker, `cy.session()`, o `test.use({storageState: '...'})` |
| `Different result in CI vs local` | Viewport, network lento, race | Misma config de viewport; `retries: 2` en CI; `networkidle` con cautela |
| `Test passes solo` | Dependencia de orden | `fullyParallel: true` + aislar cada test |

**Regla de oro:** Un test que falla 1 de 10 veces sin cambio de código es un bug del test, no de la app. Fix inmediato.

## FASE 5 — CI/CD Integration

```yaml
# .github/workflows/e2e.yml
name: E2E Tests
on: [push, pull_request]
jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run build        # build del app
      - run: npx playwright test  # o cypress run
        env:
          BASE_URL: http://localhost:3000
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

**Checks antes de declarar "CI listo":**

1. `forbidOnly: !!process.env.CI` — evita `test.only` silencioso
2. `retries: process.env.CI ? 2 : 0` — retries solo en CI, nunca local
3. Screenshots + traces solo on-failure — no generar basura en passes
4. Blob reporter en CI — para merge reports con sharding

## FASE 6 — Cobertura y Smoke

¿Qué flujos DEBEN tener tests E2E? Máximo 5-10 por feature. Prioridad:

1. **Auth** — login, logout, password reset, session expiry
2. **Onboarding** — primer uso, wizard, empty states
3. **Core loop** — la acción que hace 80% de usuarios (e.g., checkout, post creation)
4. **Pagos** — si aplica: stripe sandbox, error handling
5. **Admin** — CRUD críticos, bulk actions

**NO escribas E2E para:** validación de form field-level (unit test), cálculos (unit test), estilos visuales (visual regression o manual), permisos granulares (integration test).

## Output Format

Al entregar tests E2E, incluir:

```
Framework: [Playwright | Cypress | Selenium | Appium]
Tests escritos: [N]
Flujos cubiertos: [lista]
Selectores usados: [role-based | testid | CSS — justificado]
Setup de datos: [API | DB seed | Fixtures | UI clicks]
Anti-flakiness aplicado: [lista]
CI checklist: [PASS/FAIL por item]
```

## References

- [references/locators.md](references/locators.md) — Selector strategies por framework
- [references/anti-flakiness.md](references/anti-flakiness.md) — Diagnóstico y fixes de tests flaky
- [references/ci-cd-patterns.md](references/ci-cd-patterns.md) — Configuraciones por framework y plataforma CI
- [references/test-data-strategies.md](references/test-data-strategies.md) — Factories, API setup, DB seed
