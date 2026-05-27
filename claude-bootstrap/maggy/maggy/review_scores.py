"""Reviewer reward table — tracks reviewer performance by category.

SQLite-backed with time decay so old data ages out naturally.
Follows same pattern as scores.py for model rewards.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS review_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reviewer TEXT NOT NULL,
    category TEXT NOT NULL,
    score REAL NOT NULL,
    task_type TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_review_lookup
    ON review_scores(reviewer, category);
"""

MIN_SAMPLES = 3
DECAY_RATE = 0.95


@contextmanager
def _connect(path: Path) -> Iterator[sqlite3.Connection]:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class ReviewerTable:
    """SQLite-backed reviewer performance with time decay."""

    def __init__(self, db_path: Path):
        self._db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        with _connect(self._db_path) as conn:
            conn.executescript(SCHEMA)

    def record(
        self, reviewer: str, category: str,
        score: float, task_type: str,
    ) -> None:
        """Record a reviewer score observation."""
        now = datetime.now(timezone.utc).isoformat()
        with _connect(self._db_path) as conn:
            conn.execute(
                "INSERT INTO review_scores "
                "(reviewer, category, score, "
                "task_type, recorded_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (reviewer, category, score, task_type, now),
            )
            conn.commit()

    def best_reviewer(self, category: str) -> str | None:
        """Return best reviewer for category, or None."""
        with _connect(self._db_path) as conn:
            rows = conn.execute(
                "SELECT reviewer, score, recorded_at "
                "FROM review_scores WHERE category = ?",
                (category,),
            ).fetchall()
        if not rows:
            return None
        return _best_with_decay(rows)

    def heatmap(self) -> list[dict]:
        """Return reviewer × category averages."""
        with _connect(self._db_path) as conn:
            rows = conn.execute(
                "SELECT reviewer, category, "
                "AVG(score) as avg_score, "
                "COUNT(*) as n "
                "FROM review_scores "
                "GROUP BY reviewer, category",
            ).fetchall()
        return [
            {
                "reviewer": r["reviewer"],
                "category": r["category"],
                "avg_score": round(r["avg_score"], 3),
                "samples": r["n"],
            }
            for r in rows
        ]

    def compare(self) -> dict:
        """Side-by-side: {category: {reviewer: avg}}."""
        hm = self.heatmap()
        result: dict[str, dict[str, float]] = {}
        for entry in hm:
            cat = entry["category"]
            rev = entry["reviewer"]
            if cat not in result:
                result[cat] = {}
            result[cat][rev] = entry["avg_score"]
        return result


def _best_with_decay(rows) -> str | None:
    """Pick best reviewer using time-decayed scores."""
    scores: dict[str, tuple[float, int]] = {}
    today = date.today()
    for r in rows:
        rev = r["reviewer"]
        rec = datetime.fromisoformat(r["recorded_at"]).date()
        days = (today - rec).days
        weight = DECAY_RATE ** days
        weighted = r["score"] * weight
        total, count = scores.get(rev, (0.0, 0))
        scores[rev] = (total + weighted, count + 1)
    candidates = {
        r: total / count
        for r, (total, count) in scores.items()
        if count >= MIN_SAMPLES
    }
    if not candidates:
        return None
    return max(candidates, key=candidates.get)
