# Test Data Strategies

## Hierarchy (fastest → slowest)

| Method | Speed | Reliability | When to use |
|---|---|---|---|
| **API setup** | Fastest | High | Auth, user creation, order seeding. Use `cy.request()` or `request.post()` |
| **DB seed / Factory** | Fast | High | Complex relational data. Use Prisma/TypeORM/Sequelize factories |
| **Static fixtures (JSON)** | Fast | Medium | Immutable catalogs, configs, enums. Never for user-specific data |
| **UI clicks** | Slowest | Low | Last resort. Only when no API/DB access exists |

## Auth Setup (do NOT login via UI per test)

### Playwright: globalSetup + storageState

```typescript
// playwright.config.ts
export default defineConfig({
  globalSetup: './tests/global-setup.ts',
  use: {
    storageState: './tests/auth/user.json',
  },
});

// tests/global-setup.ts
import { request } from '@playwright/test';
export default async () => {
  const req = await request.newContext();
  await req.post('/api/auth/login', { data: { email: 'test@example.com', password: 'pass' } });
  await req.storageState({ path: './tests/auth/user.json' });
  await req.dispose();
};
```

### Cypress: cy.session()

```typescript
// cypress/support/commands.ts
Cypress.Commands.add('login', (email, password) => {
  cy.session([email, password],
    () => {
      cy.request('POST', '/api/auth/login', { email, password })
        .then((res) => {
          window.localStorage.setItem('token', res.body.token);
        });
    },
    {
      validate() {
        cy.request('/api/auth/me').its('status').should('eq', 200);
      },
    }
  );
});
```

## Factories vs Fixtures

```typescript
// Factory (preferred) — generates unique data per test
import { faker } from '@faker-js/faker';
export const userFactory = () => ({
  email: faker.internet.email(),
  password: faker.internet.password(),
  name: faker.person.fullName(),
});

// Static fixture — only for immutable data
// fixtures/products.json — catalog SKUs that never change
```

## Cleanup Strategy

| Approach | When | Implementation |
|---|---|---|
| **API teardown** | Each test cleans its own data | `afterEach` → DELETE /api/users/:id |
| **DB transaction rollback** | Integration test suite | Wrap in transaction, rollback on teardown |
| **Fresh DB per worker** | CI parallel jobs | Reset DB schema + seed before each worker |
| **No cleanup (disposable env)** | Ephemeral CI | Spin up fresh DB container per job |

**Rule:** Tests must not leave orphaned data that breaks subsequent tests.
