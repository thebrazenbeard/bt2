"""Local SQLite transaction owner for immutable MESO EventSequencer state.

No daemon, distributed locks, network path or authority for model effects.
"""
from __future__ import annotations

from contextlib import closing
from pathlib import Path
import sqlite3

from meso_crct import EventSequencer, EventIdentity


class DurableEventIssuer:
    """Serialize ownership of each (stream_id, sequence) on one local SQLite DB."""

    def __init__(self, database: Path):
        self.database = Path(database)
        if not self.database.parent.is_dir():
            raise ValueError("event ledger parent directory does not exist")
        with closing(sqlite3.connect(self.database, timeout=30)) as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS event_sequence ("
                "stream_id TEXT PRIMARY KEY, "
                "next_sequence INTEGER NOT NULL CHECK(next_sequence >= 1))"
            )
            connection.commit()

    def issue(self, stream_id: str) -> EventIdentity:
        # Validate with MESO's own immutable event contract first.
        EventSequencer(stream_id)
        with closing(sqlite3.connect(self.database, timeout=30, isolation_level=None)) as db:
            db.execute("PRAGMA busy_timeout=30000")
            db.execute("BEGIN IMMEDIATE")
            try:
                row = db.execute(
                    "SELECT next_sequence FROM event_sequence WHERE stream_id=?",
                    (stream_id,),
                ).fetchone()
                current = EventSequencer(
                    stream_id, next_sequence=1 if row is None else row[0]
                )
                successor, event = current.issue()
                db.execute(
                    "INSERT INTO event_sequence(stream_id,next_sequence) VALUES(?,?) "
                    "ON CONFLICT(stream_id) DO UPDATE SET next_sequence=excluded.next_sequence",
                    (stream_id, successor.next_sequence),
                )
                db.commit()
            except Exception:
                db.rollback()
                raise
        return event
