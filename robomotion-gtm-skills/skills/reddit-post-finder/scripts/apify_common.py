#!/usr/bin/env python3
"""apify_common.py — vendored Apify async run+poll + COST-GATE helper (stdlib only).

Vendored into THIS skill (reddit-post-finder); no cross-skill imports — each skill keeps
its own copy. Unlike a naive `run-sync-get-dataset-items` call (which can TIME OUT on a
large job or silently OVERSPEND), this implements a managed run lifecycle:
  - starts the actor run ASYNC (POST /v2/acts/<actor>/runs),
  - POLLS the run to a terminal state with backoff and a wall-clock timeout
    (aborting the run if the timeout trips, to stop the meter),
  - enforces a COST GATE: refuses to start / aborts if reported usage-USD exceeds
    --max-cost-usd, so a runaway actor can't burn credits,
  - fetches dataset items only on SUCCEEDED (GET /v2/datasets/<id>/items).

Auth: APIFY_API_TOKEN. The COST-GATE / run-poll path applies ONLY to the Apify branch —
every keyless degrade path in the skill is untouched.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.apify.com/v2"


class CostGateError(RuntimeError):
    """Raised when the cost gate refuses to start or aborts a run over budget."""


class ApifyError(RuntimeError):
    """Raised on actor failure, timeout, or transport error."""


def token():
    return os.environ.get("APIFY_API_TOKEN", "").strip()


def _req(url, method="GET", body=None, timeout=90):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode("utf-8")
                return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            detail = e.read().decode("utf-8", "ignore")[:300]
            if e.code == 402:
                raise CostGateError(f"Apify quota/credit exceeded (HTTP 402): {detail}")
            raise ApifyError(f"Apify {e.code}: {detail}")
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise ApifyError(f"network: {e}")


def _usd(run):
    """Best-effort actual-cost read from a run object (Apify usageTotalUsd)."""
    if not isinstance(run, dict):
        return 0.0
    for k in ("usageTotalUsd", "usageUsd"):
        if run.get(k) is not None:
            try:
                return float(run[k])
            except (TypeError, ValueError):
                pass
    usage = run.get("usage") or {}
    if isinstance(usage, dict) and usage.get("USD") is not None:
        try:
            return float(usage["USD"])
        except (TypeError, ValueError):
            pass
    return 0.0


def estimate(actor, run_input, max_cost_usd, timeout_s, items_hint=None,
             per_item_usd=None, label=""):
    """Print the projected cost/limits for an Apify run WITHOUT spending, return a dict.

    Used by `--estimate-only`: callers print this and exit 0. The per-result price of an
    Apify Store actor isn't exposed via a stable public endpoint, so the projection is a
    transparent best-effort from the caller's --max-cost-usd budget and (optionally) a
    known per-item price + an item-count hint. No run is started.
    """
    projected = None
    if per_item_usd is not None and items_hint is not None:
        projected = round(per_item_usd * max(items_hint, 0), 4)
    est = {
        "estimate_only": True,
        "actor": actor,
        "label": label or actor,
        "max_cost_usd": max_cost_usd,
        "timeout_s": timeout_s,
        "items_hint": items_hint,
        "per_item_usd": per_item_usd,
        "projected_cost_usd": projected,
        "would_spend": False,
        "note": ("hard cost gate: the run is aborted if reported usage exceeds "
                 "--max-cost-usd or the wall-clock timeout trips. Pass --yes to spend."),
        "input_preview": {k: run_input[k] for k in list(run_input)[:6]},
    }
    return est


def run_actor(actor, run_input, max_cost_usd=1.0, timeout_s=600, poll_s=6,
              memory_mbytes=None, tok=None):
    """Start <actor> async, poll to terminal, enforce cost gate, return dataset items (list).

    actor          : "user~actor-name" or actor id.
    run_input      : dict — the actor's input payload.
    max_cost_usd   : abort if the run's reported usage exceeds this (hard gate).
    timeout_s      : wall-clock budget; abort + raise ApifyError if exceeded.
    Raises CostGateError on budget breach, ApifyError on actor failure/timeout.
    """
    tok = tok or token()
    if not tok:
        raise ApifyError("APIFY_API_TOKEN not set")
    if max_cost_usd <= 0:
        raise CostGateError(
            f"cost gate refusal: --max-cost-usd={max_cost_usd} (<=0) forbids any spend. "
            "Raise the budget to run the Apify actor.")

    qs = urllib.parse.urlencode({"token": tok})
    start_url = f"{API}/acts/{urllib.parse.quote(actor, safe='~')}/runs?{qs}"
    if memory_mbytes:
        start_url += f"&memory={int(memory_mbytes)}"

    started = _req(start_url, method="POST", body=dict(run_input))
    run = started.get("data") or started
    run_id = run.get("id")
    if not run_id:
        raise ApifyError(f"no run id returned: {json.dumps(started)[:200]}")

    deadline = time.time() + timeout_s
    status = run.get("status", "")
    while status not in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
        if time.time() > deadline:
            try:
                _req(f"{API}/actor-runs/{run_id}/abort?{qs}", method="POST")
            except (ApifyError, CostGateError):
                pass
            raise ApifyError(f"actor run timed out after {timeout_s}s (status={status}); aborted")
        time.sleep(poll_s)
        got = _req(f"{API}/actor-runs/{run_id}?{qs}")
        run = got.get("data") or got
        status = run.get("status", "")
        cost = _usd(run)
        if cost > max_cost_usd:
            try:
                _req(f"{API}/actor-runs/{run_id}/abort?{qs}", method="POST")
            except (ApifyError, CostGateError):
                pass
            raise CostGateError(
                f"cost gate hit: run used ${cost:.4f} > --max-cost-usd ${max_cost_usd:.2f}; "
                "aborted. Raise --max-cost-usd or narrow the input.")

    final_cost = _usd(run)
    if status != "SUCCEEDED":
        raise ApifyError(f"actor run {status} (cost ${final_cost:.4f}): "
                         f"{(run.get('statusMessage') or '')[:200]}")
    if final_cost > max_cost_usd:
        raise CostGateError(
            f"cost gate hit post-run: ${final_cost:.4f} > ${max_cost_usd:.2f}")

    ds = run.get("defaultDatasetId")
    if not ds:
        return []
    items_url = (f"{API}/datasets/{ds}/items?"
                 + urllib.parse.urlencode({"token": tok, "format": "json", "clean": "true"}))
    items = _req(items_url, timeout=120)
    if isinstance(items, dict):
        items = items.get("items") or items.get("data") or []
    return items if isinstance(items, list) else []
