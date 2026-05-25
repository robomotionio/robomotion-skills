---
name: spotify
version: 1.0.0
summary: Control Spotify — play, search, queue, manage playlists, devices, and library — via the Web API.
tags: ["spotify", "music", "playback", "media"]
---

# Spotify

Control the user's Spotify account through the Spotify Web API. The skill ships `scripts/spotify_api.py`, a stdlib-only Python CLI that authenticates with a stored refresh token and wraps the catalog, playback, queue, playlist, device, and library endpoints. Invoke it with the `terminal` tool.

> This is a CLI port. Upstream Spotify ran as registered agent tools (`spotify_*`); Robomotion skills can't register tools, so the same capability is delivered as this script.

## Capabilities

- Search the catalog (tracks, albums, artists, playlists)
- Playback: play/resume, pause, next/previous, seek, volume, repeat, shuffle
- "What's playing" / full player state / recently played
- Queue: view and add
- Devices: list and transfer playback
- Playlists: list, get, create, add/remove tracks
- Library: save / remove / list saved tracks and albums

Playback-mutating actions require **Spotify Premium** and an **active device**. Reads (search, library, playlists, state) work on Free.

## Usage

```sh
S=${SKILL_DIR}/scripts/spotify_api.py

# Search → play in ONE call (preferred — don't search then play separately)
python3 $S play --query "miles davis kind of blue" --type album
python3 $S play --query "bad guy billie eilish" --type track
python3 $S play --query "radiohead" --type artist     # artist radio / smart shuffle

# Play an explicit URI/URL/id, or resume current playback
python3 $S play --context spotify:playlist:37i9dQZF1DX4wta20PHgwo
python3 $S play --uris spotify:track:0DiWol3AO6WpXZgp0goxAV
python3 $S play                                        # resume

# Direct transport — no preflight needed
python3 $S pause
python3 $S next
python3 $S volume 50
python3 $S shuffle true
python3 $S repeat context

# What's playing / state
python3 $S now-playing
python3 $S state
python3 $S recently-played --limit 5

# Queue
python3 $S queue-get
python3 $S queue-add spotify:track:0DiWol3AO6WpXZgp0goxAV

# Devices
python3 $S devices-list
python3 $S devices-transfer DEVICE_ID --play

# Playlists (find user playlists with playlists-list, NOT search)
python3 $S playlists-list
python3 $S playlists-create "Focus 2026" --description "deep work" --public
python3 $S playlists-add PLAYLIST_ID spotify:track:abc,spotify:track:def
python3 $S playlists-remove PLAYLIST_ID spotify:track:abc

# Library (kind = tracks | albums)
python3 $S library-save tracks spotify:track:0DiWol3AO6WpXZgp0goxAV
python3 $S library-list albums --limit 50
```

Run any subcommand with `--help` for its flags. The script accepts Spotify URIs (`spotify:track:…`), open.spotify.com URLs, or bare ids interchangeably.

## When to use

- "Play Kind of Blue", "pause", "skip", "turn it down to 30"
- "What am I listening to?"
- "Add this to my Late Night Jazz playlist"
- "Make a playlist called Focus and add the last 3 songs I played"
- "Save this track to my library"

## When NOT to use

- Lyrics, podcasts transcripts, or audio download — not supported by the API
- Finding a *user* playlist by name — use `playlists-list` (search hits the public catalog, not the user's library)

## Operating notes

- **One call to play.** `play --query … --type …` searches and plays the top match in a single step. Don't list/describe search results unless the user asked for options.
- **Don't preflight.** Spotify accepts play/pause/skip without checking state first. Only call `now-playing`/`state` when the user asks what's playing or you genuinely need device/track context.
- **`403` = Premium required OR no active device.** The script returns a clear message. These are permanent until the user acts (start Spotify on a device / upgrade) — do **not** retry blindly.
- **`now-playing` returning `{"is_playing": false}`** means nothing is playing; that's not an error. Report it and stop.
- **`401`** means the refresh token was revoked — tell the user to regenerate it (see env.required). **`429`** is rate limiting — wait and retry once, then stop if it persists.
- Use the right entity for the action: `--context` takes album/playlist/artist; `--uris` takes track URIs.
- The script caches the access token in the temp dir until just before it expires, so a multi-step session won't re-hit the token endpoint each call.

## Attribution

Adapted from the [Nous Hermes Agent](https://github.com/NousResearch/hermes-agent) `spotify` skill (MIT). Upstream shipped a registered plugin toolset; this port re-implements the same surface as a Web API CLI driven by the `terminal` tool.
