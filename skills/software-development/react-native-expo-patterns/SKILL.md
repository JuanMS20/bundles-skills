---
name: react-native-expo-patterns
description: "React Native + Expo SDK patterns: Atomic Design structure, navigation, camera/GPS services, platform quirks, and common pitfalls. Use when building or reviewing React Native/Expo apps, setting up project structure, or debugging RN-specific issues."
tags: [react-native, expo, mobile, atomic-design, typescript]
---

# React Native + Expo Patterns

Project structure, navigation, services, and platform-specific pitfalls for React Native apps using Expo SDK 54+.

## Project Structure (Atomic Design)

```
src/
├── constants/       (colors.ts, typography.ts, spacing.ts)
├── types/           (shared TypeScript types, enums)
├── services/        (business logic: GPS, camera, storage)
├── components/
│   ├── atoms/       (Button, Text, Icon, Badge — reusable primitives)
│   ├── molecules/   (StatusSelector, CaptureButton — composites)
│   ├── organisms/   (CameraControls, Header — complex UI sections)
│   └── templates/   (CameraTemplate, MapTemplate — page layouts)
├── screens/         (one folder per screen: camera/, home/, map/, alerts/, profile/)
├── navigation/      (AppNavigator with BottomTabNavigator)
└── index.ts         (barrel exports)
```

**Rules:**
- Atoms: zero internal dependencies, accept all data via props
- Molecules: compose 2-3 atoms, no business logic
- Organisms: compose molecules + services, handle user interactions
- Templates: define page structure, accept screen content as props
- Screens: orchestrate template + services + state

## Navigation Pattern

```tsx
// BottomTabNavigator with centered camera tab
const Tab = createBottomTabNavigator();

<Tab.Navigator screenOptions={{ headerShown: false }}>
  <Tab.Screen name="Inicio" component={HomeScreen} />
  <Tab.Screen name="Mapa" component={MapScreen} />
  <Tab.Screen name="Camara" component={CameraScreen}
    options={{
      tabBarLabel: () => null,
      tabBarIcon: ({ size }) => (
        <View style={cameraTabStyle}> {/* elevated circle */ }
          <Entypo name="camera" size={24} color={Colors.white} />
        </View>
      ),
    }}
  />
  <Tab.Screen name="Alertas" component={AlertsScreen} />
  <Tab.Screen name="Perfil" component={ProfileScreen} />
</Tab.Navigator>
```

**Dependencies:** `@react-navigation/native`, `@react-navigation/bottom-tabs`, `react-native-safe-area-context`, `react-native-screens`

## Service Pattern (Camera/GPS)

```tsx
// services/camera.ts — defensive imports for optional native modules
let CameraView: any;
try {
  CameraView = require('expo-camera').CameraView;
} catch { CameraView = null; }

export async function capturePhoto(cameraRef: React.RefObject<any>) {
  if (!cameraRef?.current) throw new Error('No camera ref');
  const camera = cameraRef.current;
  // Different expo-camera versions expose different methods
  if (typeof camera.takePictureAsync === 'function') {
    return await camera.takePictureAsync({ quality: 0.9 });
  }
  if (typeof camera.takePicture === 'function') {
    return await camera.takePicture({ quality: 0.9 });
  }
  throw new Error('Camera does not expose capture method');
}
```

```tsx
// services/gps.ts — API: expo-location v18
import * as Location from 'expo-location';

export async function getCurrentPosition() {
  const { status } = await Location.requestForegroundPermissionsAsync();
  if (status !== 'granted') throw new Error('Location permission denied');
  return await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.High });
}

// Safe variant — returns null instead of throwing
export async function getCurrentPositionSafe() {
  try { return await getCurrentPosition(); }
  catch { return null; }
}
```

## Project Config

### package.json
Key dependencies for Expo SDK 54:
```json
{
  "expo": "~54.0.33",
  "expo-camera": "~17.0.10",
  "expo-location": "~18.0.1",
  "expo-media-library": "~18.2.1",
  "@react-navigation/bottom-tabs": "^7.15.9",
  "@react-navigation/native": "^7.2.2",
  "react-native-safe-area-context": "~5.6.0",
  "react-native-screens": "~4.16.0",
  "@expo/vector-icons": "^15.0.3"
}
```

### babel.config.js (for `@/` imports)
```js
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      ['module-resolver', {
        extensions: ['.ios.js', '.android.js', '.js', '.ts', '.tsx', '.json'],
        alias: { '@': './src' },
      }],
    ],
  };
};
```

### tsconfig.json
```json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] }
  },
  "include": ["**/*.ts", "**/*.tsx"]
}
```

## TypeScript Smoke Test (FIRST STEP before any QA)

Always run `npx tsc --noEmit` as the first verification step. Catches:
- Wrong variant names (e.g. `"h3"` vs `"heading3"`)
- Broken imports
- Type mismatches
- Missing props

