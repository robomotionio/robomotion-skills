"""Project-aware competitor intelligence — per-project competitor tracking.

Auto-discovers competitors, tracks their moves via X/Reddit/Grok,
surfaces insights through the Maggy dashboard.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Competitor:
    name: str
    domain: str  # memory_management, dynamic_routing, autonomous_sdlc, etc.
    x_handle: str = ""
    website: str = ""
    last_sighting: str = ""
    signals: list[dict] = field(default_factory=list)
    threat_level: str = "low"  # low, medium, high


@dataclass
class CompetitorMove:
    competitor: str
    ts: str
    type: str  # launch, funding, hire, feature, pricing, blog
    summary: str
    source: str  # x, reddit, grok
    url: str = ""


# Base competitor definitions per project type
PROJECT_COMPETITORS = {
    "maggy": {
        "memory_management": [
            {"name": "Mem0", "x_handle": "@mem0ai", "website": "mem0.ai"},
            {"name": "Letta/MemGPT", "x_handle": "@letta_ai", "website": "letta.ai"},
            {"name": "Pinecone Assistant", "x_handle": "@pinecone", "website": "pinecone.io"},
            {"name": "Zep", "x_handle": "@getzep", "website": "getzep.com"},
            {"name": "Cognee", "x_handle": "@cognee_ai", "website": "cognee.ai"},
        ],
        "dynamic_routing": [
            {"name": "Martian", "x_handle": "@martianai", "website": "withmartian.com"},
            {"name": "OpenRouter", "x_handle": "@OpenRouterAI", "website": "openrouter.ai"},
            {"name": "Portkey", "x_handle": "@portkeyai", "website": "portkey.ai"},
            {"name": "Not Diamond", "x_handle": "@notdiamondai", "website": "notdiamond.ai"},
            {"name": "Semantic Router", "x_handle": "@AurelioAI", "website": "aurelio.ai"},
        ],
        "autonomous_sdlc": [
            {"name": "Devin/Cognition", "x_handle": "@cognition_labs", "website": "cognition.ai"},
            {"name": "Factory AI", "x_handle": "@factory_ai", "website": "factory.ai"},
            {"name": "Cosine Genie", "x_handle": "@cosine_ai", "website": "cosine.sh"},
            {"name": "OpenHands", "x_handle": "@allhands_ai", "website": "allhands.dev"},
            {"name": "Pythagora", "x_handle": "@pythagora_ai", "website": "pythagora.ai"},
        ],
    },
    "chessiega": {
        "chess_platforms": [
            {"name": "Chess.com", "x_handle": "@chesscom", "website": "chess.com"},
            {"name": "Lichess", "x_handle": "@lichess", "website": "lichess.org"},
        ],
        "ai_chess": [
            {"name": "Leela Chess Zero", "x_handle": "@LeelaChessZero", "website": "lczero.org"},
            {"name": "Stockfish", "x_handle": "@stockfishchess", "website": "stockfishchess.org"},
        ],
    },
    "edubites": {
        "edtech": [
            {"name": "Duolingo", "x_handle": "@duolingo", "website": "duolingo.com"},
            {"name": "Khan Academy", "x_handle": "@khanacademy", "website": "khanacademy.org"},
            {"name": "Coursera", "x_handle": "@coursera", "website": "coursera.org"},
        ],
    },
}


class CompetitorIntel:
    """Per-project competitor intelligence engine."""

    def __init__(self, project: str = "maggy"):
        self._project = project
        self._competitors = self._load_competitors()
        self._moves = self._load_moves()
        self._briefings = self._load_briefings()

    def _data_dir(self) -> Path:
        d = Path.home() / ".maggy" / "competitors" / self._project
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _load_competitors(self) -> list[Competitor]:
        path = self._data_dir() / "competitors.json"
        if path.exists():
            try:
                return [Competitor(**c) for c in json.loads(path.read_text())]
            except Exception:
                pass
        # Seed from defaults
        defaults = PROJECT_COMPETITORS.get(self._project, {})
        competitors = []
        for domain, entries in defaults.items():
            for entry in entries:
                competitors.append(Competitor(
                    name=entry["name"], domain=domain,
                    x_handle=entry.get("x_handle", ""),
                    website=entry.get("website", ""),
                ))
        self._save_competitors(competitors)
        return competitors

    def _save_competitors(self, competitors: list[Competitor]):
        path = self._data_dir() / "competitors.json"
        path.write_text(json.dumps([c.__dict__ for c in competitors], indent=2, default=str))

    def _load_moves(self) -> list[CompetitorMove]:
        path = self._data_dir() / "moves.jsonl"
        if not path.exists():
            return []
        moves = []
        for line in path.read_text().strip().split("\n"):
            try:
                moves.append(CompetitorMove(**json.loads(line)))
            except Exception:
                pass
        return moves[-100:]

    def _load_briefings(self) -> list[dict]:
        path = self._data_dir() / "briefings.json"
        try:
            return json.loads(path.read_text())
        except Exception:
            return []

    def get_competitors(self) -> list[dict]:
        """Get all tracked competitors for this project."""
        return [
            {
                "name": c.name, "domain": c.domain,
                "x_handle": c.x_handle, "website": c.website,
                "last_sighting": c.last_sighting,
                "signal_count": len(c.signals),
                "threat_level": c.threat_level,
            }
            for c in self._competitors
        ]

    def get_moves(self, limit: int = 20) -> list[dict]:
        """Get recent competitor moves."""
        return [m.__dict__ for m in self._moves[-limit:]]

    def get_briefing(self) -> dict:
        """Get latest AI-generated competitor briefing."""
        if self._briefings:
            return self._briefings[-1]
        return {"project": self._project, "generated_at": "", "summary": "No briefing generated yet. Run competitor scan."}

    def record_move(self, competitor: str, move_type: str,
                    summary: str, source: str = "unknown", url: str = "") -> CompetitorMove:
        """Record a competitor's move."""
        move = CompetitorMove(
            competitor=competitor,
            ts=datetime.now(timezone.utc).isoformat(),
            type=move_type, summary=summary, source=source, url=url,
        )
        self._moves.append(move)

        # Update competitor last_sighting
        for c in self._competitors:
            if c.name.lower() == competitor.lower():
                c.last_sighting = move.ts
                c.signals.append({"ts": move.ts, "type": move_type, "summary": summary[:200]})
                c.signals = c.signals[-20:]
                break

        # Persist
        path = self._data_dir() / "moves.jsonl"
        with path.open("a") as f:
            f.write(json.dumps(move.__dict__, default=str) + "\n")
        self._save_competitors(self._competitors)

        return move

    def discover_competitors(self) -> list[dict]:
        """Use Grok to auto-discover new competitors in this project's space."""
        # This would call the Grok API to find similar companies
        # For now, return seed data + any manually added
        return self.get_competitors()

    def add_competitor(self, name: str, domain: str,
                       x_handle: str = "", website: str = "") -> Competitor:
        """Manually add a competitor to track."""
        c = Competitor(name=name, domain=domain, x_handle=x_handle, website=website)
        self._competitors.append(c)
        self._save_competitors(self._competitors)
        return c

    def scan_moves(self) -> list[CompetitorMove]:
        """Scan X/Reddit for recent competitor activity."""
        new_moves = []

        # For each tracked competitor, search X for recent mentions
        for comp in self._competitors[:10]:  # Limit per scan
            if not comp.x_handle:
                continue
            # Note: actual API calls delegated to SocialMonitor
            # This records that we WOULD scan — real scanning requires async
            logger.info("CompetitorIntel: would scan %s (%s)", comp.name, comp.x_handle)

        # Generate a briefing if we found moves
        if new_moves:
            self._generate_briefing()

        return new_moves

    def _generate_briefing(self) -> dict:
        """Generate a competitor briefing via AI."""
        recent = [m.__dict__ for m in self._moves[-10:]]
        if not recent:
            return {"summary": "No recent competitor activity."}

        # In production, this calls Grok/DeepSeek to synthesize
        summary = f"Tracked {len(self._competitors)} competitors. {len(recent)} recent moves."
        domains = {}
        for m in self._moves[-20:]:
            domains[m.type] = domains.get(m.type, 0) + 1
        top_activity = max(domains, key=domains.get) if domains else "none"

        briefing = {
            "project": self._project,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "competitors_tracked": len(self._competitors),
            "recent_moves": len(recent),
            "top_activity_type": top_activity,
            "summary": summary,
            "latest_moves": [
                {"competitor": m.competitor, "type": m.type, "summary": m.summary[:200]}
                for m in self._moves[-5:]
            ],
        }

        self._briefings.append(briefing)
        self._briefings = self._briefings[-50:]
        path = self._data_dir() / "briefings.json"
        path.write_text(json.dumps(self._briefings, indent=2, default=str))

        return briefing
