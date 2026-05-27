"""Token budget manager — tracks spend per provider with daily limits."""

from __future__ import annotations

import sqlite3
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from maggy.config import MaggyConfig


def _today_utc() -> str:
    return datetime.now(timezone.utc).date().isoformat()


@contextmanager
def _connect(path: Path) -> Iterator[sqlite3.Connection]:
    try:
        conn = _open_conn(path)
    except sqlite3.OperationalError:
        fallback = Path(tempfile.gettempdir()) / "maggy" / path.name
        conn = _open_conn(fallback)
    try:
        yield conn
    finally:
        conn.close()


def _open_conn(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.row_factory = sqlite3.Row
    return conn

SCHEMA = """
CREATE TABLE IF NOT EXISTS spend (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    cost_usd REAL NOT NULL,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    day TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_spend_day
    ON spend(day, provider);
"""


@dataclass(frozen=True)
class ProviderBudget:
    """Budget limit and preferred model for a provider."""

    provider: str
    daily_limit_usd: float
    model_preference: str


class TaskSpendTracker:
    """Track task-level spend and repeated edits."""

    def __init__(self, max_spend: float):
        self.max_spend = max_spend
        self._spent = 0.0
        self.files_edited: dict[str, int] = {}

    def record(self, cost: float) -> None:
        self._spent += cost

    def total(self) -> float:
        return self._spent

    def is_exceeded(self) -> bool:
        return self._spent >= self.max_spend

    def record_edit(self, file_path: str) -> None:
        count = self.files_edited.get(file_path, 0)
        self.files_edited[file_path] = count + 1

    def detect_loop(self, threshold: int = 3) -> list[str]:
        return [
            path for path, count in self.files_edited.items()
            if count >= threshold
        ]


class BudgetManager:
    """Track token spend per provider with daily limits."""

    def __init__(self, cfg: MaggyConfig):
        self.daily_limit = cfg.budget.daily_limit_usd
        self._plan = cfg.budget.plan
        self.providers = list(cfg.budget.providers)
        self._provider_budgets = {
            item.provider: item for item in self.providers
        }
        self.warning_threshold = cfg.budget.warning_threshold
        db_dir = Path(cfg.storage.path).expanduser().parent
        self._db_path = db_dir / "budget.db"
        self._init_db()

    def _init_db(self) -> None:
        with _connect(self._db_path) as conn:
            conn.executescript(SCHEMA)

    def record_spend(
        self, provider: str, model: str, cost_usd: float,
        input_tokens: int = 0, output_tokens: int = 0,
    ) -> None:
        now = datetime.now(timezone.utc)
        with _connect(self._db_path) as conn:
            conn.execute(
                "INSERT INTO spend "
                "(provider,model,cost_usd,input_tokens,output_tokens,day,created_at) "
                "VALUES (?,?,?,?,?,?,?)",
                (provider, model, cost_usd, input_tokens, output_tokens,
                 now.date().isoformat(), now.isoformat()),
            )
            conn.commit()

    def today_spend(self, provider: str | None = None) -> float:
        today = _today_utc()
        sql = "SELECT COALESCE(SUM(cost_usd),0) FROM spend WHERE day=?"
        params: list = [today]
        if provider:
            sql += " AND provider=?"
            params.append(provider)
        with _connect(self._db_path) as conn:
            row = conn.execute(sql, params).fetchone()
        return float(row[0])

    def today_tokens(self, provider: str | None = None) -> dict:
        today = _today_utc()
        sql = ("SELECT COALESCE(SUM(input_tokens),0),"
               "COALESCE(SUM(output_tokens),0) FROM spend WHERE day=?")
        params: list = [today]
        if provider:
            sql += " AND provider=?"
            params.append(provider)
        with _connect(self._db_path) as conn:
            row = conn.execute(sql, params).fetchone()
        return {"input": int(row[0]), "output": int(row[1])}

    def budget_status(self) -> dict:
        spent = self.today_spend()
        ratio = spent / self.daily_limit if self.daily_limit > 0 else 0
        status = "exhausted" if ratio >= 1.0 else (
            "warning" if ratio >= self.warning_threshold else "ok")
        tokens = self.today_tokens()
        return {
            "spent_today_usd": round(spent, 4),
            "daily_limit_usd": self.daily_limit,
            "utilization": round(ratio, 3),
            "status": status,
            "plan": self._plan,
            "input_tokens": tokens["input"],
            "output_tokens": tokens["output"],
        }

    def by_provider(self) -> list[dict]:
        today = _today_utc()
        with _connect(self._db_path) as conn:
            rows = conn.execute(
                "SELECT provider, SUM(cost_usd) as total "
                "FROM spend WHERE day=? GROUP BY provider",
                (today,),
            ).fetchall()
        return [
            {"provider": r["provider"], "spent_usd": round(r["total"], 4)}
            for r in rows
        ]

    def is_exhausted(
        self, provider: str | None = None,
    ) -> bool:
        """Check if daily budget is exhausted."""
        spent = self.today_spend(provider)
        return spent >= self.daily_limit

    def is_provider_exhausted(self, provider: str) -> bool:
        """Check provider-specific budget when configured."""
        budget = self._provider_budgets.get(provider)
        if budget is None:
            return self.is_exhausted(provider)
        return self.today_spend(provider) >= budget.daily_limit_usd

    def cheapest_available(self) -> str | None:
        """Return preferred model for the first provider with budget left."""
        for budget in self.providers:
            if not self.is_provider_exhausted(budget.provider):
                return budget.model_preference
        return None