```bash
cd project/ && npx tsc --noEmit 2>&1
```

Zero errors = proceed. Any error = fix before anything else.

## Architecture Decision: Atomic Design > Clean Architecture

When building React Native apps with Atomic Design (atoms/molecules/organisms/templates), do NOT use Clean Architecture (domain/application/infrastructure/presentation) — even if existing code uses it. The user may have a strong preference for consistency across the codebase.

If you encounter Clean Architecture code that needs to be integrated:
1. Extract the business logic into `src/services/` (replaces use cases + adapters)
2. Extract types into `src/types/` (replaces domain entities)
3. Rewrite UI components into atoms/molecules/organisms structure
4. Delete the old domain/application/infrastructure folders

## Platform Quirks

| Issue | Cause | Fix |
|-------|-------|-----|
| `gap: -4` not working | React Native doesn't support negative gap | Use `marginRight: -N` or flex layout |
| Text not rendering | Text inside `<View>` doesn't display | Always wrap text in `<Text>` |
| Camera `takePictureAsync` undefined | expo-camera version difference | Defensive check: try `takePictureAsync` then `takePicture` |
| `@/` import fails | Missing babel module-resolver | Add plugin to babel.config.js + paths to tsconfig |
| MediaLibrary fails in Expo Go | Not declared in manifest | Wrap in try/catch, treat as optional |
| Opacity affects children | RN `opacity` property applies to entire view | Use hex alpha: `#00308780` instead of `opacity: 0.5` |
| Text variant `"h3"` type error | Text component uses `heading3` not `h3` | Use full names: `heading1`, `heading2`, `heading3`, `body`, `bodySmall`, `caption`, `overline` |
| app.json has wrong name | Inherited from main branch or teammate's branch | Check all branches: `git show <branch>:app.json | grep name` before assuming it's your bug |
| Metro busca `./src/App` | Expo SDK 54 defaults to Expo Router entry | Add `"main": "./App.tsx"` in app.json > expo |
| `Cannot find module 'babel-preset-expo'` | Nested dep, not resolved at root | `npm install --save-dev babel-preset-expo@~SDK.0.10` — pin version! |
| App crash = white screen | No Error Boundary in component tree | Wrap App in `<ErrorBoundary>` with fallback UI |

## Color Palette Convention

Use hex with alpha for transparency, NEVER the `opacity` property:
```tsx
// ✅ CORRECT
backgroundColor: '#00308780'  // primary with 50% alpha

// ❌ WRONG — affects all children
style={{ opacity: 0.5 }}
```

## Metro Bundler Pitfalls (SDK 54+)

### app.json requiere `"main"` explícito cuando NO usas Expo Router

Expo SDK 54 asume Expo Router por defecto y busca `./src/App`. Si usas el patrón clásico con `App.tsx` en la raíz, Metro falla con:

```
Unable to resolve module ./src/App from C:\project/.
None of these files exist: src\App(.web.ts|.ts|.web.tsx|.tsx|...)
```

**Fix:** Agregar campo `main` en `app.json`:
```json
{
  "expo": {
    "name": "MyApp",
    "main": "./App.tsx",
    ...
  }
}
```

### babel-preset-expo debe ser devDependency directa

Aunque `babel-preset-expo` está anidado dentro de `expo` en node_modules, Metro no siempre lo resuelve desde ahí. El bundler falla con:

```
Cannot find module 'babel-preset-expo'
```

`npx expo install --fix` NO siempre resuelve esto. La instalación de la versión correcta para tu SDK es obligatoria:

```bash
npm install --save-dev babel-preset-expo@~SDK_VERSION.0.10
# Ejemplo para SDK 54:
npm install --save-dev babel-preset-expo@~54.0.10
```

**NUNCA** instales la última versión sin pinning — `npm install --save-dev babel-preset-expo` instala la v56 en SDK 54, y Expo muestra warning de incompatibilidad.

### "Cannot find module" en bundle compilado NO es error real

Al greppear "Cannot find module" en el bundle JS compilado, encontrarás 2 matches en las primeras ~60 líneas. Son **throw statements del Metro runtime** (mecanismo interno de `require()`), no errores de resolución reales.

```bash
# Esto muestra 2 matches FALSOS:
curl -s "http://localhost:PORT/App.bundle?platform=web&dev=true" | grep "Cannot find module"
# Líneas 61 y 63 son Metro boilerplate: throw new Error("Cannot find module...")
```

Para detectar errores reales, buscar `UnableToResolve` o `TransformError` en su lugar.

### Error Boundary obligatorio

React Native SIN Error Boundary = pantalla blanca silenciosa si cualquier componente crashea. Agregar en App.tsx:

