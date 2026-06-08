
# Projectile Physics Simulation Template

Frame-by-frame simulation matching a typical canvas game loop.
Adapt constants and geometry to your specific game.

```python
import math

# === GAME CONSTANTS (match your game code) ===
SLING_X, SLING_Y = 150, 480
MAX_STRETCH = 120
GRAVITY = 0.5          # per frame
GROUND = 550
DRAG = 0.999           # velocity multiplier per frame
POWER = 0.20           # stretch * power = max velocity
BIRD_R = 15

# === LEVEL GEOMETRY ===
targets = [{'x': 790, 'y': 380, 'r': 20, 'hp': 2}]  # circles
obstacles = [{'x': 700, 'y': 430, 'w': 40, 'h': 120, 'hp': 3}]  # rectangles

def simulate(aim_angle_deg, stretch=MAX_STRETCH):
    angle = math.radians(aim_angle_deg)
    speed = stretch * POWER
    vx = speed * math.cos(angle)
    vy = -speed * math.sin(angle)  # negative = upward
    x, y = float(SLING_X), float(SLING_Y)
    
    # Deep copy targets/obstacles for mutation
    targets_left = [dict(t) for t in targets]
    obstacles_left = [dict(o) for o in obstacles]
    
    for frame in range(300):
        vx *= DRAG
        vy += GRAVITY
        x += vx
        y += vy
        speed_now = math.sqrt(vx*vx + vy*vy)
        
        # Ground
        if y + BIRD_R >= GROUND:
            break
        
        # Target collision (circle-circle)
        for t in targets_left:
            if t['hp'] > 0 and math.hypot(x - t['x'], y - t['y']) < BIRD_R + t['r']:
                dmg = max(1, int(speed_now / 5))
                t['hp'] -= dmg
                # Option A: bounce backward (harder)
                # vx *= -0.4; vy *= -0.4
                # Option B: plow through (easier, more fun)
                vx *= 0.5; vy *= 0.5
        
        # Obstacle collision (AABB)
        for o in obstacles_left:
            if o['hp'] > 0:
                if x < o['x']+o['w'] and x+BIRD_R > o['x'] and y < o['y']+o['h'] and y+BIRD_R > o['y']:
                    dmg = max(1, int(speed_now / 5))
                    o['hp'] -= dmg
                    vx *= 0.5; vy *= 0.5
    
    alive = sum(1 for t in targets_left if t['hp'] > 0)
    return alive == 0  # True = all targets destroyed

# === BRUTE FORCE ===
print("Checking all angle combos (10-50°, step 5)...")
for a1 in range(10, 55, 5):
    for a2 in range(10, 55, 5):
        for a3 in range(10, 55, 5):
            if simulate(a3):  # adjust for your bird sequence
                print(f"  SOLVABLE: [{a1}, {a2}, {a3}]")
                break
        else: continue
        break
    else: continue
    break
else:
    print("  NOT SOLVABLE — adjust physics or layout")
```

## Key Tuning Knobs

| Parameter | Effect | Typical Range |
|-----------|--------|---------------|
| POWER | Higher = faster = longer range | 0.15 - 0.25 |
| GRAVITY | Higher = steeper arc = shorter range | 0.3 - 0.8 |
| DRAG | Lower = more air resistance = shorter range | 0.995 - 1.0 |
| BOUNCE factor | Negative = bounce back (hard), Positive = plow through (easy) | -0.5 to 0.6 |

## Reachability Formula (no drag)

max_range ≈ (2 * v² * sin(2θ)) / g
at 45°: max_range = v² / g

With POWER=0.20 and MAX_STRETCH=120:
  v_max = 24, range = 24²/0.5 = 1152 px (no drag)
  With drag 0.999: effective range ≈ 75-85% of max
