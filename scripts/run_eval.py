#!/usr/bin/env python3
"""Minimal eval tool for SKILL.md files.

Tests two dimensions:
  1. Trigger precision — does Claude activate the skill for the right queries?
  2. Output quality — when activated, does the skill produce good results?

Usage:
  python run_eval.py <skill_path>                    # Run all evals
  python run_eval.py <skill_path> --type trigger     # Trigger evals only
  python run_eval.py <skill_path> --type quality     # Quality evals only
  python run_eval.py <skill_path> --case <id>        # Single case
  python run_eval.py <skill_path> --verbose          # Full JSON output
  python run_eval.py <skill_path> --model <model>    # Override model (default: sonnet)
"""

import argparse
import json
import os
import subprocess
import sys
import textwrap


def run_claude(query: str, cwd: str, model: str = "sonnet") -> dict:
    """Execute claude -p with stream-json output and return parsed response with messages."""
    cmd = [
        "claude",
        "-p", query,
        "--output-format", "stream-json",
        "--verbose",
        "--model", model,
    ]
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except FileNotFoundError:
        print("Error: 'claude' CLI not found. Install it first.", file=sys.stderr)
        sys.exit(2)
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "messages": []}

    if result.returncode != 0 and not result.stdout.strip():
        return {"error": result.stderr.strip(), "messages": []}

    # Parse stream-json: each line is a JSON object
    messages = []
    final_result = {}
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("type") == "assistant":
            msg = obj.get("message", {})
            if msg:
                messages.append(msg)
        elif obj.get("type") == "result":
            final_result = obj

    final_result["messages"] = messages
    return final_result


def check_skill_invoked(response: dict, skill_name: str) -> bool:
    """Walk JSON messages looking for a Skill tool_use block matching skill_name."""
    messages = response.get("messages", [])
    for msg in messages:
        if msg.get("role") != "assistant":
            continue
        content = msg.get("content", [])
        if isinstance(content, str):
            continue
        for block in content:
            if block.get("type") != "tool_use":
                continue
            if block.get("name") != "Skill":
                continue
            inp = block.get("input", {})
            if inp.get("skill", "") == skill_name:
                return True
    return False


def eval_trigger(case: dict, skill_name: str, cwd: str, model: str, verbose: bool) -> dict:
    """Run a trigger eval case. Returns result dict with pass/fail."""
    case_id = case["id"]
    query = case["query"]
    expect = case["expect_triggered"]

    if verbose:
        print(f"  Running: {query!r}")

    response = run_claude(query, cwd, model)

    if "error" in response:
        return {
            "id": case_id,
            "type": "trigger",
            "passed": False,
            "reason": f"Claude error: {response['error']}",
            "response": response if verbose else None,
        }

    invoked = check_skill_invoked(response, skill_name)
    passed = invoked == expect

    reason = ""
    if not passed:
        if expect:
            reason = f"Expected skill '{skill_name}' to trigger but it did NOT"
        else:
            reason = f"Expected skill '{skill_name}' NOT to trigger but it DID"

    return {
        "id": case_id,
        "type": "trigger",
        "passed": passed,
        "expected": expect,
        "actual": invoked,
        "reason": reason,
        "response": response if verbose else None,
    }


def run_judge(response_text: str, criteria: list[str], model: str = "sonnet") -> dict:
    """Use LLM-as-judge to grade response quality against criteria."""
    criteria_block = "\n".join(f"  {i+1}. {c}" for i, c in enumerate(criteria))
    prompt = textwrap.dedent(f"""\
        You are an eval judge. Grade the following AI assistant response against each criterion.

        RESPONSE TO GRADE:
        ---
        {response_text}
        ---

        CRITERIA:
        {criteria_block}

        For each criterion, determine if the response satisfies it.
        Respond with ONLY valid JSON (no markdown fences) in this exact format:
        {{
          "grades": [
            {{"criterion": "...", "passed": true/false, "reason": "brief explanation"}}
          ],
          "overall_pass": true/false
        }}

        overall_pass should be true only if ALL criteria pass.
    """)

    cmd = [
        "claude",
        "-p", prompt,
        "--output-format", "text",
        "--model", model,
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {"overall_pass": False, "grades": [], "error": "judge failed"}

    text = result.stdout.strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.startswith("```")]
        text = "\n".join(lines)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"overall_pass": False, "grades": [], "error": "judge returned invalid JSON", "raw": text}


def extract_response_text(response: dict) -> str:
    """Extract human-readable text from Claude's JSON response."""
    messages = response.get("messages", [])
    parts = []
    for msg in messages:
        if msg.get("role") != "assistant":
            continue
        content = msg.get("content", [])
        if isinstance(content, str):
            parts.append(content)
            continue
        for block in content:
            if block.get("type") == "text":
                parts.append(block["text"])
            elif block.get("type") == "tool_use":
                parts.append(f"[tool_use: {block.get('name', '?')}({json.dumps(block.get('input', {}), indent=2)})]")
    # Fallback: check top-level result field
    if not parts and "result" in response:
        parts.append(str(response["result"]))
    return "\n".join(parts) if parts else json.dumps(response, indent=2)


