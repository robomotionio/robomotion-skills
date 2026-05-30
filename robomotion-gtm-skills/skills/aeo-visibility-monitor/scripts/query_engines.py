#!/usr/bin/env python3
"""query_engines.py — query AI answer engines and capture answer text + citations.

The legitimate paid-API case: run a set of buyer-intent prompts against one or more
answer engines and return each engine's natural-language answer plus its cited source
URLs. The host agent then SCORES each response (brand mention? prominence? competitors?
source domains?) — this script does NOT score; it only fetches.

Engines (each gated by its own key; absent engines are skipped, not fatal):
  - perplexity  -> PERPLEXITY_API_KEY   (Sonar API, returns citations)
  - openai      -> OPENAI_API_KEY       (ChatGPT-style; web-search citations if available)
  - tavily      -> TAVILY_API_KEY       (cited live-web answer fallback)
  - gemini      -> GEMINI_API_KEY       (Generative Language API)

At least ONE engine key must be set or the script exits non-zero.
Stdlib only (urllib). No LLM scoring here — that's the host agent's job.

Example:
  query_engines.py --queries-file prompts.json --engines perplexity,openai \
      --output responses.json
  query_engines.py --query "best RPA tool for finance teams" --engines perplexity
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

TIMEOUT = 60


def _post(url, headers, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/json", **headers})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.loads(r.read().decode("utf-8")), None
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "ignore")[:300]
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return None, f"HTTP {e.code}: {detail}"
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            return None, f"network: {e}"
    return None, "exhausted retries"


def ask_perplexity(query, key):
    body = {"model": "sonar", "messages": [{"role": "user", "content": query}],
            "return_citations": True}
    data, err = _post("https://api.perplexity.ai/chat/completions",
                      {"Authorization": f"Bearer {key}"}, body)
    if err:
        return {"answer": "", "citations": [], "error": err}
    answer = ""
    try:
        answer = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        pass
    citations = data.get("citations") or data.get("search_results") or []
    cites = [c if isinstance(c, str) else c.get("url", "") for c in citations]
    return {"answer": answer, "citations": [c for c in cites if c], "error": None}


def ask_openai(query, key):
    # Plain chat completion (ChatGPT-style answer). Citations only if the model includes
    # URLs in text; web-search tool variants may add structured citations.
    body = {"model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": query}]}
    data, err = _post("https://api.openai.com/v1/chat/completions",
                      {"Authorization": f"Bearer {key}"}, body)
    if err:
        return {"answer": "", "citations": [], "error": err}
    answer = ""
    try:
        answer = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        pass
    return {"answer": answer, "citations": [], "error": None}


def ask_tavily(query, key):
    body = {"api_key": key, "query": query, "include_answer": True,
            "search_depth": "advanced", "max_results": 8}
    data, err = _post("https://api.tavily.com/search", {}, body)
    if err:
        return {"answer": "", "citations": [], "error": err}
    cites = [r.get("url", "") for r in data.get("results", []) if r.get("url")]
    return {"answer": data.get("answer", ""), "citations": cites, "error": None}


def ask_gemini(query, key):
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           f"gemini-1.5-flash:generateContent?key={key}")
    body = {"contents": [{"parts": [{"text": query}]}]}
    data, err = _post(url, {}, body)
    if err:
        return {"answer": "", "citations": [], "error": err}
    answer = ""
    try:
        answer = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        pass
    return {"answer": answer, "citations": [], "error": None}


ENGINES = {
    "perplexity": ("PERPLEXITY_API_KEY", ask_perplexity),
    "openai": ("OPENAI_API_KEY", ask_openai),
    "tavily": ("TAVILY_API_KEY", ask_tavily),
    "gemini": ("GEMINI_API_KEY", ask_gemini),
}


def main():
    ap = argparse.ArgumentParser(description="Query AI answer engines; capture answers + citations.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--query", help="single prompt")
    g.add_argument("--queries-file", help="JSON array of prompt strings")
    ap.add_argument("--engines", default="perplexity",
                    help="comma-separated: " + ",".join(ENGINES))
    ap.add_argument("--delay", type=float, default=0.5, help="delay between calls (s)")
    ap.add_argument("--output", default="-", help="output JSON path (default stdout)")
    args = ap.parse_args()

    requested = [e.strip().lower() for e in args.engines.split(",") if e.strip()]
    active, skipped = [], []
    for e in requested:
        if e not in ENGINES:
            sys.exit(f"ERROR: unknown engine '{e}'. Known: {', '.join(ENGINES)}")
        env_name, fn = ENGINES[e]
        if os.environ.get(env_name, "").strip():
            active.append((e, fn))
        else:
            skipped.append((e, env_name))

    if not active:
        miss = "; ".join(f"{e} needs {n}" for e, n in skipped)
        sys.exit(f"ERROR: no answer-engine key set. At least one required. ({miss})")

    if args.query:
        queries = [args.query]
    else:
        with open(args.queries_file, encoding="utf-8") as f:
            queries = [str(x) for x in json.load(f)]

    results = []
    for q in queries:
        row = {"query": q, "engines": {}}
        for ename, fn in active:
            key = os.environ[ENGINES[ename][0]]
            row["engines"][ename] = fn(q, key)
            time.sleep(args.delay)
        results.append(row)

    payload = {
        "active_engines": [e for e, _ in active],
        "skipped_engines": [{"engine": e, "missing_key": n} for e, n in skipped],
        "query_count": len(queries),
        "responses": results,
    }
    out = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"{len(queries)} queries x {len(active)} engines -> {args.output}",
              file=sys.stderr)
        if skipped:
            print("skipped (no key): " + ", ".join(e for e, _ in skipped), file=sys.stderr)


if __name__ == "__main__":
    main()
