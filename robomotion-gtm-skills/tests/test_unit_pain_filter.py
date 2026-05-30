"""Unit tests for pain-language-engagers/pain_filter.py — the pain-vs-solution classifier
that keeps buyers in pain and drops vendors/announcers, with the frustration-cue rescue."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import load_script, run_script  # noqa: E402

mod = load_script("pain-language-engagers", "pain_filter.py")

PAIN_TERMS = ["manual data entry", "copy paste between systems", "spreadsheet hell"]


class TestClassify(unittest.TestCase):
    def test_pain_post_is_kept(self):
        res = mod.classify_post("I waste hours on manual data entry every week", PAIN_TERMS)
        self.assertTrue(res["keep"])
        self.assertIn("manual data entry", res["matched_pain_terms"])
        self.assertEqual(res["reason"], "pain_match")

    def test_announcement_is_dropped_even_with_pain_word(self):
        res = mod.classify_post(
            "Excited to announce we just launched a tool that kills manual data entry! Book a demo",
            PAIN_TERMS)
        self.assertFalse(res["keep"])
        self.assertTrue(res["reason"].startswith("excluded:"))

    def test_frustration_cue_rescues_a_borderline_post(self):
        # contains an exclude phrase ("our platform") but a clear first-person frustration cue
        res = mod.classify_post(
            "I'm so tired of manual data entry — even our platform makes me copy paste between systems",
            PAIN_TERMS)
        self.assertTrue(res["keep"])
        self.assertIn("frustration_cue", res["reason"])

    def test_no_pain_match_is_dropped(self):
        res = mod.classify_post("Great weather today, loving life", PAIN_TERMS)
        self.assertFalse(res["keep"])
        self.assertEqual(res["reason"], "no_pain_match")

    def test_regex_match_is_flagged(self):
        res = mod.classify_post("why am I still doing this manually by hand", PAIN_TERMS,
                                pain_regex=r"still doing this manually")
        self.assertTrue(res["keep"])
        self.assertIn("(regex)", res["matched_pain_terms"])


class TestPostFieldExtraction(unittest.TestCase):
    def test_text_pulled_from_varied_field_names(self):
        self.assertEqual(mod.post_text({"postContent": "hello"}), "hello")
        self.assertEqual(mod.post_text("raw string"), "raw string")
        self.assertEqual(mod.post_url({"shareUrl": "http://x"}), "http://x")


class TestSelftestCli(unittest.TestCase):
    def test_selftest_exits_zero(self):
        r = run_script("pain-language-engagers", "pain_filter.py", "--selftest")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("PASS", r.stdout)


if __name__ == "__main__":
    unittest.main()
