---
name: remotion-video
description: |
  Edición profesional de video con Remotion — React-based programmatic video.
  Use cuando el usuario quiera crear, editar o renderizar videos: contenido para YouTube,
  TikTok, Reels, shorts, motion graphics, subtítulos animados, transiciones, color grading,
  o cualquier flujo de post-producción programática.
---

# Remotion Video — Edición Profesional

## Quick Start

```bash
# Proyecto limpio (sin Tailwind — las animaciones CSS no renderizan)
npx create-video@latest --yes --blank --no-tailwind mi-video
cd mi-video
npx remotion studio
```

**Prohibido en Remotion:** CSS transitions, CSS animations, Tailwind animation classes.
Todo motion es frame-driven.

---

## Fundamentos Frame-Driven

| Concepto | API | Para qué sirve |
|---|---|---|
| Frame actual | `useCurrentFrame()` | Devuelve frame 0-indexado del timeline |
| Config de video | `useVideoConfig()` | fps, width, height, durationInFrames |
| Interpolación | `interpolate(frame, [inicio, fin], [desde, hasta], opts)` | Mapear tiempo a valores |
| Curvas Bézier | `Easing.bezier(x1,y1,x2,y2)` | Timing tipo CSS cubic-bezier |
| Física | `spring({frame, fps, config})` | Movimiento natural con damping/stiffness |
| Secuencias | `<Sequence from={frame} durationInFrames={n}>` | Delay o recorte de clips |
| Layout full-bleed | `<AbsoluteFill>` | Contenedor posicionado absolute 0,0,100%,100% |

### Patrón base: entrada suave

```tsx
import { useCurrentFrame, useVideoConfig, interpolate, Easing } from "remotion";

export const FadeUp = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, 1 * fps], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  const y = interpolate(frame, [0, 1 * fps], [30, 0], {
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  return (
    <div style={{ opacity, transform: `translateY(${y}px)` }}>
      Contenido
    </div>
  );
};
```

---

## Formatos por Plataforma

Define resolution y fps en `src/Root.tsx` según destino:

| Plataforma | Resolution | FPS | Ratio | Notas |
|---|---|---|---|---|
| YouTube (landscape) | 1920x1080 | 30/60 | 16:9 | Estándar general |
| YouTube Shorts | 1080x1920 | 30/60 | 9:16 | Vertical |
| TikTok / Reels | 1080x1920 | 30 | 9:16 | Max 10min (TikTok 3min) |
| Instagram Feed | 1080x1080 | 30 | 1:1 | También 4:5 para posts |
| Instagram Stories | 1080x1920 | 30 | 9:16 | 15s max por story |
| Twitter/X | 1280x720 | 30 | 16:9 | También 1:1 |
| LinkedIn | 1920x1080 | 30 | 16:9 | Native video preferido |

---

## Media: Import, Trim, Layering

Assets van en `public/`. Se referencian con `staticFile()`.

### Imágenes
```tsx
import { Img, staticFile } from "remotion";
<Img src={staticFile("fotos/intro.jpg")} style={{ width: "100%" }} />
```

### Video clips (requiere `@remotion/media`)
```bash
npx remotion add @remotion/media
```
```tsx
import { Video, staticFile } from "remotion";
<Video
  src={staticFile("clips/entrevista.mp4")}
  startFrom={120}   // trim inicio (frames)
  endAt={480}       // trim fin
  volume={0.8}
/>
```

### Audio (requiere `@remotion/media`)
```tsx
import { Audio } from "@remotion/media";
<Audio src={staticFile("audio/musica.mp3")} volume={0.2} />
<Audio src={staticFile("audio/voz.mp3")} volume={1} />
```

---

## Secuencias y Timeline

`<Sequence>` es tu herramienta de edición: define inicio y duración de cada clip.

```tsx
import { Sequence, AbsoluteFill } from "remotion";

export const Timeline = () => (
  <AbsoluteFill>
    {/* Capa 0: fondo siempre visible */}
    <Background />

    {/* Capa 1: intro 0-3s */}
    <Sequence from={0} durationInFrames={90}>
      <IntroTitulo />
    </Sequence>

    {/* Capa 2: segmento A 3-10s */}
    <Sequence from={90} durationInFrames={210}>
      <VideoClip src="entrevista.mp4" />
    </Sequence>

    {/* Capa 3: lower thirds (overlay) 4-9s */}
    <Sequence from={120} durationInFrames={150}>
      <LowerThird nombre="Juan Pérez" rol="CEO" />
    </Sequence>

    {/* Capa 4: outro 10-12s */}
    <Sequence from={300} durationInFrames={60}>
      <OutroCTA />
    </Sequence>
  </AbsoluteFill>
);
```

