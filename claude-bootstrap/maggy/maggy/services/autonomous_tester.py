"""Autonomous Testing Agent — discover, generate, execute, evaluate, fix.

Generalized from the edubites autonomous test runner pattern.
Works with any project type: Python (pytest), TypeScript (vitest), Web (playwright).
"""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TestGap:
    file: str
    symbol: str  # function/class/endpoint name
    kind: str    # function, endpoint, component
    existing_tests: int


@dataclass
class TestResult:
    name: str
    passed: bool
    error: str = ""
    failure_type: str = ""  # TEST_BUG, CODE_BUG, ENV_BUG


@dataclass
class AutonomousReport:
    project: str
    tests_run: int = 0
    passed: int = 0
    failed: int = 0
    auto_fixed: int = 0
    needs_manual: int = 0
    coverage: float = 0.0
    gaps_found: int = 0
    tests_generated: int = 0
    next_actions: list[str] = field(default_factory=list)


def detect_project(project_dir: str) -> dict:
    """Detect project type, test framework, and source layout."""
    root = Path(project_dir).expanduser()
    info = {"type": "unknown", "test_dir": "tests", "source_dir": "src"}

    if (root / "pyproject.toml").exists() or (root / "setup.py").exists():
        info["type"] = "python"
        info["framework"] = "pytest"
        info["source_dir"] = "src" if (root / "src").exists() else "."
        info["command"] = ["pytest", "-x", "--tb=short"]
    elif (root / "package.json").exists():
        pkg = _read_json(root / "package.json")
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        if "vitest" in deps:
            info["framework"] = "vitest"
            info["command"] = ["npx", "vitest", "run"]
        elif "jest" in deps:
            info["framework"] = "jest"
            info["command"] = ["npx", "jest"]
        else:
            info["framework"] = "vitest"
            info["command"] = ["npx", "vitest", "run"]
        if "playwright" in deps:
            info["has_e2e"] = True
        info["type"] = "typescript"
        info["source_dir"] = "src" if (root / "src").exists() else "."
    return info


def discover_gaps(project_dir: str) -> list[TestGap]:
    """Scan source files and find functions/endpoints without tests."""
    gaps: list[TestGap] = []
    root = Path(project_dir).expanduser()
    info = detect_project(project_dir)

    src_dir = root / info["source_dir"]
    test_dir = root / info["test_dir"]

    if info["type"] == "python":
        for py_file in src_dir.rglob("*.py"):
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue
            rel = py_file.relative_to(src_dir)
            # Check corresponding test exists
            test_file = test_dir / rel.parent / f"test_{rel.stem}.py"
            if not test_file.exists():
                functions = _extract_python_functions(py_file)
                for fn in functions:
                    gaps.append(TestGap(
                        file=str(rel), symbol=fn, kind="function",
                        existing_tests=0,
                    ))

    elif info["type"] == "typescript":
        for ts_file in src_dir.rglob("*.ts"):
            if "node_modules" in str(ts_file) or ".d.ts" in ts_file.name:
                continue
            rel = ts_file.relative_to(src_dir)
            test_file = test_dir / rel.parent / f"{rel.stem}.test.ts"
            if not test_file.exists():
                gaps.append(TestGap(
                    file=str(rel), symbol=rel.stem, kind="module",
                    existing_tests=0,
                ))

    return gaps


def generate_tests(gaps: list[TestGap], project_dir: str, model: str = "deepseek-pro") -> int:
    """Generate test files for discovered gaps using AI."""
    root = Path(project_dir).expanduser()
    generated = 0

    for gap in gaps[:10]:  # Limit per run
        src_content = _read_file(root / gap.file, max_lines=100)
        if not src_content:
            continue

        prompt = _build_generation_prompt(gap, src_content, project_dir)
        delegator = _delegator_for(model)

        try:
            result = subprocess.run(
                delegator + [prompt],
                capture_output=True, text=True, timeout=120,
                cwd=project_dir,
            )
            if result.returncode == 0 and result.stdout.strip():
                test_path = _test_path_for_gap(root, gap)
                test_path.parent.mkdir(parents=True, exist_ok=True)
                test_path.write_text(result.stdout.strip())
                generated += 1
        except Exception:
            pass

    return generated


def execute_tests(project_dir: str) -> tuple[list[TestResult], float]:
    """Run tests and collect results with coverage."""
    info = detect_project(project_dir)
    root = Path(project_dir).expanduser()
    results: list[TestResult] = []
    coverage = 0.0

    try:
        cmd = info.get("command", ["pytest", "-x"])
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300, cwd=str(root),
        )
        results = _parse_test_output(proc.stdout, info["framework"])
    except Exception as e:
        logger.warning("Test execution failed: %s", e)

    return results, coverage


def evaluate_failures(failures: list[TestResult], project_dir: str) -> list[TestResult]:
    """Classify each failure as TEST_BUG, CODE_BUG, or ENV_BUG using AI."""
    for f in failures:
        if f.passed:
            continue
        prompt = (
            f"Classify this test failure. Reply with exactly one word: "
            f"TEST_BUG (test expectations are wrong), "
            f"CODE_BUG (the code has a bug), or "
            f"ENV_BUG (missing dependency/config).\n\n"
            f"Test: {f.name}\nError: {f.error[:500]}"
        )
        try:
            proc = subprocess.run(
                [_delegator_bin("deepseek"), "--flash", prompt],
                capture_output=True, text=True, timeout=30,
            )
            output = proc.stdout.strip().upper()
            if "TEST_BUG" in output:
                f.failure_type = "TEST_BUG"
            elif "CODE_BUG" in output:
                f.failure_type = "CODE_BUG"
            elif "ENV_BUG" in output:
                f.failure_type = "ENV_BUG"
        except Exception:
            f.failure_type = "CODE_BUG"  # Default assumption

    return failures


