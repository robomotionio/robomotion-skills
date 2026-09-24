#!/usr/bin/env python3
"""spine.py: build the timing spine every scene is cut and animated to.

One file, spine.json, whatever drives the video:
  - a song:        beats + bars + energy sections, and the sung words if there are vocals
  - a voiceover:   the spoken words and lines (no beat grid unless there is music under it)
  - a music bed:   beats + sections only
  - no sound:      a steady pacing grid of the length you give (a silent
                   recipe, a loop, a piece that gets its music later)

Usage:
  python3 spine.py --audio assets/track.mp3 [--transcript transcript.json]
                   [--script lyrics_or_script.txt] [--no-beats] -o spine.json
  python3 spine.py --silent 30 [--bpm 100] -o spine.json

--transcript is word timings from `hyperframes transcribe <audio> --json`
(or any JSON list of {text|word, start|s, end|e}). Repeat it to patch: every
transcript after the first is a re-transcription of one section, given as
path@offset (the section's start in the track), and replaces the first one's
words over its span. Speech recognition often misses whole sung passages;
spine.py lists those lines as GUESSED, and the fix is to cut that section,
transcribe it again with a larger model (medium.en) and pass it here. --script is the text the
person gave you (lyrics or the voiceover script), one line per line. With
both, the script's exact words are laid onto the transcript's timings, which
fixes what speech recognition gets wrong on sung vocals. With only a
transcript, lines are cut at pauses.

Output (all times in seconds of the track):
  { "duration", "bpm", "offset", "beats": [...], "bars": [...],
    "sections": [{"s","e","energy","label"}],
    "words": [{"w","s","e"}], "lines": [{"s","e","text","words":[...]}] }
"""
import argparse, difflib, json, re, subprocess, sys


def duration_of(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def load_words(path):
    data = json.load(open(path))
    if isinstance(data, dict):
        for k in ("words", "transcript", "segments", "result"):
            if k in data:
                data = data[k]
                break
    words = []
    def take(item):
        if isinstance(item, dict) and "words" in item and isinstance(item["words"], list):
            for x in item["words"]:
                take(x)
            return
        if not isinstance(item, dict):
            return
        text = item.get("text", item.get("word", item.get("w", "")))
        s = item.get("start", item.get("s", item.get("from")))
        e = item.get("end", item.get("e", item.get("to")))
        if text is None or s is None:
            return
        text = str(text).strip()
        if not re.search(r"\w", text):  # music notes, [Music], punctuation-only tokens
            return
        s = float(s) / (1000 if isinstance(s, (int, float)) and s > 10000 else 1)
        e = float(e if e is not None else s) / (1000 if isinstance(e, (int, float)) and e > 10000 else 1)
        words.append({"w": text, "s": round(s, 3), "e": round(max(e, s + 0.05), 3)})
    for item in data if isinstance(data, list) else []:
        take(item)
    words.sort(key=lambda w: w["s"])
    return words


norm = lambda w: re.sub(r"[^a-z0-9']", "", w.lower())


def align_script(script_lines, heard):
    """Lay the script's words onto the heard words' timings (difflib on normalised tokens)."""
    script = [(li, w) for li, line in enumerate(script_lines) for w in line.split()]
    a = [norm(w) for _, w in script]
    b = [norm(w["w"]) for w in heard]
    timed = [None] * len(script)
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):
            for k in range(i2 - i1):
                timed[i1 + k] = (heard[j1 + k]["s"], heard[j1 + k]["e"])
        elif tag == "replace" and j2 > j1:
            s, e = heard[j1]["s"], heard[j2 - 1]["e"]
            n = i2 - i1
            for k in range(n):
                timed[i1 + k] = (s + (e - s) * k / n, s + (e - s) * (k + 1) / n)
    # Fill words the recogniser missed by spreading them between their timed neighbours.
    i = 0
    while i < len(timed):
        if timed[i] is None:
            j = i
            while j < len(timed) and timed[j] is None:
                j += 1
            left = timed[i - 1][1] if i > 0 else (timed[j][0] - 0.3 * (j - i) if j < len(timed) else 0)
            right = timed[j][0] if j < len(timed) else left + 0.3 * (j - i)
            n = j - i
            for k in range(n):
                timed[i + k] = (left + (right - left) * k / n, left + (right - left) * (k + 1) / n)
            i = j
        else:
            i += 1
    words = [{"w": w, "s": round(t[0], 3), "e": round(t[1], 3), "line": li} for (li, w), t in zip(script, timed)]
    lines = []
    for li, text in enumerate(script_lines):
        ws = [dict(w) for w in words if w["line"] == li]
        for w in ws:
            w.pop("line")
        if ws:
            lines.append({"s": ws[0]["s"], "e": ws[-1]["e"], "text": text, "words": ws})
    matched = sum(1 for op in sm.get_opcodes() if op[0] == "equal" for _ in range(op[2] - op[1]))
    return [dict((k, v) for k, v in w.items() if k != "line") for w in words], lines, matched / max(1, len(a))


def lines_from_pauses(words, gap=0.45, max_words=8):
    lines, cur = [], []
    for w in words:
        if cur and (w["s"] - cur[-1]["e"] > gap or len(cur) >= max_words or re.search(r"[.!?,;:]$", cur[-1]["w"])):
            lines.append(cur)
            cur = []
        cur.append(w)
    if cur:
        lines.append(cur)
    return [{"s": l[0]["s"], "e": l[-1]["e"], "text": " ".join(w["w"] for w in l), "words": l} for l in lines]