**Overlaps permitidos:** Secuencias superpuestas = layers. El orden en JSX = z-index.

---

## Transiciones Profesionales

```bash
npx remotion add @remotion/transitions
```

```tsx
import { TransitionSeries, linearTiming, springTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";

<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={180}>
    <Escena1 />
  </TransitionSeries.Sequence>

  <TransitionSeries.Transition
    presentation={fade()}
    timing={linearTiming({ durationInFrames: 15 })}
  />

  <TransitionSeries.Sequence durationInFrames={240}>
    <Escena2 />
  </TransitionSeries.Sequence>

  <TransitionSeries.Transition
    presentation={slide({ direction: "from-left" })}
    timing={springTiming({ config: { damping: 18 } })}
  />

  <TransitionSeries.Sequence durationInFrames={120}>
    <Escena3 />
  </TransitionSeries.Sequence>
</TransitionSeries>
```

**Timing:**
- **Fade**: 12-20 frames (0.4-0.7s @ 30fps) — universal, nunca falla
- **Slide/Wipe**: 15-25 frames — dinámico, cuidado con dirección
- **Match cuts**: Sin transición — corte seco en frame exacto

---

## Subtítulos / Captions Animados

### Estilo YouTube / Standard

```tsx
import { useCurrentFrame, Sequence } from "remotion";

const subtitles = [
  { text: "Hola a todos", start: 0, end: 60 },
  { text: "Hoy vamos a aprender", start: 60, end: 150 },
  { text: "cómo editar videos", start: 150, end: 240 },
];

export const Subtitulos = () => (
  <>
    {subtitles.map((sub, i) => (
      <Sequence key={i} from={sub.start} durationInFrames={sub.end - sub.start}>
        <SubtituloLine text={sub.text} />
      </Sequence>
    ))}
  </>
);

const SubtituloLine = ({ text }: { text: string }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  return (
    <div style={{
      position: "absolute", bottom: 80, left: 0, right: 0,
      textAlign: "center", opacity,
    }}>
      <span style={{
        background: "rgba(0,0,0,0.7)", color: "#fff",
        padding: "12px 24px", borderRadius: 8, fontSize: 48, fontWeight: 700,
      }}>{text}</span>
    </div>
  );
};
```

### TikTok Style — Word-by-Word Highlight (Bounce + Color)

```bash
npx remotion add @remotion/captions
```

```tsx
import { useCurrentFrame } from "remotion";
import { parseSrt, createTikTokStyleCaptions, Caption } from "@remotion/captions";

export const TikTokCaptions = () => {
  const frame = useCurrentFrame();

  // Parse SRT file → array of Caption objects
  const captions = parseSrt(srtContent);  // srtContent: string from file

  // Group into "pages" that display together
  const pages = createTikTokStyleCaptions({
    captions,
    combineTokensWithinMilliseconds: 300,  // words closer than 300ms = same page
  });

  // Find current page based on frame
  const currentPage = pages.find(
    (p) => frame >= p.startInFrames && frame < p.endInFrames
  );
  if (!currentPage) return null;

  // Find current word index for highlight
  const currentWordIndex = currentPage.tokens.findIndex(
    (word) => frame >= word.startInFrames && frame < word.endInFrames
  );

  return (
    <div style={{
      position: "absolute",
      bottom: 150, left: 0, right: 0,
      textAlign: "center",
      fontSize: 60, fontWeight: 900,
      fontFamily: "sans-serif",
      textTransform: "uppercase",
      lineHeight: 1.3,
    }}>
      {currentPage.tokens.map((word, i) => (
        <span key={i} style={{
          color: i <= currentWordIndex ? "#ff0055" : "#fff",
          textShadow: "3px 3px 0 #000",
          display: "inline-block",
          marginRight: 12,
          transform: i === currentWordIndex
            ? `scale(${spring({ frame, fps: 30, config: { damping: 8 } })})`
            : "scale(1)",
        }}>
          {word.text}
        </span>
      ))}
    </div>
  );
};
```

**Key props:**
- `combineTokensWithinMilliseconds`: menor = más páginas, word-by-word; mayor = frases completas
- `white-space: pre` en el contenedor para preservar espacios del SRT

### Whisper.cpp Auto-Caption (Local)

