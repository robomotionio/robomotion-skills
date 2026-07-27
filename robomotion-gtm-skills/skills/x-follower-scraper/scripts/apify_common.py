#!/usr/bin/env python3
"""Vendored Apify async run, polling, and cost-gate helper.

Each installable skill keeps its own copy. The helper:
  - starts an Actor asynchronously through POST /v2/actors/<actor>/runs,
  - sends credentials only in the Authorization header,
  - applies Apify's server-side maximum charge,
  - polls to every terminal state with a wall-clock timeout,
  - aborts on timeout or a reported budget breach,
  - fetches dataset items only after SUCCEEDED.

Authentication uses APIFY_API_TOKEN.
"""
import json
import math
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


def _req(url, method="GET", body=None, timeout=90, tok=""):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Accept": "application/json"}
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as error:
            if error.code in (429, 502, 503, 504) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            detail = error.read().decode("utf-8", "ignore")[:300]
            if error.code == 402:
                raise CostGateError(
                    f"Apify quota/credit exceeded (HTTP 402): {detail}"
                )
            raise ApifyError(f"Apify {error.code}: {detail}")
        except urllib.error.URLError as error:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise ApifyError(f"network: {error}")


def _usd(run):
    """Best-effort actual-cost read from an Apify run object."""
    if not isinstance(run, dict):
        return 0.0
    for key in ("usageTotalUsd", "usageUsd"):
        if run.get(key) is not None:
            try:
                return float(run[key])
            except (TypeError, ValueError):
                pass
    usage = run.get("usage") or {}
    if isinstance(usage, dict) and usage.get("USD") is not None:
        try:
            return float(usage["USD"])
        except (TypeError, ValueError):
            pass
    return 0.0


def estimate(
    actor,
    run_input,
    max_cost_usd,
    timeout_s,
    items_hint=None,
    per_item_usd=None,
    label="",
):
    """Return the projected limits for an Apify run without spending.

    Callers may provide a current per-item price for a best-effort projection.
    The live Actor pricing box remains authoritative. No run is started.
    """
    projected = None
    if per_item_usd is not None and items_hint is not None:
        projected = round(per_item_usd * max(items_hint, 0), 4)
    return {
        "estimate_only": True,
        "actor": actor,
        "label": label or actor,
        "max_cost_usd": max_cost_usd,
        "timeout_s": timeout_s,
        "items_hint": items_hint,
        "per_item_usd": per_item_usd,
        "projected_cost_usd": projected,
        "would_spend": False,
        "note": (
            "hard cost gate: Apify receives the maximum charge before start, "
            "and polling aborts on a reported breach or timeout. Pass --yes to spend."
        ),
        "input_preview": {
            key: run_input[key]
            for key in list(run_input)[:6]
        },
    }


def run_actor(
    actor,
    run_input,
    max_cost_usd=1.0,
    timeout_s=600,
    poll_s=6,
    memory_mbytes=None,
    tok=None,
):
    """Run an Actor within the supplied time and charge limits."""
    tok = tok or token()
    if not tok:
        raise ApifyError("APIFY_API_TOKEN not set")
    try:
        max_cost_usd = float(max_cost_usd)
    except (TypeError, ValueError) as error:
        raise CostGateError("max cost must be a finite positive number") from error
    if not math.isfinite(max_cost_usd) or max_cost_usd <= 0:
        raise CostGateError(
            f"cost gate refusal: --max-cost-usd={max_cost_usd} forbids spend. "
            "Raise the budget to run the Apify Actor."
        )

    run_params = {"maxTotalChargeUsd": max_cost_usd}
    if memory_mbytes:
        run_params["memory"] = int(memory_mbytes)
    query = urllib.parse.urlencode(run_params)
    start_url = (
        f"{API}/actors/{urllib.parse.quote(actor, safe='~')}/runs?{query}"
    )

    started = _req(
        start_url,
        method="POST",
        body=dict(run_input),
        tok=tok,
    )
    run = started.get("data") or started
    run_id = run.get("id")
    if not run_id:
        raise ApifyError(f"no run id returned: {json.dumps(started)[:200]}")

    deadline = time.time() + timeout_s
    status = run.get("status", "")
    terminal = ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT")
    while status not in terminal:
        if time.time() > deadline:
            try:
                _req(
                    f"{API}/actor-runs/{run_id}/abort",
                    method="POST",
                    tok=tok,
                )
            except (ApifyError, CostGateError):
                pass
            raise ApifyError(
                f"Actor run timed out after {timeout_s}s "
                f"(status={status}); aborted"
            )
        time.sleep(poll_s)
        received = _req(f"{API}/actor-runs/{run_id}", tok=tok)
        run = received.get("data") or received
        status = run.get("status", "")
        cost = _usd(run)
        if cost > max_cost_usd:
            try:
                _req(
                    f"{API}/actor-runs/{run_id}/abort",
                    method="POST",
                    tok=tok,
                )
            except (ApifyError, CostGateError):
                pass
            raise CostGateError(
                f"cost gate hit: run used ${cost:.4f} above "
                f"--max-cost-usd ${max_cost_usd:.2f}; aborted"
            )

    final_cost = _usd(run)
    if status != "SUCCEEDED":
        message = (run.get("statusMessage") or "")[:200]
        raise ApifyError(
            f"Actor run {status} (cost ${final_cost:.4f}): {message}"
        )
    if final_cost > max_cost_usd:
        raise CostGateError(
            f"cost gate hit post-run: ${final_cost:.4f} "
            f"above ${max_cost_usd:.2f}"
        )

    dataset_id = run.get("defaultDatasetId")
    if not dataset_id:
        return []
    items_url = (
        f"{API}/datasets/{dataset_id}/items?"
        + urllib.parse.urlencode({"format": "json", "clean": "true"})
    )
    items = _req(items_url, timeout=120, tok=tok)
    if isinstance(items, dict):
        items = items.get("items") or items.get("data") or []
    return items if isinstance(items, list) else []
