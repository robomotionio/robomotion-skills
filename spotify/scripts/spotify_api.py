#!/usr/bin/env python3
"""Spotify Web API CLI (stdlib only).

Robomotion port of the upstream Hermes `spotify` skill. Upstream exposed the
capability through 7 registered plugin tools (`spotify_playback`, ...).
Robomotion skills cannot register tools, so this re-implements the same
surface as a terminal-invokable CLI over the Spotify Web API — no third-party
packages, just Python's stdlib.

Auth: Authorization-Code *refresh* flow (headless). Reads three env vars,
bound from the Vault in the Designer's Environment tab:

    SPOTIFY_CLIENT_ID
    SPOTIFY_CLIENT_SECRET
    SPOTIFY_REFRESH_TOKEN

An access token is derived from the refresh token and cached in the system
temp dir until just before it expires, so a multi-step session does not
re-hit the token endpoint on every call.

Playback-mutating actions require Spotify Premium and an active device,
exactly like upstream. Reads (search, library, playlists) work on Free.
"""

import argparse
import base64
import hashlib
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://api.spotify.com/v1"
TOKEN_URL = "https://accounts.spotify.com/api/token"


def _die(msg, **extra):
    out = {"error": msg}
    out.update(extra)
    print(json.dumps(out, indent=2))
    sys.exit(1)


def _env(name):
    val = os.environ.get(name)
    if not val:
        _die(f"{name} is not set. Bind it from the Vault in the Designer's "
             "Environment tab (see this skill's env.required).")
    return val


# --------------------------------------------------------------------------
# Auth — refresh-token flow with a small on-disk access-token cache
# --------------------------------------------------------------------------

def _cache_path():
    return Path(tempfile.gettempdir()) / "robomotion_spotify_token.json"


def _cache_key(client_id, refresh_token):
    return hashlib.sha256(f"{client_id}:{refresh_token}".encode()).hexdigest()[:16]


def _get_access_token():
    client_id = _env("SPOTIFY_CLIENT_ID")
    client_secret = _env("SPOTIFY_CLIENT_SECRET")
    refresh_token = _env("SPOTIFY_REFRESH_TOKEN")
    key = _cache_key(client_id, refresh_token)

    cache = _cache_path()
    try:
        data = json.loads(cache.read_text())
        if data.get("key") == key and data.get("expires_at", 0) - 60 > time.time():
            return data["access_token"]
    except Exception:
        pass  # missing / stale / corrupt cache → refresh below

    body = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }).encode()
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    req = urllib.request.Request(TOKEN_URL, data=body, method="POST")
    req.add_header("Authorization", f"Basic {basic}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            tok = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        _die("Token refresh failed — the refresh token may be revoked, or the "
             "client id/secret are wrong. Regenerate the refresh token.",
             status=e.code, detail=detail)
    except urllib.error.URLError as e:
        _die(f"Network error reaching Spotify accounts service: {e}")

    access = tok.get("access_token")
    if not access:
        _die("Token refresh returned no access_token", response=tok)
    try:
        cache.write_text(json.dumps({
            "key": key,
            "access_token": access,
            "expires_at": time.time() + int(tok.get("expires_in", 3600)),
        }))
    except Exception:
        pass  # cache is an optimization; never fatal
    return access


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------

def _request(method, path, params=None, body=None):
    url = API_BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {_get_access_token()}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            if not raw:
                return {"ok": True, "status": resp.status}
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        _http_error(e)
    except urllib.error.URLError as e:
        _die(f"Network error reaching Spotify API: {e}")


def _http_error(e):
    detail = e.read().decode(errors="replace")
    reason = message = None
    try:
        err = json.loads(detail).get("error", {})
        reason = err.get("reason")
        message = err.get("message")
    except Exception:
        message = detail
    hints = {
        401: "Access token rejected — refresh token likely revoked. Regenerate it.",
        403: ("Forbidden. Usually Spotify Premium is required for this playback "
              "action, OR there is no active device. Open Spotify on a device, "
              "play a track for a second, then retry. Do not retry blindly."),
        404: ("Not found — often means 'no active device'. Open Spotify "
              "somewhere and start playback once, then retry."),
        429: "Rate limited. Wait, then retry once. If it persists, you are looping.",
    }
    _die(hints.get(e.code, f"Spotify API error: {message or detail}"),
         status=e.code, reason=reason, message=message)


# --------------------------------------------------------------------------
# URI / ID normalization (accepts spotify: URI, open.spotify.com URL, or bare id)
# --------------------------------------------------------------------------

def _to_uri(value, default_type):
    value = value.strip()
    if value.startswith("spotify:"):
        return value
    if "open.spotify.com" in value:
        parts = urllib.parse.urlparse(value).path.strip("/").split("/")
        if len(parts) >= 2:
            return f"spotify:{parts[-2]}:{parts[-1].split('?')[0]}"
    return f"spotify:{default_type}:{value}"


