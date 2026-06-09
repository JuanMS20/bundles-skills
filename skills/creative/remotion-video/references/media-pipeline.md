# Media Pipeline

## Screen Recording → Remotion

1. Record app at target resolution (1920x1080)
2. Export as MP4 (H.264, high quality)
3. Place in `public/recordings/`
4. Use `<Video>` component with trim

```tsx
import { Video } from "@remotion/media";
import { staticFile } from "remotion";

export const ScreenDemo = () => (
  <Video
    src={staticFile("recordings/feature.mp4")}
    startFrom={30}      // trim start
    endAt={300}         // trim end
    style={{ width: "100%" }}
  />
);
```

## Audio Sync

```tsx
import { Audio, useCurrentFrame, useVideoConfig } from "remotion";

// Match voiceover timing with visual cues
const frame = useCurrentFrame();
const { fps } = useVideoConfig();

// Show highlight at 3 seconds (90 frames @ 30fps)
const isActive = frame >= 90 && frame < 120;
```

## Batch Render (Personalized Videos)

```tsx
// data.json
[{ "name": "Juan", "company": "Acme", "metric": "+40%" }, ...]

// Render all
npx remotion render MyComp out/video.mp4 --props=./data.json
```
