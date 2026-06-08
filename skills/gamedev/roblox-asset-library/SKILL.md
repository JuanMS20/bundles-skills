---
name: roblox-asset-library
description: "Directorio curado de assets gratuitos para desarrollo de juegos Roblox: 3D models, texturas PBR, UI kits, sonidos, musica, VFX, fuentes, iconos. USA ANTES de generar desde cero."
---

# Roblox Asset Library — Directorio de Recursos Gratuitos

NO generes assets desde cero si ya existen gratuitos. Consulta esta lista PRIMERO.

## Inventario físico actual (C:\Users\ASUS\Desktop\Roblox-Assets\)

```
Roblox-Assets/
├── 3D-Models/                    (~535MB, 23 packs Kenney)
│   ├── Nature/                   nature-kit, kenney-nature-kit
│   ├── Buildings/                city-kit (commercial, industrial, suburban, roads),
│   │                             fantasy-town, modular-dungeon, mini-dungeon, pirate, graveyard
│   ├── Characters/               blocky-characters, animated (retro, protagonists, survivors), cube-pets
│   ├── Vehicles/                 car-kit
│   ├── Weapons/                  blaster-kit
│   ├── Props/                    platformer-kit, food-kit
│   └── Sci-Fi/                   modular-space-kit, factory-kit, space-kit
│   └── (50+ sistemas .rbxm)      combat, quests, tycoon, obby, pets, admin, etc.
│
├── Textures-PBR/                 (~416MB, 45 texturas ambientCG 1K JPG, 14 categorías)
│   ├── Wood/                     Wood049, Wood050, Wood051, Wood065, Wood072, Wood092
│   ├── Stone/                    Rock021, Rock022, Rock023, Rock034, Rock042
│   ├── Metal/                    Metal024, Metal036, Metal042, Metal044B, Metal046B
│   ├── Concrete/                 Concrete040, Concrete041, Ground037, Ground039
│   ├── Fabric/                   Fabric024, Fabric039
│   ├── Ground/                   Ground022, Ground026, Ground030, Tiles058, Tiles078
│   ├── Tiles/                    Tiles059, Tiles060, Tiles075
│   ├── Brick/                    Brick045, Brick049
│   ├── Plastic/                  Plastic004, Plastic006
│   ├── Carpet/                   Carpet004, Carpet005
│   ├── Roof/                     RoofingTiles013A, RoofingTiles013D, RoofingTiles014A
│   ├── Asphalt/                  Asphalt005, Asphalt009
│   ├── Snow/                     Snow002, Snow004
│   ├── Ice/                      Ice002, Ice003
│   ├── Leather/                  Leather002, Leather003
│   ├── Marble/                   Marble004, Marble005
│   └── Plaster/                  Plaster003, Plaster004
│
├── UI/
│   ├── Buttons/                  kenney-ui-pack, kenney-ui-pack-rpg-expansion
│   ├── Icons/                    kenney-game-icons, kenney-game-icons-expansion,
│   │                             kenney_board-game-icons
│   ├── Backgrounds/              kenney-abstract-platformer, kenney_fantasy-ui-borders
│   ├── (root)                    kenney_cursor-pack, kenney_input-prompts,
│   │                             kenney_emotes-pack, kenney_ranks-pack,
│   │                             kenney_ui-pack-sci-fi, kenney_ui-pack-adventure
│
├── Audio/
│   ├── Music/                    kenney-impact-sounds, kenney_music-jingles
│   ├── SFX-UI/                   kenney-ui-audio, kenney-interface-sounds, kenney-casino-audio
│   └── SFX-Combat/               kenney-voiceover-pack, kenney-digital-audio,
│                                 kenney-rpg-audio, kenney_sci-fi-sounds
│
├── VFX/Particles/
│   ├── kenney_particlePack.zip   (80+ sprites: fire, smoke, magic, hearts, sparks, electricity)
│   └── cc0_packs/                (8 packs, 141 PNGs)
│       ├── Explosions            atlas, 50 frames, ring explosion
│       ├── Fire                  8 animated variants + spritesheet
│       ├── Smoke                 spritesheet + Kenney smoke particles
│       └── Magic/Spells          22 animated spells (arcane, fire, ice, water, wind, dark, light)
│
└── Fonts/                        (13 Google Fonts, OFL)
    ├── Fredoka.zip               display variable
    ├── Bangers.zip               comic display
    ├── PressStart2P.zip          pixel/retro
    ├── RubikGlitch.zip           glitch display
    ├── Sigmar.zip                bold display
    ├── LilitaOne.zip             chunky display
    ├── Inter.zip                 UI sans-serif
    ├── DMSans.zip                UI sans-serif
    ├── Nunito.zip                rounded UI sans
    ├── Outfit.zip                geometric sans
    ├── Raleway.zip               elegant sans
    ├── Caveat.zip                handwritten
    └── PatrickHand.zip           handwriting
```

**Todos CC0 (dominio público).** Uso comercial libre sin crédito.
**Google Fonts** son OFL (Open Font License) — uso comercial permitido.

## 1. MODELOS 3D (Low Poly + Realista)

| Fuente | URL | Licencia | Compatibilidad Roblox |
|--------|-----|----------|----------------------|
| **Kenney** | kenney.nl/assets | CC0 | OBJ/FBX → MeshPart |
| **Quaternius** | quaternius.com | CC0 | OBJ/FBX → MeshPart |
| **OpenGameArt** | opengameart.org | Mixta (CC0/CC-BY/GPL) | Verificar por asset |
| **itch.io (3D free)** | itch.io/game-assets/free/tag-3d | Mixta | FBX/OBJ |
| **Roblox Creator Store** | create.roblox.com/store/models | Roblox ToS | Nativa via MCP |

