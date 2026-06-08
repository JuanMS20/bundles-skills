# AppCaracol — React Native/Expo Reference

## Stack
- Expo SDK 54, React 19.1, React Native 0.81.5, TypeScript 5.9
- Navigation: @react-navigation/bottom-tabs v7
- Camera: expo-camera v17, expo-media-library v18
- Location: expo-location v18

## Unified Color Palette
```ts
primary: '#003087'    // azul — navegación, headers, botones principales
success: '#13EC37'    // verde — estado "vivo", feedback positivo
accent: '#6C63FF'     // púrpura — highlights, mapa, elementos destacados
```

## SnailStatus Enum
```ts
enum SnailStatus {
  UNKNOWN = 'unknown',
  ALIVE = 'alive',    // Caracol vivo
  EMPTY = 'empty',    // Concha vacía
  GROUP = 'group',    // Grupo de caracoles
}
```

## Camera Flow
1. SafetyGuide (pre-capture recommendations)
2. CameraPreview (expo-camera CameraView)
3. StatusSelector (alive/empty/group)
4. CaptureButton (disabled until status selected)
5. On capture: photo → classify → save to library → GPS coordinates

## GPS Integration
- `requestForegroundPermissionsAsync()` → check status
- `getCurrentPositionAsync({ accuracy: Accuracy.High })` → LocationObject
- Always use safe variant (returns null on failure) — GPS is supplementary, not blocking

## Branch Strategy
- `integration` = target merge branch
- Each contributor owns their branch (read-only for others)
- Use `git show branch:path` to read other branches without checkout

## Known Pitfalls
- Text component variants use FULL names: `heading1`, `heading2`, `heading3`, `body`, `bodySmall`, `caption`, `overline` — NOT `h1`, `h2`, `h3`
- `gap: -4` is invalid in React Native — use `marginRight: -N` or flex layout
- app.json name can be inherited from main branch — verify with `git show main:app.json | grep name`
- TypeScript compilation check (`npx tsc --noEmit`) catches these issues before runtime
