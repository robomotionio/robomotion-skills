"""Two-tier Lexon router — fast keyword + fallback LLM."""

from __future__ import annotations

from .disambiguate import disambiguate
from .personalization import PersonalizationEngine
from .record import LexonRecord
from .terminology import TerminologyMap

CONFIDENCE_THRESHOLD = 0.82
TOP2_GAP = 0.15
DEFAULT_TOOL_MANIFEST = {
    "deploy": ["vercel_deploy", "docker_push"],
    "test": ["pytest", "vitest", "jest"],
    "fix": ["code_edit", "patch"],
    "create": ["file_create", "scaffold"],
    "delete": ["file_delete", "cleanup"],
    "update": ["code_edit", "config_update"],
    "search": ["grep", "glob", "find"],
    "review": ["code_review", "pr_review"],
}


class LexonRouter:
    """Routes user phrases to tools using two tiers.

    Tier 1: Fast keyword/terminology lookup
    Tier 2: LLM-based intent classification (stub)
    """

    def __init__(self, config: dict[str, object] | None = None):
        self._config = config or {}
        self._terms = TerminologyMap()
        self._personal = PersonalizationEngine()
        self._tool_map = self._load_tool_manifest()

    def route(self, phrase: str) -> LexonRecord:
        """Route a phrase to a tool."""
        preferred = self._personal.get_preferred(phrase)
        if preferred:
            return LexonRecord(
                phrase=phrase,
                resolved_tool=preferred,
                confidence=0.95,
                candidates=[preferred],
            )
        tier1 = self._route_tier1(phrase)
        if tier1:
            return tier1
        return self._llm_classify(phrase)

    def learn(self, phrase: str, tool: str) -> None:
        """Record a confirmed tool selection."""
        self._personal.record_use(tool)
        self._personal.record_alias(phrase, tool)

    @property
    def terminology(self) -> TerminologyMap:
        return self._terms

    @property
    def personalization(self) -> PersonalizationEngine:
        return self._personal

    def _load_tool_manifest(self) -> dict[str, list[str]]:
        manifest = self._config.get("tool_manifest", DEFAULT_TOOL_MANIFEST)
        if not isinstance(manifest, dict):
            return dict(DEFAULT_TOOL_MANIFEST)
        return {
            str(key): [str(item) for item in value]
            for key, value in manifest.items()
            if isinstance(value, list)
        } or dict(DEFAULT_TOOL_MANIFEST)

    def _llm_classify(self, phrase: str) -> LexonRecord:
        return LexonRecord(
            phrase=phrase,
            confidence=0.55,
            disambiguation_mode="llm",
        )

    def _route_tier1(self, phrase: str) -> LexonRecord | None:
        for word in phrase.lower().split():
            canonical = self._terms.resolve(word)
            if canonical and canonical in self._tool_map:
                return self._resolve_manifest_match(phrase, self._tool_map[canonical])
        return None

    def _resolve_manifest_match(
        self,
        phrase: str,
        candidates: list[str],
    ) -> LexonRecord:
        confidence = self._keyword_confidence(candidates)
        if confidence < CONFIDENCE_THRESHOLD:
            return self._llm_classify(phrase)
        if self._top2_gap(candidates) < TOP2_GAP:
            return self._llm_classify(phrase)
        result = disambiguate(confidence, candidates)
        return LexonRecord(
            phrase=phrase,
            resolved_tool=result.tool if result.resolved else "",
            confidence=confidence,
            candidates=candidates,
            disambiguation_mode=result.mode,
        )

    def _keyword_confidence(self, candidates: list[str]) -> float:
        if len(candidates) == 1:
            return 0.9
        if len(candidates) == 2:
            return 0.84
        return 0.8

    def _top2_gap(self, candidates: list[str]) -> float:
        if len(candidates) <= 1:
            return 1.0
        if len(candidates) == 2:
            return 0.18
        return 0.1
