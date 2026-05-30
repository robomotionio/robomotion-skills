# robomotion-gtm-skills — test suite

Zero-dependency tests for the GTM skill scripts. Every test is a stdlib `unittest.TestCase`,
so the suite runs with **just `python3`** — and `pytest` discovers it too if installed.
The skill scripts are stdlib-only and the harness keeps that property: no `pip install` needed.

## Running

```bash
# from the group root (robomotion-gtm-skills/)
python3 -m unittest discover -s tests -p 'test_*.py'     # offline; the default
pytest -q tests                                          # same suite, if pytest is present
GTM_NET_TESTS=1 python3 -m unittest discover -s tests -p 'test_*.py'   # + live keyless endpoints
```

`bash validate.sh` runs the offline suite as its last step. Env toggles:

- `GTM_NET_TESTS=1` — also run the live keyless-endpoint tests (Hacker News, Wayback,
  Google Suggest, DuckDuckGo). Off by default so the suite is deterministic and offline.
- `GTM_SKIP_TESTS=1` — skip the suite in `validate.sh` (syntax/contract checks still run).

## Layout (flat, by layer)

| Prefix | Layer | What it covers |
|--------|-------|----------------|
| `test_contract_*` | **CLI contract** (whole library) | every script's `--help` parses; every `--flag` in every SKILL.md example is declared by its script — incl. argparse subcommands and cross-skill (`../other-skill/scripts/…`) references |
| `test_unit_*` | **Unit** (deterministic logic, no network) | scoring/tiering (`score_icp`, `score_results`, `score_tam`, `ab_significance`), parsers/linters (`normalize_campaigns`, `cluster_url_patterns`, `pain_filter`, `lint_post`), dedup, and the Apify cost-gate refusals |
| `test_mocked_*` | **Mocked paid-API** (no network, no keys) | Apify / Apollo / DataForSEO request parsing + cost-gate + the keyless no-creds contract, with the HTTP layer monkeypatched |
| `test_keyless_*` | **Keyless integration** | the SERP HTML parser offline (always), plus the live public endpoints behind `@net_gate` (`GTM_NET_TESTS=1`) |

## Shared helpers — `_util.py`

- `load_script(skill, script)` — import a script as a uniquely-named module (sibling imports
  like `apify_common` / `pain_filter` / `sigdb` resolve as they do at runtime).
- `run_script(skill, script, *args, env=, stdin=)` — run a script as a subprocess.
- `parse_skill_examples(SKILL.md)` / `script_declared_flags(path)` — back the contract tests.
- `net_gate` — decorator skipping a test unless `GTM_NET_TESTS` is set.

## Adding a test

Drop a `test_<layer>_<name>.py` file in this directory, start it with

```python
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import load_script   # etc.
```

and write plain `unittest.TestCase` classes. New scripts are picked up by the contract sweep
automatically; add a `test_unit_*` file when a script has non-trivial deterministic logic.
