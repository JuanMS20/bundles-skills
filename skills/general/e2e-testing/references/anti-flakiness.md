# Anti-Flakiness Diagnostic

## Symptom → Cause → Fix

| Symptom | Cause | Fix |
|---|---|---|
| `Timeout waiting for element` | Conditional render / lazy loading / skeleton | Use `getByRole` + auto-wait, or `waitForResponse` before interact |
| `Element detached from DOM` | Re-render after fetch | Use `locator` (re-query) not `ElementHandle` (stale) |
| `State leaked between tests` | Shared auth / data | `storageState` per worker, `cy.session()`, `test.use({storageState})` |
| `Different result CI vs local` | Viewport, slow network, race | Same viewport config; `retries: 2` in CI; avoid `networkidle` |
| `Test passes only when run solo` | Order dependency | `fullyParallel: true` + isolate each test |
| `File chooser not appearing` | Dialog blocked by headless | Use `setInputFiles` (Playwright) instead of clicking file input |
| `Hover not triggering dropdown` | Mouse event timing | Use `hover({force: true})` or `dispatchEvent` as fallback |
| `Date picker value not set` | Custom component not firing events | Trigger `blur` / `change` events after `fill` |

## Playwright-Specific

```typescript
// Bad: arbitrary wait
await page.waitForTimeout(5000);

// Good: wait for specific condition
await page.waitForResponse('**/api/products');
await expect(page.getByText('Loaded')).toBeVisible();

// Bad: single-shot query
const btn = await page.$('button');  // ElementHandle → stale
await btn.click();

// Good: re-querying locator
const btn = page.locator('button');   // Locator → re-evaluated
await btn.click();
```

## Cypress-Specific

```typescript
// Bad: arbitrary wait
cy.wait(5000);

// Good: wait for network or DOM
cy.wait('@getProducts');
cy.get('[data-testid="loading"]', { timeout: 10000 }).should('not.exist');

// Bad: shared state via before
cy.before(() => { cy.login(); });  // runs once → leaks

// Good: isolated session
cy.session('user', () => { cy.login(); }, { validate() { ... } });
```

## Retry Strategy

```typescript
// playwright.config.ts
retries: process.env.CI ? 2 : 0,  // CI only

// cypress.config.ts
retries: {
  runMode: 2,   // CI headless
  openMode: 0,  // interactive → no retries (developer sees real failures)
}
```

**Rule:** A test that fails 1 in 10 runs without code changes is a test bug. Fix immediately.
