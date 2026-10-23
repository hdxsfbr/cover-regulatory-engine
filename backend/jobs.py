"""One bounded local worker; durable states survive API restarts."""

import hashlib
import json
import threading
import time
import uuid
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from backend import store, evidence, extraction, lot_depth
from backend.gis import now

POOL = ThreadPoolExecutor(max_workers=1, thread_name_prefix="evidence")
LOCK = threading.Lock()
STARTED = False
TERMINAL = {"completed", "failed", "cancelled"}


def read(identity):
    with store.transaction() as db:
        row = db.execute("SELECT * FROM jobs WHERE id=?", (identity,)).fetchone()
    if not row:
        raise KeyError("Job not found")
    result = dict(row)
    if (
        result["status"] in ("queued", "running")
        and (
            datetime.now(timezone.utc) - datetime.fromisoformat(result["created_at"])
        ).total_seconds()
        > 240
    ):
        update(identity, "failed", "expired", error="Queue time budget exceeded; retry")
        result.update(
            status="failed", stage="expired", error="Queue time budget exceeded; retry"
        )
    for key in ("payload", "result"):
        result[key] = json.loads(result[key]) if result[key] else None
    return result


def update(identity, status, stage, result=None, error=None):
    with store.transaction() as db:
        db.execute(
            "UPDATE jobs SET status=?,stage=?,result=?,error=?,updated_at=? WHERE id=? AND status NOT IN ('completed','cancelled','failed')",
            (
                status,
                stage,
                json.dumps(result) if result is not None else None,
                error,
                now(),
                identity,
            ),
        )


def cancel(identity):
    read(identity)
    update(identity, "cancelled", "cancelled")
    return read(identity)


def work(identity):
    job = read(identity)
    if job["status"] != "queued":
        return
    started = time.monotonic()
    queued_seconds = (
        datetime.now(timezone.utc) - datetime.fromisoformat(job["created_at"])
    ).total_seconds()
    cancelled = lambda: read(identity)["status"] in ("cancelled", "failed")
    watchdog = threading.Timer(
        max(0, 240 - queued_seconds),
        lambda: update(
            identity, "failed", "expired", error="Job exceeded 240 seconds; retry"
        ),
    )
    watchdog.daemon = True
    watchdog.start()

    def stage(name):
        if cancelled():
            raise ValueError("Cancelled")
        if time.monotonic() - started + queued_seconds > 240:
            raise TimeoutError("Evidence job exceeded 240 seconds")
        update(identity, "running", name)

    try:
        stage("starting")
        if job["payload"].get("kind") == "source-refresh":
            from backend.ingest import snapshot
            from backend.rules import ROOT

            stage("fetching-source")
            result = {
                "changed": snapshot(
                    job["payload"]["section"],
                    ROOT / "data/rules/unused.json",
                    extract_candidate=False,
                )
            }
        elif job["payload"].get("kind") == "rule-extraction":
            from backend.synthesis import extract

            stage("extracting-rules")
            result = extract(
                job["payload"]["sources"],
                job["payload"]["scope"],
                cancelled,
                timeout=max(1, min(175, 230 - queued_seconds)),
            )
        else:
            result = extraction.extract(
                job["payload"],
                stage,
                cancelled,
                timeout=max(1, min(230, 230 - queued_seconds)),
            )
        stage("saving")
        update(
            identity,
            "completed",
            "completed",
            result={**result, "elapsed_seconds": time.monotonic() - started},
        )
    except Exception as error:
        update(identity, "failed", "failed", error=str(error)[:1000])
    finally:
        watchdog.cancel()


def recover():
    global STARTED
    with LOCK:
        if STARTED:
            return
        with store.transaction() as db:
            db.execute(
                "UPDATE jobs SET status='failed',stage='interrupted',error='Worker restarted; retry this job',updated_at=? WHERE status='running'",
                (now(),),
            )
            queued = [
                r["id"] for r in db.execute("SELECT id FROM jobs WHERE status='queued'")
            ]
        for identity in queued:
            POOL.submit(work, identity)
        STARTED = True


def submit(context, retry=False):
    recover()
    doc = context.get("document", {})
    if doc.get("status") != "available":
        raise ValueError("No available map to extract; refresh parcel sources")
    cache_key = evidence.digest(
        {
            "parcel": context["parcel"],
            "document": doc["content_hash"],
            "prompt": extraction.PROMPT,
            "geometry": [
                f.get("geometry")
                for f in context.get("records", {})
                .get("Parcels", {})
                .get("features", [])
            ],
            "regime": context.get("regime"),
            "jurisdiction": context.get("jurisdiction"),
            "window": datetime.now(timezone.utc).date().isoformat(),
            "depth_version": lot_depth.VERSION,
            "guidance": [
                hashlib.sha256((lot_depth.ROOT / pin["path"]).read_bytes()).hexdigest()
                for pin in json.loads(
                    (
                        lot_depth.ROOT / "data/sources/measurement-guidance/pins.json"
                    ).read_text()
                )
            ],
            "version": 3,
        }
    )
    return submit_task(context, cache_key, retry)


def submit_task(context, cache_key, retry=False):
    recover()
    launch = False
    with LOCK:
        with store.transaction() as db:
            previous = db.execute(
                "SELECT id,status FROM jobs WHERE cache_key=?", (cache_key,)
            ).fetchone()
            if previous and not (
                retry and previous["status"] in ("failed", "cancelled")
            ):
                identity = previous["id"]
            else:
                if previous:
                    db.execute(
                        "UPDATE jobs SET cache_key=? WHERE id=?",
                        (cache_key + ":attempt:" + previous["id"], previous["id"]),
                    )
                queued = db.execute(
                    "SELECT count(*) FROM jobs WHERE status IN ('queued','running')"
                ).fetchone()[0]
                if queued >= 12:
                    raise ValueError("Evidence queue full; retry shortly")
                identity = str(uuid.uuid4())
                db.execute(
                    "INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?,?)",
                    (
                        identity,
                        cache_key,
                        "queued",
                        "queued",
                        now(),
                        now(),
                        json.dumps(context),
                        None,
                        None,
                    ),
                )
                launch = True
        if launch:
            POOL.submit(work, identity)
    return read(identity)
