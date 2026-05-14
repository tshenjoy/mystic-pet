"""Reading log: insert and query past tarot readings."""

from __future__ import annotations

import json
from datetime import datetime, timedelta

from persistence.db import connect


def log_reading(question: str, cards: list[dict], reading: str, model: str) -> int:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO readings (question, cards, reading, model) VALUES (?, ?, ?, ?)",
            (question, json.dumps(cards), reading, model),
        )
        return cur.lastrowid


def count_readings_today() -> int:
    cutoff = (datetime.utcnow() - timedelta(hours=24)).isoformat(sep=" ")
    with connect() as conn:
        cur = conn.execute(
            "SELECT COUNT(*) FROM readings WHERE ts >= ?", (cutoff,)
        )
        return cur.fetchone()[0]


def recent_readings(limit: int = 20) -> list[dict]:
    with connect() as conn:
        cur = conn.execute(
            "SELECT id, ts, question, cards, reading, model "
            "FROM readings ORDER BY ts DESC LIMIT ?",
            (limit,),
        )
        return [
            {
                "id": r[0],
                "ts": r[1],
                "question": r[2],
                "cards": json.loads(r[3]) if r[3] else [],
                "reading": r[4],
                "model": r[5],
            }
            for r in cur.fetchall()
        ]
