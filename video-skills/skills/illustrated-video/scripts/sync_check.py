#!/usr/bin/env python3
"""sync_check.py: does a generated performance clip really sing/speak in time?

Two measurements, then a verdict:

1. Soundtrack offset. The clip's own audio against the slice you sent
   (cross-correlation of onset envelopes). Tells you where the model put
   your audio, so the composition can line the clip up exactly.
2. Picture lag. Motion in the mouth region against the vocal envelope. The
   peak of their cross-correlation is how far the lips run ahead of (−) or
   behind (+) the voice, and its height is how much the lips follow the
   voice at all. This is the check that catches a clip whose mouth flaps at
   random, which no audio check can see.

  python3 sync_check.py --clip assets/fal/s04.mp4 --slice assets/slices/s04-chorus.wav \
      [--face 0.35,0.25,0.3,0.35] [--words spine.json --win 21.9] [--sheet out/check/s04-mouth.jpg]

--face is the mouth box as fractions of the frame (x, y, w, h). Default: the
middle of the upper half, which suits a head-and-shoulders shot. With
--words (the spine) and --win (the slice's window start in track time) it
also writes a sheet of the frames on the loudest sung/spoken words, so you
can look at the mouth shapes yourself.

Verdict: PASS when |picture lag| ≤ 2 frames and correlation ≥ 0.25;
SHIFT when correlation is fine but the lag is larger (move the clip by the lag
and look again); REDO when correlation is low (regenerate: tighter face
framing, another seed, or another model).
"""
import argparse, json, subprocess, sys
import numpy as np

SR = 16000


def audio(path, fps, band=False):
    # band=True keeps the voice band only, so drums and bass move the lips less.
    af = ["-af", "highpass=f=250,lowpass=f=3400"] if band else []
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", *af, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    hop = int(SR / fps)
    n = len(x) // hop
    if n == 0:
        return np.zeros(0)
    fr = x[:n * hop].reshape(n, hop)
    rms = np.sqrt((fr ** 2).mean(1))
    return rms


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                          "-of", "json", path], capture_output=True, text=True).stdout
    s = json.loads(out)["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return s["width"], s["height"], float(num) / float(den)


def motion(path, box, W, H, fps):
    x, y, w, h = box
    cw, ch = int(W * w) // 2 * 2, int(H * h) // 2 * 2
    cx, cy = int(W * x), int(H * y)
    sw, sh = 64, max(8, int(64 * ch / max(cw, 1)))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"crop={cw}:{ch}:{cx}:{cy},scale={sw}:{sh},format=gray",
                          "-r", str(fps), "-f", "rawvideo", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, dtype=np.uint8).reshape(-1, sh, sw).astype(np.float32)
    if len(fr) < 3:
        return np.zeros(0)
    d = np.abs(np.diff(fr, axis=0)).mean((1, 2))
    return np.concatenate([[d[0]], d])


def smooth(x, k=3):
    return np.convolve(x, np.ones(k) / k, mode="same") if len(x) > k else x


def mouth_motion(path, box, W, H, fps):
    """Mouth-box motion minus whole-frame motion: camera moves, cuts and hair
    swaying move everything; only the mouth moves the mouth box on its own."""
    m = motion(path, box, W, H, fps)
    g = motion(path, (0.0, 0.0, 1.0, 1.0), W, H, fps)
    n = min(len(m), len(g))
    if n == 0:
        return m
    m, g = m[:n], g[:n]
    beta = float((m * g).sum() / ((g * g).sum() or 1))
    r = m - beta * g
    cut = g > (np.median(g) + 6 * (np.median(np.abs(g - np.median(g))) + 1e-6))  # hard cuts: blank them out
    r[cut] = 0
    return smooth(r)


def xcorr(a, b, maxlag):
    n = min(len(a), len(b))
    if n < 8:
        return 0, 0.0
    a = a[:n] - a[:n].mean()
    b = b[:n] - b[:n].mean()
    best, lag = -2.0, 0
    for L in range(-maxlag, maxlag + 1):
        x, y = (a[L:], b[:n - L]) if L >= 0 else (a[:n + L], b[-L:])
        den = np.sqrt((x ** 2).sum() * (y ** 2).sum()) or 1
        c = float((x * y).sum() / den)
        if c > best:
            best, lag = c, L
    return lag, best


def onset(e):
    d = np.diff(e, prepend=e[:1])
    return np.clip(d, 0, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", required=True)
    ap.add_argument("--slice", required=True, help="the audio you sent the model (or the track section the clip must match)")
    ap.add_argument("--face", default="0.3,0.28,0.4,0.34")
    ap.add_argument("--words")
    ap.add_argument("--win", type=float, default=0.0, help="the slice's window start, in track seconds")
    ap.add_argument("--sheet")
    ap.add_argument("--json")
    a = ap.parse_args()
    W, H, fps = probe(a.clip)
    fps = min(fps, 30)
    src = audio(a.slice, fps)
    voice = smooth(audio(a.slice, fps, band=True))
    own = audio(a.clip, fps)
    res = {"clip": a.clip, "fps": fps}
    if len(own) and own.max() > 1e-3:
        lag, c = xcorr(onset(own), onset(src), int(fps * 1.0))
        res["soundtrack_offset_s"] = round(lag / fps, 3)
        res["soundtrack_corr"] = round(c, 3)
    mot = mouth_motion(a.clip, [float(v) for v in a.face.split(",")], W, H, fps)
    # Positive lag: the picture moves after the voice (lips late).
    lag, c = xcorr(mot, voice, int(fps * 0.34))
    res["picture_lag_frames"] = lag
    res["picture_lag_ms"] = round(1000 * lag / fps)
    res["lip_corr"] = round(c, 3)
    if c < 0.25:
        res["verdict"] = "REDO"
        res["why"] = "the mouth barely follows the voice: regenerate with the face larger in frame, another seed or another lip-sync model"
    elif abs(lag) > 2:
        res["verdict"] = "SHIFT"
        res["why"] = f"lips {'late' if lag > 0 else 'early'} by {abs(lag)} frames: move the clip {'earlier' if lag > 0 else 'later'} by {abs(lag) / fps:.3f}s (data-media-start) and check again"
    else:
        res["verdict"] = "PASS"
    if a.words and a.sheet:
        sp = json.load(open(a.words))
        dur = len(src) / fps
        ws = [w for w in sp.get("words", []) if a.win <= w["s"] < a.win + dur]
        ws = sorted(ws, key=lambda w: -(w["e"] - w["s"]))[:8]
        ws = sorted(ws, key=lambda w: w["s"])
        if ws:
            sel = "+".join(f"between(t,{w['s'] - a.win + 0.04:.3f},{w['s'] - a.win + 0.08:.3f})" for w in ws)
            labels = ",".join(w["w"] for w in ws)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.clip, "-vf",
                            f"select='{sel}',scale=480:-1,drawtext=text='%{{pts\\:hms}}':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6,tile={min(4, len(ws))}x{(len(ws) + 3) // 4}",
                            "-frames:v", "1", "-vsync", "vfr", a.sheet], check=False)
            res["sheet"] = a.sheet
            res["sheet_words"] = labels
    print(json.dumps(res, indent=1))
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1)
    sys.exit(0 if res["verdict"] == "PASS" else 2)


if __name__ == "__main__":
    main()
