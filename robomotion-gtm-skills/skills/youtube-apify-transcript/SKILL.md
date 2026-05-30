---
name: youtube-apify-transcript
description: Fetch a YouTube video's transcript. Keyless by default (reads YouTube's public timedtext caption track via urllib — no key, no cost); if APIFY_API_TOKEN is set it uses Apify's residential-proxy transcript actor instead, which is more reliable from cloud/datacenter IPs that YouTube blocks. Supports single, batch, and timestamped-JSON output with local caching so repeat fetches are free. Use whenever a skill needs a video's text for research, summarization, or content repurposing.
metadata:
  version: 1.1.1
  category: research
  type: capability
---

# YouTube Apify Transcript

Fetch YouTube transcripts. **Default is keyless:** the script reads the watch page for the
caption-track list, then fetches YouTube's public `timedtext` track and parses its segments
(json3 / srv3 / legacy XML) with stdlib urllib — no key, no cost. **Optional upgrade:** if
`APIFY_API_TOKEN` is set, it routes through the Apify actor
`pintostudio/youtube-transcript-scraper`, which runs on residential proxies and is more
reliable from cloud/datacenter IPs that YouTube otherwise blocks at the caption endpoint.

Routing: `--prefer auto` (default) uses Apify when `APIFY_API_TOKEN` is set, else keyless;
`--prefer keyless` always uses the free path; `--prefer apify` requires the token. The
Apify path runs via a **managed async run/poll lifecycle** (start, poll to terminal with a
wall-clock timeout, then fetch the dataset) under a **cost gate**. The keyless path is free,
so its `--estimate-only` reports `$0` and `--yes` is a no-op.

## When to use

- "Get the transcript for [YouTube URL]." / any skill needing a video's text.
- Running from a cloud/server environment where direct transcript fetches get blocked.

## How to run

### Single video (keyless default)

```bash
# No key set -> free timedtext path; no --yes needed:
python3 ${SKILL_DIR}/scripts/youtube_transcript.py \
  --url "https://youtu.be/VIDEOID" \
  --format text \
  --cache-dir ${WORKSPACE}/.yt-cache \
  --output ${WORKSPACE}/transcript.txt
```

### Single video (Apify upgrade, when APIFY_API_TOKEN is set)

```bash
# Preview cost first (exits 0, no spend) — cache hits count as $0:
python3 ${SKILL_DIR}/scripts/youtube_transcript.py \
  --url "https://youtu.be/VIDEOID" --cache-dir ${WORKSPACE}/.yt-cache --estimate-only

# Then fetch, confirming spend with --yes:
python3 ${SKILL_DIR}/scripts/youtube_transcript.py \
  --url "https://youtu.be/VIDEOID" \
  --format text --yes \
  --cache-dir ${WORKSPACE}/.yt-cache \
  --output ${WORKSPACE}/transcript.txt
```

### Batch (one URL per line; dedups by video id, caches each)

```bash
python3 ${SKILL_DIR}/scripts/youtube_transcript.py \
  --urls-file ${WORKSPACE}/urls.txt \
  --format json --yes --max-cost-usd 0.50 \
  --cache-dir ${WORKSPACE}/.yt-cache \
  --output ${WORKSPACE}/transcripts.json
```

Options: `--lang de` (preferred language, best effort), `--format text|json` (json adds
per-segment `start`/`dur` timestamps + `full_text`), `--no-cache` (force re-fetch),
`--prefer keyless|apify|auto` (force the free path, require Apify, or auto-route on the
token). Output JSON includes a `source: "keyless"|"apify"` field so you know which path ran.

## Cost gate & run/poll lifecycle

Each uncached video runs the actor via an async run/poll lifecycle with a wall-clock
timeout (aborting on timeout to stop the meter) and a **cost gate**:

- `--estimate-only` prints the projected cost for the **uncached** videos (at
  ~$0.007/video) and **exits 0 without spending**; cached videos are reported as skipped.
- Fetching any uncached video **requires `--yes`** — without it the script refuses and
  exits non-zero. **Cache hits never spend and never need `--yes`** (re-fetch is free).
- Each video's run is **aborted** if reported usage exceeds `--max-cost-usd` (default
  `0.50`/video) or the `--apify-timeout` (default `300s`) trips.

## Outputs

- `--format text`: plain transcript text (single) or per-video sections (batch).
- `--format json`: `{video_id, title, transcript:[{start,dur,text}], full_text,
  from_cache}` — array in batch mode.
- Cached by `video_id` under `--cache-dir`; cache hits cost $0 and set `from_cache:true`.

## Credentials / env

- **Required:** none. The default keyless `timedtext` path needs no key.
- **Optional:** `APIFY_API_TOKEN` — if set → the Apify residential-proxy actor (better
  reliability from blocked cloud/datacenter IPs); if not → the keyless timedtext path
  (default). `APIFY_YT_TRANSCRIPT_ACTOR` overrides the actor slug. For an external cache
  store instead of the filesystem, the agent can wrap with `REDIS_URL`/`sqlite`;
  `--cache-dir` covers the default case.

If `APIFY_API_TOKEN` is set → Apify path (cost-gated). If not → keyless timedtext path
(free, default). The keyless path can be IP-throttled on some cloud hosts; that's the exact
case where setting `APIFY_API_TOKEN` pays off.

## Notes & edge cases

- Keyless path is free; Apify is ~$0.007/video ($5/mo free ≈ 700+ videos). Always pass
  `--cache-dir` so repeat/batch fetches are free on either path.
- Clear errors (not empty output) for: unparseable URL, captions disabled (`no
  transcript returned`), and quota exceeded (HTTP 402).
- The script accepts `watch?v=`, `youtu.be/`, `/shorts/`, `/embed/`, and bare 11-char
  ids; it normalizes to a canonical watch URL before calling the actor.
- Language preference is best-effort — falls back to the default track if `--lang` is
  unavailable.
