"""Design by Contract layer for ReasonNodes.

Handles inference, evaluation, and formatting of preconditions,
postconditions, and invariants.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from .models import ReasonNode


def infer_contracts(
    reason: ReasonNode,
    code_context: str = '',
    project_dir: str = '.'
) -> dict[str, list[str]]:
    """Use LLM to infer contracts from stated purpose + code context.

    Returns dict with 'preconditions', 'postconditions', 'invariants'.
    Falls back to heuristic extraction if no LLM available.
    """
    # Try Claude CLI first
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if api_key:
        return _infer_via_claude(reason, code_context)

    # Try OpenAI
    openai_key = os.environ.get('OPENAI_API_KEY')
    if openai_key:
        return _infer_via_openai(reason, code_context)

    # Fallback: heuristic extraction
    return _infer_heuristic(reason, project_dir)


def _infer_via_claude(
    reason: ReasonNode, code_context: str
) -> dict[str, list[str]]:
    """Call Claude API to infer contracts."""
    prompt = _build_inference_prompt(reason, code_context)
    try:
        result = subprocess.run(
            ['claude', '--print', '-p', prompt],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return _parse_contract_response(result.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return _empty_contracts()


def _infer_via_openai(
    reason: ReasonNode, code_context: str
) -> dict[str, list[str]]:
    """Call OpenAI API to infer contracts."""
    try:
        import openai
        client = openai.OpenAI()
        prompt = _build_inference_prompt(reason, code_context)
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.2
        )
        return _parse_contract_response(
            response.choices[0].message.content or ''
        )
    except Exception:
        return _empty_contracts()


def _infer_heuristic(
    reason: ReasonNode, project_dir: str
) -> dict[str, list[str]]:
    """Basic heuristic contract extraction — no LLM needed."""
    pre = []
    post = []
    inv = []

    # Scope-based invariants
    for scope_path in reason.scope:
        inv.append(f'file_exists("{scope_path}")')

    # If goal mentions "test" or "validation"
    goal_lower = reason.goal.lower()
    if 'test' in goal_lower:
        for sp in reason.scope:
            if 'test' not in sp:
                test_path = _guess_test_path(sp)
                if test_path:
                    post.append(f'test_exists("{test_path}")')

    return {
        'preconditions': pre,
        'postconditions': post,
        'invariants': inv
    }


def _build_inference_prompt(
    reason: ReasonNode, code_context: str
) -> str:
    scope_str = ', '.join(reason.scope) if reason.scope else 'unspecified'
    return f"""Given this intent for a code change, infer formal contracts.

INTENT:
  Goal: {reason.goal}
  Decision type: {reason.decision_type}
  Scope: {scope_str}

{f'CODE CONTEXT:{chr(10)}{code_context[:2000]}' if code_context else ''}

Return ONLY a JSON object with three arrays:
{{
  "preconditions": ["predicate1", "predicate2"],
  "postconditions": ["predicate1", "predicate2"],
  "invariants": ["predicate1", "predicate2"]
}}

Predicate format examples:
  file_exists("src/auth/middleware.ts")
  test_exists("src/auth/__tests__/middleware.test.ts")
  symbol_count("src/auth/") <= 15
  function_signature("validateToken") == "(token: string) => Promise<User>"

Rules:
- Preconditions: what must exist before this change
- Postconditions: what must be true after this change is complete
- Invariants: what must NOT change during or after this change
- Be specific. Use file paths from the scope.
- 2-5 predicates per category max."""


def _parse_contract_response(response: str) -> dict[str, list[str]]:
    """Parse LLM response into contract dict."""
    # Try to extract JSON
    try:
        # Find JSON block
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            data = json.loads(response[start:end])
            return {
                'preconditions': data.get('preconditions', []),
                'postconditions': data.get('postconditions', []),
                'invariants': data.get('invariants', [])
            }
    except (json.JSONDecodeError, KeyError):
        pass
    return _empty_contracts()


def _empty_contracts() -> dict[str, list[str]]:
    return {'preconditions': [], 'postconditions': [], 'invariants': []}


def _guess_test_path(source_path: str) -> str | None:
    """Guess test file path from source path."""
    p = Path(source_path)
    stem = p.stem
    suffix = p.suffix

    # Python: test_foo.py
    if suffix == '.py':
        test_dir = p.parent / 'tests'
        return str(test_dir / f'test_{stem}.py')

    # TS/JS: foo.test.ts
    if suffix in ('.ts', '.tsx', '.js', '.jsx'):
        return str(p.parent / f'{stem}.test{suffix}')

    return None


def format_contracts(reason: ReasonNode) -> str:
    """Format contracts for human-readable display."""
    lines = []

    if reason.preconditions:
        lines.append('PRECONDITIONS:')
        for p in reason.preconditions:
            lines.append(f'  - {p}')

    if reason.postconditions:
        lines.append('POSTCONDITIONS:')
        for p in reason.postconditions:
            lines.append(f'  - {p}')

    if reason.invariants:
        lines.append('INVARIANTS:')
        for p in reason.invariants:
            lines.append(f'  - {p}')

    return '\n'.join(lines) if lines else '(no contracts defined)'