def _to_id(value):
    value = value.strip()
    if value.startswith("spotify:"):
        return value.split(":")[-1]
    if "open.spotify.com" in value:
        return urllib.parse.urlparse(value).path.strip("/").split("/")[-1].split("?")[0]
    return value


def _emit(obj):
    print(json.dumps(obj, indent=2))


def _csv(value, default_type):
    return [_to_uri(x, default_type) for x in value.split(",") if x.strip()]


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def cmd_whoami(a):
    _emit(_request("GET", "/me"))


def cmd_search(a):
    types = ",".join(t.strip() for t in a.types.split(",") if t.strip())
    _emit(_request("GET", "/search", params={"q": a.query, "type": types, "limit": a.limit}))


def cmd_play(a):
    params = {"device_id": _to_id(a.device)} if a.device else None
    body = None
    if a.query:
        t = a.type
        sr = _request("GET", "/search", params={"q": a.query, "type": t, "limit": 1})
        items = (sr.get(t + "s") or {}).get("items") or []
        if not items:
            _die(f"No {t} found for query: {a.query!r}")
        uri = items[0]["uri"]
        body = {"uris": [uri]} if t == "track" else {"context_uri": uri}
    elif a.context:
        body = {"context_uri": _to_uri(a.context, "album")}
    elif a.uris:
        body = {"uris": _csv(a.uris, "track")}
    _emit(_request("PUT", "/me/player/play", params=params, body=body))


def cmd_pause(a):
    _emit(_request("PUT", "/me/player/pause"))


def cmd_next(a):
    _emit(_request("POST", "/me/player/next"))


def cmd_prev(a):
    _emit(_request("POST", "/me/player/previous"))


def cmd_seek(a):
    _emit(_request("PUT", "/me/player/seek", params={"position_ms": a.position_ms}))


def cmd_volume(a):
    _emit(_request("PUT", "/me/player/volume", params={"volume_percent": a.percent}))


def cmd_repeat(a):
    _emit(_request("PUT", "/me/player/repeat", params={"state": a.state}))


def cmd_shuffle(a):
    _emit(_request("PUT", "/me/player/shuffle", params={"state": a.state}))


def cmd_now_playing(a):
    res = _request("GET", "/me/player/currently-playing")
    if isinstance(res, dict) and res.get("status") == 204:
        res = {"is_playing": False, "message": "Nothing is currently playing."}
    _emit(res)


def cmd_state(a):
    res = _request("GET", "/me/player")
    if isinstance(res, dict) and res.get("status") == 204:
        res = {"is_playing": False, "message": "No active device."}
    _emit(res)


def cmd_recently_played(a):
    _emit(_request("GET", "/me/player/recently-played", params={"limit": a.limit}))


def cmd_queue_get(a):
    _emit(_request("GET", "/me/player/queue"))


def cmd_queue_add(a):
    _emit(_request("POST", "/me/player/queue", params={"uri": _to_uri(a.uri, "track")}))


def cmd_devices_list(a):
    _emit(_request("GET", "/me/player/devices"))


def cmd_devices_transfer(a):
    _emit(_request("PUT", "/me/player", body={"device_ids": [_to_id(a.device)], "play": a.play}))


def cmd_playlists_list(a):
    _emit(_request("GET", "/me/playlists", params={"limit": a.limit}))


def cmd_playlists_get(a):
    _emit(_request("GET", f"/playlists/{_to_id(a.playlist)}"))


def cmd_playlists_create(a):
    me = _request("GET", "/me")
    uid = me.get("id")
    if not uid:
        _die("Could not resolve current user id", response=me)
    body = {"name": a.name, "public": a.public}
    if a.description:
        body["description"] = a.description
    _emit(_request("POST", f"/users/{uid}/playlists", body=body))


def cmd_playlists_add(a):
    _emit(_request("POST", f"/playlists/{_to_id(a.playlist)}/tracks",
                   body={"uris": _csv(a.uris, "track")}))


def cmd_playlists_remove(a):
    tracks = [{"uri": u} for u in _csv(a.uris, "track")]
    _emit(_request("DELETE", f"/playlists/{_to_id(a.playlist)}/tracks",
                   body={"tracks": tracks}))


def cmd_albums_get(a):
    _emit(_request("GET", f"/albums/{_to_id(a.album)}"))


def cmd_albums_tracks(a):
    _emit(_request("GET", f"/albums/{_to_id(a.album)}/tracks", params={"limit": a.limit}))


_LIB_PATH = {"tracks": "/me/tracks", "albums": "/me/albums"}


def cmd_library_save(a):
    ids = ",".join(_to_id(x) for x in a.ids.split(",") if x.strip())
    _emit(_request("PUT", _LIB_PATH[a.kind], params={"ids": ids}))


def cmd_library_remove(a):
    ids = ",".join(_to_id(x) for x in a.ids.split(",") if x.strip())
    _emit(_request("DELETE", _LIB_PATH[a.kind], params={"ids": ids}))


def cmd_library_list(a):
    _emit(_request("GET", _LIB_PATH[a.kind], params={"limit": a.limit}))


