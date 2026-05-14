"""SQLite database init and connection."""

from __future__ import annotations

import sqlite3
from pathlib import Path

_DB_DIR = Path.home() / ".local" / "share" / "mystic-pet"
_DB_PATH = _DB_DIR / "mystic.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    question TEXT,
    cards TEXT,
    reading TEXT,
    model TEXT
);

CREATE TABLE IF NOT EXISTS settings_kv (
    k TEXT PRIMARY KEY,
    v TEXT
);
"""


def connect() -> sqlite3.Connection:
    _DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.executescript(_SCHEMA)
    return conn


def db_path() -> Path:
    return _DB_PATH
