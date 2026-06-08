# Consistent Concat Pattern — Full Build Script Template

Patrón probado para ensamblar videos documentales con múltiples tipos de assets
(fotos, videos verticales, videos horizontales, tarjetas de texto) en un solo
video final con seek funcional y audio sincronizado.

## Estructura del Script

```python
#!/usr/bin/env python3
"""Build script pattern for multi-segment video assembly."""
import subprocess, os, json, sys

WORKDIR = "/path/to/project"
TEMP = os.path.join(WORKDIR, "temp")
FINAL = os.path.join(WORKDIR, "output")
os.makedirs(TEMP, exist_ok=True)
os.makedirs(FINAL, exist_ok=True)

# === CRITICAL: Consistent encoding for ALL segments ===
VENC = "-c:v libx264 -preset fast -crf 20 -profile:v high -level 4.0 -pix_fmt yuv420p -g 60 -sc_threshold 0"
AENC = "-c:a aac -ar 44100 -ac 2 -b:a 128k"

def run(cmd, desc="", timeout=600):
    print(f"  -> {desc}", flush=True)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        print(f"  FAIL: {r.stderr[:400]}", file=sys.stderr)
        sys.exit(1)
    print(f"  OK", flush=True)

def get_dur(path):
    r = subprocess.run(f'ffprobe -v quiet -print_format json -show_format "{path}"',
                       shell=True, capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])

def verify(path, name):
    """Verify: has video+audio, correct resolution, no decode errors."""
    r = subprocess.run(f'ffprobe -v quiet -print_format json -show_streams "{path}"',
                       shell=True, capture_output=True, text=True)
    streams = json.loads(r.stdout)["streams"]
    hv = any(s["codec_type"] == "video" for s in streams)
    ha = any(s["codec_type"] == "audio" for s in streams)
    d = get_dur(path)
    if not hv or not ha:
        print(f"  FAIL {name}: missing streams"); sys.exit(1)
    vs = next(s for s in streams if s["codec_type"] == "video")
    if int(vs["width"]) != 1920 or int(vs["height"]) != 1080:
        print(f"  FAIL {name}: {vs['width']}x{vs['height']}"); sys.exit(1)
    r2 = subprocess.run(f'ffmpeg -v error -i "{path}" -f null -',
                        shell=True, capture_output=True, text=True, timeout=60)
    if r2.stderr.strip():
        print(f"  FAIL {name}: decode errors"); sys.exit(1)
    print(f"  OK {name:35s} {d:6.1f}s")
    return d
```

## Prologos (Fotos + Audio Narrado) — Single-Pass

```python
# Build slideshow with narration in ONE pass using filter_complex
# Input: N photos + 1 audio file
# Output: slideshow video with sped-up narration

SPEED = 1.25
SETPTS = 1.0 / SPEED  # 0.8

photos = ["photo1.png", "photo2.png", "photo3.png"]
audio_dur = 39.27  # original duration
speed_dur = audio_dur / SPEED
per_photo = speed_dur / len(photos)

# Build inputs: each photo as loop input + audio
inputs = ""
for i, photo in enumerate(photos):
    inputs += f'-loop 1 -t {per_photo:.2f} -i "{photo}" '
inputs += f'-i "{audio_path}" '

# Build filter_complex
fc_parts = []
for i in range(len(photos)):
    fc_parts.append(f'[{i}:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1[v{i}]')
fc_parts.append(f'{" ".join(f"[v{i}]" for i in range(len(photos)))}concat=n={len(photos)}:v=1:a=0[vcat]')
aud_idx = len(photos)
fo = max(0, speed_dur - 1.5)
fc_parts.append(f'[{aud_idx}:a]atempo={SPEED},afade=t=in:st=0:d=0.8,afade=t=out:st={fo:.2f}:d=1.5[a]')
fc_parts.append(f'[vcat]format=yuv420p[vout]')
fc = ";".join(fc_parts)

run(f'ffmpeg -y {inputs} '
    f'-filter_complex "{fc}" '
    f'-map "[vout]" -map "[a]" -shortest '
    f'{VENC} {AENC} "{output}"',
    "Prologo single-pass")
```

