---
name: remotion-video
description: |
  Video creation with Remotion — React-based programmatic video rendering.
  Use when user mentions Remotion, creating videos with React, programmatic video,
  motion graphics, screen recordings, SaaS promos, or animated explainers.
  Covers setup, composition, animation, media, rendering, and cloud deployment.
---

# Remotion Video

## Quick Start

```bash
# Scaffold new project (blank, no Tailwind)
npx create-video@latest --yes --blank --no-tailwind my-video
cd my-video
npx remotion studio
```

**Forbidden:** CSS transitions, CSS animations, Tailwind animation classes — they won't render.

## Core Concepts

| Concept | API | Purpose |
|---|---|---|
| Frame-driven animation | `useCurrentFrame()` | Current frame (0-indexed) |
| Timing | `interpolate()` | Map frame ranges to values |
| Easing | `Easing.bezier(x1,y1,x2,y2)` | CSS-compatible curves |
| Physics | `spring()` | Natural motion |
| Sequencing | `<Sequence from={} durationInFrames={}>` | Delay / limit clips |
| Layout | `<AbsoluteFill>` | Full-bleed container |

## Animation Patterns

```tsx
import { useCurrentFrame, useVideoConfig, interpolate, Easing, spring } from "remotion";

export const FadeSlideIn = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, 1.5 * fps], [0, 1], {
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  const translateX = spring({
    frame,
    fps,
    from: -100,
    to: 0,
    config: { damping: 15, stiffness: 100 },
  });

  return (
    <div style={{ opacity, transform: `translateX(${translateX}px)` }}>
      Content
    </div>
  );
};
```

## Media Assets

Place assets in `public/`. Reference with `staticFile()`.

```tsx
import { Img, Video, Audio, staticFile } from "remotion";

// Image
<Img src={staticFile("logo.png")} style={{ width: 200 }} />

// Video (requires @remotion/media)
<Video src={staticFile("demo.mp4")} />

// Audio (requires @remotion/media)
<Audio src={staticFile("bgm.mp3")} volume={0.5} />
```

## Composition Setup

```tsx
// src/Root.tsx
import { Composition } from "remotion";

export const RemotionRoot = () => (
  <Composition
    id="SaaSPromo"
    component={SaaSPromo}
    durationInFrames={30 * 30}  // 30s @ 30fps
    fps={30}
    width={1920}
    height={1080}
    defaultProps={{ title: "My SaaS" }}
  />
);
```

## Sequencing with Sequence

```tsx
import { Sequence, AbsoluteFill } from "remotion";

export const Timeline = () => (
  <AbsoluteFill>
    <Sequence durationInFrames={90}>
      <IntroScene />
    </Sequence>
    <Sequence from={90} durationInFrames={180}>
      <FeatureDemo />
    </Sequence>
    <Sequence from={270} durationInFrames={120}>
      <CTAScene />
    </Sequence>
  </AbsoluteFill>
);
```

## Transitions

```bash
npx remotion add @remotion/transitions
```

```tsx
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";

<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={90}>
    <Scene1 />
  </TransitionSeries.Sequence>
  <TransitionSeries.Transition
    presentation={fade()}
    timing={linearTiming({ durationInFrames: 15 })}
  />
  <TransitionSeries.Sequence durationInFrames={120}>
    <Scene2 />
  </TransitionSeries.Sequence>
</TransitionSeries>
```

## Rendering

```bash
# Still frame sanity check (frame 30 = 1s at 30fps)
npx remotion still SaaSPromo --scale=0.25 --frame=30

# Full video render locally
npx remotion render SaaSPromo out/video.mp4

# Cloud render (AWS Lambda)
npx remotion lambda render <site-id> SaaSPromo out/video.mp4
```

## SaaS-Specific Tips

1. **Screen recordings**: Capture app at 1920x1080, use as `<Video>` layer under callouts
2. **Data-driven**: Pass JSON props (metrics, prices, names) → dynamic renders
3. **Hot reload**: Tweak timing in studio, see instantly
4. **Deterministic**: Same props = same output → batch generate personalized videos

## References

- [references/timing-cheatsheet.md](references/timing-cheatsheet.md) — Bézier curves copy-paste
- [references/saas-templates.md](references/saas-templates.md) — SaaS video templates (explainer, feature, changelog)
- [references/media-pipeline.md](references/media-pipeline.md) — Video/audio/image processing patterns
