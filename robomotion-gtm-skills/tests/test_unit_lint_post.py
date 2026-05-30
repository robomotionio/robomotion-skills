"""End-to-end unit test for create-linkedin-content/lint_post.py — the deterministic post
self-check (banned phrases, word count, 'why this matters' beat, hashtag cap). Reads from
stdin; exit code is always advisory (0), the JSON `pass` field is the gate."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import load_script, run_script  # noqa: E402

mod = load_script("create-linkedin-content", "lint_post.py")

# A clean post: ~160 words, a "why this matters" beat, a number, <=2 hashtags, no banned terms.
GOOD_BODY = (
    "We cut onboarding time from 12 days to 3 by deleting steps nobody used. "
    + "Here is the short version of what happened and what we learned along the way. " * 14
    + "Why this matters: every removed step compounds. #ops #automation"
)
BANNED_BODY = "We will leverage synergy to circle back. " * 40 + "Why this matters: nothing."


class TestStripFrontmatter(unittest.TestCase):
    def test_removes_yaml_frontmatter(self):
        out = mod.strip_frontmatter("---\ntitle: x\n---\nbody here")
        self.assertEqual(out.strip(), "body here")


class TestLintCli(unittest.TestCase):
    def _run(self, body, *args):
        r = run_script("create-linkedin-content", "lint_post.py", "--file", "-", *args,
                       stdin=body)
        self.assertEqual(r.returncode, 0, r.stderr)  # always advisory exit 0
        return json.loads(r.stdout)

    def test_clean_post_passes(self):
        out = self._run(GOOD_BODY)
        self.assertEqual(out["banned_hits"], [])
        self.assertTrue(out["length_ok"])
        self.assertTrue(out["has_why_this_matters"])
        self.assertTrue(out["pass"])

    def test_banned_phrases_fail_the_gate(self):
        out = self._run(BANNED_BODY)
        self.assertIn("synergy", out["banned_hits"])
        self.assertIn("leverage", out["banned_hits"])
        self.assertFalse(out["pass"])

    def test_too_many_hashtags_flagged(self):
        out = self._run(GOOD_BODY + " #a #b #c #d", "--max-hashtags", "2")
        self.assertFalse(out["hashtags_ok"])
        self.assertFalse(out["pass"])


if __name__ == "__main__":
    unittest.main()
