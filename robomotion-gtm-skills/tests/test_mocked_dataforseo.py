"""Mocked paid-API tests for the DataForSEO adapter (seo-domain-analyzer/paid_seo.py).

No network and no credentials: the HTTP layer (``_post``) is monkeypatched with canned
DataForSEO envelopes so we test (a) the keyless-first no-creds contract, (b) the defensive
envelope digger ``_items``, and (c) the per-subcommand response parsing."""
import os
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import load_script, run_script  # noqa: E402

mod = load_script("seo-domain-analyzer", "paid_seo.py")


class TestNoCredsContract(unittest.TestCase):
    def test_missing_creds_exits_3_without_breaking_keyless(self):
        r = run_script("seo-domain-analyzer", "paid_seo.py", "keywords", "--keywords", "rpa",
                       env={"DATAFORSEO_LOGIN": "", "DATAFORSEO_PASSWORD": ""})
        self.assertEqual(r.returncode, mod.EXIT_NO_CREDS)
        self.assertIn("keyless path still applies", r.stderr)


class TestItemsEnvelope(unittest.TestCase):
    def test_nested_items_are_flattened(self):
        resp = {"status_code": 20000,
                "tasks": [{"status_code": 20000,
                           "result": [{"items": [{"keyword": "a"}, {"keyword": "b"}]}]}]}
        self.assertEqual(mod._items(resp), [{"keyword": "a"}, {"keyword": "b"}])

    def test_result_row_is_itself_the_datum(self):
        resp = {"status_code": 20000,
                "tasks": [{"status_code": 20000, "result": [{"rank": 42, "backlinks": 9}]}]}
        self.assertEqual(mod._items(resp), [{"rank": 42, "backlinks": 9}])

    def test_nonzero_status_raises(self):
        with self.assertRaises(RuntimeError):
            mod._items({"status_code": 40000, "status_message": "auth failed"})

    def test_task_level_error_raises(self):
        with self.assertRaises(RuntimeError):
            mod._items({"status_code": 20000,
                        "tasks": [{"status_code": 40400, "status_message": "not found"}]})


class TestSubcommandParsing(unittest.TestCase):
    def test_keywords_merges_volume_and_difficulty(self):
        def fake_post(path, payload, creds):
            if "search_volume" in path:
                return {"status_code": 20000, "tasks": [{"status_code": 20000, "result": [
                    {"items": [{"keyword": "rpa software", "search_volume": 1200,
                                "cpc": 4.5, "competition": 0.7}]}]}]}
            if "bulk_keyword_difficulty" in path:
                return {"status_code": 20000, "tasks": [{"status_code": 20000, "result": [
                    {"items": [{"keyword": "rpa software", "keyword_difficulty": 38}]}]}]}
            raise AssertionError(f"unexpected path {path}")

        mod._post = fake_post
        args = SimpleNamespace(keywords="rpa software", location_code=2840, language_code="en")
        out = mod.cmd_keywords(args, ("login", "pw"))
        self.assertEqual(out["metric"], "measured")
        row = out["keywords"][0]
        self.assertEqual(row["volume"], 1200)
        self.assertEqual(row["cpc"], 4.5)
        self.assertEqual(row["difficulty"], 38)

    def test_backlinks_summary_parsing(self):
        mod._post = lambda path, payload, creds: {
            "status_code": 20000, "tasks": [{"status_code": 20000, "result": [
                {"rank": 512, "backlinks": 8400, "referring_domains": 310}]}]}
        out = mod.cmd_backlinks(SimpleNamespace(target="example.com"), ("l", "p"))
        self.assertEqual(out["summary"]["domain_rank"], 512)
        self.assertEqual(out["summary"]["referring_domains"], 310)


if __name__ == "__main__":
    unittest.main()