```bash
# En template oficial de Remotion TikTok
npm run sub   # transcribe videos en public/ con Whisper.cpp
```

Genera `subtitles.srt` automáticamente. Luego parsear con `parseSrt()` como arriba.

### Estilos por plataforma

| Estilo | Fuente | Color highlight | Tamaño |
|---|---|---|---|
| YouTube | Sans-serif 500 | Blanco sobre fondo negro semitransparente | 36-48px |
| TikTok | Sans-serif 900 uppercase | Color primario vibrante (#ff0055, #00ff88) | 60-72px |
| Instagram Reels | Sans-serif 700 | Blanco con text-stroke negro | 48-60px |
| Podcast | Sans-serif 500 | Amarillo (#ffd700) | 32-40px |

---

## Lower Thirds

```tsx
export const LowerThird = ({ nombre, rol }: { nombre: string; rol: string }) => {
  const frame = useCurrentFrame();
  const x = interpolate(frame, [0, 20], [-400, 0], {
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  return (
    <div style={{
      position: "absolute",
      bottom: 120,
      left: x,
      background: "linear-gradient(90deg, #ff0055, transparent)",
      padding: "16px 32px",
      borderRadius: "0 8px 8px 0",
    }}>
      <div style={{ fontSize: 36, fontWeight: 700, color: "#fff" }}>{nombre}</div>
      <div style={{ fontSize: 24, color: "#ddd" }}>{rol}</div>
    </div>
  );
};
```

---

## Color Grading / Overlay Effects

Ajustes de color, vignette, film grain — todo programático.

```tsx
export const ColorGrade = ({ children }: { children: React.ReactNode }) => (
  <div style={{ position: "relative", width: "100%", height: "100%" }}>
    {children}
    {/* Vignette */}
    <div style={{
      position: "absolute",
      inset: 0,
      background: "radial-gradient(circle, transparent 60%, rgba(0,0,0,0.4) 100%)",
      pointerEvents: "none",
    }} />
    {/* Warm overlay */}
    <div style={{
      position: "absolute",
      inset: 0,
      background: "rgba(255, 160, 60, 0.08)",
      mixBlendMode: "overlay",
      pointerEvents: "none",
    }} />
  </div>
);
```

---

## Audio Waveform Visualizer (Audiograms)

Para podcasts, audio clips, o cualquier video que necesite visualización de audio.

```bash
npx remotion add @remotion/media-utils
```

```tsx
import { useCurrentFrame, useVideoConfig } from "remotion";
import { useAudioData, visualizeAudio } from "@remotion/media-utils";

export const Waveform = ({ audioSrc }: { audioSrc: string }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const audioData = useAudioData(audioSrc);
  if (!audioData) return null;

  // Generate 64 frequency bars from audio data
  const visualization = visualizeAudio({
    audioData,
    frame,
    fps,
    numberOfSamples: 64,
    audioStartTime: 0,
  });

  // Map to bar heights (0-200px)
  const bars = visualization.map((v) => v * 200);

  return (
    <div style={{
      position: "absolute",
      bottom: 100,
      left: 0,
      right: 0,
      display: "flex",
      alignItems: "flex-end",
      justifyContent: "center",
      gap: 4,
      height: 250,
    }}>
      {bars.map((height, i) => (
        <div key={i} style={{
          width: 8,
          height,
          background: "linear-gradient(to top, #ff0055, #ff8800)",
          borderRadius: 4,
        }} />
      ))}
    </div>
  );
};
```

**Alternativas de visualización:**
- **Circular/Radial**: Barras distribuidas en círculo alrededor de centro
- **Wave line**: SVG path con smooth curve basada en samples
- **Spectrum**: Frecuencias bajas, medias, altas con colores distintos

### Variantes de audiogram

| Estilo | Uso | Config |
|---|---|---|
| **Classic bars** | Podcast clips | 64 samples, bar width 6-10px, gradient warm |
| **Circular** | Music visualizer | 128 samples, radius 200px, neon colors |
| **Minimal line** | Professional/corporate | 256 samples, single path, white on dark |
| **Reaction video** | Bottom overlay | 32 samples, large bars, covers bottom 30% |

---

## `<Series>` + Premounting (Performance)

`<Series>` ahorra calcular `from` manualmente — los items se encadenan automáticamente.

```tsx
import { Series } from "remotion";

<Series>
  <Series.Sequence durationInFrames={90}>
    <Intro />
  </Series.Sequence>
  <Series.Sequence durationInFrames={180}>
    <SegmentoA />
  </Series.Sequence>
  <Series.Sequence durationInFrames={120}>
    <SegmentoB />
  </Series.Sequence>
</Series>
```

**Premounting**: Pre-carga un componente N frames antes de que aparezca. Elimina stutter en renders largos.

```tsx
<Sequence from={300} durationInFrames={120}>
  <Sequence premountFor={30}>  {/* preload 30 frames antes */}
    <EscenaCompleja />
  </Sequence>
</Sequence>
```

Regla: premount todo componente que cargue assets grandes (videos, imágenes, fuentes, Lottie).

---

## `<Still>` — Thumbnails y Social Cards

Exporta un frame único como PNG/JPEG para thumbnails de YouTube, Twitter cards, OG images.

```tsx
import { Still } from "remotion";

export const RemotionRoot = () => (
  <>
    <Composition id="Video" component={MiVideo} durationInFrames={900} fps={30} width={1920} height={1080} />
    <Still id="Thumbnail" component={ThumbnailComponent} width={1280} height={720} />
  </>
);
```

```bash
# Render thumbnail
npx remotion still Thumbnail out/thumbnail.png --frame=150
```

**Uso común:** Frame en el peak del video (momento más visualmente interesante).

---

## Dynamic Metadata (`calculateMetadata`)

Cuando la duración del video depende de datos externos (ej: podcast de duración variable, video generado desde API).

```tsx
import { Composition, CalculateMetadataFunction } from "remotion";

const calculateMetadata: CalculateMetadataFunction<MyProps> = async ({
  props,
  abortSignal,
}) => {
  // Fetch data o medir duración de audio
  const audioDuration = await getAudioDuration(props.audioSrc);

  return {
    durationInFrames: Math.ceil(audioDuration * 30),  // 30fps
    width: 1920,
    height: 1080,
    props: {
      ...props,
      duration: audioDuration,
    },
  };
};

export const RemotionRoot = () => (
  <Composition
    id="DynamicVideo"
    component={MiVideo}
    fps={30}
    width={1920}
    height={1080}
    defaultProps={{ audioSrc: staticFile("audio.mp3") }}
    calculateMetadata={calculateMetadata}
  />
);
```

**Casos de uso:**
- Podcast visualizer: duración = duración del audio
- Batch generation: duración = longitud del script JSON
- API-driven: duración = datos del servidor

---

## Export y Render

```bash
# Preview en tiempo real
npx remotion studio

# Render frame único para revisar composición
npx remotion still MiComp --frame=45 --scale=0.5

# Render local (MP4 H.264)
npx remotion render MiComp out/video.mp4

# Render múltiples variantes (formatos)
npx remotion render MiComp out/youtube.mp4 --props='{"format":"landscape"}'
npx remotion render MiComp out/shorts.mp4 --props='{"format":"vertical"}'

# Cloud render (AWS Lambda) — para batch o alta resolución
npx remotion lambda render <site-id> MiComp out/video.mp4
```

---

## Pitfalls

### Defaulting to SaaS/product assumptions
This skill is for **content creators** (YouTube, TikTok, Reels, podcasts, motion graphics), not SaaS explainer videos. Unless the user explicitly says "SaaS promo", "feature announcement", or "product demo", assume content creation context. Always ask: "¿qué tipo de contenido y para qué plataforma?" before proposing templates.

### Forgetting visual design system
Remotion handles motion, not aesthetics. Always pair with `frontend-design` (or equivalent design skill) to define palette, typography, and spacing before animating. Code-first without a design system produces generic "AI slop" video.

### Ignoring platform specs
A video that looks good in Remotion Studio at 1920x1080 may be unreadable on TikTok mobile. Preview at target resolution and test text legibility at 50% scale.

## References

- [references/timing-cheatsheet.md](references/timing-cheatsheet.md) — Curvas Bézier copy-paste, configs spring, duraciones por tipo de motion
- [references/platform-templates.md](references/platform-templates.md) — Templates por plataforma: YouTube intro, TikTok hook, Instagram reel, podcast visualizer
- [references/subtitle-pipeline.md](references/subtitle-pipeline.md) — Generar subtítulos desde SRT/VTT, sincronización word-by-word, estilos por plataforma
- [references/advanced-features.md](references/advanced-features.md) — TikTok captions, audio waveform visualizer, Lottie, light leaks, GIFs, `<Series>`, `<Still>`, FFmpeg, dynamic metadata
