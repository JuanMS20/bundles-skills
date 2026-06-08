# Roblox Built-in Assets for MCP Development

## Sound IDs

| Sound | Path | Use |
|-------|------|-----|
| Electronic ping | `rbxasset://sounds/electronic_ping.wav` | Zap, laser, sci-fi UI |
| Click | `rbxasset://sounds/click.wav` | UI click, gun cock |
| Powerup | `rbxasset://sounds/powerup.wav` | Pickup, activate |

**Note**: Increase pitch (`.Pitch = 1.2-1.5`) for higher-pitched zap effects without finding a different sound file.

## Particle Textures

| Texture | Path | Use |
|---------|------|-----|
| Sparkles | `rbxasset://textures/particles/sparkles_main.dds` | Lightning beams, impact sparks, glow effects |

## Beam Configuration Quick Reference

| Property | Lightning Gun Value | Effect |
|----------|-------------------|--------|
| `LightEmission = 1` | Additive blending | Glows through other objects |
| `LightInfluence = 0` | Unaffected by lighting | Stays bright in dark areas |
| `FaceCamera = true` | Always visible | Beam visible from any angle |
| `TextureMode = Wrap` | Repeats along beam | TextureSpeed creates motion |
| `TextureSpeed = 10` | Fast cycling | Creates electrical flicker effect |

## Mesh Generation Notes

- `generate_mesh` produces: `Model → world → body → body_geom (MeshPart)`
- Mesh has built-in texture/UV mapping
- Default color is medium stone grey
- The generated model auto-parents to Workspace — must be reparented
- The empty `Model → world → body` container can be deleted after extracting `body_geom`
