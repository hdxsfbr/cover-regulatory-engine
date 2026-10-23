"""Transactional local records; immutable revisions retain evidence and rule identities."""

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from backend.gis import ROOT, now


def database():
    return Path(os.getenv("COVER_DATABASE", str(ROOT / "data/workspace.sqlite3")))


@contextmanager
def transaction():
    path = database()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    try:
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA journal_mode=WAL")
        db.executescript("""
          CREATE TABLE IF NOT EXISTS migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY, kind TEXT NOT NULL, parent TEXT, created_at TEXT NOT NULL, data TEXT NOT NULL);
          CREATE INDEX IF NOT EXISTS record_parent ON records(kind,parent);
          CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, cache_key TEXT UNIQUE NOT NULL, status TEXT NOT NULL, stage TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, payload TEXT NOT NULL, result TEXT, error TEXT);
        """)
        db.execute("INSERT OR IGNORE INTO migrations VALUES(1,?)", (now(),))
        yield db
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()


def put(kind, data, parent=None, identity=None, db=None):
    identity = identity or str(uuid.uuid4())
    if db is None:
        with transaction() as connection:
            return put(kind, data, parent, identity, connection)
    db.execute(
        "INSERT INTO records VALUES(?,?,?,?,?)",
        (identity, kind, parent, now(), json.dumps(data, allow_nan=False)),
    )
    return identity


def get(identity, kind=None):
    with transaction() as db:
        row = db.execute("SELECT * FROM records WHERE id=?", (identity,)).fetchone()
    if not row or (kind and row["kind"] != kind):
        raise KeyError("Record not found")
    return {**dict(row), "data": json.loads(row["data"])}


def listing(kind, parent=None):
    with transaction() as db:
        rows = db.execute(
            "SELECT * FROM records WHERE kind=? AND (? IS NULL OR parent=?) ORDER BY created_at DESC",
            (kind, parent, parent),
        ).fetchall()
    return [{**dict(row), "data": json.loads(row["data"])} for row in rows]


def import_existing():
    """Index immutable originals without copying or rewriting their bytes."""
    import hashlib

    paths = (
        list((ROOT / "data/sources/regulations").glob("*.json"))
        + list((ROOT / "data/rules/versions").glob("*.json"))
        + list((ROOT / "data/parcel-evidence").glob("*.pdf"))
    )
    count = 0
    with transaction() as db:
        for path in paths:
            content_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            identity = "artifact:" + content_hash
            if db.execute("SELECT 1 FROM records WHERE id=?", (identity,)).fetchone():
                continue
            put(
                "artifact",
                {
                    "path": str(path.relative_to(ROOT)),
                    "sha256": content_hash,
                    "bytes": path.stat().st_size,
                },
                identity=identity,
                db=db,
            )
            count += 1
    return count


if __name__ == "__main__":
    print(json.dumps({"imported": import_existing(), "database": str(database())}))