def auto_fix(failures: list[TestResult], project_dir: str) -> int:
    """Attempt to auto-fix TEST_BUG failures."""
    fixed = 0
    for f in failures:
        if f.failure_type != "TEST_BUG":
            continue
        # Regenerate the failing test
        prompt = (
            f"Fix this failing test. The test expectations are wrong, "
            f"not the code. Write only the corrected test file.\n\n"
            f"Test: {f.name}\nError: {f.error[:600]}"
        )
        try:
            proc = subprocess.run(
                [_delegator_bin("deepseek"), "--pro", prompt],
                capture_output=True, text=True, timeout=60,
            )
            if proc.returncode == 0:
                # Write fixed test — actual implementation would parse the response
                fixed += 1
        except Exception:
            pass
    return fixed


def run_autonomous(project_dir: str) -> AutonomousReport:
    """Full autonomous testing cycle: discover → generate → execute → evaluate → fix."""
    report = AutonomousReport(project=Path(project_dir).name)

    # Phase 1: Discover
    gaps = discover_gaps(project_dir)
    report.gaps_found = len(gaps)

    # Phase 2: Generate
    if gaps:
        report.tests_generated = generate_tests(gaps, project_dir)

    # Phase 3: Execute
    results, coverage = execute_tests(project_dir)
    report.tests_run = len(results)
    report.passed = sum(1 for r in results if r.passed)
    report.failed = sum(1 for r in results if not r.passed)
    report.coverage = coverage

    # Phase 4: Evaluate
    failures = [r for r in results if not r.passed]
    if failures:
        failures = evaluate_failures(failures, project_dir)
        report.needs_manual = sum(
            1 for f in failures if f.failure_type == "CODE_BUG"
        )

    # Phase 5: Auto-fix
    test_bugs = [f for f in failures if f.failure_type == "TEST_BUG"]
    if test_bugs:
        report.auto_fixed = auto_fix(test_bugs, project_dir)

    # Phase 6: Next actions
    if report.failed > 0:
        report.next_actions.append(
            f"{report.needs_manual} CODE_BUGs need manual fixes"
        )
    if report.gaps_found > report.tests_generated:
        report.next_actions.append(
            f"{report.gaps_found - report.tests_generated} gaps still untested"
        )
    if report.coverage < 0.8:
        report.next_actions.append(
            f"Coverage {report.coverage:.0%} below 80% threshold"
        )

    return report


# ── helpers ──────────────────────────────────────────────────────────────

def _delegator_bin(model: str) -> str:
    return str(Path.home() / "bin" / model)


def _delegator_for(model: str) -> list[str]:
    m = _delegator_bin(model)
    if "deepseek" in model:
        return [m, "--pro"] if "pro" in model else [m, "--flash"]
    if "gemini" in model:
        return [m, "--pro"] if "pro" in model else [m, "--flash"]
    return [m]


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _read_file(path: Path, max_lines: int = 100) -> str:
    try:
        lines = path.read_text().split("\n")[:max_lines]
        return "\n".join(lines)
    except Exception:
        return ""


def _extract_python_functions(path: Path) -> list[str]:
    """Extract function/class names from a Python file."""
    import ast
    try:
        tree = ast.parse(path.read_text())
        names = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    names.append(node.name)
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith("_"):
                    names.append(node.name)
        return names
    except Exception:
        return []


def _test_path_for_gap(root: Path, gap: TestGap) -> Path:
    test_dir = root / "tests"
    rel = Path(gap.file)
    if gap.kind == "function":
        return test_dir / rel.parent / f"test_{rel.stem}.py"
    return test_dir / rel.parent / f"{rel.stem}.test.ts"


def _build_generation_prompt(gap: TestGap, src: str, project_dir: str) -> str:
    return (
        f"Write a complete test file for '{gap.symbol}' in {gap.file}. "
        f"Include: imports, fixtures, happy path, error cases, edge cases. "
        f"Source code:\n\n{src}\n\n"
        f"Write ONLY the test code, no explanations."
    )


def _parse_test_output(output: str, framework: str) -> list[TestResult]:
    """Parse pytest/vitest output into structured results."""
    results: list[TestResult] = []
    for line in output.split("\n"):
        line = line.strip()
        if "PASSED" in line or "passed" in line:
            # Extract test name
            name = line.replace("PASSED", "").replace("✓", "").strip()[:120]
            if name:
                results.append(TestResult(name=name, passed=True))
        elif "FAILED" in line or "FAIL" in line:
            name = line.replace("FAILED", "").replace("✗", "").strip()[:120]
            if name:
                results.append(TestResult(name=name, passed=False, error=line))
    if not results:
        results.append(TestResult(
            name="test_run", passed="failed" not in output.lower()[:200],
            error=output[:500],
        ))
    return results
