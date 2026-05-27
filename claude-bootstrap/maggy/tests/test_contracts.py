"""Tests for contract generation."""

from __future__ import annotations

from maggy.contracts import ContractGenerator


def test_generates_test_code_from_postcondition() -> None:
    generator = ContractGenerator()

    code = generator.from_postcondition(
        "returns sorted results",
        "maggy.services.planner.DualPlanner.plan",
    )

    assert "returns sorted results" in code
    assert "DualPlanner.plan" in code
    assert "def test_dualplanner_plan_contract()" in code