```tsx
import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 }}>
      <Text style={{ fontSize: 18, fontWeight: 'bold' }}>Algo salió mal</Text>
      <Text style={{ color: '#666', marginTop: 8 }}>{error.message}</Text>
      <Button label="Reintentar" onPress={resetErrorBoundary} />
    </View>
  );
}

export default function App() {
  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <SafeAreaProvider>
        <AppNavigator />
      </SafeAreaProvider>
    </ErrorBoundary>
  );
}
```

Ver detalles en `references/expo-sdk54-metro-pitfalls.md`.

## Testing con Jest (SDK 54+)

### Setup

```bash
npx expo install jest-expo jest @types/jest -- --dev
```

### jest.config.js

El preset `jest-expo` NO maneja path aliases (`@/`). Se necesita `moduleNameMapper` manual:

```js
module.exports = {
  preset: 'jest-expo',
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  transformIgnorePatterns: [
    'node_modules/(?!((jest-)?react-native|@react-native(-community)?)|expo(nent)?|@expo(nent)?|react-navigation|@react-navigation/.*|react-native-svg)',
  ],
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{ts,tsx}',
    '<rootDir>/src/**/*.{spec,test}.{ts,tsx}',
  ],
};
```

### Mocking expo modules

Los módulos nativos de Expo necesitan mocks explícitos:

```ts
jest.mock('expo-location', () => ({
  requestForegroundPermissionsAsync: jest.fn(),
  getCurrentPositionAsync: jest.fn(),
  Accuracy: { High: 4 },
}));

jest.mock('expo-camera', () => ({
  CameraView: { requestCameraPermissionsAsync: jest.fn() },
}));

jest.mock('expo-media-library', () => ({
  requestPermissionsAsync: jest.fn(),
  createAssetAsync: jest.fn(),
}));
```

### Mock setup para `saveToLibrary` y similares

Los mocks de funciones del servicio deben retornar valores — de lo contrario `undefined` rompe los tests:

```ts
// ❌ WRONG — mock no configurado, retorna undefined
const result = await saveToLibrary('file:///photo.jpg');
expect(result).toBeDefined(); // FALLA: result is undefined

// ✅ CORRECT — mock con retorno explícito
const { createAssetAsync } = require('expo-media-library');
(createAssetAsync as jest.Mock).mockResolvedValue({ uri: 'file:///photo.jpg' });
const result = await saveToLibrary('file:///photo.jpg');
expect(result).toBeDefined();
```

### Qué testear primero

Prioridad para apps RN/Expo:
1. **Tipos y enums** (cero mocks, rápido verificar contratos)
2. **Constantes** (paleta, tipografía, spacing — validar valores y orden)
3. **Servicios** con mocks de expo-* (GPS, camera)
4. **Components** con `react-test-renderer` (solo si hay lógica no trivial)

## Prod Bundle Verification

Verificar el bundle de producción ANTES de declarar "listo":

```bash
# Arrancar en modo producción
npx expo start --web --port 8088 --no-dev --minify

# Medir bundle
curl -s "http://localhost:8088/App.bundle?platform=web&dev=false&minify=true" > /tmp/bundle-prod.js
wc -c /tmp/bundle-prod.js          # raw size
gzip -c /tmp/bundle-prod.js | wc -c  # gzip size (el que importa)

# Verificar errores reales (no Metro boilerplate)
grep "UnableToResolve\|TransformError" /tmp/bundle-prod.js
```

**Budgets típicos:**
- Dev bundle: ~3.5MB (normal, incluye sourcemaps)
- Prod bundle raw: ~1.3MB
- Prod bundle gzip: **< 500KB** es el target. Si pasa de 500KB, hay libs pesadas.

## npm audit en Expo

Expo SDK 54 reporta ~11 vulnerabilidades "moderate" en canary versions de @expo/config-plugins. Son **falsos positivos del auditor** (afectan canary builds, no stable). No bloquean. No intentar `npm audit fix --force` — puede romper deps.

## Checklist: New RN/Expo Project

- [ ] package.json with all required deps
- [ ] babel.config.js with module-resolver
- [ ] tsconfig.json with `@/` paths
- [ ] app.json with `"main": "./App.tsx"` (if not using Expo Router)
- [ ] babel-preset-expo@~SDK_VERSION.0.10 as devDependency
- [ ] src/constants/ (colors, typography, spacing)
- [ ] src/types/ (shared enums, interfaces)
- [ ] src/components/atoms/ (Button, Text, Icon, Badge)
- [ ] src/services/ (GPS, camera, storage)
- [ ] src/navigation/ (AppNavigator)
- [ ] src/screens/ (one per tab)
- [ ] App.tsx with SafeAreaProvider + AppNavigator + ErrorBoundary
- [ ] jest.config.js + test scripts in package.json
- [ ] Prod bundle verification (< 500KB gzip)
