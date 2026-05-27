"""SQLite-backed model calibration tracking."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS calibration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT NOT NULL,
    task_type TEXT NOT NULL,
    predicted REAL NOT NULL,
    actual REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_calibration_model
    ON calibration(model);
"""


@contextmanager
def _connect(path: Path) -> Iterator[sqlite3.Connection]:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class CalibrationTracker:
    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._init_db()

    def record(
        self, model: str, task_type: str, predicted: float, actual: float,
    ) -> None:
        with _connect(self._db_path) as conn:
            conn.execute(
                "INSERT INTO calibration (model, task_type, predicted, actual) "
                "VALUES (?, ?, ?, ?)",
                (model, task_type, predicted, actual),
            )
            conn.commit()

    def accuracy(self, model: str) -> float:
        errors = self._errors(model)
        if not errors:
            return 0.0
        score = sum(max(0.0, 1.0 - err) for err in errors) / len(errors)
        return round(score, 6)

    def calibration_error(self, model: str) -> float:
        errors = self._errors(model)
        if not errors:
            return 0.0
        return round(sum(errors) / len(errors), 6)

    def _errors(self, model: str) -> list[float]:
        with _connect(self._db_path) as conn:
            rows = conn.execute(
                "SELECT predicted, actual FROM calibration WHERE model = ?",
                (model,),
            ).fetchall()
        return [abs(row["predicted"] - row["actual"]) for row in rows]

    def _init_db(self) -> None:
        with _connect(self._db_path) as conn:
            conn.executescript(SCHEMA)
