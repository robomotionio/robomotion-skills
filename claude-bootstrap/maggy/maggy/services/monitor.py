"""MonitorService — background polling for issue trackers."""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
MONDAY_API = "https://api.monday.com/v2"


@dataclass
class MonitorConfig:
    """Config for a single project monitor."""

    project_key: str
    provider: str  # "github" | "asana" | "monday"
    poll_command: str = ""
    interval_seconds: int = 300
    enabled: bool = True


@dataclass
class MonitorEvent:
    """A detected new item from a tracker."""

    id: str
    title: str
    url: str
    provider: str
    project_key: str
    seen_at: str = ""


class MonitorService:
    """SQLite-backed tracker polling service."""

    def __init__(self, db_path: Path) -> None:
        self._db = sqlite3.connect(str(db_path))
        self._init_tables()

    def _init_tables(self) -> None:
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS monitors (
                project_key TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                poll_command TEXT DEFAULT '',
                interval_seconds INTEGER DEFAULT 300,
                enabled INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS seen_events (
                event_id TEXT,
                project_key TEXT,
                seen_at TEXT,
                PRIMARY KEY (event_id, project_key)
            );
        """)

    def add(self, cfg: MonitorConfig) -> None:
        self._db.execute(
            "INSERT OR REPLACE INTO monitors VALUES (?,?,?,?,?)",
            (cfg.project_key, cfg.provider, cfg.poll_command,
             cfg.interval_seconds, int(cfg.enabled)),
        )
        self._db.commit()

    def remove(self, project_key: str) -> None:
        self._db.execute(
            "DELETE FROM monitors WHERE project_key=?",
            (project_key,),
        )
        self._db.commit()

    def list_active(self) -> list[MonitorConfig]:
        rows = self._db.execute(
            "SELECT * FROM monitors WHERE enabled=1",
        ).fetchall()
        return [_row_to_config(r) for r in rows]

    def is_new(self, event_id: str, project_key: str) -> bool:
        row = self._db.execute(
            "SELECT 1 FROM seen_events WHERE event_id=? AND project_key=?",
            (event_id, project_key),
        ).fetchone()
        return row is None

    def mark_seen(self, event_id: str, project_key: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._db.execute(
            "INSERT OR IGNORE INTO seen_events VALUES (?,?,?)",
            (event_id, project_key, now),
        )
        self._db.commit()

    def status(self) -> dict:
        active = len(self.list_active())
        total = self._db.execute(
            "SELECT COUNT(*) FROM seen_events",
        ).fetchone()[0]
        return {"active": active, "seen_events": total}

    async def poll(self, cfg: MonitorConfig) -> list[MonitorEvent]:
        """Poll tracker and return new events."""
        if cfg.provider == "github":
            return await _poll_github(self, cfg)
        if cfg.provider == "monday":
            return await _poll_monday(self, cfg)
        return []


def _row_to_config(row: tuple) -> MonitorConfig:
    return MonitorConfig(
        project_key=row[0], provider=row[1],
        poll_command=row[2], interval_seconds=row[3],
        enabled=bool(row[4]),
    )


async def _poll_github(svc: MonitorService, cfg: MonitorConfig) -> list[MonitorEvent]:
    repo = cfg.poll_command or ""
    if not repo:
        return []
    events: list[MonitorEvent] = []
    async with httpx.AsyncClient(timeout=15) as client:
        url = f"{GITHUB_API}/repos/{repo}/pulls"
        resp = await client.get(url, params={"state": "open"})
        if resp.status_code != 200:
            return []
        for pr in resp.json():
            eid = f"gh-pr-{pr.get('number', '')}"
            if svc.is_new(eid, cfg.project_key):
                events.append(MonitorEvent(
                    id=eid, title=pr.get("title", ""),
                    url=pr.get("html_url", ""),
                    provider="github",
                    project_key=cfg.project_key,
                ))
                svc.mark_seen(eid, cfg.project_key)
    return events


async def _poll_monday(svc: MonitorService, cfg: MonitorConfig) -> list[MonitorEvent]:
    board_id = cfg.poll_command or ""
    if not board_id:
        return []
    events: list[MonitorEvent] = []
    query = f'{{ boards(ids: [{board_id}]) {{ items_page(limit: 20) {{ items {{ id name }} }} }} }}'
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            MONDAY_API,
            json={"query": query},
        )
        if resp.status_code != 200:
            return []
        boards = resp.json().get("data", {}).get("boards", [])
        if not boards:
            return []
        items = boards[0].get("items_page", {}).get("items", [])
        for item in items:
            eid = f"mon-{item.get('id', '')}"
            if svc.is_new(eid, cfg.project_key):
                events.append(MonitorEvent(
                    id=eid, title=item.get("name", ""),
                    url="", provider="monday",
                    project_key=cfg.project_key,
                ))
                svc.mark_seen(eid, cfg.project_key)
    return events
