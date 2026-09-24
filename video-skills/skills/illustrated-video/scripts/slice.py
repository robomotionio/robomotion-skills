#!/usr/bin/env python3
"""slice.py: cut the track into the audio clips a lip-sync or performance model needs.

A performance shot on screen is often shorter than a model accepts (MiniMax H3
lip-sync wants 5 to 14.8 s, Seedance 1.8 to 30 s). So each clip is a window
around the shot, grown to the model's minimum, and the shot then plays the
part of the generated video that lines up with it: the composition sets the
clip's data-media-start to `lead` (shot start minus window start).

  python3 slice.py --audio assets/track.mp3 --shots shots.json --model h3 --out assets/slices

shots.json: [{"name": "s04-chorus", "s": 23.0, "e": 26.4}, ...] in track seconds.
Writes <out>/<name>.mp3 (and .wav) and <out>/slices.json:
  [{"name", "file", "s", "e", "win_s", "win_e", "lead"}]

Models: h3 (MiniMax lip-sync, 5–14.8 s), seedance (1.8–30 s), sync (sync-3, 1–300 s),
or --min/--max to set your own.
"""
import argparse, json, os, subprocess

LIMITS = {"h3": (5.0, 14.8), "seedance": (1.8, 15.0), "sync": (1.0, 300.0)}


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout.strip() or 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--shots", required=True)
    ap.add_argument("--model", default="h3", choices=sorted(LIMITS))
    ap.add_argument("--min", type=float)
    ap.add_argument("--max", type=float)
    ap.add_argument("--pre", type=float, default=0.35, help="seconds of run-up before the shot (the mouth opens before the sound)")
    ap.add_argument("--out", default="assets/slices")
    a = ap.parse_args()
    lo, hi = LIMITS[a.model]
    lo, hi = a.min or lo, a.max or hi
    total = dur(a.audio)
    os.makedirs(a.out, exist_ok=True)
    res = []
    for sh in json.load(open(a.shots)):
        s, e = float(sh["s"]), float(sh["e"])
        ws, we = max(0.0, s - a.pre), e + 0.25
        if we - ws < lo:  # grow the window evenly to the minimum, inside the track
            pad = (lo - (we - ws)) / 2
            ws, we = ws - pad, we + pad
            if ws < 0:
                we, ws = we - ws, 0.0
            if we > total:
                ws, we = max(0.0, ws - (we - total)), total
        if we - ws > hi:
            we = ws + hi
            print(f"slice: {sh['name']} is longer than {hi}s; split the shot or the model will cut it at {we:.2f}s")
        base = os.path.join(a.out, sh["name"])
        for ext, codec in ((".wav", ["-c:a", "pcm_s16le"]), (".mp3", ["-c:a", "libmp3lame", "-b:a", "192k"])):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ws:.3f}", "-t", f"{we - ws:.3f}", "-i", a.audio, "-ac", "2", "-ar", "44100", *codec, base + ext], check=True)
        res.append({"name": sh["name"], "file": base + ".mp3", "s": s, "e": e, "win_s": round(ws, 3), "win_e": round(we, 3), "lead": round(s - ws, 3)})
        print(f"slice: {sh['name']}  shot {s:.2f}-{e:.2f}  window {ws:.2f}-{we:.2f} ({we - ws:.2f}s)  lead {s - ws:.2f}s")
    json.dump(res, open(os.path.join(a.out, "slices.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
