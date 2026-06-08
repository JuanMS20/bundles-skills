# Physics Simulation Script for Game Design

## Usage
Run this Python script BEFORE implementing a projectile-based game. Adjust constants to match your game's physics, then verify all targets are reachable.

## Script
```python
import math

# === GAME CONSTANTS (copy from your actual game) ===
SLING_X, SLING_Y = 150, 480
MAX_STRETCH = 120
GRAVITY = 0.5
GROUND = 550
DRAG = 0.999
POWER = 0.20

def simulate(aim_angle_deg, targets, blocks):
    """Simulate bird trajectory. Returns hit info."""
    angle = math.radians(aim_angle_deg)
    speed = MAX_STRETCH * POWER
    vx = speed * math.cos(angle)
    vy = -speed * math.sin(angle)
    x, y = float(SLING_X), float(SLING_Y)
    R = 15  # bird radius

    for frame in range(300):
        vx *= DRAG; vy += GRAVITY
        x += vx; y += vy
        speed_now = math.sqrt(vx*vx + vy*vy)

        if y + R >= GROUND:
            return {'final_x': round(x), 'hit': 'ground'}

        for t in targets:
            if t['hp'] > 0:
                if math.hypot(x - t['x'], y - t['y']) < R + t.get('r', 20):
                    dmg = max(1, int(speed_now / 5))
                    t['hp'] -= dmg
                    vx *= 0.4; vy *= 0.4
                    if t['hp'] <= 0:
                        return {'final_x': round(x), 'hit': t.get('name', 'target'), 'destroyed': True}

        for b in blocks:
            if b['hp'] > 0:
                if x < b['x']+b['w'] and x+R > b['x'] and y < b['y']+b['h'] and y+R > b['y']:
                    dmg = max(1, int(speed_now / 5))
                    b['hp'] -= dmg
                    vx *= 0.5; vy *= 0.5
                    if b['hp'] <= 0:
                        blocks.remove(b)

    return {'final_x': round(x), 'hit': 'timeout'}

# === TEST ===
# Brute-force angles to find solution
for angle in range(10, 60, 5):
    targets = [{'x': 790, 'y': 380, 'r': 20, 'hp': 2, 'name': 'pig'}]
    blocks = [{'x': 700, 'y': 430, 'w': 40, 'h': 120, 'hp': 3}]
    result = simulate(angle, targets, blocks)
    status = "HIT!" if result.get('destroyed') else result['hit']
    print(f"  {angle:2d}° → x={result['final_x']:4d}, {status}")
```

## Key formulas
- Max velocity: `MAX_STRETCH * POWER`
- Optimal angle for max range: ~45° (with drag, slightly less)
- Time of flight (no drag): `2 * vy_initial / GRAVITY`
- Range (no drag): `vx * time_of_flight`
- Damage: `max(1, floor(speed / 5))`

## Verification checklist
1. All angles from 10° to 50° tested
2. At least one angle hits each pig
3. At least one angle destroys enough blocks to expose pigs
4. Not too easy: multiple birds shouldn't trivially clear everything
