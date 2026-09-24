#!/usr/bin/env python3
"""sheet.py: look at a video the way a director does, on one image.

  python3 sheet.py renders/video.mp4 --every 2 -o out/check/whole.jpg            the whole piece
  python3 sheet.py renders/video.mp4 --at 23.0:25.0 --step 0.125 -o strip.jpg   every frame of a moment
  python3 sheet.py renders/video.mp4 --times 3.2,9.8,14.1 --w 960 -o keys.jpg   chosen frames, bigger
  python3 sheet.py renders/video.mp4 --at 23:25 --step .125 --crop 700,200,600,500 -o face.jpg

Each tile is stamped with its time. With --spine spine.json each tile also
shows the words being sung or spoken at that moment, so you can check that
the picture says what the sound says.
"""
import argparse, json, math, os, subprocess, tempfile


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout.strip() or 0)


def esc(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--every", type=float)
    ap.add_argument("--at")
    ap.add_argument("--step", type=float, default=0.125)
    ap.add_argument("--times")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--w", type=int, default=480)
    ap.add_argument("--crop")
    ap.add_argument("--spine")
    ap.add_argument("-o", "--out", default="sheet.jpg")
    a = ap.parse_args()
    D = dur(a.video)
    if a.times:
        ts = [float(x) for x in a.times.split(",")]
    elif a.at:
        s, e = (float(x) for x in a.at.split(":"))
        ts = [round(s + i * a.step, 3) for i in range(int((e - s) / a.step) + 1)]
    else:
        ev = a.every or max(1.0, D / 24)
        ts = [round(i * ev, 3) for i in range(int(D / ev) + 1)]
    ts = [t for t in ts if t < D - 0.02][:60]
    words = json.load(open(a.spine)).get("words", []) if a.spine else []
    tmp = tempfile.mkdtemp()
    tiles = []
    for i, t in enumerate(ts):
        f = os.path.join(tmp, f"t{i:03d}.png")
        vf = []
        if a.crop:
            x, y, w, h = a.crop.split(",")
            vf.append(f"crop={w}:{h}:{x}:{y}")
        vf.append(f"scale={a.w}:-2")
        label = f"{t:.2f}s"
        near = [w["w"] for w in words if w["s"] - 0.05 <= t <= w["e"] + 0.05]
        if near:
            label += "  " + " ".join(near)[:40]
        vf.append(f"drawtext=text='{esc(label)}':x=6:y=6:fontsize={max(14, a.w // 30)}:fontcolor=white:box=1:boxcolor=black@0.65")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", a.video, "-frames:v", "1", "-vf", ",".join(vf), f], check=True)
        tiles.append(f)
    cols = min(a.cols, len(tiles))
    rows = math.ceil(len(tiles) / cols)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", os.path.join(tmp, "t%03d.png"),
                    "-vf", f"tile={cols}x{rows}:padding=4:color=0x222222", "-frames:v", "1", a.out], check=True)
    print(f"sheet: {len(tiles)} frames → {a.out}")


if __name__ == "__main__":
    main()
