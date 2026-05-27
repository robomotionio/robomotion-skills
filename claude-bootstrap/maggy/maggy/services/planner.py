"""Dual-model planning service."""

from __future__ import annotations

from dataclasses import dataclass, field

from maggy.adapters.pi import PiAdapter, RunResult


@dataclass
class PlanResult:
    primary_plan: str
    counter_check: str
    conflicts: list[str] = field(default_factory=list)


class DualPlanner:
    def __init__(self, pi: PiAdapter):
        self._pi = pi

    async def plan(
        self, task_title: str, task_desc: str, wd: str,
    ) -> str:
        prompt = _plan_prompt(task_title, task_desc)
        return await self._send("claude", prompt, wd)

    async def counter_check(self, plan_text: str, wd: str) -> str:
        prompt = _review_prompt(plan_text)
        return await self._send("codex", prompt, wd)

    async def dual_plan(
        self, task_title: str, task_desc: str, wd: str,
    ) -> PlanResult:
        primary = await self.plan(task_title, task_desc, wd)
        review = await self.counter_check(primary, wd)
        return PlanResult(primary, review, _conflicts(review))

    async def _send(self, model: str, prompt: str, wd: str) -> str:
        result = await self._pi.send_prompt(model, prompt, wd, 5)
        return _result_text(result, model)


def _plan_prompt(task_title: str, task_desc: str) -> str:
    return (
        "Create an implementation plan.\n"
        "Return numbered steps, files to touch, risks, and tests.\n\n"
        f"Title: {task_title}\n"
        f"Description: {task_desc}"
    )


def _review_prompt(plan_text: str) -> str:
    return (
        "Review this implementation plan.\n"
        "Flag conflicts as 'CONFLICT:' and keep the note short.\n"
        "Call out risky omissions and invalid assumptions.\n\n"
        f"Plan:\n{plan_text}"
    )


def _result_text(result: RunResult, model: str) -> str:
    if result.success:
        return result.output.strip()
    message = result.output or result.error
    raise RuntimeError((message or f"{model} planning failed").strip())


def _conflicts(text: str) -> list[str]:
    return [
        line.partition(":")[2].strip()
        for line in text.splitlines()
        if line.upper().startswith("CONFLICT:")
    ]
