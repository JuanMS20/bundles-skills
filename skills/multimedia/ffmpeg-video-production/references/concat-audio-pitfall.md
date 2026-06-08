# Concat Demuxer Audio Pitfall — Deep Dive

## Reproduction Recipe

1. Create 3 video segments: A (video+audio), B (video only), C (video+audio)
2. Create concat_list.txt with all 3 in order
3. Run: `ffmpeg -y -f concat -safe 0 -i concat_list.txt -c copy output.mp4`
4. Result: output.mp4 has NO audio stream, despite A and C having audio

## Why This Happens

The concat demuxer (`-f concat`) operates at the container level. It copies
raw packets from input containers into the output container. It does NOT
re-encode or reconcile stream differences.

When it encounters the first file, it creates output streams matching that
file's stream layout. If file B has fewer streams, the demuxer simply skips
the missing stream type for B's packets. But critically, if B is listed
FIRST and has only video, the output stream layout is video-only from the
start — audio packets from A and C are orphaned and dropped.

Even if A is first (video+audio), when B (video-only) is encountered, the
muxer may finalize the audio stream state prematurely, causing corruption
or silence in the output.

## The Fix

Every segment in a concat list MUST have identical stream types. For segments
without audio (title cards, dividers, image slideshows), add a silent audio
track:

```bash
ffmpeg -y -i no_audio_segment.mp4 \
  -f lavfi -i "anullsrc=r=44100:cl=stereo" \
  -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 128k \
  -shortest segment_with_silent_audio.mp4
```

For segments without video (audio-only files), add a black video:

```bash
ffmpeg -y -i audio_only.mp4 \
  -f lavfi -i "color=c=black:s=1920x1080:r=30" \
  -map 1:v -map 0:a \
  -c:v libx264 -c:a copy \
  -shortest segment_with_black_video.mp4
```

## Detection

After concatenation, ALWAYS verify:
```bash
ffprobe -v quiet -print_format json -show_streams output.mp4 | python -c "
import sys,json
d=json.load(sys.stdin)
types = [s['codec_type'] for s in d['streams']]
print(f'Streams: {len(d[\"streams\"])} ({types})')
if 'audio' not in types:
    print('WARNING: No audio stream — concat pitfall likely triggered')
"
```

## Alternative: Re-encode Concat

Using `-c copy` (stream copy) is fast but unforgiving about stream mismatches.
Re-encoding during concat is slower but more forgiving:

```bash
ffmpeg -y -f concat -safe 0 -i concat_list.txt \
  -c:v libx264 -c:a aac output.mp4
```

This still requires matching stream counts, but produces clearer errors.
However, it does NOT fix the fundamental issue — silent audio segments
are still needed.

## Related: Multiple Audio Streams

If segments have different audio configurations (e.g., stereo vs mono,
different sample rates), the concat demuxer may produce audio glitches
or drop channels. Normalize audio before concatenation:

```bash
ffmpeg -y -i input.mp4 \
  -af "aresample=44100,pan=stereo|FL=c0|FR=c0" \
  -c:v copy -c:a aac normalized.mp4
```
