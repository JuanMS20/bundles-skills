# AppCaracol — Multi-Branch Exploration Example

## Repo
`https://github.com/esteban-dev-131/AppCaracol`

## Branches
- `main` — base
- `camara` — Clean Architecture (domain/application/infrastructure/presentation)
- `home_screen` — Atomic Design + navigation (merged camara code)
- `mapa` — Atomic Design + react-native-maps
- `integration` — target merge branch (empty at time of analysis)

## Commands Used

```bash
# List all branches
git branch -a

# Map files per branch
git ls-tree -r --name-only camara | grep -E '\.(ts|tsx|js|jsx)$'
git ls-tree -r --name-only origin/home_screen | grep -E '\.(ts|tsx|js|jsx)$'
git ls-tree -r --name-only origin/mapa | grep -E '\.(ts|tsx|js|jsx)$'

# Read key files without checkout
git show camara:package.json
git show camara:src/constants/colors.ts
git show camara:src/camera/presentation/screens/CameraScreen.tsx
git show origin/home_screen:App.tsx
git show origin/home_screen:src/home/navigator/AppNavigator.tsx
git show origin/mapa:constants/colors.ts
```

## Conflicts Found

1. **3 color palettes**: camara=#003087, home_screen=#13EC37, mapa=#6C63FF
2. **Duplicate components**: home_screen and mapa share identical atoms/molecules
3. **Import paths**: home_screen uses `@/` (babel module-resolver), camara uses relative paths
4. **Entry points**: each branch has different App.tsx/App.js
5. **Dependencies**: each branch has different package.json

## Key Insight
`home_screen` had already merged `camara` code (camera/ directory present). `mapa` had duplicate shared components. The integration branch was empty — all code needed to be brought in.

## What We Built

After exploration, the integration branch was populated with:
- **25 files** in `src/` following Atomic Design
- **Shared constants**: colors.ts (unified palette), typography.ts, spacing.ts
- **Types**: SnailStatus enum, Hallazgo, GpsCoordinates
- **Atoms**: Button (4 variants), Text (7 variants), Icon (5 families), Badge (4 variants), SnailIcon
- **Molecules**: StatusSelector, CaptureButton
- **Organisms**: CameraControls, CameraPreview, SafetyGuide
- **Templates**: CameraTemplate
- **Services**: camera.ts (permissions, capture, save), gps.ts (location)
- **Screens**: CameraScreen (full flow), HomeScreen/MapScreen/AlertsScreen/ProfileScreen (placeholders)
- **Navigation**: AppNavigator with BottomTabNavigator (5 tabs, centered camera)
- **Config**: package.json, tsconfig.json, babel.config.js, App.tsx

## Bugs Found During QA
1. TypeScript error: `"h3"` variant → should be `"heading3"` (Text component uses full names)
2. `gap: -4` not supported in React Native (StatusSelector groupIcons)
3. app.json had "AppCaballo" inherited from main branch (not from our code)
4. Missing `|` in Icon.tsx union type (syntax error)
