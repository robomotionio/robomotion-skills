#!/usr/bin/env python3
"""envelope.py: how open the mouth is, frame by frame, from the voice.

For the no-video-model path: a drawn or generated character with a closed and
an open (and optionally a wide) mouth variant flips between them on the
vocal's energy in the speech band. Cheap, deterministic and always in sync.

  python3 envelope.py --audio assets/voice.wav --fps 30 -o assets/mouth.json

Writes {"fps": 30, "env": [0..1 per frame]} in track time. In a scene:
  const open = kit.mouth(MOUTH.env, MOUTH.fps);   // 0..1
  const img = open > .55 ? mouthWide : open > .2 ? mouthOpen : mouthClosed;

For a song, run it on the vocal stem if you have one; on a full mix the
drums also open the mouth, so raise --gate (0.25–0.35) and check a strip.
"""
import argparse, json, subprocess
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--fps", type=float, default=30)
    ap.add_argument("--lo", type=float, default=300, help="speech band low edge, Hz")
    ap.add_argument("--hi", type=float, default=3400, help="speech band high edge, Hz")
    ap.add_argument("--gate", type=float, default=0.12, help="below this (0..1) the mouth is shut")
    ap.add_argument("-o", "--out", default="mouth.json")
    a = ap.parse_args()
    sr = 16000
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.audio, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    hop = int(sr / a.fps)
    win = hop * 2
    n = max(1, (len(x) - win) // hop + 1)
    freqs = np.fft.rfftfreq(win, 1 / sr)
    band = (freqs >= a.lo) & (freqs <= a.hi)
    w = np.hanning(win)
    env = np.zeros(n)
    for i in range(n):
        seg = x[i * hop:i * hop + win]
        if len(seg) < win:
            seg = np.pad(seg, (0, win - len(seg)))
        env[i] = np.sqrt(np.mean(np.abs(np.fft.rfft(seg * w))[band] ** 2))
    env = env / (np.percentile(env, 97) or 1)
    env = np.clip((env - a.gate) / (1 - a.gate), 0, 1)
    # Fast attack, slower release: mouths snap open and ease shut.
    out = np.zeros_like(env)
    for i, v in enumerate(env):
        prev = out[i - 1] if i else 0
        out[i] = v if v > prev else prev * 0.55 + v * 0.45
    json.dump({"fps": a.fps, "env": [round(float(v), 3) for v in out]}, open(a.out, "w"))
    print(f"envelope: {len(out)} frames at {a.fps} fps, open {np.mean(out > .2):.0%} of the time → {a.out}")


if __name__ == "__main__":
    main()
