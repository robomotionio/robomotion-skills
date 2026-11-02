"""Community docs must not point at disabled or missing destinations.

Regression for #542. Discussions are disabled, so questions go to issues and
conduct reports stay on the uupm.cc contact. The stack quickstart clones this
repository and enters stack/ before ./scripts/setup.sh.
"""

import re
import unittest
from pathlib import Path

REPO = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / "scripts" / "generate-catalog-summary.py").is_file()
)
DISCUSSIONS_URL = "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/discussions"
ISSUES_URL = "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/issues"
STACK_CLONE = "git clone https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git"
STACK_CD = "cd ui-ux-pro-max-skill/stack"


def read_repo_text(relative_path):
    return (REPO / relative_path).read_text(encoding="utf-8")


def section_until_next_heading(text, heading):
    """Body under `heading`, up to the next `## ` heading.

    A missing heading fails here. Returning an empty slice would let the
    negative checks (no /discussions, no old clone URL) pass vacuously.
    """
    match = re.search(
        rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"missing heading: ## {heading}")
    return match.group(1)


class CommunityDocsTest(unittest.TestCase):
    def test_questions_issues_conduct_contact_and_stack_clone(self):
        contributing = read_repo_text("CONTRIBUTING.md")
        questions = section_until_next_heading(contributing, "Questions?")
        self.assertIn(ISSUES_URL, questions)
        self.assertIn("README.md", questions)
        self.assertNotIn(DISCUSSIONS_URL, contributing)

        conduct = read_repo_text("CODE_OF_CONDUCT.md")
        enforcement = section_until_next_heading(conduct, "Enforcement")
        self.assertIn("https://www.uupm.cc", enforcement)
        self.assertNotIn("/discussions", enforcement)
        self.assertNotIn("/issues", enforcement)
        self.assertNotIn("mailto:", enforcement)
        self.assertNotIn(DISCUSSIONS_URL, conduct)

        quickstart = section_until_next_heading(read_repo_text("stack/README.md"), "Quickstart")
        self.assertIn(STACK_CLONE, quickstart)
        self.assertIn(STACK_CD, quickstart)
        self.assertLess(quickstart.index(STACK_CLONE), quickstart.index(STACK_CD))
        self.assertLess(quickstart.index(STACK_CD), quickstart.index("./scripts/setup.sh"))
        self.assertNotIn("YMungerDev/claude-website-design-stack", quickstart)
        self.assertTrue((REPO / "stack" / "scripts" / "setup.sh").is_file())
