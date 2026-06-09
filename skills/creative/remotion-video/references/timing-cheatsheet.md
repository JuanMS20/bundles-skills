# Timing Cheatsheet

## Bézier Curves (CSS-compatible)

| Name | Curve | Use Case |
|---|---|---|
| Crisp ease-out | `bezier(0.16, 1, 0.3, 1)` | UI entrances, modals, toasts |
| Smooth ease-in-out | `bezier(0.65, 0, 0.35, 1)` | General transitions |
| Snappy spring-like | `bezier(0.34, 1.56, 0.64, 1)` | Buttons, badges, playful |
| Gentle ease-out | `bezier(0.25, 1, 0.5, 1)` | Text fades, backgrounds |

## Spring Configs

| Type | Config | Use Case |
|---|---|---|
| Quick bounce | `{damping: 10, stiffness: 100}` | Pop-in elements |
| Smooth settle | `{damping: 20, stiffness: 80}` | Panel slides |
| Heavy object | `{damping: 25, stiffness: 40}` | Large blocks, dramatic |

## Duration Rules

- **Entrance**: 0.5-1.5s (15-45 frames @ 30fps)
- **Exit**: 0.3-0.8s (faster than entrance)
- **Hold / read**: 2-4s for text, 1-2s for icons
- **Transition**: 0.5-1s between scenes
