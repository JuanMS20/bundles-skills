# Selector Strategies by Framework

## Ranking (universal)

1. **Role + accessible name** — `getByRole('button', {name: 'Submit'})`
2. **Label text** — `getByLabel('Email')`
3. **Test ID** — `getByTestId('checkout-submit')`
4. **Text content** — `getByText('Welcome')` (fragile under i18n)
5. **CSS/XPath** — `.btn-primary > span` — LAST RESORT

## Playwright

```typescript
// Best: role-based
await page.getByRole('button', { name: 'Add to Cart' }).click();
await page.getByRole('heading', { name: 'Dashboard' }).isVisible();
await page.getByLabel('Email address').fill('user@example.com');

// Good: test ID (stable if team respects it)
await page.getByTestId('checkout-submit').click();

// Avoid
await page.locator('.btn-primary.add-cart-btn').click();        // CSS classes change
await page.locator('div.container > div:nth-child(3)').click(); // structure-based
```

## Cypress

```typescript
// Best: Cypress Testing Library queries (if installed)
cy.findByRole('button', { name: 'Submit' }).click();
cy.findByLabelText('Email address').type('user@example.com');

// Native: data-testid
cy.get('[data-testid="checkout-submit"]').click();

// Avoid
cy.get('.btn-primary').click();
cy.get('#submit-button'); // IDs can change
```

## Selenium / WebDriver

```python
# Best: XPath with accessible attributes
driver.find_element(By.XPATH, "//button[@aria-label='Submit']")
driver.find_element(By.CSS_SELECTOR, "[data-testid='checkout-submit']")

# Avoid
driver.find_element(By.CLASS_NAME, "btn-primary")
driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/button")
```

## Appium (Mobile)

```python
# iOS: accessibility id (maps to accessibilityIdentifier)
driver.find_element(By.ACCESSIBILITY_ID, "login-button")

# Android: content-desc or resource-id
driver.find_element(By.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Login")')
driver.find_element(By.ID, "com.app:id/login_button")
```
