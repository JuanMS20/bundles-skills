# Expo SDK 54 — Metro Bundler Debug Log

Sesión de QA AppCaracol (2026-05-29). Documenta la cadena de errores Metro y sus resoluciones.

## Cadena de Errores (orden de aparición)

### Error 1: react-dom / react-native-web faltantes
```
Cannot find module 'react-dom'
Cannot find module 'react-native-web'
```
**Causa:** `expo start --web` requiere estas deps para web pero no estaban en package.json.
**Fix:** `npx expo install react-dom react-native-web`

### Error 2: babel-plugin-module-resolver faltante
```
Cannot find module 'babel-plugin-module-resolver'
```
**Causa:** babel.config.js referencia module-resolver pero no estaba instalado.
**Fix:** `npm install --save-dev babel-plugin-module-resolver`

### Error 3: babel-preset-expo no resuelve (BLOCKER principal)
```
Cannot find module 'babel-preset-expo'
```
**Causa:** babel-preset-expo existe como dep anidada de expo (node_modules/expo/node_modules/babel-preset-expo/) pero Metro no la resuelve desde el root.
**`npx expo install --fix` NO lo resolvió.** Reportó "Dependencies are up to date" incorrectamente.
**Fix:** `npm install --save-dev babel-preset-expo@~54.0.10`
**LECCIÓN:** Siempre pinning a la versión del SDK. `@latest` instala v56 para SDK 54.

### Error 4: Metro busca ./src/App (entry point incorrecto)
```
Unable to resolve module ./src/App from C:\AppCaracol/.
None of these files exist: src\App(.web.ts|.ts|.web.tsx|.tsx|...)
```
**Causa:** Expo SDK 54 default busca `./src/App` (Expo Router pattern). App.tsx estaba en la raíz.
**Fix:** Agregar `"main": "./App.tsx"` en app.json > expo.

## Diagnóstico: Cómo verificar cada capa

```bash
# 1. ¿babel-preset-expo está instalado?
ls node_modules/babel-preset-expo/package.json
# Si NO existe: npm install --save-dev babel-preset-expo@~SDK_VERSION.0.10

# 2. ¿Está como dep anidada (no accesible)?
find node_modules -path "*/babel-preset-expo/package.json"
# Si solo aparece en node_modules/expo/node_modules/: instalar como dep directa

# 3. ¿El bundler arranca?
npx expo start --web --port 8085
# Verificar: netstat -an | grep PORT → LISTENING

# 4. ¿El bundle JS compila sin errores?
curl -s "http://localhost:PORT/App.bundle?platform=web&dev=true" | head -5
# Si devuelve JS (var __BUNDLE_START_TIME__...): OK
# Si devuelve JSON con "UnableToResolveError": fix imports

# 5. ¿Errores reales vs boilerplate?
curl -s "http://localhost:PORT/App.bundle?platform=web&dev=true" | grep -c "UnableToResolve\|TransformError"
# 0 = limpio
```

## tsconfig + react-native type conflicts

Al editar archivos .ts/.tsx, el linter puede mostrar errores de conflictos entre `@types/node` y `react-native` globals (Blob, Request, Response, WebSocket). Estos son **falsos positivos** del linter estático — `npx tsc --noEmit` pasa limpio porque expo/tsconfig.base los maneja correctamente.

No intentar "fixear" estos conflictos agregando `skipLibCheck` o modificando types — es un problema conocido de Expo web.