## Vertical Videos (Blurred BG + Speed) — Single-Pass

```python
# setpts AFTER overlay, BEFORE fade
run(f'ffmpeg -y -i "{input}" -filter_complex '
    f'"[0:v]split=2[bg][fg];'
    f'[bg]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,gblur=sigma=40[b];'
    f'[fg]scale=1920:1080:force_original_aspect_ratio=decrease[f];'
    f'[b][f]overlay=(W-w)/2:(H-h)/2,setpts={SETPTS}*PTS,'
    f'fade=t=in:st=0:d=0.5,fade=t=out:st={fo:.2f}:d=0.5,format=yuv420p[v];'
    f'[0:a]atempo={SPEED}[a]" '
    f'-map "[v]" -map "[a]" {VENC} {AENC} "{output}"',
    "Vertical 1.25x", timeout=300)
```

## Horizontal Videos (Normalize + Speed) — Single-Pass

```python
run(f'ffmpeg -y -i "{input}" -filter_complex '
    f'"[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,'
    f'pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setpts={SETPTS}*PTS,'
    f'fade=t=in:st=0:d=0.5,fade=t=out:st={fo:.2f}:d=0.5,format=yuv420p[v];'
    f'[0:a]atempo={SPEED}[a]" '
    f'-map "[v]" -map "[a]" {VENC} {AENC} "{output}"',
    "Horizontal 1.25x", timeout=300)
```

## Final Concatenation with Forced Keyframes

```python
sequence = ["title.mp4", "prologo1.mp4", ..., "final.mp4"]

# Write concat list
with open(concat_list, "w") as f:
    for seg in sequence:
        f.write(f"file '{os.path.join(TEMP, seg)}'\n")

# Re-encode with forced keyframes for seek support
run(f'ffmpeg -y -f concat -safe 0 -i "{concat_list}" '
    f'-c:v libx264 -preset fast -crf 20 -profile:v high -level 4.0 '
    f'-pix_fmt yuv420p -g 60 -sc_threshold 0 '
    f'-force_key_frames "expr:gte(t,n_forced*2)" '
    f'-c:a aac -ar 44100 -ac 2 -b:a 128k '
    f'-movflags +faststart "{final_output}"',
    "Final concat", timeout=600)
```

## Final Verification

```python
# Decode check
r = subprocess.run(f'ffmpeg -v error -i "{final}" -f null -',
                   shell=True, capture_output=True, text=True, timeout=300)
if r.stderr.strip():
    print(f"DECODE ERRORS: {r.stderr[:500]}"); sys.exit(1)

# Keyframe check
r3 = subprocess.run(
    f'ffprobe -v quiet -select_streams v:0 -show_entries frame=pts_time,pict_type -of csv=p=0 "{final}"',
    shell=True, capture_output=True, text=True, timeout=120)
kfs = [float(l.split(',')[0]) for l in r3.stdout.strip().split('\n')[:600]
       if len(l.split(',')) >= 2 and l.split(',')[1].strip() == 'I']
if len(kfs) > 1:
    gaps = [kfs[i+1]-kfs[i] for i in range(min(len(kfs)-1, 30))]
    print(f"Keyframes: avg gap {sum(gaps)/len(gaps):.1f}s, max {max(gaps):.1f}s")

# A/V sync check
info = json.loads(subprocess.run(f'ffprobe -v quiet -print_format json -show_streams "{final}"',
    shell=True, capture_output=True, text=True).stdout)
adur = float(next(s for s in info["streams"] if s["codec_type"] == "audio")["duration"])
vdur = float(next(s for s in info["streams"] if s["codec_type"] == "video")["duration"])
print(f"A/V sync: diff {abs(adur-vdur):.2f}s")
```
