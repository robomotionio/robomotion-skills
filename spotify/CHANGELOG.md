# Changelog

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/); semver tracks the
`version:` field in SKILL.md.

## [1.0.0] - 2026-05-25

Initial port to Robomotion from the upstream `spotify` skill (v1.0.0).

### Changed

- **Re-implemented as a CLI equivalent.** Upstream Spotify was a plugin
  that registered 7 `spotify_*` tools; Robomotion skills cannot register
  tools, so the capability is delivered as a stdlib-only Python CLI,
  `scripts/spotify_api.py`, invoked through the `terminal` tool. This
  makes the skill container-mode (it ships a script).
- **Headless auth.** Replaced upstream's interactive `hermes auth spotify`
  OAuth flow with the Authorization-Code *refresh* flow: the script reads
  `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` / `SPOTIFY_REFRESH_TOKEN`
  from the environment (declared in `env.required`, bound from the Vault)
  and caches the derived access token in the temp dir.

### Capabilities

- Catalog search
- Playback: play/resume, pause, next/prev, seek, volume, repeat, shuffle
- Now-playing, full state, recently played
- Queue: view + add
- Devices: list + transfer
- Playlists: list, get, create, add/remove tracks
- Library: save/remove/list tracks and albums
