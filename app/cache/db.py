"""SQLite connection handling and schema.

Plain sqlite3 with WAL mode; connections are short lived and per call, which
keeps multi-worker gunicorn safe at this scale.
"""

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS vin_lookups (
    vin TEXT PRIMARY KEY,
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    hit_count INTEGER NOT NULL DEFAULT 1,
    make TEXT,
    model TEXT,
    year INTEGER,
    confidence REAL,
    confidence_bucket TEXT,
    schema_version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_responses (
    vin TEXT NOT NULL,
    provider TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    status TEXT NOT NULL,
    latency_ms INTEGER,
    raw_json TEXT,
    PRIMARY KEY (vin, provider)
);

CREATE TABLE IF NOT EXISTS catalog_cache (
    cache_key TEXT PRIMARY KEY,
    payload_json TEXT NOT NULL,
    fetched_at TEXT NOT NULL
);
"""

# Bump when consensus logic changes enough that cached summaries mislead.
SCHEMA_VERSION = 1


def connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_db(db_path: str) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
