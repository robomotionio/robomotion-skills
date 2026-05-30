"""CLI contract: every flag used in a SKILL.md example must exist in the script.

For each skill, parses the ``scripts/<name>.py`` invocations out of SKILL.md's fenced
code blocks (joining ``\\`` line-continuations), collects the ``--flags`` used, and
asserts each one is actually declared by that script's argparse. This catches the
``--max-tweets``-class drift bug — a doc example referencing a renamed/removed flag —
across the whole library.

Also asserts that every script referenced by an example actually exists on disk.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import (  # noqa: E402
    iter_skills,
    parse_skill_examples,
    script_declared_flags,
)


class TestSkillExamples(unittest.TestCase):
    def test_example_flags_match_script_argparse(self):
        skills = list(iter_skills())
        checked = 0
        for slug, d in skills:
            md = os.path.join(d, "SKILL.md")
            if not os.path.isfile(md):
                continue
            # {absolute script path -> flags used}; cross-skill refs already resolved.
            for path, used in parse_skill_examples(md).items():
                rel = os.path.relpath(path, os.path.dirname(d))
                with self.subTest(skill=slug, script=rel):
                    self.assertTrue(
                        os.path.isfile(path),
                        f"{slug}/SKILL.md references {rel} which does not exist on disk",
                    )
                    declared = script_declared_flags(path)
                    self.assertIsNotNone(
                        declared, f"{slug}: `{rel} --help` failed to run")
                    unknown = used - declared
                    self.assertFalse(
                        unknown,
                        f"{slug}/SKILL.md uses flags not declared by {rel}: "
                        f"{sorted(unknown)}\n  declared: {sorted(declared)}",
                    )
                    checked += 1
        self.assertGreater(checked, 0, "no SKILL.md examples were parsed — parser broken?")


if __name__ == "__main__":
    unittest.main()