def eval_quality(case: dict, skill_name: str, cwd: str, model: str, judge_model: str, verbose: bool) -> dict:
    """Run a quality eval case. Returns result dict with per-criterion grades."""
    case_id = case["id"]
    query = case["query"]
    criteria = case["criteria"]

    if verbose:
        print(f"  Running: {query!r}")

    response = run_claude(query, cwd, model)

    if "error" in response:
        return {
            "id": case_id,
            "type": "quality",
            "passed": False,
            "reason": f"Claude error: {response['error']}",
            "grades": [],
            "response": response if verbose else None,
        }

    response_text = extract_response_text(response)

    if verbose:
        print(f"  Judging against {len(criteria)} criteria...")

    judge_result = run_judge(response_text, criteria, judge_model)

    return {
        "id": case_id,
        "type": "quality",
        "passed": judge_result.get("overall_pass", False),
        "grades": judge_result.get("grades", []),
        "reason": judge_result.get("error", ""),
        "response": response if verbose else None,
    }


def load_eval_set(skill_path: str) -> dict:
    """Load eval-set.json from a skill directory."""
    eval_file = os.path.join(skill_path, "eval-set.json")
    if not os.path.isfile(eval_file):
        print(f"Error: {eval_file} not found", file=sys.stderr)
        sys.exit(1)
    with open(eval_file) as f:
        return json.load(f)


def print_summary(results: list[dict]) -> None:
    """Print a summary table of results."""
    if not results:
        print("\nNo cases executed.")
        return

    # Header
    print(f"\n{'ID':<25} {'Type':<10} {'Result':<8} {'Details'}")
    print("-" * 80)

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        details = r.get("reason", "")
        if r["type"] == "trigger" and not details:
            expected = "trigger" if r.get("expected") else "no trigger"
            details = f"expected={expected}"
        if r["type"] == "quality" and r["passed"]:
            n = len(r.get("grades", []))
            details = f"{n}/{n} criteria passed"
        elif r["type"] == "quality" and not r["passed"]:
            grades = r.get("grades", [])
            failed = [g for g in grades if not g.get("passed", False)]
            details = f"{len(grades) - len(failed)}/{len(grades)} criteria passed"
            if r.get("reason"):
                details = r["reason"]

        print(f"{r['id']:<25} {r['type']:<10} {status:<8} {details}")

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    print(f"\n{passed}/{total} passed")


def main():
    parser = argparse.ArgumentParser(
        description="Eval runner for SKILL.md files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            examples:
              python run_eval.py ./skills/yeet/
              python run_eval.py ./skills/yeet/ --type trigger
              python run_eval.py ./skills/yeet/ --case trigger-pos-1
              python run_eval.py ./skills/yeet/ --verbose
        """),
    )
    parser.add_argument("skill_path", help="Path to skill directory containing eval-set.json")
    parser.add_argument("--type", choices=["trigger", "quality"], help="Run only this eval type")
    parser.add_argument("--case", help="Run only this case ID")
    parser.add_argument("--model", default="sonnet", help="Model for running queries (default: sonnet)")
    parser.add_argument("--judge-model", default="sonnet", help="Model for quality judging (default: sonnet)")
    parser.add_argument("--verbose", action="store_true", help="Show full JSON responses")

    args = parser.parse_args()

    skill_path = os.path.abspath(args.skill_path)
    if not os.path.isdir(skill_path):
        print(f"Error: {skill_path} is not a directory", file=sys.stderr)
        sys.exit(1)

    eval_set = load_eval_set(skill_path)
    skill_name = eval_set["skill_name"]
    cases = eval_set["cases"]

    # Filter cases
    if args.type:
        cases = [c for c in cases if c["type"] == args.type]
    if args.case:
        cases = [c for c in cases if c["id"] == args.case]

    if not cases:
        print("No matching cases found.", file=sys.stderr)
        sys.exit(1)

    print(f"Evaluating skill: {skill_name}")
    print(f"Cases to run: {len(cases)}")
    print(f"Model: {args.model}")
    if any(c["type"] == "quality" for c in cases):
        print(f"Judge model: {args.judge_model}")
    print()

    results = []
    for case in cases:
        case_type = case["type"]
        print(f"[{case['id']}] ", end="", flush=True)

        if case_type == "trigger":
            result = eval_trigger(case, skill_name, skill_path, args.model, args.verbose)
        elif case_type == "quality":
            result = eval_quality(case, skill_name, skill_path, args.model, args.judge_model, args.verbose)
        else:
            print(f"SKIP (unknown type: {case_type})")
            continue

        status = "PASS" if result["passed"] else "FAIL"
        print(status)

        if args.verbose and result.get("response"):
            print(json.dumps(result["response"], indent=2)[:2000])

        results.append(result)

    print_summary(results)

    # Write results to file
    results_file = os.path.join(skill_path, "eval-results.json")
    with open(results_file, "w") as f:
        json.dump({"skill_name": skill_name, "results": results}, f, indent=2)
    print(f"\nResults written to {results_file}")

    # Exit code: 0 if all pass, 1 if any fail
    if all(r["passed"] for r in results):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
