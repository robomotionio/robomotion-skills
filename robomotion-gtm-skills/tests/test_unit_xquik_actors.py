"""Offline contract tests for the Xquik Actor skills."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import load_script, script_path  # noqa: E402


def load_with_vendored_helper(skill, script):
    """Load a CLI with its own apify_common module."""
    previous = sys.modules.pop("apify_common", None)
    try:
        return load_script(skill, script)
    finally:
        sys.modules.pop("apify_common", None)
        if previous is not None:
            sys.modules["apify_common"] = previous


tweet = load_with_vendored_helper("x-mention-tracker", "x_search.py")
followers = load_with_vendored_helper(
    "x-follower-scraper",
    "x_followers.py",
)
helper = load_script("x-follower-scraper", "apify_common.py")


class TestVendoredHelper(unittest.TestCase):
    def setUp(self):
        self.original_request = helper._req
        self.original_urlopen = helper.urllib.request.urlopen

    def tearDown(self):
        helper._req = self.original_request
        helper.urllib.request.urlopen = self.original_urlopen

    def test_actor_helpers_are_identical(self):
        with open(
            script_path("x-mention-tracker", "apify_common.py"),
            encoding="utf-8",
        ) as tweet_helper:
            tweet_source = tweet_helper.read()
        with open(
            script_path("x-follower-scraper", "apify_common.py"),
            encoding="utf-8",
        ) as follower_helper:
            follower_source = follower_helper.read()
        self.assertEqual(tweet_source, follower_source)

    def test_request_uses_authorization_header(self):
        requests = []

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

            def read(self):
                return b"{}"

        def fake_urlopen(request, timeout):
            requests.append((request, timeout))
            return FakeResponse()

        helper.urllib.request.urlopen = fake_urlopen
        helper._req(
            "https://api.apify.com/v2/actors/example~actor/runs",
            method="POST",
            body={"maxItems": 1},
            tok="secret-token",
        )

        request, timeout = requests[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer secret-token")
        self.assertNotIn("secret-token", request.full_url)
        self.assertEqual(timeout, 90)

    def test_run_uses_current_routes_and_server_charge_cap(self):
        calls = []

        def fake_req(
            url,
            method="GET",
            body=None,
            timeout=90,
            tok="",
        ):
            calls.append(
                {
                    "url": url,
                    "method": method,
                    "body": body,
                    "timeout": timeout,
                    "token": tok,
                }
            )
            if method == "POST" and "/runs?" in url:
                return {
                    "data": {
                        "id": "run-1",
                        "status": "SUCCEEDED",
                        "usageTotalUsd": 0.01,
                        "defaultDatasetId": "dataset-1",
                    }
                }
            if "/datasets/dataset-1/items?" in url:
                return [{"id": "result-1"}]
            raise AssertionError(f"unexpected request: {method} {url}")

        helper._req = fake_req
        items = helper.run_actor(
            "xquik~x-tweet-scraper",
            {"maxItems": 1},
            max_cost_usd=0.25,
            tok="secret-token",
        )

        self.assertEqual(items, [{"id": "result-1"}])
        self.assertIn(
            "/v2/actors/xquik~x-tweet-scraper/runs?",
            calls[0]["url"],
        )
        self.assertIn("maxTotalChargeUsd=0.25", calls[0]["url"])
        self.assertNotIn("token=", calls[0]["url"])
        self.assertEqual(calls[0]["token"], "secret-token")
        self.assertEqual(calls[-1]["token"], "secret-token")

    def test_nonfinite_budget_is_rejected_before_http(self):
        calls = []
        helper._req = lambda *args, **kwargs: calls.append((args, kwargs))

        with self.assertRaises(helper.CostGateError):
            helper.run_actor(
                "xquik~x-tweet-scraper",
                {"maxItems": 1},
                max_cost_usd=float("nan"),
                tok="secret-token",
            )

        self.assertEqual(calls, [])


class TestTweetActor(unittest.TestCase):
    def test_existing_actor_remains_the_default(self):
        self.assertEqual(tweet.APIFY_ACTOR, "apidojo~tweet-scraper")
        self.assertEqual(
            tweet.apify_input("robomotion since:2026-07-01", 25),
            {
                "searchTerms": ["robomotion since:2026-07-01"],
                "maxTweets": 25,
                "maxItems": 25,
                "searchMode": "live",
            },
        )

    def test_xquik_actor_uses_its_own_input_contract(self):
        self.assertEqual(
            tweet.apify_input(
                "robomotion since:2026-07-01",
                25,
                tweet.XQUIK_APIFY_ACTOR,
            ),
            {
                "searchTerms": ["robomotion since:2026-07-01"],
                "maxItems": 25,
                "queryType": "Latest",
                "outputVariant": "rich",
                "fieldStyle": "camelCase",
                "includeSearchTerms": True,
            },
        )
        self.assertTrue(tweet.is_xquik_actor("xquik/x-tweet-scraper"))

    def test_control_rows_do_not_become_posts(self):
        calls = []
        tweet.apify_common.run_actor = (
            lambda actor, body, **kwargs: [
                {"resultType": "diagnostic", "status": "empty"},
                {"resultType": "run-report", "status": "completed"},
                {"id": "tweet-1", "text": "Hello"},
            ]
        )
        tweet.normalize = lambda row: calls.append(row) or row

        posts = tweet.fetch_apify("hello", 10, "token", 0.25, 30)

        self.assertEqual(posts, [{"id": "tweet-1", "text": "Hello"}])
        self.assertEqual(calls, [{"id": "tweet-1", "text": "Hello"}])


class TestFollowerActor(unittest.TestCase):
    def test_current_actor_and_input_contract(self):
        args = followers.build_parser().parse_args(
            [
                "--handle",
                "apify",
                "--relation",
                "followers",
                "--max-profiles",
                "25",
                "--estimate-only",
            ]
        )
        self.assertEqual(followers.APIFY_ACTOR, "xquik~x-follower-scraper")
        self.assertEqual(
            followers.build_input(args),
            {
                "maxItems": 25,
                "outputMode": "compact",
                "dedupeMode": "first",
                "includeTargetMetadata": True,
                "twitterHandles": ["apify"],
                "relation": "followers",
            },
        )

    def test_control_rows_are_partitioned(self):
        rows = [
            {"resultType": "diagnostic", "status": "empty"},
            {"resultType": "run-report", "status": "completed"},
            {"id": "profile-1", "username": "apify"},
            "invalid",
        ]

        profiles, diagnostics, reports = followers.partition_rows(rows)

        self.assertEqual(profiles, [{"id": "profile-1", "username": "apify"}])
        self.assertEqual(
            diagnostics,
            [{"resultType": "diagnostic", "status": "empty"}],
        )
        self.assertEqual(
            reports,
            [{"resultType": "run-report", "status": "completed"}],
        )


if __name__ == "__main__":
    unittest.main()
