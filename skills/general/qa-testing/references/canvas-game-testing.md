# Canvas Game Testing Patterns

## Why Programmatic Testing Fails on Canvas Games

HTML5 Canvas games are single-file, no-DOM, no-framework. Standard testing approaches hit walls:

### Problem 1: Variables not on `window`
```javascript
// In a <script> tag:
const C = document.getElementById('c');  // NOT on window
let state, birdQueue, pigs, blocks;      // NOT on window
function update() { ... }                // ON window (function declaration hoisting)
```
- `let`/`const` at top-level are block-scoped in script context
- `function` declarations ARE hoisted to global scope
- **Workaround**: Only test via function calls, not variable reads

### Problem 2: Synthetic events don't work
```javascript
// This often fails:
canvas.dispatchEvent(new MouseEvent('mousedown', {clientX: x, clientY: y}));
// Handler may check: event.isTrusted (always false for synthetic)
// Or coordinate mapping differs from real input
```
- `isTrusted` is `false` for programmatically created events
- Some handlers use `e.touches` which synthetic events don't populate
- **Workaround**: Test via direct function calls, not event simulation

## Effective Testing Strategy for Canvas Games

### 1. Code Review (Primary Method)
Read the entire codebase and check:
- **State machine**: Are all states reachable? Are transitions correct?
- **Collision detection**: AABB vs circle-rect mismatches? Edge cases?
- **Boundary conditions**: What happens at screen edges? Negative coords?
- **Score logic**: Reset conditions? Accumulation bugs?
- **Physics constants**: Gravity, friction, bounce — do they feel right?

### 2. Function-Level Testing (When Accessible)
```javascript
// If functions are on window, call them directly:
window.loadLevel(0);    // Does it reset state correctly?
window.init();          // Does it initialize all variables?
```

### 3. Visual Verification
- Open in browser, play through manually
- Screenshot key states (start, mid-action, win, lose)
- Compare expected vs actual rendering

### 4. Console State Inspection (Limited)
```javascript
// Check what IS accessible:
typeof window.functionName  // 'function' if hoisted
typeof window.variableName  // 'undefined' for let/const
```

## Common Bugs in Canvas Games

| Bug Type | How to Find |
|----------|-------------|
| State machine gaps | Map all states, check every transition |
| Score accumulation | Check reset paths (retry, new level, game over) |
| Collision precision | AABB vs circle-rect mismatch |
| Boundary escapes | Check all 4 edges + off-screen cleanup |
| Frame-dependent logic | `Math.random()` in render = jittery visuals |
| Memory leaks | Arrays that grow (trail, explosions) — check max sizes |

## Quick Checklist for Canvas Games

```
[ ] All game variables accessible (or documented why not)
[ ] State machine has no dead ends
[ ] Score resets correctly on retry/new level
[ ] Collision detection matches visual shapes
[ ] Boundary checks on all 4 edges
[ ] No Math.random() in render functions
[ ] Trail/particle arrays have max size limits
[ ] Event handlers work with touch AND mouse
[ ] Responsive scaling preserves aspect ratio
[ ] Game loop uses requestAnimationFrame (not setInterval)
```
