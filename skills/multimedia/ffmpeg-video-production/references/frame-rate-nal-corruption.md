# Frame Rate Inconsistency → NAL Corruption

## Problem
When concatenating segments from different sources (WhatsApp videos, lavfi-generated
cards, photo slideshows), each source has a different native frame rate:
- WhatsApp: 29.92fps (359/12) or 29.75fps (119/4)
- lavfi color source: 25fps by default
- Photo loop: depends on `-r` flag
- Screen recordings: variable

The concat demuxer does NOT normalize frame rates. It passes timestamps through
as-is, which causes the H.264 encoder to produce Invalid NAL units at segment
boundaries. Symptoms:
- "Invalid NAL unit size (0 > N)" in ffmpeg error output
- "missing picture in access unit" warnings
- Gray screen when seeking forward/backward
- Video freezes but audio continues

## Diagnosis
```bash
# Check frame rate of each segment
for f in temp/*.mp4; do
  fr=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$f")
  echo "$f: $fr"
done
```
If any segment has a different `r_frame_rate` → problem.

## Fix: Force 30fps CFR everywhere

### Step 1: Add to VENC constant
```bash
VENC="-c:v libx264 -preset fast -crf 20 -profile:v high -level 4.0 -pix_fmt yuv420p -r 30 -g 60 -sc_threshold 0 -vsync cfr"
```

Key flags:
- `-r 30`: output frame rate = 30fps
- `-vsync cfr`: constant frame rate (not variable)
- `-g 60`: keyframe interval = 60 frames (2s at 30fps)
- `-sc_threshold 0`: disable scene change detection (prevents random keyframes)

### Step 2: Add -r 30 to lavfi inputs
```bash
# BAD: lavfi defaults to 25fps
ffmpeg -f lavfi -i "color=c=black:s=1920x1080:d=3"

# GOOD: explicit 30fps
ffmpeg -f lavfi -i "color=c=black:s=1920x1080:d=3:r=30"
```

### Step 3: Add -r 30 to photo loop inputs
```bash
# BAD: default fps
ffmpeg -loop 1 -t 5 -i photo.jpg ...

# GOOD: explicit 30fps
ffmpeg -loop 1 -t 5 -r 30 -i photo.jpg ...
```

### Step 4: Force 30fps on final concat
```bash
ffmpeg -y -f concat -safe 0 -i list.txt \
  -r 30 -vsync cfr -g 60 -sc_threshold 0 \
  -force_key_frames "expr:gte(t,n_forced*2)" \
  ... output.mp4
```

## If concat demuxer still produces NAL errors

Switch to `filter_complex concat`:
```bash
ffmpeg -y -i seg1.mp4 -i seg2.mp4 -i seg3.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset fast -crf 20 -r 30 -vsync cfr -g 60 \
  -force_key_frames "expr:gte(t,n_forced*2)" \
  -c:a aac -ar 44100 -ac 2 -b:a 128k \
  -movflags +faststart output.mp4
```

This re-encodes everything from scratch with clean timestamps.

## Verification
```bash
# 1. Check all segments are 30fps
for f in temp/*.mp4; do
  ffprobe -v quiet -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$f"
done

# 2. Decode check (should be 0 errors)
ffmpeg -v error -i output.mp4 -f null -

# 3. Seek test at multiple points
for t in 30 120 240 360; do
  ffmpeg -v error -ss $t -i output.mp4 -t 3 -f null - 2>&1
done

# 4. Verify output fps
ffprobe -v quiet -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 output.mp4
# Should output: 30/1
```