### Importar modelos externos a Roblox
1. Descargar FBX/OBJ
2. En Studio: Import 3D → seleccionar archivo → MeshPart
3. Ajustar Size, Material, Color
4. Para PBR: agregar SurfaceAppearance con texturas ambientCG

## 2. TEXTURAS PBR (SurfaceAppearance)

| Fuente | URL | Licencia | Notas |
|--------|-----|----------|-------|
| **ambientCG** | ambientcg.com | CC0 | 2,000+ materiales. Descargar 1K. Roblox rechaza 2K+ |
| **PolyHaven** | polyhaven.com/textures | CC0 | Calidad profesional. Usar 1K, NormalMap OpenGL |

Un material PBR completo: ColorMap + NormalMap + RoughnessMap + MetalnessMap (opcional).
Formato: PNG. NormalMap: OpenGL (NO DirectX).

## 3. UI / BOTONES / ICONOS

| Fuente | URL | Licencia |
|--------|-----|----------|
| **Game-Icons.net** | game-icons.net | CC-BY (crédito requerido) |
| **Kenney UI** | kenney.nl/assets/ui-pack | CC0 |
| **itch.io (UI free)** | itch.io/game-assets/free/tag-ui | Mixta |
| **CraftPix** | craftpix.net | Mixta |

Roblox UI: ImageLabel/ImageButton, PNG con transparencia, potencias de 2.

## 4. SONIDOS / SFX / MUSICA

| Fuente | URL | Licencia | Formato |
|--------|-----|----------|---------|
| **Kenney Audio** | kenney.nl/assets | CC0 | WAV/MP3 |
| **Pixabay Sound** | pixabay.com/sound-effects | Pixabay License | MP3/WAV |
| **Freesound** | freesound.org | CC0/CC-BY | WAV |
| **SONNISS GDC** | sonniss.com/gameaudiogdc | Royalty-free | WAV |
| **Incompetech** | incompetech.com | CC-BY | MP3 (crédito) |

Roblox acepta: MP3, OGG. Máx ~7 min. Subir via Creator Dashboard.
SoundId: `rbxassetid://XXXXX`

## 5. VFX / PARTICULAS / SPRITE SHEETS

Ya descargados en `VFX/Particles/`:
- Kenney Particle Pack (80+ sprites CC0): fire, smoke, magic, hearts, sparks, electricity
- Explosiones: atlas + 50 frames + ring explosion
- Fuego: 8 variantes animadas + spritesheet
- Humo: spritesheet + Kenney smoke particles
- Magia: 22 hechizos (arcane, fire, ice, water, wind, dark, light)

Para Roblox: ParticleEmitter.Image = sprite PNG subido como ImageAsset.

## 6. FUENTES (Google Fonts OFL)

Ya descargadas en `Fonts/` (ver inventario arriba).
13 fuentes: 6 display, 5 sans-serif UI, 2 decorativas.

Roblox: TextLabel/TextButton usan FontFace. Subir TTF como FontFamily asset.

## 7. CREATOR STORE (VÍA MCP)

Siempre primera opción — nativo, sin conversión.

```
search_creator_store("sword") → insert_from_creator_store
search_creator_store("obby kit")
search_creator_store("tycoon kit")
search_creator_store("particle vfx")
search_creator_store("lighting")
```

## FLUJO: Buscar antes de crear

```
1. Necesito un asset
   ↓
2. Busco en la carpeta física (C:\Users\ASUS\Desktop\Roblox-Assets/)
   → Si existe → importar a Studio
   ↓
3. Busco en Roblox Creator Store via MCP (search_creator_store)
   → Si existe → insert_from_creator_store
   ↓
4. Busco en Kenney/OpenGameArt/ambientCG (CC0)
   → Descargo → Import a Studio
   ↓
5. Recién ahí uso generate_mesh o creación manual
```

## PATRONES DE DESCARGA DIRECTA

### Kenney.nl
```
curl -s 'https://kenney.nl/assets/{slug}' | grep -oP 'https://kenney.nl/media/pages/assets/[^"\s]+\.zip'
curl -L -o output.zip '<URL>'
```

### ambientCG
```
https://ambientcg.com/get?file={Nombre}_1K-JPG.zip
```
Verificar tamaño > 5KB (algunos nombres no existen, devuelven HTML 404 de 33 bytes).

### Google Fonts (vía GitHub)
```
https://github.com/google/fonts/raw/main/ofl/{slug}/{Family}-{Weight}.ttf
```
La API directa de fonts.google.com ya no funciona para descarga programática.

## Licencias rápidas

| Licencia | Crédito? | Comercial? |
|----------|----------|-----------|
| **CC0** | No | Sí |
| **CC-BY** | Sí | Sí |
| **CC-BY-NC** | Sí | NO |
| **OFL (Open Font)** | No | Sí |

## Pitfalls

- **Siempre buscar assets existentes antes de generar desde cero.** La carpeta ya tiene cientos de assets.
- **Kenney URLs no son estáticas**: extraer el hash de la página cada vez.
- **ambientCG nombres inconsistentes**: algunos IDs no existen (HTML 404). Verificar tamaño.
- **Quaternius requiere JS**: no funciona con curl. Usar browser o links manuales.
- **Google Fonts download API rota**: usar GitHub raw como fallback.
- **Roblox rechaza texturas 2K+**: siempre descargar en 1K para SurfaceAppearance.
- **No ejecutar scripts de assets descargados**: revisar .rbxm antes de insertar si son de fuente no confiable.
