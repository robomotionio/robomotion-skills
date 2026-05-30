#!/usr/bin/env python3
"""github_profile.py — fetch a GitHub user's public profile + top repos (keyless).

Deterministic I/O only (stdlib). NO LLM. The GitHub REST API is public (60 req/hr without
a token; 5000/hr with GITHUB_TOKEN). The host agent folds the result into the meeting brief.

Example:
  github_profile.py --user octocat --max-repos 6 --output gh.json
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"


def get(path):
    headers = {"User-Agent": "robomotion-gtm-skills/meeting-brief", "Accept": "application/vnd.github+json"}
    tok = os.environ.get("GITHUB_TOKEN", "").strip()
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    req = urllib.request.Request(API + path, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        if e.code == 403:
            sys.exit("ERROR: GitHub rate limit hit (set GITHUB_TOKEN to raise it).")
        sys.exit(f"ERROR: GitHub API HTTP {e.code}: {e.read().decode('utf-8','ignore')[:200]}")
    except urllib.error.URLError as e:
        sys.exit(f"ERROR: network: {e}")


def main():
    ap = argparse.ArgumentParser(description="Fetch a GitHub user's public profile + top repos (keyless).")
    ap.add_argument("--user", required=True, help="GitHub username")
    ap.add_argument("--max-repos", type=int, default=6, help="how many top repos by stars (default 6)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    profile = get("/users/" + urllib.parse.quote(args.user))
    if profile is None:
        out = json.dumps({"user": args.user, "error": "user not found"}, indent=2)
        print(out)
        return

    repos = get("/users/" + urllib.parse.quote(args.user) + "/repos?per_page=100&sort=updated") or []
    repos = [r for r in repos if not r.get("fork")]
    repos.sort(key=lambda r: r.get("stargazers_count", 0), reverse=True)
    top = [{
        "name": r.get("name"), "description": r.get("description"),
        "language": r.get("language"), "stars": r.get("stargazers_count", 0),
        "url": r.get("html_url"), "updated_at": r.get("updated_at"),
    } for r in repos[: args.max_repos]]

    result = {
        "user": args.user,
        "name": profile.get("name"),
        "bio": profile.get("bio"),
        "company": profile.get("company"),
        "location": profile.get("location"),
        "blog": profile.get("blog"),
        "public_repos": profile.get("public_repos"),
        "followers": profile.get("followers"),
        "html_url": profile.get("html_url"),
        "top_repos": top,
    }
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"github profile -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
