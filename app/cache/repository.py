"""Repositories over the SQLite cache."""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.cache.db import SCHEMA_VERSION, connect, init_db


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CachedResponse:
    provider: str
    fetched_at: datetime
    status: str
    latency_ms: int
    raw: dict | None


class VinCacheRepository:
    def __init__(self, db_path: str, response_ttl_days: int = 30) -> None:
        self.db_path = db_path
        self.response_ttl = timedelta(days=response_ttl_days)
        init_db(db_path)

    def fresh_responses(self, vin: str) -> dict[str, CachedResponse]:
        """Cached provider responses younger than the TTL, keyed by provider."""
        cutoff = datetime.now(timezone.utc) - self.response_ttl
        with connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT provider, fetched_at, status, latency_ms, raw_json "
                "FROM provider_responses WHERE vin = ?",
                (vin,),
            ).fetchall()
        fresh: dict[str, CachedResponse] = {}
        for row in rows:
            fetched_at = datetime.fromisoformat(row["fetched_at"])
            if fetched_at < cutoff or row["status"] != "ok":
                continue
            fresh[row["provider"]] = CachedResponse(
                provider=row["provider"],
                fetched_at=fetched_at,
                status=row["status"],
                latency_ms=row["latency_ms"] or 0,
                raw=json.loads(row["raw_json"]) if row["raw_json"] else None,
            )
        return fresh

    def save_response(self, vin: str, provider: str, status: str,
                      latency_ms: int, raw: dict | None) -> None:
        with connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO provider_responses "
                "(vin, provider, fetched_at, status, latency_ms, raw_json) "
                "VALUES (?, ?, ?, ?, ?, ?) "
                "ON CONFLICT (vin, provider) DO UPDATE SET "
                "fetched_at = excluded.fetched_at, status = excluded.status, "
                "latency_ms = excluded.latency_ms, raw_json = excluded.raw_json",
                (vin, provider, _now(), status, latency_ms,
                 json.dumps(raw) if raw is not None else None),
            )

    def record_lookup(self, vin: str, make: str | None, model: str | None,
                      year: int | None, confidence: float | None,
                      bucket: str | None) -> None:
        with connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO vin_lookups (vin, first_seen_at, last_seen_at, hit_count, "
                "make, model, year, confidence, confidence_bucket, schema_version) "
                "VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT (vin) DO UPDATE SET "
                "last_seen_at = excluded.last_seen_at, "
                "hit_count = vin_lookups.hit_count + 1, "
                "make = excluded.make, model = excluded.model, year = excluded.year, "
                "confidence = excluded.confidence, "
                "confidence_bucket = excluded.confidence_bucket, "
                "schema_version = excluded.schema_version",
                (vin, _now(), _now(), make, model, year, confidence, bucket,
                 SCHEMA_VERSION),
            )

    def recent_lookups(self, limit: int = 10) -> list[dict]:
        with connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT vin, last_seen_at, hit_count, make, model, year, "
                "confidence, confidence_bucket FROM vin_lookups "
                "ORDER BY last_seen_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]


class CatalogCacheRepository:
    def __init__(self, db_path: str, ttl_days: int = 7) -> None:
        self.db_path = db_path
        self.ttl = timedelta(days=ttl_days)
        init_db(db_path)

    def get(self, key: str) -> dict | list | None:
        cutoff = datetime.now(timezone.utc) - self.ttl
        with connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT payload_json, fetched_at FROM catalog_cache WHERE cache_key = ?",
                (key,),
            ).fetchone()
        if row is None:
            return None
        if datetime.fromisoformat(row["fetched_at"]) < cutoff:
            return None
        return json.loads(row["payload_json"])

    def put(self, key: str, payload: dict | list) -> None:
        with connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO catalog_cache (cache_key, payload_json, fetched_at) "
                "VALUES (?, ?, ?) "
                "ON CONFLICT (cache_key) DO UPDATE SET "
                "payload_json = excluded.payload_json, fetched_at = excluded.fetched_at",
                (key, json.dumps(payload), _now()),
            )