# --------------------------------------------------------------------------
# Parser
# --------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(prog="spotify_api.py", description="Spotify Web API CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("whoami", help="Current user profile")

    sp = sub.add_parser("search", help="Search the catalog")
    sp.add_argument("query")
    sp.add_argument("--types", default="track", help="comma list: track,album,artist,playlist")
    sp.add_argument("--limit", type=int, default=10)

    pp = sub.add_parser("play", help="Play/resume; optionally search-and-play in one call")
    pp.add_argument("--query", help="search text; plays the top match")
    pp.add_argument("--type", default="track",
                    choices=["track", "album", "artist", "playlist"],
                    help="entity type for --query")
    pp.add_argument("--context", help="album/playlist/artist URI/URL/id to play")
    pp.add_argument("--uris", help="comma list of track URIs/URLs/ids")
    pp.add_argument("--device", help="target device id")

    sub.add_parser("pause", help="Pause playback")
    sub.add_parser("next", help="Skip to next track")
    sub.add_parser("prev", help="Skip to previous track")

    sk = sub.add_parser("seek", help="Seek to position (ms)")
    sk.add_argument("position_ms", type=int)
    vol = sub.add_parser("volume", help="Set volume percent (0-100)")
    vol.add_argument("percent", type=int)
    rep = sub.add_parser("repeat", help="Set repeat mode")
    rep.add_argument("state", choices=["track", "context", "off"])
    shf = sub.add_parser("shuffle", help="Set shuffle on/off")
    shf.add_argument("state", choices=["true", "false"])

    sub.add_parser("now-playing", help="What's currently playing")
    sub.add_parser("state", help="Full player state")
    rp = sub.add_parser("recently-played", help="Recently played tracks")
    rp.add_argument("--limit", type=int, default=20)

    sub.add_parser("queue-get", help="View the playback queue")
    qa = sub.add_parser("queue-add", help="Add a track to the queue")
    qa.add_argument("uri")

    sub.add_parser("devices-list", help="List available devices")
    dt = sub.add_parser("devices-transfer", help="Transfer playback to a device")
    dt.add_argument("device")
    dt.add_argument("--play", action="store_true", help="start playing on transfer")

    pl = sub.add_parser("playlists-list", help="List the user's playlists")
    pl.add_argument("--limit", type=int, default=50)
    pg = sub.add_parser("playlists-get", help="Get a playlist by id/URL")
    pg.add_argument("playlist")
    pc = sub.add_parser("playlists-create", help="Create a playlist")
    pc.add_argument("name")
    pc.add_argument("--public", action="store_true")
    pc.add_argument("--description")
    pa = sub.add_parser("playlists-add", help="Add tracks to a playlist")
    pa.add_argument("playlist")
    pa.add_argument("uris", help="comma list of track URIs/URLs/ids")
    prm = sub.add_parser("playlists-remove", help="Remove tracks from a playlist")
    prm.add_argument("playlist")
    prm.add_argument("uris", help="comma list of track URIs/URLs/ids")

    ag = sub.add_parser("albums-get", help="Get an album by id/URL")
    ag.add_argument("album")
    at = sub.add_parser("albums-tracks", help="List an album's tracks")
    at.add_argument("album")
    at.add_argument("--limit", type=int, default=50)

    for name, helptext in (("library-save", "Save tracks/albums to the library"),
                           ("library-remove", "Remove tracks/albums from the library")):
        lp = sub.add_parser(name, help=helptext)
        lp.add_argument("kind", choices=["tracks", "albums"])
        lp.add_argument("ids", help="comma list of ids/URIs/URLs")
    ll = sub.add_parser("library-list", help="List saved tracks/albums")
    ll.add_argument("kind", choices=["tracks", "albums"])
    ll.add_argument("--limit", type=int, default=50)

    return p


_DISPATCH = {
    "whoami": cmd_whoami, "search": cmd_search, "play": cmd_play,
    "pause": cmd_pause, "next": cmd_next, "prev": cmd_prev, "seek": cmd_seek,
    "volume": cmd_volume, "repeat": cmd_repeat, "shuffle": cmd_shuffle,
    "now-playing": cmd_now_playing, "state": cmd_state,
    "recently-played": cmd_recently_played,
    "queue-get": cmd_queue_get, "queue-add": cmd_queue_add,
    "devices-list": cmd_devices_list, "devices-transfer": cmd_devices_transfer,
    "playlists-list": cmd_playlists_list, "playlists-get": cmd_playlists_get,
    "playlists-create": cmd_playlists_create, "playlists-add": cmd_playlists_add,
    "playlists-remove": cmd_playlists_remove,
    "albums-get": cmd_albums_get, "albums-tracks": cmd_albums_tracks,
    "library-save": cmd_library_save, "library-remove": cmd_library_remove,
    "library-list": cmd_library_list,
}


def main():
    args = build_parser().parse_args()
    _DISPATCH[args.cmd](args)


if __name__ == "__main__":
    main()
