"""Unit tests for the vendored Apify cost gate (reddit-post-finder/apify_common.py) — the
no-spend estimate, the hard refusal on a non-positive budget, and the in-flight abort when
reported usage exceeds --max-cost-usd. No network: the HTTP layer (_req) is monkeypatched."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import load_script  # noqa: E402

mod = load_script("reddit-post-finder", "apify_common.py")


class TestEstimate(unittest.TestCase):
    def test_estimate_never_spends_and_projects_cost(self):
        est = mod.estimate("user~actor", {"q": "x", "limit": 100}, max_cost_usd=5.0,
                           timeout_s=600, items_hint=200, per_item_usd=0.01, label="probe")
        self.assertTrue(est["estimate_only"])
        self.assertFalse(est["would_spend"])
        self.assertEqual(est["projected_cost_usd"], 2.0)  # 0.01 * 200
        self.assertIn("Pass --yes to spend", est["note"])


class TestRunActorGate(unittest.TestCase):
    def test_nonpositive_budget_refuses_before_any_call(self):
        called = []
        mod._req = lambda *a, **k: called.append(a) or {}
        with self.assertRaises(mod.CostGateError):
            mod.run_actor("user~actor", {"q": "x"}, max_cost_usd=0, tok="tok")
        self.assertEqual(called, [], "must refuse before making any HTTP call")

    def test_missing_token_raises_apify_error(self):
        with self.assertRaises(mod.ApifyError):
            mod.run_actor("user~actor", {"q": "x"}, max_cost_usd=1.0, tok="")

    def test_overspend_run_is_aborted(self):
        aborts = []

        def fake_req(url, method="GET", body=None, timeout=90):
            if method == "POST" and "/runs?" in url:
                return {"data": {"id": "run1", "status": "RUNNING"}}
            if "abort" in url:
                aborts.append(url)
                return {}
            # poll: report usage above the budget
            return {"data": {"id": "run1", "status": "RUNNING", "usageTotalUsd": 9.99}}

        mod._req = fake_req
        with self.assertRaises(mod.CostGateError):
            mod.run_actor("user~actor", {"q": "x"}, max_cost_usd=1.0, poll_s=0, tok="tok")
        self.assertTrue(aborts, "an over-budget run must be aborted to stop the meter")


if __name__ == "__main__":
    unittest.main()
