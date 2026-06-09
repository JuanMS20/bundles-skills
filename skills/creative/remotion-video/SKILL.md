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

Subtítulos programáticos sincronizados con audio. No dependen de tool externa.

```tsx
import { useCurrentFrame, useVideoConfig, Sequence } from "remotion";

const subtitles = [
  { text: "Hola a todos", start: 0, end: 60 },
  { text: "Hoy vamos a aprender", start: 60, end: 150 },
  { text: "cómo editar videos", start: 150, end: 240 },
];

export const Subtitulos = () => {
  return (
    <>
      {subtitles.map((sub, i) => (
        <Sequence key={i} from={sub.start} durationInFrames={sub.end - sub.start}>
          <SubtituloLine text={sub.text} />
        </Sequence>
      ))}
    </>
  );
};

const SubtituloLine = ({ text }: { text: string }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  const scale = interpolate(frame, [0, 10], [0.95, 1], { extrapolateRight: "clamp" });

  return (
    <div style={{
      position: "absolute",
      bottom: 80,
      left: 0,
      right: 0,
      textAlign: "center",
      opacity,
      transform: `scale(${scale})`,
    }}>
      <span style={{
        background: "rgba(0,0,0,0.7)",
        color: "#fff",
        padding: "12px 24px",
        borderRadius: 8,
        fontSize: 48,
        fontFamily: "sans-serif",
        fontWeight: 700,
        textShadow: "2px 2px 4px rgba(0,0,0,0.5)",
      }}>
        {text}
      </span>
    </div>
  );
};
```

**Estilos de caption populares:**
- **YouTube standard**: Fondo negro semitransparente, texto blanco, bottom-center
- **TikTok style**: Texto grande (60px), color primario vibrante, con animación pop-in
- **Karaoke**: Palabra resaltada progresivamente según timing exacto

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

## References

- [references/timing-cheatsheet.md](references/timing-cheatsheet.md) — Curvas Bézier copy-paste, configs spring, duraciones por tipo de motion
- [references/platform-templates.md](references/platform-templates.md) — Templates por plataforma: YouTube intro, TikTok hook, Instagram reel, podcast visualizer
- [references/subtitle-pipeline.md](references/subtitle-pipeline.md) — Generar subtítulos desde SRT/VTT, sincronización word-by-word, estilos por plataforma
