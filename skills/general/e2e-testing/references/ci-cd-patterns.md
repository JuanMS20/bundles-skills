# CI/CD Patterns by Framework

## Playwright

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
        with: { node-version: '20' }
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run build
      - run: npx playwright test
        env:
          BASE_URL: http://localhost:3000
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

```typescript
// playwright.config.ts — production-ready
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,      // blocks test.only in CI
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 4 : undefined,
  reporter: process.env.CI ? 'blob' : 'html',
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
});
```

## Cypress

```yaml
# .github/workflows/e2e.yml
name: Cypress Tests
on: [push, pull_request]
jobs:
  cypress:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chrome, firefox, edge]
    steps:
      - uses: actions/checkout@v4
      - uses: cypress-io/github-action@v6
        with:
          browser: ${{ matrix.browser }}
          start: npm run dev
          wait-on: 'http://localhost:3000'
          record: true
        env:
          CYPRESS_RECORD_KEY: ${{ secrets.CYPRESS_RECORD_KEY }}
```

```typescript
// cypress.config.ts
export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    defaultCommandTimeout: 10000,
    requestTimeout: 15000,
    responseTimeout: 30000,
    retries: { runMode: 2, openMode: 0 },
    video: false,
    screenshotOnRunFailure: true,
    experimentalRunAllSpecs: true,
  },
});
```

## Selenium (Python)

```yaml
# .github/workflows/e2e.yml
name: Selenium Tests
on: [push, pull_request]
jobs:
  selenium:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - run: pytest tests/e2e/ -v --tb=short
        env:
          SELENIUM_HEADLESS: '1'
          BASE_URL: http://localhost:8000
```

## Pre-Deploy Smoke in CI

Run a minimal smoke suite (3-5 critical paths) before full E2E:

```yaml
- name: Smoke Test
  run: npx playwright test tests/smoke/
- name: Full E2E Suite
  run: npx playwright test
  if: github.ref == 'refs/heads/main'
```
