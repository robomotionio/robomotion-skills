## v3.3.0 — install everywhere, ship the reliability sweep

The AI world reinvents itself every month. This skill keeps you current.

`/last30days` researches your topic across Reddit, X, YouTube, TikTok, Instagram, Hacker News, Polymarket, GitHub, Digg, and 5+ more sources from the last 30 days, finds what the community is actually upvoting, sharing, betting on, and saying on camera, and writes you a grounded narrative with real citations.

## What's new in v3.3.0

### Install everywhere with one command

`npx skills add mvanhorn/last30days-skill -g -y` is now the canonical install path for **every harness** — Claude Code, OpenAI Codex CLI, Cursor, Gemini CLI, GitHub Copilot, Windsurf, and 50+ other Agent Skills hosts. The skill auto-detects each harness's skills directory and symlinks in place, so edits propagate live. No more per-harness manual paths in the README.

### New emit mode: `--emit=html`

Shareable, print-friendly HTML briefs. Drop the file in Slack, mail it to a stakeholder, or print it for the meeting. Same data as compact mode, structured for human reading.

### New source: Digg

Digg surfaces curated story clusters from the AI 1000 leaderboard and pulls attributable X-post quotes directly into the brief. Auto-enabled when `digg-pp-cli` is on PATH. Footer line: `⛏️ Digg: N clusters │ K posts │ M authors`. No X auth required for the inline quotes.

### YouTube residential-IP routing (`LAST30DAYS_YOUTUBE_SSH_HOST`)

Running on a datacenter VPS (Hetzner, DigitalOcean, AWS, etc.)? YouTube's bot-wall fingerprints datacenter IP ranges before any cookie check. Set `LAST30DAYS_YOUTUBE_SSH_HOST=<ssh-alias>` and yt-dlp runs over SSH against a residential-IP host instead. One env var, no proxy service required.

### macOS Keychain credential source

When env vars and config files aren't set, the engine now reads credentials from the macOS Keychain. Stores secrets where macOS expects them; nothing on disk in plaintext.

### `EXCLUDE_SOURCES` env var

The inverse of `INCLUDE_SOURCES`. Useful for "everything except TikTok" or "everything except the slow ones."

## Reliability sweep

This release closes a long tail of platform-specific issues that have been accumulating:

- **Reddit**: subreddits starting with `r` no longer get mangled by `lstrip("r/")`. Browser-like headers + gzip handling fix urllib 403s on the public JSON endpoint. HTTP 402 now triggers the OpenAI/public-JSON fallback chain when ScrapeCreators credits are exhausted.
- **xAI**: empty or malformed responses now surface in `errors_by_source` instead of silently returning zero results.
- **Windows**: process cleanup no longer crashes on `os.killpg`. POSIX-style secret-permission warnings skipped. Save-path footer uses forward slashes.
- **Auth**: comma-separated `SCRAPECREATORS_API_KEY=key1,key2` rotation restored (accidentally dropped in v3.0.6).
- **YouTube + HN**: SC YouTube + multi-token HN searches unblocked. Transcript-fetch ratio surfaced.
- **HTTP**: retry budget expanded with exponential backoff on DNS failure. Parallel AI search aligned with current API schema.
- **OpenClaw**: now works without a ScrapeCreators key. Poll-timing initialized once.

## Multi-harness reframe

`AGENTS.md` is now the canonical project doc; `CLAUDE.md` points at it. The skill is positioned as a multi-harness Agent Skills package, not a Claude-Code-specific tool. SKILL.md's path resolution rewrote `SKILL_ROOT` → `SKILL_DIR`, removing ~80 lines of bash and fixing a real spec-vs-engine divergence bug.

## Breaking change

**`.codex-plugin/plugin.json` removed.** Codex native-plugin users should install via `npx skills add mvanhorn/last30days-skill` or copy the skill to `~/.codex/skills/last30days/`. The `npx skills add` path now reaches every harness uniformly.

## Install

Any harness (recommended):

```
npx skills add mvanhorn/last30days-skill -g -y
```

Claude Code marketplace:

```
/plugin marketplace add mvanhorn/last30days-skill
```

OpenClaw:

```
clawhub install last30days-official
```

Zero config. Reddit, Hacker News, Polymarket, and GitHub work immediately. Run it once and the setup wizard unlocks X, YouTube, TikTok, and more in 30 seconds.

## Contributors

First-time contributors whose fixes shipped in v3.3.0 (most via PR triage salvage — the fix re-applied directly to main with co-author credit when path migration made the original branch un-rebaseable):

- Dave Morin — portable test-harness paths
- Alex Key — `removeprefix("r/")` for subreddit names
- Eric Oberhofer — multi-key rotation restored
- gujishh — Windows process cleanup
- Franco Carballar — Reddit browser-like headers
- Jonathan Oppenheim — Reddit 402 fallback chain
- Kaustav Mishra — xAI error surfacing
- [@thinkun](https://github.com/thinkun) — OpenClaw ScrapeCreators-key-optional fix

Plus every contributor who shipped one of the ~75 PRs merged this cycle. See [CHANGELOG.md](CHANGELOG.md) under `[3.3.0]` for the full PR list and `git log v3.2.0..v3.3.0` for the complete commit graph.

30 days of research. 30 seconds of work. Thirteen sources. Zero stale prompts.
