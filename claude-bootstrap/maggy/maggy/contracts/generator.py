"""Generate lightweight contract tests from postconditions."""

from __future__ import annotations

import re


class ContractGenerator:
    def from_postcondition(self, postcondition: str, symbol: str) -> str:
        test_name = _test_name(symbol)
        return (
            f"def {test_name}() -> None:\n"
            f'    """Contract for {symbol}."""\n'
            f"    # Postcondition: {postcondition}\n"
            f"    raise NotImplementedError("
            f"\"Verify: {postcondition}\")\n"
        )


def _test_name(symbol: str) -> str:
    short = symbol.split(".")[-2:]
    slug = "_".join(short).lower()
    slug = re.sub(r"[^a-z0-9_]+", "_", slug)
    return f"test_{slug}_contract"
