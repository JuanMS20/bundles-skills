# Physics Verification Pattern

Before shipping a physics-based game, run this simulation to verify parameters produce playable results.

## When to run
After implementing the game loop and before declaring "done". Especially when:
- Game has projectile motion (slingshot, cannon, bow)
- Objects must reach specific positions
- Damage model depends on velocity
- Collision response affects reachability

## Simulation script pattern (Python)

```python
import math

# Mirror game constants exactly
SLING_X, SLING_Y = 150, 480
MAX_STRETCH = 120
POWER = 0.20
GRAVITY = 0.5
GROUND = 550
DRAG = 0.999
BIRD_R = 15

def simulate(angle_deg, power=POWER, stretch=MAX_STRETCH):
    angle = math.radians(angle_deg)
    speed = stretch * power
    vx = speed * math.cos(angle)
    vy = -speed * math.sin(angle)
    x, y = float(SLING_X), float(SLING_Y)

    for i in range(300):
        vx *= DRAG
        vy += GRAVITY
        x += vx
        y += vy

        if y + BIRD_R >= GROUND:
            return {'x': round(x), 'hit': 'ground'}
        # Add collision checks against targets here

    return {'x': round(x), 'hit': 'timeout'}

# Sweep angles to find viable strategies
for angle in range(10, 80, 5):
    r = simulate(angle)
    print(f"{angle:3d} deg -> x={r['x']:4d}, hit={r['hit']}")
```

## What to check
1. **Max range >= target distance**: At least one angle reaches the target
2. **Multiple viable angles**: Not just one magic angle (boring gameplay)
3. **Damage math**: At impact speed, does damage >= target HP?
4. **After first collision**: Does reduced velocity still reach secondary targets?

## Common parameter fixes

| Problem | Fix |
|---------|-----|
| Projectile falls short | Increase POWER or MAX_STRETCH |
| Projectile overshoots everything | Decrease POWER or increase GRAVITY |
| Only one angle works | Adjust target positions or increase max range |
| Blocks too hard to break | Reduce block HP or increase damage multiplier |
| Bird bounces off blocks backward | Change collision from bounce (negative) to slow (positive fraction) |
