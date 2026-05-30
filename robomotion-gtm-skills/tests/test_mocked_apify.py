"""Mocked paid-API tests for the vendored Apify run/poll layer (apify_common.py).

Complements the cost-gate unit tests with the SUCCESS path: the HTTP layer (``_req``) is
monkeypatched to walk an actor run from RUNNING -> SUCCEEDED and serve dataset items, so we
verify run_actor returns parsed items and respects the budget when usage stays under it."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import load_script  # noqa: E402

mod = load_script("reddit-post-finder", "apify_common.py")


class TestRunActorSuccess(unittest.TestCase):
    def test_immediate_success_returns_dataset_items(self):
        items = [{"title": "post 1"}, {"title": "post 2"}]

        def fake_req(url, method="GET", body=None, timeout=90):
            if method == "POST" and "/runs?" in url:
                return {"data": {"id": "r1", "status": "SUCCEEDED",
                                 "usageTotalUsd": 0.20, "defaultDatasetId": "ds1"}}
            if "/datasets/ds1/items" in url:
                return items
            raise AssertionError(f"unexpected request {method} {url}")

        mod._req = fake_req
        got = mod.run_actor("user~actor", {"q": "x"}, max_cost_usd=1.0, tok="tok")
        self.assertEqual(got, items)

    def test_polls_running_then_succeeds_within_budget(self):
        states = [
            {"data": {"id": "r1", "status": "RUNNING", "usageTotalUsd": 0.10}},
            {"data": {"id": "r1", "status": "SUCCEEDED", "usageTotalUsd": 0.40,
                      "defaultDatasetId": "ds1"}},
        ]
        polls = {"n": 0}

        def fake_req(url, method="GET", body=None, timeout=90):
            if method == "POST" and "/runs?" in url:
                return {"data": {"id": "r1", "status": "RUNNING", "usageTotalUsd": 0.0}}
            if "/datasets/ds1/items" in url:
                return [{"ok": True}]
            # poll of the run object
            s = states[min(polls["n"], len(states) - 1)]
            polls["n"] += 1
            return s

        mod._req = fake_req
        got = mod.run_actor("user~actor", {"q": "x"}, max_cost_usd=1.0, poll_s=0, tok="tok")
        self.assertEqual(got, [{"ok": True}])

    def test_items_dict_envelope_unwrapped(self):
        def fake_req(url, method="GET", body=None, timeout=90):
            if method == "POST" and "/runs?" in url:
                return {"data": {"id": "r1", "status": "SUCCEEDED",
                                 "defaultDatasetId": "ds1"}}
            return {"items": [{"a": 1}]}  # some endpoints wrap items in a dict

        mod._req = fake_req
        got = mod.run_actor("user~actor", {"q": "x"}, max_cost_usd=1.0, tok="tok")
        self.assertEqual(got, [{"a": 1}])


if __name__ == "__main__":
    unittest.main()
