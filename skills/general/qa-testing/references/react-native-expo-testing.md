# React Native + Expo Testing Pitfalls

## Expo SDK 54 Specific

### babel-preset-expo not resolving
`babel.config.js` references `babel-preset-expo` as a preset. Starting SDK 54, this package
lives as a **nested dependency** of `expo` (`node_modules/expo/node_modules/babel-preset-expo/`).
Metro may not resolve it from the root.

**Fix:** Install explicitly as devDependency with the SDK-matching version:
```bash
npm install --save-dev babel-preset-expo@~54.0.10
```
**Pitfall:** `npm install --save-dev babel-preset-expo@latest` installs the latest (e.g. 56.x)
which is incompatible. Always pin to `~SDK_MAJOR.0.x`. Check with `npx expo-doctor` or watch
the startup warning.

### Missing `main` field in app.json
Expo SDK 54 defaults to `./src/App` as entry point (Expo Router convention). Classic apps
with `App.tsx` in the root **must** explicitly set:
```json
{
  "expo": {
    "main": "./App.tsx"
  }
}
```
**Symptom:** Metro serves HTML 200 but JS bundle fails with `Unable to resolve module ./src/App`.
**Diagnosis:** Check the bundle endpoint directly: `curl http://localhost:PORT/App.bundle?platform=web&dev=true`

### Version mismatch warnings
`npx expo install --fix` may report "Dependencies are up to date" even when a critical
package is missing from the root `node_modules/`. Always verify with `ls node_modules/<pkg>/package.json`.

---

## General React Native QA Patterns

### HTML 200 ≠ App works
The Expo dev server serves an HTML shell that always returns 200, even when the JS bundle
has resolution errors. **Testing the HTML endpoint is insufficient.**

Correct verification chain:
1. HTML endpoint → 200 (server running)
2. Bundle endpoint → valid JS, no `UnableToResolveError` or `TransformError`
3. Browser console → no React errors
4. Visual render → at least one screen loads

### Web vs Native differences
- `expo-camera` and `expo-media-library` may not work on web. Code using `require()` with
  try/catch fallbacks is intentional for web compatibility — don't flag as errors.
- `Platform.OS === 'web'` guards are valid, not code smells.
- `gap` in StyleSheet works on web but not on older RN versions. Test on target platform.

### Metro cache issues
After changing babel config or installing new packages, clear Metro cache:
```bash
npx expo start --clear
```
Or delete `.expo/` and restart.

### TypeScript passes but app crashes
`tsc --noEmit` with `baseUrl` + `paths` aliases only checks type resolution, not runtime
module resolution. Metro has its own resolver (configured via `babel-plugin-module-resolver`).
Both must agree on alias configuration:
- `tsconfig.json` → `paths: { "@/*": ["src/*"] }`
- `babel.config.js` → `plugins: [["module-resolver", { alias: { "@": "./src" } }]]`