def beat_grid(path):
    try:
        import librosa, numpy as np
    except ImportError:
        print("spine: librosa is not installed; no beat grid (pip install librosa)", file=sys.stderr)
        return None
    y, sr = librosa.load(path, sr=22050, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time", trim=False)
    tempo = float(np.atleast_1d(tempo)[0])
    beats = [round(float(b), 3) for b in beats]
    rms = librosa.feature.rms(y=y, hop_length=512)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=512)
    # Downbeat guess: the phase (0..3) whose beats carry the most onset strength.
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    ot = librosa.frames_to_time(np.arange(len(onset)), sr=sr)
    strength = [float(np.interp(b, ot, onset)) for b in beats]
    phase = max(range(4), key=lambda p: sum(strength[p::4])) if len(beats) >= 8 else 0
    bars = beats[phase::4]
    # Sections: 8-bar windows (or ~15 s when there is no clear beat), labelled by loudness.
    edges = bars[::8] if len(bars) > 8 else [round(x, 3) for x in np.arange(0, times[-1], 15.0)]
    edges = list(edges) + [round(float(times[-1]), 3)]
    en = [float(np.mean(rms[(times >= a) & (times < b)]) if np.any((times >= a) & (times < b)) else 0) for a, b in zip(edges, edges[1:])]
    hi = max(en) or 1
    sections = []
    for (a, b), v in zip(zip(edges, edges[1:]), en):
        k = v / hi
        sections.append({"s": round(a, 3), "e": round(b, 3), "energy": round(k, 3),
                         "label": "peak" if k > .8 else "high" if k > .6 else "mid" if k > .35 else "low"})
    offset = beats[0] % (60 / tempo) if beats else 0
    return {"bpm": round(tempo, 2), "offset": round(offset, 3), "beats": beats, "bars": bars, "sections": sections}


def pacing_grid(duration, bpm):
    """A beat grid for a video with no sound: steady beats, 4-beat bars, 8-bar sections."""
    step = 60 / bpm
    beats = [round(i * step, 3) for i in range(int(duration / step) + 1)]
    bars = beats[::4]
    edges = bars[::8] + [round(duration, 3)]
    sections = [{"s": a, "e": b, "energy": 0.5, "label": "mid"} for a, b in zip(edges, edges[1:]) if b > a]
    return {"bpm": bpm, "offset": 0, "beats": beats, "bars": bars, "sections": sections}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio")
    ap.add_argument("--silent", type=float, metavar="SECONDS", help="no sound: a pacing grid this long instead of audio")
    ap.add_argument("--bpm", type=float, default=100, help="with --silent: the pacing grid's tempo")
    ap.add_argument("--transcript", action="append", default=[], help="path or path@offset; repeat to patch sections")
    ap.add_argument("--script")
    ap.add_argument("--no-beats", action="store_true", help="speech only: skip the beat grid")
    ap.add_argument("-o", "--out", default="spine.json")
    a = ap.parse_args()
    if a.silent:
        spine = {"audio": None, "duration": round(a.silent, 3), "words": [], "lines": [], **pacing_grid(a.silent, a.bpm)}
        json.dump(spine, open(a.out, "w"), indent=1)
        print(f"spine: silent {spine['duration']}s, pacing grid at {a.bpm:g} bpm, {len(spine['bars'])} bars → {a.out}")
        return
    if not a.audio:
        ap.error("--audio is required (or --silent SECONDS for a video with no sound)")
    spine = {"audio": a.audio, "duration": round(duration_of(a.audio), 3), "bpm": None, "offset": 0,
             "beats": [], "bars": [], "sections": [], "words": [], "lines": []}
    if not a.no_beats:
        g = beat_grid(a.audio)
        if g:
            spine.update(g)
    if a.transcript:
        heard = []
        for n, spec in enumerate(a.transcript):
            path, _, off = spec.partition("@")
            ws = load_words(path)
            off = float(off or 0)
            for w in ws:
                w["s"] = round(w["s"] + off, 3)
                w["e"] = round(w["e"] + off, 3)
            if n and ws:
                lo, hi = ws[0]["s"] - 0.05, ws[-1]["e"] + 0.05
                heard = [w for w in heard if not (lo <= w["s"] <= hi)]
            heard = sorted(heard + ws, key=lambda w: w["s"])
        if a.script:
            script_lines = [l.strip() for l in open(a.script) if l.strip() and not l.strip().startswith("[")]
            spine["words"], spine["lines"], match = align_script(script_lines, heard)
            spine["script_match"] = round(match, 3)
            if match < .5:
                print(f"spine: only {match:.0%} of the script matched what was heard; check the lines' times by ear or on a sheet", file=sys.stderr)
            # A line none of whose words were heard has guessed times.
            heard_keys = {(norm(w["w"]), round(w["s"], 2)) for w in heard}
            for ln in spine["lines"]:
                hit = sum(1 for w in ln["words"] if (norm(w["w"]), round(w["s"], 2)) in heard_keys)
                ln["heard"] = round(hit / max(1, len(ln["words"])), 2)
            guessed = [ln for ln in spine["lines"] if ln["heard"] < .34]
            for ln in guessed:
                print(f"spine: GUESSED {ln['s']:.2f}-{ln['e']:.2f}  {ln['text']}", file=sys.stderr)
            if guessed:
                print("spine: re-transcribe those stretches with a larger model and pass them as --transcript part.json@<start>", file=sys.stderr)
        else:
            spine["words"], spine["lines"] = heard, lines_from_pauses(heard)
    json.dump(spine, open(a.out, "w"), indent=1)
    print(f"spine: {spine['duration']}s, bpm {spine['bpm']}, {len(spine['beats'])} beats, "
          f"{len(spine['sections'])} sections, {len(spine['words'])} words in {len(spine['lines'])} lines → {a.out}")


if __name__ == "__main__":
    main()
