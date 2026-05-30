"""CLI contract: every skill script must parse ``--help`` cleanly.

Runs each ``scripts/*.py`` as a subprocess with ``--help`` and asserts it exits 0 and
emits an argparse usage line. This catches scripts that crash at import (bad sibling
import, syntax/typo reachable only at run time) or that lack an argument parser. Covers
the whole library in one sweep.
"""
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import is_cli_script, iter_scripts  # noqa: E402


class TestCliHelp(unittest.TestCase):
    def test_help_parses_for_every_script(self):
        # Vendored import-only helpers (apify_common.py, sigdb.py) expose no CLI — skip them.
        scripts = [t for t in iter_scripts() if is_cli_script(t[2])]
        self.assertGreater(len(scripts), 100, "expected the full GTM CLI script set")
        for skill, fn, path in scripts:
            with self.subTest(skill=skill, script=fn):
                r = subprocess.run(
                    [sys.executable, path, "--help"],
                    capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(
                    r.returncode, 0,
                    f"{skill}/{fn} --help exited {r.returncode}\n"
                    f"stderr:\n{r.stderr[:800]}",
                )
                self.assertIn(
                    "usage:", r.stdout[:400].lower(),
                    f"{skill}/{fn} --help produced no usage line (not an argparse CLI?)",
                )


if __name__ == "__main__":
    unittest.main()
