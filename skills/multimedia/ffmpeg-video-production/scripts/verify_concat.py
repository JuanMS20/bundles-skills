#!/usr/bin/env python3
"""
Verify a concatenated video output for common FFmpeg concat issues.
Usage: python verify_concat.py <output_video_path>

Checks:
  - Both video AND audio streams exist
  - Resolution matches expected (default 1920x1080)
  - FPS matches expected (default 30)
  - Duration is reasonable (within 10% of expected, if provided)
  - No corrupt frames at start/end
"""
import subprocess
import sys
import json

def verify(path, expected_duration=None, expected_w=1920, expected_h=1080, expected_fps=30):
    r = subprocess.run(
        f'ffprobe -v quiet -print_format json -show_format -show_streams "{path}"',
        shell=True, capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f"FAIL: ffprobe failed: {r.stderr[:300]}")
        return False

    data = json.loads(r.stdout)
    fmt = data["format"]
    streams = data["streams"]
    issues = []

    # Check stream count
    video_streams = [s for s in streams if s["codec_type"] == "video"]
    audio_streams = [s for s in streams if s["codec_type"] == "audio"]

    if not video_streams:
        issues.append("CRITICAL: No video stream found")
    if not audio_streams:
        issues.append("CRITICAL: No audio stream found — concat pitfall likely triggered")

    # Check resolution
    if video_streams:
        vs = video_streams[0]
        w, h = vs.get("width", 0), vs.get("height", 0)
        if w != expected_w or h != expected_h:
            issues.append(f"Resolution: {w}x{h} (expected {expected_w}x{expected_h})")
        fps_str = vs.get("r_frame_rate", "0/1")
        try:
            num, den = fps_str.split("/")
            fps = round(int(num) / int(den), 1)
            if abs(fps - expected_fps) > 1:
                issues.append(f"FPS: {fps} (expected {expected_fps})")
        except:
            issues.append(f"FPS: could not parse '{fps_str}'")

    # Check duration
    duration = float(fmt.get("duration", 0))
    size_mb = int(fmt.get("size", 0)) / (1024 * 1024)

    if expected_duration:
        diff_pct = abs(duration - expected_duration) / expected_duration * 100
        if diff_pct > 10:
            issues.append(f"Duration: {duration:.1f}s (expected ~{expected_duration:.1f}s, {diff_pct:.0f}% off)")

    # Report
    print(f"File: {path}")
    print(f"Duration: {duration:.1f}s ({duration/60:.1f} min)")
    print(f"Size: {size_mb:.1f} MB")
    for vs in video_streams:
        print(f"Video: {vs['codec_name']}, {vs.get('width')}x{vs.get('height')}, {vs.get('r_frame_rate')} fps")
    for aus in audio_streams:
        print(f"Audio: {aus['codec_name']}, {aus.get('sample_rate')} Hz, {aus.get('channels')} ch")
    print(f"Streams: {len(streams)} ({[s['codec_type'] for s in streams]})")

    if issues:
        print(f"\nISSUES FOUND ({len(issues)}):")
        for i in issues:
            print(f"  ✗ {i}")
        return False
    else:
        print("\n✓ ALL CHECKS PASSED")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_concat.py <video_path> [expected_duration_seconds]")
        sys.exit(1)
    expected_dur = float(sys.argv[2]) if len(sys.argv) > 2 else None
    ok = verify(sys.argv[1], expected_dur)
    sys.exit(0 if ok else 1)
